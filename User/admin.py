from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from User.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'linkedin', 'watched_jobs', 'simulation_date', 'interpersonal_intelligence', 'composure', 'body_posture', 'mentorship', 'collaboration', 'modesty', 'caring', 'selflessness', 'emotional_balance', 'integrity', 'courageous_authenticity', 'strategic_focus', 'results_achievement', 'decisiveness', 'drive', 'autocratic_personality', 'self_awareness', 'relating_to_team', 'communication', 'openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism', 'system_1_awareness', 'system_2_awareness', 'doctors_notes', 'analysis_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_paid', 'is_verified',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
