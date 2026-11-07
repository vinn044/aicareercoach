
from django.db.models import Max
from django.test import TestCase
from django.urls import reverse
from datetime import date, timedelta   

from courses.factory import CourseFactory, AccountFactory, InstructorFactory
from courses.models import Course, Account


def _nonexistent_course_pk():
    """PK guaranteed not to match any Course row in the test database."""
    max_pk = Course.objects.aggregate(m=Max('pk'))['m']
    return (max_pk or 0) + 10_000

class CourseViewTestAsStudent(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.student = AccountFactory()
        self.client.login(username=self.student.username, password='password123')

    def test_course_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)

    def test_course_detail_view(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)

    def test_student_cannot_see_new_course_button(self):
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'New Course')

    def test_student_cannot_see_edit_button_on_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertNotContains(response, 'Edit this course')

    def test_student_cannot_see_delete_button_on_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertNotContains(response, 'Delete Course')

    def test_student_can_see_register_button_on_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertContains(response, 'Register course')

    def test_student_can_see_search_bar_on_course_list(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Search for courses...')
    
    def test_student_can_see_course_in_search_results_using_name(self):
        response = self.client.get(reverse('home') + '?q=' + self.course.name)
        self.assertContains(response, self.course.name)

    def test_student_can_see_course_in_search_results_using_description(self):
        response = self.client.get(reverse('home') + '?q=' + self.course.description)
        self.assertContains(response, self.course.name)

    def test_student_can_see_course_in_search_results_using_crn(self):
        response = self.client.get(reverse('home') + '?q=' + self.course.crn)
        self.assertContains(response, self.course.name)

class CourseViewTestAsTeacher(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.teacher = InstructorFactory()
        self.course.instructor = self.teacher
        self.course.save()
        self.client.login(username=self.teacher.username, password='password123')

    def test_course_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)

    def test_course_detail_view(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)
        self.assertContains(response, self.course.instructor.get_full_name())

    def test_teacher_can_see_new_course_button(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'New Course')

    def test_teacher_can_see_edit_button_on_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertContains(response, 'Edit this course')

    def test_teacher_can_see_delete_button_on_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertContains(response, 'Delete Course')

    def test_teacher_cannot_see_register_button_on_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertNotContains(response, 'Register course')


class CourseAccessTestAsNotLoggedIn(TestCase):
    def setUp(self):
        self.course = CourseFactory()

    def test_non_logged_in_user_cannot_access_course_list(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_non_logged_in_user_cannot_access_course_detail(self):
        response = self.client.get(reverse('course_detail', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)

    def test_non_logged_in_user_cannot_access_course_enroll(self):
        response = self.client.get(reverse('course_enroll', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)

    def test_non_logged_in_user_cannot_access_course_drop(self):
        response = self.client.get(reverse('course_drop', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)


class CoursePermissionTests(TestCase):
    def setUp(self):
        self.course = CourseFactory()
        self.student = AccountFactory()
        self.teacher = InstructorFactory()

    def test_students_cannot_access_course_create(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_teachers_can_access_course_create(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 200)

    def test_teacher_can_create_course(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.post(reverse('course_create'), {
            'name': 'New Course',
            'description': 'New course description',
            'crn': 'CRN99',
            'credits': 3,
            'start_date': (date.today() + timedelta(days=1)).isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Course.objects.filter(name='New Course').count(), 1)

    def test_students_cannot_edit_course(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.get(reverse('course_edit', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_teachers_can_edit_course(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.get(reverse('course_edit', args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)

    def test_students_cannot_delete_course(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.post(reverse('course_delete', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())

    def test_teachers_can_delete_course(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.post(reverse('course_delete', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

    def test_student_can_enroll_and_drop_course(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.post(reverse('course_enroll', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.student.account.enrolled_courses.filter(pk=self.course.pk).exists())

        response = self.client.post(reverse('course_drop', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.student.account.enrolled_courses.filter(pk=self.course.pk).exists())

    def test_teacher_cannot_enroll_in_course(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.post(reverse('course_enroll', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('course_detail', args=[self.course.pk]))
        self.assertFalse(self.teacher.account.enrolled_courses.filter(pk=self.course.pk).exists())
class CourseSearchTests(TestCase):
    def setUp(self):
        self.student = AccountFactory()
        self.teacher = InstructorFactory()
        self.course1 = CourseFactory(name='Introduction to Python', crn='PY101')
        self.course2 = CourseFactory(name='Data Structures', crn='DS201')
        self.course3 = CourseFactory(name='Web Development with Django', crn='WB301')
        self.course1.instructor = self.teacher
        self.course1.save()
        self.client.login(username=self.student.username, password='password123')

    def test_search_by_name(self):
        response = self.client.get(reverse('home') + '?q=python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Introduction to Python')
        self.assertNotContains(response, 'Data Structures')

    def test_search_by_crn(self):
        response = self.client.get(reverse('home') + '?q=DS201')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Structures')
        self.assertNotContains(response, 'Introduction to Python')

    def test_search_by_instructor_name(self):
        response = self.client.get(reverse('home') + '?q=Instructor')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Introduction to Python')

    def test_empty_search_returns_all_courses(self):
        response = self.client.get(reverse('home') + '?q=')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Introduction to Python')
        self.assertContains(response, 'Data Structures')
        self.assertContains(response, 'Web Development with Django')

    def test_search_no_results(self):
        response = self.client.get(reverse('home') + '?q=zzznomatch')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Introduction to Python')
        self.assertNotContains(response, 'Data Structures')

class CourseFilterAndSortTests(TestCase):
    def setUp(self):
        self.student = AccountFactory()
        self.instructor_a = InstructorFactory(first_name='Alice', last_name='Able')
        self.instructor_b = InstructorFactory(first_name='Brian', last_name='Baker')

        self.course1 = CourseFactory(
            name='Algorithms',
            crn='AL101',
            credits=3,
            start_date=date(2026, 1, 10),
            end_date=date(2026, 5, 10),
            instructor=self.instructor_a,
        )
        self.course2 = CourseFactory(
            name='Biology',
            crn='BI202',
            credits=4,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 6, 1),
            instructor=self.instructor_b,
        )
        self.client.login(username=self.student.username, password='password123')

    def test_filter_and_sort_controls_render(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="credits"')
        self.assertContains(response, 'name="start_date"')
        self.assertContains(response, 'name="end_date"')
        self.assertContains(response, 'name="sort"')

    def test_selecting_filter_updates_displayed_courses(self):
        response = self.client.get(reverse('home'), {
            'credits': '3',
            'start_date': '2026-01-10',
            'sort': 'name',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algorithms')
        self.assertNotContains(response, 'Biology')

        # Selected filter values should remain set after GET reload.
        self.assertContains(response, 'name="credits"')
        self.assertContains(response, 'value="3" selected')
        self.assertContains(response, 'value="2026-01-10" selected')



class CourseEnrollDropTests(TestCase):
    """Tests focused on the POST-only enforcement for enroll and drop (SCRUM-16)."""

    def setUp(self):
        self.course = CourseFactory()
        self.student = AccountFactory()
        self.teacher = InstructorFactory()

    # --- GET request rejection ---

    def test_get_request_to_enroll_redirects_to_detail(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.get(reverse('course_enroll', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('course_detail', args=[self.course.pk]))

    def test_get_request_to_enroll_does_not_enroll_student(self):
        self.client.login(username=self.student.username, password='password123')
        self.client.get(reverse('course_enroll', args=[self.course.pk]))
        self.assertFalse(self.student.account.enrolled_courses.filter(pk=self.course.pk).exists())

    def test_get_request_to_drop_redirects_to_detail(self):
        self.client.login(username=self.student.username, password='password123')
        self.student.account.enrolled_courses.add(self.course)
        response = self.client.get(reverse('course_drop', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('course_detail', args=[self.course.pk]))

    def test_get_request_to_drop_does_not_drop_student(self):
        self.client.login(username=self.student.username, password='password123')
        self.student.account.enrolled_courses.add(self.course)
        self.client.get(reverse('course_drop', args=[self.course.pk]))
        self.assertTrue(self.student.account.enrolled_courses.filter(pk=self.course.pk).exists())

    # --- Duplicate enrollment ---

    def test_student_cannot_enroll_in_same_course_twice(self):
        self.client.login(username=self.student.username, password='password123')
        self.client.post(reverse('course_enroll', args=[self.course.pk]))
        self.client.post(reverse('course_enroll', args=[self.course.pk]))
        self.assertEqual(self.student.account.enrolled_courses.filter(pk=self.course.pk).count(), 1)

    # --- Dropping without enrollment ---

    def test_student_cannot_drop_course_they_are_not_enrolled_in(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.post(reverse('course_drop', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.student.account.enrolled_courses.filter(pk=self.course.pk).exists())

    # --- Teacher restrictions ---

    def test_teacher_cannot_drop_course_via_post(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.post(reverse('course_drop', args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('course_detail', args=[self.course.pk]))
        self.assertFalse(self.teacher.account.enrolled_courses.filter(pk=self.course.pk).exists())


class NonexistentCourse404Tests(TestCase):
    """URLs with a missing course pk return 404 instead of 500 (SCRUM-18)."""

    def setUp(self):
        CourseFactory()
        self.student = AccountFactory()
        self.teacher = InstructorFactory()
        self.missing_pk = _nonexistent_course_pk()

    def test_course_detail_returns_404_for_missing_pk(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.get(reverse('course_detail', args=[self.missing_pk]))
        self.assertEqual(response.status_code, 404)

    def test_course_edit_returns_404_for_missing_pk(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.get(reverse('course_edit', args=[self.missing_pk]))
        self.assertEqual(response.status_code, 404)

    def test_course_delete_confirm_returns_404_for_missing_pk(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.get(reverse('course_delete', args=[self.missing_pk]))
        self.assertEqual(response.status_code, 404)

    def test_course_delete_post_returns_404_for_missing_pk(self):
        self.client.login(username=self.teacher.username, password='password123')
        response = self.client.post(reverse('course_delete', args=[self.missing_pk]))
        self.assertEqual(response.status_code, 404)

    def test_course_enroll_post_returns_404_for_missing_pk(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.post(reverse('course_enroll', args=[self.missing_pk]))
        self.assertEqual(response.status_code, 404)

    def test_course_drop_post_returns_404_for_missing_pk(self):
        self.client.login(username=self.student.username, password='password123')
        response = self.client.post(reverse('course_drop', args=[self.missing_pk]))
        self.assertEqual(response.status_code, 404)

class LogoutViewTests(TestCase):
    def setUp(self):
        self.student = AccountFactory()
        self.client.login(username=self.student.username, password='password123')

    def test_get_request_does_not_log_user_out(self):
        response = self.client.get(reverse('logout'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_post_request_logs_user_out(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
