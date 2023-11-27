from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True   )
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField('email address', unique=True)
    linkedin = models.URLField(max_length=200, blank=True)
    watched_jobs = models.ManyToManyField('jobs.JobPost', blank=True)
    simulation_date = models.DateTimeField(null=True, blank=True)

    INT_FIELD_CHOICES = [
        (-1, 'Average'),
        (0, 'Above Average'),
        (1, 'Exceptional'),
    ]

    interpersonal_intelligence = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    composure = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    body_posture = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    mentorship = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    collaboration = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    modesty = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    caring = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    selflessness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    emotional_balance = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    integrity = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    courageous_authenticity = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    strategic_focus = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    results_achievement = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    decisiveness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    drive = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    autocratic_personality = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    self_awareness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    relating_to_team = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    communication = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    openness_to_experience = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    conscientiousness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    extraversion = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    agreeableness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    neuroticism = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    system_1_awareness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)
    system_2_awareness = models.IntegerField(choices=INT_FIELD_CHOICES, null=True, blank=True)

    doctors_notes = models.CharField(max_length=10000, null=True, blank=True)
    analysis_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    contact_viewed = models.IntegerField(default=0)
    company_name_viewed = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Product(models.Model):
    name = models.CharField(unique=True, max_length=255)
    product_id = models.CharField(unique=True, max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created_by = models.ForeignKey(User, related_name="product", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
