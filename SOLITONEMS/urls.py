
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('', include('employees.urls')),
    path('admin/', admin.site.urls),
    path('payroll/',include('payroll.urls')),
    path('leave/',include('leave.urls')),
    path('role/',include('role.urls')),
    path('settings/',include('settings.urls'))
]
