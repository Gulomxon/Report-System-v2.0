from django.urls import path
from .views import *

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("reports/", reports, name="reports"),
    path("analytics/", analytics, name="analytics"),
    path("settings/", settings, name="settings"),
    path("orders/", orders, name="orders"),
    path("support/", support, name="support"),
    path('order_report/<int:rep_id>/', order_report, name='order_report'),
    path('orders/detail/<int:order_id>/', order_detail_api, name='order_detail_api'),
]
