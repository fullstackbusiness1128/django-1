import operator
import time
from functools import reduce

import requests
from authorizenet.apicontrollers import *
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

from User.forms import SignupForm, LoginForm
from User.token import account_activation_token
from fastforward.settings import EMAIL_HOST_USER
from .forms import JobAddEditForm, CompanyAddEditForm, RatingAddEditForm, \
    PaymentForm, EmailForm
from .mixins import AdminRequiredMixin
from .models import JobPost, Company, Rating, CompanyContactInfo, JobTitleFilter
from .scraping_v1 import parse_html_to_csv as v1_parser
from .scraping_v2 import parse_html_to_csv as v2_parser
from .scraping_v3 import parse_html_to_csv as v3_parser
from .utils import upload_contact

User = get_user_model()

email_text = '''Below you will find information about your Leader Terminal membership. If you have any questions, please contact us via email at support@leadertheory.co.

Leadership positions: you will have access to all leadership positions posted in our app. Most positions have company insider emails. All positions older than 60 days are removed from our app.

Company insider emails: for some positions you will see company insider emails to use for directly contacting and introducing yourself to company insiders. All insider emails are verified, therefore if you have any issues with emails please contact us.

If you have any questions or concerns, please feel free to get in touch with us. We'll be more than happy to help you with anything you need assistance with.

Thank you,

Leader Terminal Support
support@leadertheory.com
www.leadertheory.com'''


def create_an_accept_payment_transaction(POST):
    # Create a merchantAuthenticationType object with authentication details
    # retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = "49Uk3X6kthE"
    merchantAuth.transactionKey = ""

    # Set the transaction's refId
    refId = "ref 1"

    # Create the payment object for a payment nonce
    opaqueData = apicontractsv1.opaqueDataType()
    opaqueData.dataDescriptor = "COMMON.ACCEPT.INAPP.PAYMENT"
    opaqueData.dataValue = POST['data_value']

    # Add the payment data to a paymentType object
    paymentOne = apicontractsv1.paymentType()
    paymentOne.opaqueData = opaqueData

    # Create order information
    order = apicontractsv1.orderType()
    order.invoiceNumber = "10101"
    order.description = "LeaderTheory"

    customerAddress = apicontractsv1.customerAddressType()
    customerAddress.firstName = POST['first_name']
    customerAddress.lastName = POST['last_name']
    customerAddress.address = POST['address']
    customerAddress.city = POST['city']
    customerAddress.state = POST['state']
    customerAddress.zip = POST['zip']
    customerAddress.country = "USA"

    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # Create a transactionRequestType object and add the previous objects to it
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = 895
    transactionrequest.order = order
    transactionrequest.payment = paymentOne
    transactionrequest.transactionSettings = settings
    transactionrequest.billTo = customerAddress

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = refId
    createtransactionrequest.transactionRequest = transactionrequest

    # Create the controller and get response
    createtransactioncontroller = createTransactionController(createtransactionrequest)
    createtransactioncontroller.setenvironment(constants.PRODUCTION)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()

    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') == True:
                return True, ""
            else:
                return False, response.transactionResponse.messages.message[0].description
        # Or, print errors if the API request wasn't successful
        else:
            return False, response.transactionResponse.errors.error[0].errorText

    return response


class Index(View):
    def get(self, request):
        return redirect('job_search')


class JobList(View):
    def get(self, request):
        jobs = JobPost.objects.filter(demo=False).order_by('-posted_date')
        if 'search' in request.GET:
            companies = Company.objects.filter(
                name__icontains=request.GET['search']
            )
            jobs = jobs.filter(
                Q(job_title__icontains=request.GET['search']) |
                Q(functions__icontains=request.GET['search']) |
                Q(company__in=companies) |
                Q(company_name__icontains=request.GET['search']) |
                Q(skills__icontains=request.GET['search']) |
                Q(industry__icontains=request.GET['search'])
            )
        # if not request.user.is_authenticated:
        #     jobs = JobPost.objects.filter(demo=True).order_by('-posted_date')[:5]

        paginator = Paginator(jobs, 10)
        page = request.GET.get('page')
        jobs = paginator.get_page(page)

        context = {
            'jobs': jobs,
            'search': request.GET.get('search', ""),
        }
        return render(request, 'jobs/job_list.html', context)


