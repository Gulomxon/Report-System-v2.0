from django.contrib.auth.decorators import login_required
import random
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404, redirect
from .models import SysSReports, SysReportAccess, SysRepParams, SysRepParamsHis, SysRepOrders

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def reports(request):
    user = request.user
    
    # Get reports assigned directly to the user
    user_reports = SysReportAccess.objects.filter(user_id=user).values_list('rep_id', flat=True)
    
    # Fetch reports the user has access to
    accessible_reports = SysSReports.objects.filter(id__in=user_reports)

    return render(request, "reports.html", {"reports": accessible_reports})

@login_required
def order_report(request, rep_id):

    # Get the report
    report = get_object_or_404(SysSReports, id=rep_id)

    # Get report parameters
    parameters = SysRepParams.objects.filter(rep_id=rep_id).order_by("id")

    if request.method == "POST":
        # 1. Create SysRepOrders entry
        new_order = SysRepOrders.objects.create(
            rep=report,
            user=request.user,
            job_id=random.randint(100000, 999999),  # Generate a random 6-digit number
            machine="System Report"
        )

        # 2. Create SysRepParamsHis entries
        param_history_entries = []
        for param in parameters:
            param_value = request.POST.get(param.param_name, "")
            param_history_entries.append(SysRepParamsHis(order=new_order, param_name=param.param_name, value=param_value))

        # Bulk insert to optimize performance
        SysRepParamsHis.objects.bulk_create(param_history_entries)

        # 3. Update progress to 5 after params are added
        new_order.progress = 5
        new_order.save()

        return redirect("orders")  # Redirect to orders page after submission
    
    has_access = SysReportAccess.objects.filter(rep_id=rep_id, user_id=request.user.id).exists()

    if has_access:
        context = {
            "report": report,
            "parameters": parameters
        }
    else:
        context = {
            "error_code" : "005",
            "error_message" : "You are not allowed to this report!!!"
        }
    return render(request, "order_report.html", context)

@login_required
def order_detail_api(request, order_id):
    order = get_object_or_404(SysRepOrders, id=order_id, user=request.user)
    params = SysRepParamsHis.objects.filter(order=order)

    data = {
        "order_id": order.id,
        "report_name": order.rep.name,  # Assuming `rep` has `rep_name`
        "progress": order.progress,
        "status": order.state,
        "message": order.message,
        "date_begin": order.date_begin.strftime("%Y-%m-%d %H:%M:%S"),
        "date_end": order.date_end.strftime("%Y-%m-%d %H:%M:%S") if order.date_end else None,
        "parameters": [{"name": p.param_name, "value": p.value} for p in params]
    }

    return JsonResponse(data)

@login_required
def analytics(request):
    return render(request, "analytics.html")

@login_required
def orders(request):
    user_orders = SysRepOrders.objects.filter(user=request.user).order_by('-date_begin')
    return render(request, 'orders.html', {'orders': user_orders})

@login_required
def settings(request):
    return render(request, "settings.html")

@login_required
def support(request):
    return render(request, "support.html")