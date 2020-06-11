from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.forms import model_to_dict
import json

from django.contrib.auth.decorators import login_required

import datetime
from calendar import HTMLCalendar
from collections import namedtuple
from employees.models import Employee
from django.db import connection
from organisation_details.decorators import organisationdetail_required
from organisation_details.models import (
    Department, 
    Team)
from .models import (
    Leave_Types,
    LeaveApplication,
    annual_planner,
    Leave_Records
)
from leave.services import send_leave_application_email,send_leave_response_email
from leave.selectors import get_supervisor_users, get_hod_users, get_hr_users

from holidays.models import Holiday


def get_current_user(request, need):
    user = request.user  # getting the current logged in User

    cur_user = f'{user.solitonuser.employee.first_name} {user.solitonuser.employee.last_name}'
    # cur_role = user.solitonuser.soliton_role.name
    user_department = user.solitonuser.employee.organisationdetail.department.id
    user_team = user.solitonuser.employee.organisationdetail.team.id
    cur_id = user.solitonuser.employee.id
    gender = user.solitonuser.employee.gender

    if need == "name":
        return cur_user
    elif need == "dept":
        return user_department
    elif need == "team":
        return user_team
    elif need == "id":
        return cur_id
    elif need == "gender":
        return gender
    else:
        return 0


@login_required
@organisationdetail_required
def leave_dashboard_page(request):
    applications, role = "", ""
    user = request.user

    if user.is_supervisor:
        applications = LeaveApplication.objects.filter(supervisor_status="Pending",\
            team=get_current_user(request,"team"))
        role = "is_supervisor"
        
    elif user.is_hod:     
        applications = LeaveApplication.objects.filter(hod_status="Pending", \
                                                       supervisor_status="Approved",
                                                       department=get_current_user(request, "dept")) \
            .order_by('apply_date')
        role = "is_hod"

    elif user.is_hr:
        applications = LeaveApplication.objects \
            .filter(hr_status="Pending", supervisor_status="Approved", \
                    hod_status="Approved").order_by('apply_date')
        role = "is_hr"    

    leave_types = Leave_Types.objects.all()

    context = {
        "leave_dashboard_page": "active",
        "applications": applications,
        "role": role
    }
    return render(request, 'leave/dashboard.html', context)