class JobDetail(View):
    def get(self, request, pk):
        job = JobPost.objects.get(pk=pk)
        can_watch_job = False
        watched_job = False
        if request.user.is_authenticated:
            if job.demo:
                messages.warning(request, "You do not have authorization to view this job listing.")
                return redirect('/jobs')
            if request.user.watched_jobs.filter(pk=pk).exists():
                watched_job = True
            else:
                can_watch_job = True
        return render(request, 'jobs/job_detail.html',
                      {'job': job, 'watched_job': watched_job, 'can_watch_job': can_watch_job})

    def post(self, request, pk):
        job = JobPost.objects.get(pk=pk)
        request.user.watched_jobs.add(job)
        request.user.save()
        return render(request, 'jobs/job_detail.html', {'job': job, 'just_watched_job': True, 'watched_job': True})


class JobContactInfo(LoginRequiredMixin, View):
    def get(self, request, pk):
        if request.user.contact_viewed < 5:
            request.user.contact_viewed += 1
            request.user.save()
            job = JobPost.objects.get(pk=pk)
            return render(request, 'jobs/job_contact_info.html', {'job': job})
        else:
            return HttpResponse(
                '<div class="alert alert-warning" role="alert">Please <a href="/payment">pay</a> to view the contact information.</div>')


class JobCompanyName(LoginRequiredMixin, View):
    def get(self, request, pk):
        if request.user.company_name_viewed < 5:
            request.user.company_name_viewed += 1
            request.user.save()
            job = JobPost.objects.get(pk=pk)
            return render(request, 'jobs/job_company_name.html', {'job': job})
        else:
            return HttpResponse(
                '<div class="alert alert-warning" role="alert">Please <a href="/payment">pay</a> to view the company name.</div>')


class Payment(LoginRequiredMixin, View):
    def get(self, request):
        form = PaymentForm()
        return render(request, 'accounts/payment.html', {'form': form})

    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            successful, error = create_an_accept_payment_transaction(request.POST)
            if not successful:
                messages.error(request, "Error when processing payment: " + error)
                return render(request, 'accounts/payment.html', {'form': form})

            request.user.is_paid = True
            request.user.save()

            return redirect('/')
        else:
            messages.error(request, "Error parsing form")
            return render(request, 'accounts/payment.html', {'form': form})


