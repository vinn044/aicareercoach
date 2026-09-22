from django.contrib import admin
from django.urls import include, path
from courses import views

urlpatterns = [
    # /courses/ paths
    path("", views.courses_list, name="home"),
    path("<int:pk>/", views.course_detail, name="course_detail"),
    path("create/", views.course_create, name="course_create"),
    path("<int:pk>/edit/", views.course_edit, name="course_edit"),
    path("<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("<int:pk>/enroll/", views.course_enroll, name="course_enroll"),
    path("<int:pk>/drop/", views.course_drop, name="course_drop"),
]