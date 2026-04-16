import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time
from hr.models import Employee, Attendance
from company.models import CompanyProfile
from tests.utils import logger

User = get_user_model()


class AttendanceOnLoginTest(TestCase):
    def setUp(self):
        self.company = CompanyProfile.objects.create(
            name="Test Company",
            email="test@example.com",
            phone="1234567890",
            address="Test Address",
            fiscal_year_start_date=date(2024, 1, 1)
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.employee = Employee.objects.create(
            user=self.user,
            company=self.company,
            employee_id='EMP001',
            department=None,
            job_title='Developer',
            hire_date=date(2024, 1, 1),
            salary=50000,
            contact_info='Contact',
            address='Address',
            emergency_contact='Emergency'
        )

    def test_attendance_created_on_login(self):
        """Test that attendance is created when user logs in."""
        from django.contrib.auth.signals import user_logged_in
        from core.signals import record_attendance_on_login

        logger.test_step("Testing attendance creation on login", "INFO")
        initial_count = Attendance.objects.count()

        user_logged_in.send(sender=User, request=None, user=self.user)

        self.assertEqual(Attendance.objects.count(), initial_count + 1)
        attendance = Attendance.objects.filter(employee=self.employee, date=date.today()).first()
        self.assertIsNotNone(attendance)
        self.assertIsNotNone(attendance.check_in_time)

    def test_no_duplicate_attendance_same_day(self):
        """Test that duplicate attendance is not created for repeated login on same day."""
        from django.contrib.auth.signals import user_logged_in
        from core.signals import record_attendance_on_login

        logger.test_step("Testing no duplicate attendance on same day", "INFO")
        Attendance.objects.create(
            company=self.company,
            employee=self.employee,
            date=date.today(),
            check_in_time=time(9, 0)
        )

        user_logged_in.send(sender=User, request=None, user=self.user)

        self.assertEqual(Attendance.objects.filter(employee=self.employee, date=date.today()).count(), 1)

    def test_no_attendance_for_non_employee_user(self):
        """Test that no attendance is created for non-employee user."""
        from django.contrib.auth.signals import user_logged_in
        from core.signals import record_attendance_on_login

        logger.test_step("Testing no attendance for non-employee user", "INFO")
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )

        initial_count = Attendance.objects.count()
        user_logged_in.send(sender=User, request=None, user=other_user)

        self.assertEqual(Attendance.objects.count(), initial_count)
