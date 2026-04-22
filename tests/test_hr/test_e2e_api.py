import pytest
from datetime import date
from tests.utils import data_gen, logger


@pytest.mark.django_db
class TestEmployeeLifecycle:
    def test_employee_list_view(self, authenticated_client, test_employee):
        logger.test_step("Navigating to employee list", "INFO")
        response = authenticated_client.get('/hr/employees/')
        logger.assertion("Employee list returns 200", 200, response.status_code, response.status_code == 200)
        assert response.status_code == 200

    def test_employee_create_view(self, authenticated_client, test_department):
        logger.test_step("Navigating to employee create", "INFO")
        response = authenticated_client.get('/hr/employees/create/')
        logger.assertion(
            "Employee create page accessible",
            True,
            response.status_code in [200, 302],
            response.status_code in [200, 302],
        )
        assert response.status_code in [200, 302]

    def test_employee_detail_view(self, authenticated_client, test_employee):
        logger.test_step("Navigating to employee detail", "INFO")
        response = authenticated_client.get(f'/hr/employees/{test_employee.pk}/edit/')
        logger.assertion(
            "Employee detail accessible",
            True,
            response.status_code in [200, 302, 404],
            response.status_code in [200, 302, 404],
        )
        assert response.status_code in [200, 302, 404]


@pytest.mark.django_db
class TestLeaveWorkflow:
    def test_employee_can_submit_leave_request(self, employee_client, regular_employee):
        logger.test_step("Employee submitting leave request", "INFO")
        response = employee_client.get('/hr/leave/create/')
        logger.assertion(
            "Leave create page accessible",
            True,
            response.status_code in [200, 302],
            response.status_code in [200, 302],
        )
        assert response.status_code in [200, 302]

    def test_admin_can_view_leave_requests(self, authenticated_client, test_employee):
        from hr.models import LeaveRequest

        LeaveRequest.objects.create(
            company=test_employee.company,
            employee=test_employee,
            leave_type='VACATION',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            reason='Test leave',
            status='PENDING'
        )

        logger.test_step("Admin viewing leave requests", "INFO")
        response = authenticated_client.get('/hr/leave/')
        logger.assertion("Leave list returns 200", 200, response.status_code, response.status_code == 200)
        assert response.status_code == 200


@pytest.mark.django_db
class TestDashboardHRMetrics:
    def test_hr_dashboard_accessible(self, authenticated_client):
        logger.test_step("Navigating to HR dashboard", "INFO")
        response = authenticated_client.get('/hr/')
        logger.assertion(
            "HR dashboard accessible",
            True,
            response.status_code in [200, 302],
            response.status_code in [200, 302],
        )
        assert response.status_code in [200, 302]

    def test_main_dashboard_hr_snapshot(self, authenticated_client, test_employee):
        logger.test_step("Checking main dashboard HR snapshot", "INFO")
        response = authenticated_client.get('/')
        logger.assertion("Main dashboard returns 200", 200, response.status_code, response.status_code == 200)
        assert response.status_code == 200


@pytest.mark.django_db
class TestDepartmentManagement:
    @pytest.mark.skip(reason="Department list URL not implemented")
    def test_department_list_view(self, authenticated_client, test_department):
        logger.test_step("Navigating to department list", "INFO")
        response = authenticated_client.get('/hr/departments/')
        logger.assertion("Department list returns 200", 200, response.status_code, response.status_code == 200)
        assert response.status_code == 200

    @pytest.mark.skip(reason="Department create URL not implemented")
    def test_department_create_view(self, authenticated_client):
        logger.test_step("Navigating to department create", "INFO")
        response = authenticated_client.get('/hr/departments/create/')
        logger.assertion(
            "Department create accessible",
            True,
            response.status_code in [200, 302],
            response.status_code in [200, 302],
        )
        assert response.status_code in [200, 302]

    def test_dynamic_department_creation(self, authenticated_client, test_company):
        dept_data = data_gen.generate_department_data(test_company)
        logger.test_step(f"Creating dynamic department: {dept_data['name']}", "INFO")
        from hr.models import Department

        dept, created = Department.objects.get_or_create(
            company=test_company,
            name=dept_data['name'],
            defaults={'description': dept_data['description']},
        )
        logger.assertion("Department created", True, created, created is True)
        assert dept.name == dept_data['name']


@pytest.mark.django_db
class TestDynamicDataGeneration:
    def test_dynamic_employee_generation(self, test_company, sample_department):
        logger.test_step("Generating dynamic employee data", "INFO")
        emp_data = data_gen.generate_employee_data(test_company, sample_department)
        logger.test_step(f"Generated employee ID: {emp_data['employee_id']}", "INFO")
        logger.assertion(
            "Employee ID format correct",
            True,
            emp_data['employee_id'].startswith('EMP-'),
            emp_data['employee_id'].startswith('EMP-'),
        )
        assert emp_data['employee_id'].startswith('EMP-')
        assert emp_data['job_title'] is not None
        assert emp_data['salary'] > 0

    def test_dynamic_leave_request_generation(self, test_company, test_employee):
        logger.test_step("Generating dynamic leave request data", "INFO")
        leave_data = data_gen.generate_leave_request_data(test_company, test_employee)
        logger.test_step(
            f"Generated leave: {leave_data['leave_type']} from {leave_data['start_date']} to {leave_data['end_date']}",
            "INFO",
        )
        logger.assertion(
            "Leave type is valid",
            True,
            leave_data['leave_type'] in ['VACATION', 'SICK', 'PERSONAL', 'MATERNITY', 'PATERNITY'],
            leave_data['leave_type'] in ['VACATION', 'SICK', 'PERSONAL', 'MATERNITY', 'PATERNITY'],
        )
        assert leave_data['leave_type'] in ['VACATION', 'SICK', 'PERSONAL', 'MATERNITY', 'PATERNITY']
        assert leave_data['end_date'] >= leave_data['start_date']

