from django.contrib import admin
from .models import Course, Account

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'crn', 'credits', 'instructor', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'crn')
    list_filter = ('credits', 'start_date', 'end_date')
    date_hierarchy = 'start_date'
    ordering = ('name',)
    show_facets = admin.ShowFacets.ALWAYS

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('user__is_staff', 'user__is_active')
    date_hierarchy = 'user__date_joined'
    ordering = ('user__username',)
    show_facets = admin.ShowFacets.ALWAYS

    