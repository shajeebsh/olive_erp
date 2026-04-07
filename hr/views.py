from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Employee, LeaveRequest, Attendance, PayrollPeriod, Payslip
from .forms import EmployeeForm, LeaveRequestForm
from core.utils import get_user_company

@login_required
def employees(request):
    company = get_user_company(request)
    qs = Employee.objects.filter(company=company).select_related('user', 'department')
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(employee_id__icontains=query))
    context = {'employees': qs, 'query': query}
    return render(request, 'hr/employees.html', context)

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.company = get_user_company(request)
            employee.save()
            return redirect('hr:employees')
    else:
        form = EmployeeForm()
    return render(request, 'hr/employee_form.html', {'form': form, 'action': 'Create'})

@login_required
def employee_edit(request, pk):
    company = get_user_company(request)
    employee = get_object_or_404(Employee, pk=pk, company=company)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('hr:employees')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'hr/employee_form.html', {'form': form, 'employee': employee})

@login_required
def leave(request):
    company = get_user_company(request)
    qs = LeaveRequest.objects.filter(company=company).select_related('employee__user').order_by('-start_date')
    context = {'leave_requests': qs}
    return render(request, 'hr/leave.html', context)

@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_req = form.save(commit=False)
            company = get_user_company(request)
            leave_req.company = company
            # Find employee for current user
            employee = Employee.objects.filter(user=request.user, company=company).first()
            if employee:
                leave_req.employee = employee
                leave_req.save()
            return redirect('hr:leave')
    else:
        form = LeaveRequestForm()
    return render(request, 'hr/leave_form.html', {'form': form})

@login_required
def attendance(request):
    company = get_user_company(request)
    qs = Attendance.objects.filter(company=company).select_related('employee__user').order_by('-date')
    context = {'attendance_list': qs}
    return render(request, 'hr/attendance.html', context)

@login_required
def payroll(request):
    company = get_user_company(request)
    qs = PayrollPeriod.objects.filter(company=company).order_by('-start_date')
    context = {'payroll_periods': qs}
    return render(request, 'hr/payroll_list.html', context)

@login_required
def payroll_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        company = get_user_company(request)
        
        period = PayrollPeriod.objects.create(
            company=company,
            name=name,
            start_date=start_date,
            end_date=end_date
        )
        
        # Auto-generate payslips for all active employees
        employees = Employee.objects.filter(company=company)
        for emp in employees:
            Payslip.objects.create(
                payroll_period=period,
                employee=emp,
                basic_salary=emp.salary,
                allowances=0,
                deductions=0
            )
            
        return redirect('hr:payroll_detail', pk=period.pk)
    return render(request, 'hr/payroll_form.html')

@login_required
def payroll_detail(request, pk):
    company = get_user_company(request)
    period = get_object_or_404(PayrollPeriod, pk=pk, company=company)
    payslips = period.payslips.select_related('employee__user')
    context = {
        'period': period,
        'payslips': payslips
    }
    return render(request, 'hr/payroll_detail.html', context)
