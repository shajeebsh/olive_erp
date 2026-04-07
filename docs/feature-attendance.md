# Attendance Tracking Feature

## Overview
Attendance is automatically recorded when an employee logs into the system.

## How It Works

### Login Trigger
When a user logs in, the `record_attendance_on_login` signal handler in `core/signals.py` is triggered. This handler:
1. Looks up the user as an `Employee`
2. Checks if attendance already exists for today
3. Creates a new `Attendance` record if none exists

### Key Behaviors
- **One record per day**: If attendance already exists for today for the employee, no duplicate is created
- **Non-blocking**: If attendance recording fails (e.g., user is not an employee), the login still succeeds
- **Company scoping**: Attendance is linked to the employee's company

## Data Model
```python
class Attendance(models.Model):
    company = models.ForeignKey('company.CompanyProfile', ...)
    employee = models.ForeignKey(Employee, ...)
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(...)
```

## End-to-End Scenarios

### Scenario 1: Employee Logs In for First Time Today
1. User enters credentials on login page
2. Django authenticates the user
3. `user_logged_in` signal fires
4. System checks if user has an Employee profile
5. System checks if attendance exists for today
6. New Attendance record created with current time as check_in_time
7. User redirected to dashboard

### Scenario 2: Employee Logs In Multiple Times Same Day
1. Steps 1-5 same as above
2. System finds existing attendance for today
3. No new record created (duplicate prevention)
4. User continues to dashboard

### Scenario 3: Non-Employee User Logs In
1. Steps 1-3 same as above
4. System finds no Employee record for user
5. No attendance created
6. User continues to dashboard normally

### Scenario 4: View Attendance Records
1. Navigate to HR → Attendance
2. View list of all attendance records for user's company
3. Filter by employee, date range
4. View details (check-in, check-out times)

## Testing
Run attendance tests:
```bash
python manage.py test hr.tests.test_attendance
```

Tests verify:
- Attendance is created on login
- Duplicate attendance is not created for same-day logins
- Non-employee users don't create attendance records
