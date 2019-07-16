from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    Leave_Types, 
    Holidays,
    Approval_Path,
    LeaveApplication
)


@login_required
def leave_dashboard_page(request):
    # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request,'registration/login.html',{"message":None})

    context = {
        "leave_dashboard_page": "active"
    }
    return render(request, 'leave/dashboard.html', context)

def leave_types_page(request):
     # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request,'registration/login.html',{"message":None})

    context = {
        "leave_types_page": "active",
        "types": Leave_Types.objects.all()
    }
    return render(request, 'leave/leave_types.html', context)

def add_new_type(request):
    if request.method == 'POST':
        # Fetching data from the add new leave type form
        leave_type = request.POST['leave_type']
        leave_days = request.POST['leave_days']
        desc = request.POST['desc']

        try:
            # Creating instance of Leave Types
            type_leave = Leave_Types(leave_type=leave_type, leave_days=leave_days,description=desc)
            
            #Saving the leave type instance
            type_leave.save()
            messages.success(request, f'Info Successfully Saved')

            return redirect('leave_types_page')

        except:
            messages.error(request, f'Info Not Saved, Check Your inputs and try again!!!')

            return redirect('leave_types_page')            

    else:
        context = {
            "leave_types_page": "active",
            "failed_msg": "Failed! You performed a GET request"
        }

        return render(request, "employees/failed.html", context)

@login_required
def edit_leave_type_page(request, id):
    # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request, 'registration/login.html', {"message": None})
    
    leave = Leave_Types.objects.get(pk=id)

    context = {
        "leave_types_page": "active",
        "leave": leave
    }
    return render(request, 'leave/leave_type.html', context)

def holidays_page(request):
     # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request,'registration/login.html',{"message":None})

    context = { 
        "holidays_page": "active",
        "holidays": Holidays.objects.all()
    }
    return render(request, 'leave/holidays.html', context)

def add_new_holiday(request):
    if request.method == 'POST':
        # Fetching data from the add new holiday form
        hol_name = request.POST['hol_name']
        hol_date = request.POST['hol_date']
        duration = request.POST['duration']

        try:

            hols = Holidays(holiday_date = hol_date, holiday_name=hol_name, duration=duration)
            hols.save()

            messages.success(request, f'Info Successfully Saved')
            return redirect('holidays_page')

        except:
           messages.error(request, f'Infor Not Saved, Check you inputs and try again!')

           return redirect('holidays_page') 


def approval_path_page(request):
     # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request,'registration/login.html',{"message":None})

    context = {
        "path_page": "active",
        "a_path": Approval_Path.objects.all()
    }

    return render(request, "leave/approval_path.html", context)

def add_new_path(request):
    if request.method=="POST":
        path_name = request.POST["pname"]
        required = request.POST["required"]
        fapproval = request.POST["fapproval"]
        sapproval = request.POST["sapproval"]
        tapproval = request.POST["tapproval"]
        lapproval = request.POST["lapproval"]

    try:
        path_ = Approval_Path(path_name=path_name, required = required, 
        first_approval=fapproval, second_approval = sapproval, fourth_approval = lapproval)

        path_.save()

        messages.success(request, f'Info Successfully Saved')
        return redirect('path_page')

    except:
        messages.error(request, f'Infor Not Saved, Check you inputs and try again!')

        return redirect('path_page')

def apply_leave_page(request):
     #The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request,'registration/login.html',{"message":None})

    context = {
        "path_page": "active",
        "apps": LeaveApplication.objects.all(),
        "l_types":Leave_Types.objects.all()
    }

    return render(request, "leave/apply_leave.html", context)

def apply_leave(request):
    if request.method=="POST":
        #per = request.POST["emp"]
        l_type = Leave_Types.objects.get(pk=request.POST["ltype"])
        s_date = request.POST["s_date"]
        e_date = request.POST["e_date"]

    #try:
    leave_app = LeaveApplication(Employee_Name = "Bright", leave_type = l_type, 
    start_date=s_date, end_date = e_date)

    leave_app.save()

    messages.success(request, f'Info Successfully Saved')
    return redirect('apply_leave_page')

    #return redirect('apply_leave_page')