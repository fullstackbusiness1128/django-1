import csv
import datetime
from email.policy import default
import io

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django import forms
from django.contrib import admin
from jobs.models import JobPost, JobTitleFilter


def create_contact_list():
    name = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    data = {
        "name": name,
        "favourite": True,
        "description": "List of repeat customers"

    }

    url = "https://api.cc.email/v3/contact_lists"
    headers = {
        "Authorization": "Bearer {}".format(settings.CONSTANT_CONTACT_APP_TOKEN),
        "content-type": "application/json"
    }
    response = requests.post(url=url, json=data, headers=headers)
    print(response.status_code)
    return name, response.json()["id"]


def upload_to_constant_contact(leads, list_id):
    headers = {
        'Authorization': f'Bearer {settings.CONSTANT_CONTACT_APP_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "import_data": leads,
        "lists": [
            list_id
        ],
        "column_names": [
            "EMAIL",
            "FIRST NAME"
        ]
    }
    r = requests.post(
        'https://api.cc.email/v3/activities/contacts_json_import?api_key={}'.format(settings.CONSTANT_CONTACT_API_KEY),
        headers=headers,
        json=data)

    if not r.ok:
        print('Adding to contact list failed')


def create_and_schedule_campaign(list_name, list_id):
    headers = {
        'Authorization': f'Bearer {settings.CONSTANT_CONTACT_APP_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "name": list_name,
        "email_campaign_activities": [{
            "format_type": 5,
            "from_email": "info@leaderpact.com",
            "reply_to_email": "info@leaderpact.com",
            "from_name": "leaderpact",
            "subject": "Test",
            "html_content": "<html><body>Test</body></html>",
        }],
        "contact_list_ids": [list_id]
    }

    r = requests.post(f'https://api.cc.email/v3/emails?api_key={settings.CONSTANT_CONTACT_API_KEY}',
                      headers=headers,
                      json=data)

    if not r.ok:
        print('Creating campaign failed')

    campaign_id = r.json()["id"]
    now = datetime.datetime.now()
    data = {
        "scheduled_date": (now + datetime.timedelta(minutes=10)).isoformat()
    }
    r = requests.post(
        f'https://api.cc.email/v3/emails/activities/{campaign_id}/schedules?api_key={settings.CONSTANT_CONTACT_API_KEY}',
        headers=headers,
        json=data)

    return r.status_code


def upload_contact(file_list):
    cleaned_leads = []
    for file in file_list:
        file.seek(0)
        csv_file = csv.reader(io.StringIO(file.read().decode('utf-8')))
        next(csv_file)
        for row in csv_file:
            cleaned_lead = {'email_addresses': [row[2]], 'first_name': row[2].split('@')[0]}
            cleaned_leads.append(cleaned_lead)
    list_name, list_id = create_contact_list()
    upload_to_constant_contact(cleaned_leads, list_id)
    status = create_and_schedule_campaign(list_name, list_id)
    return status


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    # private = forms.BooleanField(
    #     required=False,
    #     initial=False)


@admin.register(JobPost)
class JobPostCsv(admin.ModelAdmin):
    change_list_template = "job_post.html"
    list_display = ['job_title', 'source']

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            with open(str(csv_file)) as f:
                for row in csv.DictReader(f):
                    job_title_filter = [i for i in list(JobTitleFilter.objects.all().values_list('title', flat=True)) if
                                        i in row['job_title']]
                    if len(job_title_filter) > 0:
                        row['job_title_filter'] = JobTitleFilter.objects.get(title=job_title_filter[0])
                    if 'apply_url' in row and JobPost.objects.filter(apply_url=row['apply_url']).exists():
                        continue
                    if 'private' in request.POST:
                        JobPost.objects.get_or_create(private=True, **row)
                    else:
                        JobPost.objects.get_or_create(**row)
                self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "csv_form.html", payload
        )
