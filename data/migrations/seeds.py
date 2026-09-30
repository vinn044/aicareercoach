import datetime

from django.contrib.auth.hashers import make_password
from django.db import migrations


def run(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    Account = apps.get_model('courses', 'Account')
    User = apps.get_model('auth', 'User')

    teacher_user1, _ = User.objects.get_or_create(
        username='teacher1',
        defaults={'email': 'teacher1@example.com', 'first_name': 'Teacher', 'last_name': 'One', 'password': make_password('password123')},
    )
    teacher_user1.is_staff = True
    teacher_user1.save()

    teacher_user2, _ = User.objects.get_or_create(
        username='teacher2',
        defaults={'email': 'teacher2@example.com', 'first_name': 'Teacher', 'last_name': 'Two', 'password': make_password('password123')},
    )
    teacher_user2.is_staff = True
    teacher_user2.save()

    # Create some sample courses
    course1, _ = Course.objects.get_or_create(
        name='Introduction to Python',
        defaults={
            'description': 'Learn the basics of Python programming.',
            'credits': 3,
            'crn': 'CRN12345',
            'instructor': teacher_user1,
            'start_date': datetime.date(2026, 9, 1),
            'end_date': datetime.date(2026, 12, 15),
        },
    )

    course2, _ = Course.objects.get_or_create(
        name='Data Structures and Algorithms',
        defaults={
            'description': 'Explore fundamental data structures and algorithms.',
            'credits': 4,
            'instructor': teacher_user2,
            'crn': 'CRN67890',
            'start_date': datetime.date(2026, 9, 1),
            'end_date': datetime.date(2026, 12, 15),
        },
    )

    course3, _ = Course.objects.get_or_create(
        name='Web Development with Django',
        defaults={
            'description': 'Build web applications using the Django framework.',
            'credits': 3,
            'instructor': teacher_user1,
            'crn': 'CRN54321',
            'start_date': datetime.date(2026, 9, 1),
            'end_date': datetime.date(2026, 12, 15),
        },
    )

    # Create/get users before accounts so FK constraints are always valid.
    student_user1, _ = User.objects.get_or_create(
        username='student1',
        defaults={'email': 'student1@example.com', 'first_name': 'Student', 'last_name': 'One', 'password': make_password('password123')},
    )
    student_user2, _ = User.objects.get_or_create(
        username='student2',
        defaults={'email': 'student2@example.com', 'first_name': 'Student', 'last_name': 'Two', 'password': make_password('password123')},
    )

    # Create some sample accounts
    teacher_account1, _ = Account.objects.get_or_create(
        user=teacher_user1,
        defaults={'email': 'teacher1@example.com'},
    )
    teacher_account1.courses_taught.add(course1, course2)

    teacher_account2, _ = Account.objects.get_or_create(
        user=teacher_user2,
        defaults={'email': 'teacher2@example.com'},
    )
    teacher_account2.courses_taught.add(course2, course3)

    student_account1, _ = Account.objects.get_or_create(
        user=student_user1,
        defaults={'email': 'student1@example.com'},
    )
    student_account1.enrolled_courses.add(course1, course3)

    student_account2, _ = Account.objects.get_or_create(
        user=student_user2,
        defaults={'email': 'student2@example.com'},
    )
    student_account2.enrolled_courses.add(course2)


def reverse_run(apps, schema_editor):
    Account = apps.get_model('courses', 'Account')
    Course = apps.get_model('courses', 'Course')
    User = apps.get_model('auth', 'User')

    Account.objects.filter(user__username__in=['teacher1', 'teacher2', 'student1', 'student2']).delete()
    User.objects.filter(username__in=['teacher1', 'teacher2', 'student1', 'student2']).delete()
    Course.objects.filter(
        name__in=[
            'Introduction to Python',
            'Data Structures and Algorithms',
            'Web Development with Django',
        ]
    ).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(run, reverse_run),
    ]


