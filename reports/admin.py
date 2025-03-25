from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django.forms import ModelForm, Select

admin.site.unregister(Group)

@admin.register(SysSReports)  # Register with ModelAdmin
class SysSReportsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner__cb_id", "rep_type", "job", "uploadable", "module", "template")
    list_filter = ("rep_type", "job", "uploadable")  # Sidebar filters
    list_display_links = ("id", "name", "owner__cb_id")
    search_fields = ("name", "owner__cb_id", "department", "position")  # Search functionality
    ordering = ("id",)  # Default sorting by ID
    readonly_fields = ("id",)  # ID should not be editable
    list_editable = ("rep_type", "job", "uploadable", "module")  # Make fields editable in list view
    fieldsets = (
        ("Report Details", {"fields": ("name", "owner", "rep_type")}),
        ("Job & Upload", {"fields": ("job", "uploadable", "module")}),
        ("File Upload", {"fields": ("template",)}),
    )

@admin.register(SysModules)
class SysModulesAdmin(admin.ModelAdmin):
    list_display = ("rep", "module_code", "list_id", "resource", "module_type", "row_number")
    readonly_fields = ("module_code",)  # Prevent manual editing of module_code
    search_fields = ("module_code", "resource")

@admin.register(SysRepParams)
class SysRepParamsAdmin(admin.ModelAdmin):
    list_display = ("rep", "param_name", "type")  # Show fields in the list view
    search_fields = ("param_name",)

@admin.register(SysRepOrders)
class SysRepOrdersAdmin(admin.ModelAdmin):
    list_display = ("rep", "user", "progress", "state", "date_begin", "date_end")
    list_filter = ("state", "date_begin")
    search_fields = ("rep__name", "user__login")

class SysRepParamsHisForm(ModelForm):
    class Meta:
        model = SysRepParamsHis
        fields = "__all__"  # Include all fields
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk and hasattr(self.instance, "order_id"):  # Check if instance has order_id
            # Get the report linked to the order
            report = SysRepOrders.objects.get(id=self.instance.order_id).rep  
            
            # Fetch only valid param_names related to the report
            valid_params = SysRepParams.objects.filter(rep=report).values_list("param_name", "param_name")
            
            # Assign choices to param_name
            self.fields["param_name"].widget = Select(choices=[("", "---------")] + list(valid_params))
        
        # Disable editing if object already exists
        if self.instance.pk:
            self.fields["param_name"].disabled = True

# Admin Panel Configuration
class SysRepParamsHisAdmin(admin.ModelAdmin):
    form = SysRepParamsHisForm  # Use the custom form
    list_display = ("order", "param_name", "value")  # Display fields
    list_filter = ("param_name",)
    search_fields = ("param_name", "order__id")

admin.site.register(SysRepParamsHis, SysRepParamsHisAdmin)

@admin.register(SysReportAccess)
class SysReportAccessAdmin(admin.ModelAdmin):
    list_display = ('rep_id', 'user_id', 'accessed_date')
    list_filter = ('accessed_date',)

@admin.register(SysAccessGroupUsers)
class SysAccessGroupUsersAdmin(admin.ModelAdmin):
    list_display = ("group_code", "group_name", "user")
    search_fields = ("group_code", "group_name", "user__fio")
    list_filter = ("group_code",)

@admin.register(SysAccessGroup)
class SysAccessGroupAdmin(admin.ModelAdmin):
    list_display = ("group_code", "group_name", "rep_id")
    search_fields = ("group_code", "group_name")
    list_filter = ("group_code", "rep_id")
