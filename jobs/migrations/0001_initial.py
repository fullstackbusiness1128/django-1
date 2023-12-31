# Generated by Django 2.1.5 on 2021-01-06 17:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('total_funding', models.CharField(blank=True, max_length=64)),
                ('categories', models.CharField(blank=True, max_length=500)),
                ('headquarters', models.CharField(blank=True, max_length=500)),
                ('funding_status', models.CharField(blank=True, max_length=500)),
                ('last_funding_type', models.CharField(blank=True, max_length=250)),
                ('ipo_status', models.CharField(blank=True, max_length=250)),
                ('website', models.CharField(blank=True, max_length=500)),
                ('linkedin', models.CharField(blank=True, max_length=500)),
                ('description', models.CharField(blank=True, max_length=50000)),
                ('contact_name', models.CharField(blank=True, max_length=250)),
                ('contact_title', models.CharField(default='N/A', max_length=250)),
                ('contact_email', models.CharField(blank=True, max_length=250)),
                ('contact_li', models.CharField(blank=True, max_length=250)),
                ('contact_name2', models.CharField(blank=True, max_length=250)),
                ('contact_title2', models.CharField(blank=True, max_length=250)),
                ('contact_email2', models.CharField(blank=True, max_length=250)),
                ('contact_li2', models.CharField(blank=True, max_length=250)),
                ('contact_name3', models.CharField(blank=True, max_length=250)),
                ('contact_title3', models.CharField(blank=True, max_length=250)),
                ('contact_email3', models.CharField(blank=True, max_length=250)),
                ('contact_li3', models.CharField(blank=True, max_length=250)),
                ('contact_name4', models.CharField(blank=True, max_length=250)),
                ('contact_title4', models.CharField(blank=True, max_length=250)),
                ('contact_email4', models.CharField(blank=True, max_length=250)),
                ('contact_li4', models.CharField(blank=True, max_length=250)),
                ('contact_name5', models.CharField(blank=True, max_length=250)),
                ('contact_title5', models.CharField(blank=True, max_length=250)),
                ('contact_email5', models.CharField(blank=True, max_length=250)),
                ('contact_li5', models.CharField(blank=True, max_length=250)),
                ('contact_name6', models.CharField(blank=True, max_length=250)),
                ('contact_title6', models.CharField(blank=True, max_length=250)),
                ('contact_email6', models.CharField(blank=True, max_length=250)),
                ('contact_li6', models.CharField(blank=True, max_length=250)),
                ('contact_name7', models.CharField(blank=True, max_length=250)),
                ('contact_title7', models.CharField(blank=True, max_length=250)),
                ('contact_email7', models.CharField(blank=True, max_length=250)),
                ('contact_li7', models.CharField(blank=True, max_length=250)),
                ('contact_name8', models.CharField(blank=True, max_length=250)),
                ('contact_title8', models.CharField(blank=True, max_length=250)),
                ('contact_email8', models.CharField(blank=True, max_length=250)),
                ('contact_li8', models.CharField(blank=True, max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyContactInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('company_name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.Company')),
            ],
        ),
        migrations.CreateModel(
            name='JobPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, default='N/A', max_length=2000, null=True)),
                ('job_title', models.CharField(default='N/A', max_length=256)),
                ('locations', models.CharField(blank=True, max_length=256, null=True)),
                ('about_role', models.TextField(blank=True, null=True)),
                ('functions', models.TextField(blank=True, null=True)),
                ('skills', models.TextField(blank=True, null=True)),
                ('known_requirements', models.TextField(blank=True, null=True)),
                ('travel', models.CharField(blank=True, max_length=256, null=True)),
                ('about_company', models.CharField(blank=True, max_length=8000, null=True)),
                ('industry', models.CharField(blank=True, max_length=256, null=True)),
                ('company_type', models.CharField(blank=True, max_length=256, null=True)),
                ('company_age', models.CharField(blank=True, max_length=200, null=True)),
                ('employees', models.CharField(blank=True, max_length=200, null=True)),
                ('salary', models.CharField(blank=True, max_length=300, null=True)),
                ('source', models.CharField(blank=True, max_length=300, null=True)),
                ('apply_url', models.URLField(blank=True, max_length=300, null=True)),
                ('job_contact_name', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_title', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_email', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_name2', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_title2', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_email2', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_name3', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_title3', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_email3', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_name4', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_title4', models.CharField(blank=True, max_length=250, null=True)),
                ('job_contact_email4', models.CharField(blank=True, max_length=250, null=True)),
                ('demo', models.BooleanField(default=False)),
                ('posted_date', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.Company')),
            ],
        ),
        migrations.CreateModel(
            name='JobTitleFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.Company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='jobpost',
            name='job_title_filter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jobs.JobTitleFilter'),
        ),
    ]
