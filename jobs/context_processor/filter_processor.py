from jobs import models


def location_list(request):
    locations = set(models.JobPost.objects.all().values_list('locations', flat=True))
    return {'locations': locations}


def job_title_filter(request):
    levels = models.JobTitleFilter.objects.all()
    return {'levels': levels}
