from django.contrib import admin
from .models import Company, JobPost, Rating, JobTitleFilter


@admin.register(JobTitleFilter)
class JobFilterAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code')


admin.site.register(Company)
# admin.site.register(JobPost)
admin.site.register(Rating)