class JobAdd(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
            messages.warning(request, "You do not have authorization to add jobs")
            return redirect('/jobs')

        form = JobAddEditForm()
        context = {
            'form': form,
            'action': 'Add',
        }
        return render(request, 'jobs/job_add_edit.html', context)

    def post(self, request):
        form = JobAddEditForm(request.POST)
        if form.is_valid():
            company = Company.objects.get(pk=request.POST['company'])
            # job = JobPost.objects.create(
            #     title=request.POST['title'],
            #     description=request.POST['description'],
            #     company=company,
            #     salary=request.POST['salary'] if len(request.POST['salary']) else None,
            #     city=request.POST['city'],
            #     state=request.POST['state']
            # )
            job = JobPost.objects.create(
                company_name=request.POST['company_name'],
                job_title=request.POST['job_title'],
                locations=request.POST['locations'],
                about_role=request.POST['about_role'],
                functions=request.POST['functions'],
                skills=request.POST['skills'],
                travel=request.POST['travel'],
                about_company=request.POST['about_company'],
                industry=request.POST['industry'],
                company_type=request.POST['company_type'],
                company_age=request.POST['company_age'],
                employees=request.POST['employees'],
                salary=request.POST['salary'],
                company=company
            )
            messages.success(request, "New job created")
            fresh_form = JobAddEditForm()
            context = {
                'form': fresh_form,
                'action': 'Add'
            }
        else:
            messages.error(request, "Error in creating new job")
            context = {
                'form': form,
                'action': 'Add'
            }
        return render(request, 'jobs/job_add_edit.html', context)


class JobEdit(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.is_staff:
            messages.warning(request, "You do not have authorization to edit this job")
            return redirect('/jobs/' + str(pk))

        job = JobPost.objects.get(pk=pk)
        form = JobAddEditForm(instance=job)
        context = {
            'job': job,
            'form': form,
            'action': 'Edit',
        }
        return render(request, 'jobs/job_add_edit.html', context)

    def post(self, request, pk):
        job = JobPost.objects.get(pk=pk)
        form = JobAddEditForm(request.POST)
        if form.is_valid():
            company = Company.objects.get(pk=request.POST['company'])
            job.job_title = request.POST['title']
            job.about_role = request.POST['about role']
            job.company = company
            job.salary = request.POST['salary'] if len(request.POST['salary']) else None
            job.save()
            messages.success(request, "Job saved successfully")
            return redirect('/jobs/' + str(job.pk))
        else:
            messages.error(request, "Error in editing job")
        context = {
            'job': job,
            'form': form,
            'action': 'Edit',
        }
        return render(request, 'jobs/job_add_edit.html', context)


class JobDelete(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.is_staff:
            messages.warning(request, "You do not have authorization to delete this job")
            return redirect('/jobs/' + str(pk))

        job = JobPost.objects.get(pk=pk)
        return render(request, 'jobs/job_delete.html', {'job': job})

    def post(self, request, pk):
        job = JobPost.objects.get(pk=pk)
        job.delete()
        messages.success(request, "Successfully deleted job")
        return redirect('/jobs')


class CompanyList(View):
    def get(self, request):
        companies = Company.objects.order_by('name')
        if 'search' in request.GET:
            companies = companies.filter(name__icontains=request.GET['search'])

        paginator = Paginator(companies, 9)
        page = request.GET.get('page')
        companies = paginator.get_page(page)

        context = {
            'companies': companies,
            'search': request.GET.get('search', ""),
        }
        return render(request, 'jobs/company_list.html', context)


class CompanyDetail(View):
    def get(self, request, pk):
        company = Company.objects.get(pk=pk)
        total_funding = Company.objects.get(pk=pk)
        jobs = company.jobs()
        if 'search' in request.GET:
            jobs = jobs.filter(
                Q(title__icontains=request.GET['search']) |
                Q(description__icontains=request.GET['search'])
            )
        if request.user.is_authenticated:
            if Rating.objects.filter(company=company, user=request.user).exists():
                user_has_rated = True
                user_rating = Rating.objects.get(company=company, user=request.user)
            else:
                user_has_rated = False
                user_rating = None
        else:
            user_has_rated = False
            user_rating = None
        context = {
            'company': company,
            'total_funding': total_funding,
            'jobs': jobs,
            'search': request.GET.get('search', ""),
            'rating': company.ratings(),
            'user_has_rated': user_has_rated,
            'user_rating': user_rating,
        }
        return render(request, 'jobs/company_detail.html', context)


class CompanyAdd(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
            messages.warning(request, "You do not have authorization to add companies")
            return redirect('/companies')

        form = CompanyAddEditForm()
        context = {
            'form': form,
            'action': 'Add',
        }
        return render(request, 'jobs/company_add_edit.html', context)

    def post(self, request):
        form = CompanyAddEditForm(request.POST)
        if form.is_valid():
            company = Company.objects.create(
                name=request.POST['name'],
                total_funding=request.POST['total funding']
            )
            messages.success(request, "New company created")
            fresh_form = CompanyAddEditForm()
            context = {
                'form': fresh_form,
                'action': 'Add'
            }
        else:
            messages.error(request, "Error in creating new company")
            context = {
                'form': form,
                'action': 'Add'
            }
        return render(request, 'jobs/company_add_edit.html', context)


class CompanyEdit(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.is_staff:
            messages.warning(request, "You do not have authorization to edit this company")
            return redirect('/companies/' + str(pk))

        company = Company.objects.get(pk=pk)
        form = CompanyAddEditForm(instance=company)
        context = {
            'company': company,
            'form': form,
            'action': 'Edit',
        }
        return render(request, 'jobs/company_add_edit.html', context)

    def post(self, request, pk):
        company = Company.objects.get(pk=pk)
        form = CompanyAddEditForm(request.POST)
        if form.is_valid():
            company.name = request.POST['name']
            company.save()
            messages.success(request, "Company saved successfully")
            return redirect('/companies/' + str(company.pk))
        else:
            messages.error(request, "Error in editing company")
        context = {
            'company': company,
            'form': form,
            'action': 'Edit',
        }
        return render(request, 'jobs/company_add_edit.html', context)


class CompanyDelete(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.is_staff:
            messages.warning(request, "You do not have authorization to delete this company")
            return redirect('/companies/' + str(pk))

        company = Company.objects.get(pk=pk)
        return render(request, 'jobs/company_delete.html', {'company': company})

    def post(self, request, pk):
        company = Company.objects.get(pk=pk)
        company.delete()
        messages.success(request, "Successfully deleted company")
        return redirect('/companies')


class CompanyRatingAdd(LoginRequiredMixin, View):
    def get(self, request, pk):
        company = Company.objects.get(pk=pk)
        context = {
            'company': company,
            'action': 'Add',
            'form': RatingAddEditForm(),
        }
        return render(request, 'jobs/rating_add_edit.html', context)

    def post(self, request, pk):
        form = RatingAddEditForm(request.POST)
        company = Company.objects.get(pk=pk)
        user = request.user
        if form.is_valid():
            new_rating = Rating.objects.create(
                rating=request.POST['rating'],
                company=company,
                user=user
            )
            messages.success(request, 'Rating successfully added')
        else:
            messages.error(request, 'Could not add rating')
        return redirect('/companies/' + str(pk))


class CompanyRatingEdit(LoginRequiredMixin, View):
    def get(self, request, pk, id):
        company = Company.objects.get(pk=pk)
        rating = Rating.objects.get(pk=id)
        context = {
            'company': company,
            'rating': rating,
            'action': 'Edit',
            'form': RatingAddEditForm(instance=rating),
        }
        return render(request, 'jobs/rating_add_edit.html', context)

    def post(self, request, pk, id):
        rating = Rating.objects.get(id=id)
        form = RatingAddEditForm(request.POST)
        if form.is_valid():
            rating.rating = request.POST['rating']
            rating.save()
            messages.success(request, "Rating updated")
        else:
            messages.success(request, "Error updating rating")
        return redirect('/companies/' + str(pk))


class Terms(View):
    def get(self, request):
        return render(request, 'accounts/terms.html')


class AboutUs(TemplateView):
    template_name = 'accounts/about-us.html'


class News(TemplateView):
    template_name = 'accounts/news.html'


class Faq(TemplateView):
    template_name = 'accounts/faq.html'


class Privacy(TemplateView):
    template_name = 'accounts/privacy.html'


def get_twilio_jwt(user, room_uuid):
    room_uuid = str(room_uuid)

    # Substitute your Twilio AccountSid and ApiKey details
    ACCOUNT_SID = 'AC231b233f30b85d59de88c5a170c39ee5'
    API_KEY_SID = 'SK5a3a36b73a6addcce0919ded74f3062c'
    API_KEY_SECRET = 'VjyUchs2ZVYpDgS77YaNTq7EYya6Ptk9'

    # Create an Access Token
    token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET)

    # Set the Identity of this token
    token.identity = user.email

    # Grant access to Video
    grant = VideoGrant(room=room_uuid)
    token.add_grant(grant)

    # Serialize the token as a JWT
    return token.to_jwt()


class VideoRoom(View):
    def get(self, request, pk):
        company = Company.objects.get(pk=pk)
        total_funding = Company.objects.get(pk=pk)
        jobs = company.jobs()
        if 'search' in request.GET:
            jobs = jobs.filter(
                Q(title__icontains=request.GET['search']) |
                Q(description__icontains=request.GET['search'])
            )
        if request.user.is_authenticated:
            if Rating.objects.filter(company=company, user=request.user).exists():
                user_has_rated = True
                user_rating = Rating.objects.get(company=company, user=request.user)
            else:
                user_has_rated = False
                user_rating = None
        else:
            user_has_rated = False
            user_rating = None
        context = {
            'company': company,
            'total_funding': total_funding,
            'jobs': jobs,
            'search': request.GET.get('search', ""),
            'rating': company.ratings(),
            'user_has_rated': user_has_rated,
            'user_rating': user_rating,
        }
        return render(request, 'video.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class SignalHireData(LoginRequiredMixin, View):
    def post(self, request):
        linkedin_url = request.POST['linkedin_url']
        if not linkedin_url or not 'linkedin.com/in/' in linkedin_url:
            return JsonResponse({'error': 'Please input a proper LinkedIn URL.'})

        uploading_data = requests.post("https://www.signalhire.com/api/v1/candidate/byLinkedInUrl",
                                       headers={'apikey': 'W4xNhyIAeXk5kCKEj9YBIzEHUNzCJaBA'},
                                       json={'urls': [linkedin_url]})
        if not uploading_data.ok:
            return JsonResponse({'error': 'Error with SignalHire API.'})
        request_id = uploading_data.json()["requestId"]

        while True:
            status = requests.get(f"https://www.signalhire.com/api/v1/candidate/request/{request_id}",
                                  headers={'apikey': 'W4xNhyIAeXk5kCKEj9YBIzEHUNzCJaBA'})
            if status.status_code == 200:
                data = status.json()
                break

            time.sleep(2)

        candidate = list(data.values())[0]
        info_request = requests.get(f"https://www.signalhire.com/api/v1/candidate/{candidate['uid']}",
                                    headers={'apikey': 'W4xNhyIAeXk5kCKEj9YBIzEHUNzCJaBA'})
        if not info_request.ok:
            return JsonResponse({'error': 'Error with SignalHire API.'})

        candidate_info = info_request.json()
        candidate_info_subset = {
            'name': candidate_info["fullName"],
            'company': candidate_info["experience"][0]["company"],
            'title': candidate_info["experience"][0]["position"]
        }
        for contact in candidate_info["contacts"]:
            if contact["type"] == "email":
                candidate_info_subset["email"] = contact["value"]
                break

        if "email" in candidate_info_subset:
            contact_info, created = CompanyContactInfo.objects.get_or_create(
                name=candidate_info_subset["name"],
                company_name=candidate_info_subset["company"],
                title=candidate_info_subset["title"],
                email=candidate_info_subset["email"]
            )
            try:
                company = CompanyContactInfo.objects.get(name=candidate_info_subset["company"])
                contact_info.company = company
                contact_info.save()
            except CompanyContactInfo.DoesNotExist:
                pass

        return JsonResponse(candidate_info_subset)


class JobSearchView(View):

    def get_queryset(self):
        return JobPost.objects.all()

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset().order_by('-pk')
        levels = {}
        page_size = int(request.GET.get("job_size", 30))
        level_set = JobTitleFilter.objects.all()
        jobs_paginated = Paginator(qs, page_size)
        for level in level_set:
            query = reduce(
                operator.and_, (
                    Q(job_title__icontains=x) for x in level.code.split(' ')
                )
            )
            levels[level.title] = qs.filter(query).count()
        return render(request, 'jobs/search.html', {
            "jobs": jobs_paginated.get_page(1),
            "levels": levels,
            "page_size": page_size
        })

    def post(self, request, *args, **kwargs):
        keyword = request.POST.get('keyword')
        location = request.POST.get('location')
        level_filter = request.POST.getlist('levels[]')
        page_size = int(request.GET.get("page_size", 30))

        qs = self.get_queryset()
        if keyword:
            qs = JobPost.objects.search(query=keyword)
        if location:
            qs = qs.filter(locations__icontains=location)
        if level_filter:
            query = reduce(
                operator.or_, (
                    reduce(
                        operator.and_, (
                            Q(job_title__icontains=x) for x in JobTitleFilter.objects.get(title=item).code.split(" ")
                        )
                    ) for item in level_filter
                )
            )
            qs = qs.filter(query)

        levels = {}
        level_set = JobTitleFilter.objects.all()
        jobs_paginated = Paginator(qs.order_by("-pk"), page_size)
        for level in level_set:
            level_query = reduce(
                operator.and_, (
                    Q(job_title__icontains=x) for x in level.code.split(" ")
                )
            )
            levels[level.title] = qs.filter(level_query).count()
        if request.is_ajax():
            html_to_render = 'jobs/ajax_search.html'
            if not qs:
                html_to_render = 'jobs/not_found.html'
            html = render_to_string(html_to_render,
                                    context={"jobs": jobs_paginated.get_page(1), "levels": levels, "checked": level_filter,
                                             "search": keyword, "page_size": page_size})
            return JsonResponse({"html": html})
        return render(request, 'jobs/search.html',
                      {"jobs": jobs_paginated.get_page(1), "search": keyword, "levels": levels, "page_size": page_size})


class ResetPasswordRequestTokenView(CreateView):
    template_name = 'jobs/reset_password.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = EmailForm(data=request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            uid = urlsafe_base64_encode(force_bytes(user)).decode()
            token = account_activation_token.make_token(user)
            current_site = get_current_site(self.request)
            site = "{}://{}".format(self.request.scheme, self.request.get_host())
            message = render_to_string('jobs/password_email_template.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'site': site
            })
            mail_subject = 'Reset your password...'
            send_mail(mail_subject, message, EMAIL_HOST_USER, [request.POST['email']],
                      html_message=message)

            messages.success(self.request, 'Check your email to reset password')
        return redirect(reverse('index'))


class JobsUploadView(AdminRequiredMixin, View):
    scripts = {
        '1': {"parser": v1_parser, "output_file": "extractedData.csv"},
        '2': {"parser": v2_parser, "output_file": "crawlData.csv"},
        '3': {"parser": v3_parser, "output_file": "linkedincrawlData.csv"},
        '4': {"parser": upload_contact}
    }

    def get(self, request, *args, **kwargs):
        return render(request, 'jobs/jobs_upload.html')

    def post(self, request, *args, **kwargs):
        files_list = request.FILES.getlist('files[]')
        script_version = request.POST.get('html_version')
        response = self.scripts[script_version]['parser'](files_list)
        contacts_updates = False
        if script_version != '4':
            try:
                call_command('load_job_posts',
                             "{}/{}".format(settings.CSV_OUTPUT_FILE, self.scripts[script_version]['output_file']), '--script', script_version)
                messages.success(request, 'Jobs Updated in Database')
            except Exception as e:
                messages.error(request, str(e))
        else:
            if response == 200:
                contacts_updates = True
                messages.success(request, 'Contacts updated')
            else:
                messages.success(request, 'Contacts upload failed')
        return render(request, 'jobs/jobs_upload.html', {"contacts_updated": contacts_updates})


class StartCampaignView(AdminRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        url = "https://api.omnisend.com/v3/campaigns/{}/actions/start".format('606382c3b1b5330bcc4388ea')
        headers = {
            "x-api-key": settings.OMNISEND_API_KEY,
            "content-type": "application/json"
        }
        response = requests.post(url=url, headers=headers)
        message = "Some error occurred"
        if response.status_code == 200:
            message = "Campaign started successfully."
        return JsonResponse({"message": message})


class EmailServiceCallbackView(AdminRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        message = request.data
        return JsonResponse({"message": message})

    def get(self, request, *args, **kwargs):
        message = request.data
        return JsonResponse({"message": message})
