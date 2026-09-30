from django.test import TestCase
from django.urls import reverse
from courses.models import Course, Account
from courses.factory import CourseFactory
from courses.forms import CourseForm
from datetime import date, timedelta

class CourseModelTest(TestCase):
    def setUp(self):
        self.course = CourseFactory()

    def test_course_creation(self):
        self.assertIsInstance(self.course, Course)
        self.assertEqual(self.course.name, 'Course 1')
        self.assertEqual(self.course.description, 'This is a sample course')
        self.assertEqual(self.course.credits, 3)
        self.assertEqual(self.course.crn, 'CRN1')
    
    def test_CRN_uniqueness(self):
        with self.assertRaises(Exception):
            course2 = Course.objects.create(
                name='Course 2',
                description='Another course',
                credits=4,
                crn='CRN0',  # same CRN as course1
                start_date=self.course.start_date,
                end_date=self.course.end_date,
            )


def make_form(crn):
    return CourseForm(data={
        'name': 'Test Course',
        'description': 'A description',
        'crn': crn,
        'credits': 3,
        'start_date': date.today() + timedelta(days=1),
        'end_date': date.today() + timedelta(days=30),
    })

def make_form_with_dates(start_date, end_date):
    return CourseForm(data={
        'name': 'Test Course',
        'description': 'A description',
        'crn': 'AB1C2',
        'credits': 3,
        'start_date': start_date,
        'end_date': end_date,
    })


class CourseFormCRNValidationTest(TestCase):

    def test_valid_crn_letters_and_digits(self):
        form = make_form('AB12C')
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_crn_digits_and_letters(self):
        form = make_form('1A2B3')
        self.assertTrue(form.is_valid(), form.errors)

    def test_crn_too_short_is_invalid(self):
        form = make_form('AB1')
        self.assertFalse(form.is_valid())
        self.assertIn('crn', form.errors)

    def test_crn_too_long_is_invalid(self):
        form = make_form('AB123C')
        self.assertFalse(form.is_valid())
        self.assertIn('crn', form.errors)

    def test_crn_all_digits_is_invalid(self):
        form = make_form('12345')
        self.assertFalse(form.is_valid())
        self.assertIn('crn', form.errors)

    def test_crn_all_letters_is_invalid(self):
        form = make_form('ABCDE')
        self.assertFalse(form.is_valid())
        self.assertIn('crn', form.errors)

    def test_crn_with_special_characters_is_invalid(self):
        form = make_form('AB1!C')
        self.assertFalse(form.is_valid())
        self.assertIn('crn', form.errors)

    def test_crn_is_saved_uppercase(self):
        form = make_form('ab1c2')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['crn'], 'AB1C2')

class CourseFormDateValidationTest(TestCase):

    def test_start_date_tomorrow_is_valid(self):
        form = make_form_with_dates(date.today() + timedelta(days=1), date.today() + timedelta(days=30))
        self.assertTrue(form.is_valid(), form.errors)

    def test_start_date_today_is_invalid(self):
        form = make_form_with_dates(date.today(), date.today() + timedelta(days=30))
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)

    def test_start_date_in_the_past_is_invalid(self):
        form = make_form_with_dates(date.today() - timedelta(days=1), date.today() + timedelta(days=30))
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)

    def test_end_date_before_start_date_is_invalid(self):
        form = make_form_with_dates(date.today() + timedelta(days=10), date.today() + timedelta(days=5))
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_end_date_same_as_start_date_is_invalid(self):
        same_date = date.today() + timedelta(days=10)
        form = make_form_with_dates(same_date, same_date)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_end_date_after_start_date_is_valid(self):
        form = make_form_with_dates(date.today() + timedelta(days=1), date.today() + timedelta(days=2))
        self.assertTrue(form.is_valid(), form.errors)