def leave_types_page(request):
    # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request, 'ems_auth/login.html', {"message": None})

    context = {
        "leave_page": "active",
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
            type_leave = Leave_Types(leave_type=leave_type, leave_days=leave_days, description=desc)

            # Saving the leave type instance
            type_leave.save()
            messages.success(request, f'Successfully Added {leave_type} leave type')

            return redirect('leave_types_page')

        except:
            messages.error(request, f'Info Not Saved, Check Your inputs and try again!!!')

            return redirect('leave_types_page')

    else:
        messages.error(request, f'Something Went Wrong')

        return redirect('leave_types_page')


@login_required
def edit_leave_type_page(request, id):
    # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request, 'ems_auth/login.html', {"message": None})

    leave = Leave_Types.objects.get(pk=id)

    context = {
        "leave_page": "active",
        "leave": leave
    }
    return render(request, 'leave/edit_leave_type.html', context)

@login_required
def edit_leave_type(request, id):
    leave = Leave_Types.objects.get(pk=id)

    if request.POST:
        leave_type=request.POST.get('leave_type')        
        no_of_days=request.POST.get('no_of_days')
        description=request.POST.get('description')

        Leave_Types.objects.filter(id=leave.id).update(
            leave_type=leave_type,
            leave_days=no_of_days,
            description=description
            )
        messages.success(request, "Leave Type Info Updated Successfully")

    context = {
        "leave_page": "active",
        "leave": leave
    }
    return redirect('leave_types_page')
    # return render(request, 'leave/leave_type.html', context)

@login_required
def delete_leave_type(request, id):
    leave = Leave_Types.objects.get(pk=id)

    leave.delete()
    messages.success(request, "Leave Type Deleted")

    context = {
        "leave_page": "active",
        "leave": leave
    }
    return redirect('leave_types_page')

@organisationdetail_required
@login_required
def apply_leave_page(request):    
    employee = request.user.solitonuser.employee
    leave_record = Leave_Records.objects.get(employee=employee, \
        leave_year=datetime.date.today().year)
    leave_balance = -1
    try:
        leave_balance = leave_record.balance
    except:
        pass
        
    context = {
        "leave_page": "active",
        "apps": LeaveApplication.objects.filter(employee=get_current_user(request, "id")),
        "l_types": Leave_Types.objects.all(),
        "l_balance": leave_balance,
        "gender": request.user.solitonuser.employee.gender,
        "role": "user"
    }
    return render(request, "leave/leave.html", context)


@login_required
def apply_leave(request):
    if request.method == "POST":

        user = request.user  
        employee = user.solitonuser.employee
        department = Department.objects.get(pk=employee.organisationdetail.department.id)
        team = Team.objects.get(pk=employee.organisationdetail.team.id)

        leave_record = Leave_Records.objects. \
            get(employee=employee, leave_year=datetime.date.today().year)

        l_type = Leave_Types.objects.get(pk=request.POST["ltype"])

        s_date = request.POST["s_date"]
        e_date = request.POST["e_date"]

        n_days = int(request.POST["no_days"]) 
        l_days = l_type.leave_days

        if n_days <= l_days:
            new_balance = 0
            if l_type.leave_type == "Annual":
                curr_balance = leave_record.balance
                new_balance = curr_balance - n_days

            if n_days <= new_balance:
                if user.is_supervisor:                    
                    leave_application = LeaveApplication(
                                employee=employee, 
                                leave_type=l_type, 
                                start_date=s_date, 
                                end_date=e_date, 
                                no_of_days=n_days,
                                balance=curr_balance, 
                                department=department,
                                team=team,
                                supervisor=employee,
                                supervisor_status="Approved",
                                )

                    leave_application.save()

                    approvers = get_hod_users(employee)
                    send_leave_application_email(approvers, leave_application)
                elif user.is_hod:
                    leave_application = LeaveApplication(
                                employee=employee, 
                                leave_type=l_type, 
                                start_date=s_date, 
                                end_date=e_date, 
                                no_of_days=n_days,
                                balance=curr_balance, 
                                department=department,
                                team=team,
                                supervisor_status="Approved",
                                hod=employee,
                                hod_status="Approved"
                                )

                    leave_application.save()

                    approvers = get_hr_users()
                    send_leave_application_email(approvers, leave_application)
                else:
                    leave_application = LeaveApplication(
                                employee=employee, 
                                leave_type=l_type, 
                                start_date=s_date, 
                                end_date=e_date, 
                                no_of_days=n_days,
                                balance=curr_balance, 
                                department=department,
                                team=team
                                )

                    leave_application.save()

                    approvers = get_supervisor_users(employee)
                    send_leave_application_email(approvers, leave_application)
                
                messages.success(request, 'Leave Request Sent Successfully')

                return redirect('apply_leave_page')

            else:
                messages.warning(request, f'You have insufficient {l_type} leave Balance {n_days}')                
                return redirect('apply_leave_page')

        else:
            messages.warning(request, f'You cannot Request({n_days}) for more than the\
                {l_type.leave_type} leave days ({l_type.leave_days})')
            return render(request, "leave/leave.html")

@login_required
def edit_leave_application(request):
    if request.method == "POST":
        applicant = request.user.solitonuser.employee

        application_id = request.POST.get("application_id")

        leave_application = LeaveApplication.objects.get(pk=application_id)

        leave_application.no_of_days = request.POST.get("no_days")
        leave_application.start_date = request.POST.get("s_date")
        leave_application.end_date = request.POST.get("e_date")
        leave_application.remarks = request.POST.get("remark")
        leave_application.save()

        messages.success(request, 'Changes saved Successfully')
        return JsonResponse({'success': True, 'redirect': "apply_leave_page"})
    
@login_required
def delete_leave_application(request):
    if request.method == "POST":
        applicant = request.user.solitonuser.employee

        application_id = request.POST.get("application_id")

        leave_application = LeaveApplication.objects.get(pk=application_id)        
        leave_application.delete()

        messages.success(request, 'Request Deleted')
        return JsonResponse({'success': True, 'redirect': "apply_leave_page"})

@login_required
def leave_application_details(request, id, role):
    leave_application = LeaveApplication.objects.get(id=id)

    context={
        "leave_application":leave_application,
        "role": role
    }

    return render(request, "leave/leave_application_details.html", context)

def check_leave_requirement(request, start_date, end_date):
    date_format="%Y-%m-d%" 

    start_date = datetime.datetime.strptime(start_date, date_format)
    apply_date = datetime.datetime.strptime(datetime.date.today(), date_format)

    difference=get_public_days(apply_date,start_date)

    if difference<7:
        messages.warning(request, \
            'leave application should be made 7 days before the leave start date')
    
    return JsonResponse({'message': 'leave application should be made 7 days before the leave start date'})

def approve_leave(request):
    if request.method == "POST":
        user = request.user  
        application_id = request.POST.get("application_id")
        comment = request.POST.get("comment")

        leave_application = LeaveApplication.objects.get(pk=application_id)
        
        employee = leave_application.employee
        l_type = leave_application.leave_type
        n_days = leave_application.no_of_days

        leave_record = Leave_Records.objects. \
            get(employee=employee, leave_year=datetime.date.today().year)

        if user.is_supervisor:
            leave_application.supervisor = user.solitonuser.employee
            leave_application.supervisor_status="Approved"
            leave_application.supervisor_comment = request.POST.get("comment")
            leave_application.save()
            
            hods = get_hod_users(employee)

            send_leave_application_email(hods, leave_application)

        elif user.is_hod:
            leave_application.hod = user.solitonuser.employee
            leave_application.hod_status = "Approved"
            leave_application.hod_comment = request.POST.get("comment")
            leave_application.save()

            hrs = get_hr_users(employee)

            send_leave_application_email(hrs, leave_application)

        elif user.is_hr:
            curr_balance = int(leave_record.balance)
            total_applied = int(leave_record.leave_applied)
            total_taken = int(leave_record.total_taken)

            if l_type.leave_type == "Annual":
                new_balance = int(curr_balance) - int(n_days)

                total_applied += 1
                total_taken += int(n_days)

            else:
                new_balance = curr_balance

            leave_application.hr=user.solitonuser.employee
            leave_application.hr_status = "Approved"
            leave_application.hr_comment = request.POST.get("comment")
            leave_application.balance=new_balance
            leave_application.overall_status = "Approved"

            leave_application.save()
                        
            Leave_Records.objects.filter(
                employee=employee, 
                leave_year=datetime.date.today().year).update(
                    leave_applied=total_applied, 
                    total_taken=total_taken, 
                    balance=new_balance
                    )
        
            send_leave_response_email(leave_application)

        else:
            messages.warning(request, 'Leave Approval Failed')
            return JsonResponse({'success': True, 'redirect': "leave_dashboard_page"})

        messages.success(request, 'Leave Approved Successfully')
        return JsonResponse({'success': True, 'redirect': "leave_dashboard_page"})

def reject_leave(request):
    if request.method == "POST":
        user = request.user  
        employee = user.solitonuser.employee

        application_id = request.POST.get("application_id")
        comment = request.POST.get("comment")

        leave_application = LeaveApplication.objects.get(pk=application_id)

        if user.is_supervisor:            
            leave_application.supervisor = employee
            leave_application.supervisor_status = "Rejected"
            leave_application.supervisor_comment = comment
            
            leave_application.save()

            send_leave_response_email(leave_application, "Supervisor", "Rejected")

        elif user.is_hod:
            leave_application.hod = employee
            leave_application.hod_status = "Rejected"
            leave_application.hod_comment = comment
            
            leave_application.save()

            send_leave_response_email(leave_application, "HOD", "Rejected")

        elif user.is_hr: 
            leave_application.hr = employee
            leave_application.hr_status = "Rejected"
            leave_application.hr_comment = comment
            
            leave_application.save()

            send_leave_response_email(leave_application, "HR", "Rejected")

        else:
            messages.warning(request, 'Activity Failed')
            return JsonResponse({'success': True, 'redirect': "leave_dashboard_page"})

        messages.success(request, 'Leave request rejected Successfully')
        return JsonResponse({'success': True, 'redirect': "leave_dashboard_page"})

def leave_records(request):
    if not request.user.is_authenticated:
        return render(request, "ems_auth/login.html", {"message": None})

    current_year = datetime.date.today().year
    context = {
        "leave_page": "active",
        "leave_records": Leave_Records.objects.filter(leave_year=current_year),
        "leave_year": current_year,
        "years": generate_years(),
    }
    return render(request, "leave/leave_records.html", context)


def add_leave_records(request):
    yr = 0

    if request.method == "POST":
        yr = request.POST["leave_yr"]

        leave_records = Leave_Records.objects.all()
        employees = Employee.objects.all()

        if not leave_records:
            for employee in employees:
                employee_name = employee.id

                leave_record = Leave_Records(employee=employee, leave_year=yr, \
                                             entitlement=21, residue=0, leave_applied=0, total_taken=0, \
                                             balance=21)

                leave_record.save()
            messages.success(request, f'Leave Records Generated for the Year - {yr}')
        else:
            try:
                year_count = leave_records.filter(leave_year=yr).count()

                entitlement = 21

                if year_count == 0:
                    for employee in employees:
                        employee_name = employee.id

                        leave_balance = leave_records.get(employee=employee, leave_year=int(yr) - 1)

                        balance = leave_balance.balance

                        residue = 0
                        if balance > 5:
                            residue = 5
                        else:
                            residue = balance

                        initial_balance = entitlement + residue

                        leave_record = Leave_Records(employee=employee, leave_year=yr, \
                                                     entitlement=entitlement, residue=residue, leave_applied=0,
                                                     total_taken=0, \
                                                     balance=initial_balance)

                        leave_record.save()
                    messages.success(request, f'Leave Records Generated for the Year - {yr}')
            except:
                messages.warning(request, f'Records Not created for the year - {yr}')
        context = {
            "leave_page": "active",
            "leave_records": Leave_Records.objects.filter(leave_year=yr),
            "leave_year": yr,
            "years": generate_years()
        }
        return render(request, "leave/leave_records.html", context)


def generate_years():
    current_year = datetime.date.today().year

    next_years = []

    start_year = current_year - 3
    i = 0
    while i < 8:
        next_years.append(start_year + 1)
        start_year += 1
        i += 1

    return next_years


def get_public_days(start_date, end_date):
    date_format = "%Y-%m-%d"
    from_date = start_date
    to_date = datetime.strptime(end_date, date_format)

    date_difference = to_date - from_date

    all_days_between = (date_difference.days + 1)

    # holidays = Holiday.objects.filter(holiday_date__range=(from_date, to_date)).count()

    #Getting all holiday objects
    holidays = Holiday.objects.all()

    public_days=0
    k = 0
    while k <= all_days_between:
        check_date = from_date + datetime.timedelta(days=k)

        is_holiday = holidays.filter(date=check_date.date()).exists()

        if check_date.weekday() == 6 or is_holiday:
            public_days +=1

        k = k + 1

    days_difference=all_days_between-public_days
    
    return days_difference

def get_end_date(request):
    if request.method=="GET":
        date_format = "%Y-%m-%d"

        #Capturing values from the request       
        start_date = request.GET["startDate"]
        days = request.GET["no_of_days"]

        #Checking 7 days requirement
        # today = date.today()
        # apply_date = datetime(year=today.year, month=today.month, day=today.day)

        # difference=get_public_days(apply_date,start_date)

        # if difference<7:
        #     # messages.warning(request, \
        #         # 'leave application should be made 7 days before the leave start date')

        #     return JsonResponse({'success': False,\
        #         'message': 'leave application should be made 7 days before the leave start date'})


        if start_date and days:
            no_days = int(days)

            from_date = datetime.datetime.strptime(start_date, date_format)
            
            #Getting all holiday objects
            holidays = Holiday.objects.all()

            k = 0
            public_days = 0
            while k < no_days:
                check_date = from_date + datetime.timedelta(days=k)

                is_holiday = holidays.filter(date=check_date.date()).exists()

                if check_date.weekday() == 6 or is_holiday:
                    public_days+=1
                    #continue

                k += 1
            
            end_date = from_date + datetime.timedelta(days=(no_days+public_days)-1)

            if end_date is None:
                return JsonResponse({'success': False, 'message': 'No Date returned'})

            return JsonResponse({'success': True, 'end_date': end_date.date()})
        else:
            return JsonResponse({'success': False, 'message': "Start Date and/or Number of days Not Specified"})

def get_no_of_days(request):
    if request.method=="GET":
        employee = request.user.solitonuser.employee
        leave_type = request.GET['leave_type']        
        no_of_days = 0

        if leave_type:
            leave = Leave_Types.objects.get(id=leave_type)

            if leave.leave_type != "Annual":                
                no_of_days=leave.leave_days
                
            else:
                leave_records = Leave_Records.objects.get(employee=employee,\
                    leave_year=datetime.date.today().year)

                no_of_days = leave_records.balance
        
            return JsonResponse({'success': True, 'no_of_days': no_of_days, 'leave':leave.leave_type})
        else:
            return JsonResponse({'success': False, 'message': 'No such Leave Type'})


def annual_calendar(request):
    # first_day = calendar.TextCalendar(calendar.MONDAY)
    # annual_calendar = first_day.formatyear(2019)
    context = {
        "annual_calendar": "active",
        "employees": Employee.objects.all()
    }

    return render(request, 'leave/annual_calendar.html', context)


def leave_planer(request):
    # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request, 'registration/login.html', {"message": None})

    current_year = datetime.datetime.now().year

    context = {
        "leave_planner": "active",
        "planner": annual_planner.objects.all(),
        "leave_types": Leave_Types.objects.all(),
        "employees": Employee.objects.all(),
        "year": current_year
    }
    return render(request, 'leave/leave_planner.html', context)


def add_new_absence(request):
    if request.method == "POST":
        employee = Employee.objects.get(pk=request.user.id)
        leave = Leave_Types.objects.get(pk=request.POST["leave_type"])
        from_date = request.POST["from_date"]
        to_date = request.POST["to_date"]

    date_format = "%Y-%m-%d"
    leave_year = datetime.datetime.strptime(from_date, date_format).year
    # leave_month = calendar.month_name[datetime.datetime.strptime(from_date, date_format).month]
    # leave_days = calculate_leave_days(from_date, to_date)

    try:
        if leave_days >= 1:
            planner = annual_planner(leave_year=leave_year, date_from=from_date, date_to=to_date, \
                                     employee=employee, leave=leave, leave_month=leave_month[0:3],
                                     no_of_days=leave_days)

            planner.save()

            messages.success(request, f'Data Saved Successfully')

            overlaps = get_leave_overlap(from_date, to_date)

            if overlaps > 1:
                messages.warning(request, f'There are {overlaps - 1} Overlap(s) during the selected period.\
                    \n Click to View Overlaps')

        else:
            messages.warning(request, f'Invalid Date Range')

        return redirect('leave_planner')

    except:
        messages.error(request, f'Data Not Saved, Check you inputs and try again!')

        #  return redirect('leave_planner')


def get_leave_overlap(start_date, end_date):
    absences = annual_planner.objects.all()

    Range = namedtuple('Range', ['start', 'end'])

    date_format = "%Y-%m-%d"
    from_date = datetime.datetime.strptime(start_date, date_format)
    to_date = datetime.datetime.strptime(end_date, date_format)

    r1 = Range(start=from_date.date(), end=to_date.date())

    overlap = 0
    overlap_count = 0
    for absence in absences:
        r2 = Range(start=absence.date_from, end=absence.date_to)
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)

        if overlap > 0:
            overlap_count += 1

    return overlap_count


