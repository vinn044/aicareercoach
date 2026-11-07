"""Tests for courses.seed data migration (teacher is_staff persisted in DB)."""

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class SeedMigrationTeacherStaffTests(TestCase):
    """
    SCRUM-14: Seeded teacher accounts must have is_staff=True in the database
    so permission checks (e.g. teacher-only views) work on a fresh migrate.
    """

    def test_seeded_teacher_users_are_staff_in_database(self):
        for username in ('teacher1', 'teacher2'):
            with self.subTest(username=username):
                user = User.objects.get(username=username)
                self.assertTrue(
                    user.is_staff,
                    f'{username} must have is_staff=True after seed migration',
                )

    def test_seeded_student_users_are_not_staff(self):
        for username in ('student1', 'student2'):
            with self.subTest(username=username):
                user = User.objects.get(username=username)
                self.assertFalse(user.is_staff)
