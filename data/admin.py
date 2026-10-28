from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Student resumes/feedback are deliberately absent from the generic admin UI.
admin.site.register(User, UserAdmin)
