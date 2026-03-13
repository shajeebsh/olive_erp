from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Employee, LeaveRequest, Attendance
from .forms import EmployeeForm, LeaveRequestForm

@login_required
def employees(request):
    qs = Employee.objects.select_related('user', 'department').all()
    query = request.GET.get('q', '')
    if query:
        qs = qs.filter(Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(employee_id__icontains=query))
    context = {'employees': qs, 'query': query}
    return render(request, 'hr/employees.html', context)

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
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
    qs = LeaveRequest.objects.select_related('employee__user').all().order_by('-start_date')
    context = {'leave_requests': qs}
    return render(request, 'hr/leave.html', context)

@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_req = form.save(commit=False)
            # Find employee for current user
            employee = Employee.objects.filter(user=request.user).first()
            if employee:
                leave_req.employee = employee
                leave_req.save()
            return redirect('hr:leave')
    else:
        form = LeaveRequestForm()
    return render(request, 'hr/leave_form.html', {'form': form})

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hr:employees')
    else:
        form = EmployeeForm()
    return render(request, 'hr/employee_form.html', {'form': form, 'action': 'Create'})


@login_required
def attendance(request):
    qs = Attendance.objects.select_related('employee__user').all().order_by('-date')
    context = {'attendance_list': qs}
    return render(request, 'hr/attendance.html', context)

@login_required
def payroll(request):
    # Payroll is a complex dashboard or list
    return render(request, 'hr/payroll.html')