def Leave_planner_summary(request):
    # The line requires the user to be authenticated before accessing the view responses.
    if not request.user.is_authenticated:
        # if the user is not authenticated it renders a login page
        return render(request, 'registration/login.html', {"message": None})

    department_id = 0
    team_id = 0
    if request.method == "POST":
        department_id = request.POST["department"]
        team_id = request.POST["team"]

    # Select multiple records
    all_plans = None
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT e.first_name || ' ' || e.last_name as Employee,\
        SUM(CASE WHEN leave_month = 'Jan' THEN no_of_days ELSE 0 END) as Jan,\
        SUM(CASE WHEN leave_month = 'Feb' THEN no_of_days ELSE 0 END) as Feb,\
        SUM(CASE WHEN leave_month = 'Mar' THEN no_of_days ELSE 0 END) as Mar,\
        SUM(CASE WHEN leave_month = 'Apr' THEN no_of_days ELSE 0 END) as Apr,\
        SUM(CASE WHEN leave_month = 'May' THEN no_of_days ELSE 0 END) as May,\
        SUM(CASE WHEN leave_month = 'Jun' THEN no_of_days ELSE 0 END) as Jun,\
        SUM(CASE WHEN leave_month = 'Jul' THEN no_of_days ELSE 0 END) as Jul,\
        SUM(CASE WHEN leave_month = 'Aug' THEN no_of_days ELSE 0 END) as Aug,\
        SUM(CASE WHEN leave_month = 'Sep' THEN no_of_days ELSE 0 END) as Sep,\
        SUM(CASE WHEN leave_month = 'Oct' THEN no_of_days ELSE 0 END) as Oct,\
        SUM(CASE WHEN leave_month = 'Nov' THEN no_of_days ELSE 0 END) as Nov,\
        SUM(CASE WHEN leave_month = 'Dec' THEN no_of_days ELSE 0 END) as Dec\
        FROM employees_employee e LEFT OUTER JOIN leave_annual_planner l ON e.id=l.employee_id\
		WHERE e.id IN \
            (SELECT employee_id FROM employees_organisationdetail \
                WHERE department_id={department_id} AND team_id={team_id})\
        GROUP BY e.id;")
        all_plans = cursor.fetchall()
    # DB API fetchall produces a list of tuples

    context = {
        "plans": all_plans,
        "departments": Department.objects.all(),
        "teams": Team.objects.all()
    }
    return render(request, 'leave/annual_calendar.html', context)


def leave_calendar(request, month=datetime.date.today().month, year=datetime.date.today().year):
    year = int(year)
    month = int(month)

    if year < 1900 or year > 2099:
        year = datetime.date.today().year

    month_name = calendar.month_name[month]

    cal = HTMLCalendar.formatmonth(year, month)

    context = {
        "title": year,
        "calendar": cal
    }
    return render(request, 'leave/leave_calendar.html', context)
