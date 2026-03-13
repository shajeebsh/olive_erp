from django.shortcuts import render


def employees(request):
    return render(request, 'hr/employees.html')


def leave(request):
    return render(request, 'hr/leave.html')


def attendance(request):
    return render(request, 'hr/attendance.html')


def payroll(request):
    return render(request, 'hr/payroll.html')
