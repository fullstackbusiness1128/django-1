from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    total_funding = models.CharField(max_length=64, blank=True)
    categories = models.CharField(max_length=500, blank=True)
    headquarters = models.CharField(max_length=500, blank=True)
    funding_status = models.CharField(max_length=500, blank=True)
    last_funding_type = models.CharField(max_length=250, blank=True)
    ipo_status = models.CharField(max_length=250, blank=True)
    website = models.CharField(max_length=500, blank=True)
    linkedin = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=50000, blank=True)
    ##################
    contact_name = models.CharField(max_length=250, blank=True)
    contact_title = models.CharField(max_length=250, default='N/A')
    contact_email = models.CharField(max_length=250, blank=True)
    contact_li = models.CharField(max_length=250, blank=True)
    ###################
    contact_name2 = models.CharField(max_length=250, blank=True)
    contact_title2 = models.CharField(max_length=250, blank=True)
    contact_email2 = models.CharField(max_length=250, blank=True)
    contact_li2 = models.CharField(max_length=250, blank=True)
    ###################
    contact_name3 = models.CharField(max_length=250, blank=True)
    contact_title3 = models.CharField(max_length=250, blank=True)
    contact_email3 = models.CharField(max_length=250, blank=True)
    contact_li3 = models.CharField(max_length=250, blank=True)
    ###################
    contact_name4 = models.CharField(max_length=250, blank=True)
    contact_title4 = models.CharField(max_length=250, blank=True)
    contact_email4 = models.CharField(max_length=250, blank=True)
    contact_li4 = models.CharField(max_length=250, blank=True)
    ###################
    contact_name5 = models.CharField(max_length=250, blank=True)
    contact_title5 = models.CharField(max_length=250, blank=True)
    contact_email5 = models.CharField(max_length=250, blank=True)
    contact_li5 = models.CharField(max_length=250, blank=True)
    ###################
    contact_name6 = models.CharField(max_length=250, blank=True)
    contact_title6 = models.CharField(max_length=250, blank=True)
    contact_email6 = models.CharField(max_length=250, blank=True)
    contact_li6 = models.CharField(max_length=250, blank=True)
    ###################
    contact_name7 = models.CharField(max_length=250, blank=True)
    contact_title7 = models.CharField(max_length=250, blank=True)
    contact_email7 = models.CharField(max_length=250, blank=True)
    contact_li7 = models.CharField(max_length=250, blank=True)
    ###################
    contact_name8 = models.CharField(max_length=250, blank=True)
    contact_title8 = models.CharField(max_length=250, blank=True)
    contact_email8 = models.CharField(max_length=250, blank=True)
    contact_li8 = models.CharField(max_length=250, blank=True)
    ###################
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name  # + ": " + self.total_funding

    def jobs(self):
        return JobPost.objects.filter(company=self).order_by('job_title')

    def ratings(self):
        points = 0
        total = 0
        average = 0
        rating_hash = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
        }
        company_ratings = Rating.objects.filter(company=self)
        total = company_ratings.count()
        for company_rating in company_ratings:
            rating_hash[company_rating.rating] += 1
            points += company_rating.rating
        if points != 0 and total != 0:
            average = points / total
        else:
            average = None
        rating_hash['total'] = total
        rating_hash['average'] = average
        return rating_hash


class JobTitleFilter(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class JobPostManager(models.Manager):

    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(job_title__icontains=query) |
                Q(functions__icontains=query) |
                Q(company_name__icontains=query)
            )
            qs = qs.filter(or_lookup).distinct()
        return qs


class JobPost(models.Model):
    company_name = models.CharField(max_length=2000, default='N/A', null=True, blank=True)
    job_title = models.CharField(max_length=256, default='N/A')
    locations = models.CharField(max_length=256, blank=True, null=True)
    job_title_filter = models.ForeignKey(JobTitleFilter, on_delete=models.SET_NULL, null=True)
    about_role = models.TextField(blank=True, null=True)
    functions = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    known_requirements = models.TextField(blank=True, null=True)
    travel = models.CharField(max_length=256, blank=True, null=True)
    about_company = models.CharField(max_length=8000, blank=True, null=True)
    industry = models.CharField(max_length=256, blank=True, null=True)
    company_type = models.CharField(max_length=256, blank=True, null=True)
    company_age = models.CharField(max_length=200, blank=True, null=True)
    employees = models.CharField(max_length=200, blank=True, null=True)
    salary = models.CharField(max_length=300, blank=True, null=True)
    source = models.CharField(max_length=300, blank=True, null=True)
    apply_url = models.URLField(max_length=300, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    job_contact_name = models.CharField(max_length=250, null=True, blank=True)
    job_contact_title = models.CharField(max_length=250, null=True, blank=True)
    job_contact_email = models.CharField(max_length=250, null=True, blank=True)
    job_contact_linkdin_url = models.URLField(null=True, blank=True, max_length=250)
    job_contact_name2 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_title2 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_email2 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_name3 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_title3 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_email3 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_name4 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_title4 = models.CharField(max_length=250, null=True, blank=True)
    job_contact_email4 = models.CharField(max_length=250, null=True, blank=True)
    demo = models.BooleanField(default=False)
    posted_date = models.DateTimeField(auto_now_add=True, blank=True)

    objects = JobPostManager()

    def __str__(self):
        return self.company_name + ": " + self.job_title




class Rating(models.Model):
    rating = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.company.name + ": " + str(self.rating)


class CompanyContactInfo(models.Model):
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
