from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    credits = models.IntegerField()
    crn = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('course_detail', args=[str(self.id)])


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    
    enrolled_courses = models.ManyToManyField(Course, related_name='enrolled_accounts', blank=True)
    courses_taught = models.ManyToManyField(Course, related_name='taught_accounts', blank=True)

    def __str__(self):
        return self.user.username