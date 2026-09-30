import factory
from faker import Factory
from .models import Course, Account
from django.contrib.auth import get_user_model
from factory import django
from datetime import date as Date, timedelta

class CourseFactory(django.DjangoModelFactory):
    class Meta:
        model = Course

    # unique name for each course instance
    name = factory.Sequence(lambda n: f'Course {n}')
    description = 'This is a sample course'
    credits = 3
    crn = factory.Sequence(lambda n: f'CRN{n}')
    start_date = Date.today()
    end_date = Date.today() + timedelta(days=30)

class AccountFactory(django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'testuser_{n}')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    email = factory.Sequence(lambda n: f'testuser_{n}@example.com')
    first_name = 'Student'
    last_name = 'One'

    @factory.post_generation
    def create_account(self, create, extracted, **kwargs):
        if create:
            Account.objects.get_or_create(user=self)

# subfactory for AccountFactory to create an instructor account
class InstructorFactory(django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'instructor{n}')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    email = factory.Sequence(lambda n: f'teacher{n+1}@example.com')
    first_name = 'Instructor'   
    last_name = 'One'
    is_staff = True

    @factory.post_generation
    def create_account(self, create, extracted, **kwargs):
        if create:
            Account.objects.get_or_create(user=self)



