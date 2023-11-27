import stripe
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login, get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.decorators.csrf import csrf_exempt

from User.forms import LoginForm, SignupForm, PasswordTokenForm, ProfileForm, EmployerSignupForm
from User.token import account_activation_token

User = get_user_model()
stripe.api_key = settings.STRIPE_PRIVATE_TEST_KEY


class Signup(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')

        form = SignupForm()
        return render(request, 'accounts/signup.html',
                      {'form': form, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_TEST_KEY})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email=request.POST['email']).exists():
                messages.error(request, "That email address is taken")
                return render(request, 'accounts/signup.html', {'form': form})

            user = User.objects.create_user(
                request.POST['email'],
                request.POST['password']
            )
            user.save()
            # customer = stripe.Customer.create(
            #     email=user.email,
            #     source=request.POST['stripeToken'],
            # )
            # user.stripe_customer_id = customer['id']
            # charge = stripe.Charge.create(
            #     customer=customer,
            #     amount=25 * 100,
            #     currency='usd',
            #     description='demo'
            # )
            # print("charge", charge)
            current_site = get_current_site(request)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=user.email,
                mode='subscription',
                line_items=[{
                    'price': settings.STRIPE_PRODUCT_PRICE,
                    'quantity': 1
                }],
                success_url="{}://{}/".format(self.request.scheme, self.request.get_host()),
                cancel_url="{}://{}/payment-fail/".format(self.request.scheme, self.request.get_host()),
            )
            token = account_activation_token.make_token(user)
            site = "{}://{}".format(self.request.scheme, self.request.get_host())
            message = render_to_string('jobs/verify_email_template.html', {
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.email)).decode(),
                'token': token,
                'site': site
            })

            send_mail('Welcome to Leader Terminal', message, settings.EMAIL_HOST_USER, [request.POST['email']],
                      html_message=message, fail_silently=True)
            # sent_mail = EmailMessage('Welcome to Leader Pact', message, from_email=settings.EMAIL_HOST_USER, to=[request.POST['email']])
            # sent_mail.content_subtype = "html"
            # sent_mail.send(fail_silently=False)

            # login(request, user)
            print("email Sent successfully")
            messages.success(request, "Check your email")
            return JsonResponse({
                'id': checkout_session.id
            })
            # if request.GET.get('next'):
            #     return redirect(request.GET.get('next'))
            # else:
            #     return redirect('/')
        else:
            return JsonResponse({'status': 'false', 'message': form.errors}, status=500)
            # messages.error(request, "Error parsing form")
            # return render(request, 'accounts/signup.html', {'form': form})


class EmployerSignupView(FormView):
    template_name = 'accounts/employer-signup.html'
    form_class = EmployerSignupForm
    success_url = 'employer-signup-success'


class EmployerSignupSuccessView(TemplateView):
    template_name = 'accounts/employer-signup-success.html'


class VerifyEmailView(View):
    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        uid = urlsafe_base64_decode(kwargs.get('uid')).decode()
        user = User.objects.get(email=uid)
        if user is not None and account_activation_token.check_token(user, token):
            user.is_verified = True
            user.save()
            messages.success(request, "Verified Successfully")
            return redirect(reverse('login'))
        else:
            messages.error(request, "Invalid Token/Token Expired")
            return redirect(reverse('index'))


class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')

        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            next_url = request.POST.get('next')
            try:
                user = User.objects.get(email=request.POST['email'])
            except:
                messages.error(request, "User with that email doesn't exist")
                return render(request, 'accounts/login.html', {'form': form})

            if user.check_password(request.POST['password']):
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('/')
            else:
                messages.error(request, "Incorrect Password")
        else:
            messages.error(request, 'Error parsing Email and/or Password')
        return render(request, 'accounts/login.html', {'form': form})


class Logout(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out")
        return redirect('/')


class Profile(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/profile.html', {'user': request.user})

    def post(self, request):
        regex = r'^(http(s)?:\/\/)?([\w]+\.)?linkedin\.com\/(pub|in|profile)\/[\w]+(\/)?'
        linkedin_url = request.POST.get('linkedin_url')
        if linkedin_url:
            pattern = re.compile(regex)
            if re.fullmatch(pattern, linkedin_url):
                request.user.linkedin = linkedin_url
                request.user.save()
                messages.success(request, "LinkedIn URL updated")
            else:
                messages.error(request, "Invalid LinkedIn URL")
        return redirect('profile')


class DemoProfile(View):
    def get(self, request):
        return render(request, 'accounts/profile_demo.html')


class ProfileEdit(LoginRequiredMixin, View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, 'accounts/profile_edit.html', {'form': form})

    def post(self, request):
        user = request.user
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            # if request.POST['linkedin'] and not request.POST['linkedin'].replace('https://', '').startswith('www.linkedin.com/in/'):
            #     messages.error(request, 'Incorrect URL. <a href="https://www.linkedin.com/help/linkedin/answer/49315/finding-your-linkedin-public-profile-url?lang=en">Click here</a> to identify your LinkedIn URL.')
            #     return redirect('/profile/edit')
            # if not request.POST['linkedin'].startswith('http'):
            #     request.POST['linkedin'] = f'https://{request.POST["linkedin"]}'
            # user.first_name = request.POST['first_name']
            # user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            # user.linkedin = request.POST['linkedin']
            user.save()
            messages.success(request, "Successfully updated profile")
        else:
            messages.error(request, "Error in updating profile")
        return redirect('/profile')


class ProfileDelete(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, 'accounts/profile_delete.html', {'user': user})

    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Successfully deleted account")
        return redirect('/')


class ResetPasswordValidateTokenView(View):
    template_name = 'accounts/reset_password_template.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'uid': kwargs['uid'], 'token': kwargs['token']})


class ResetPasswordView(View):

    def post(self, request, *args, **kwargs):
        form = PasswordTokenForm(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data
            password = form.data.get('password')
            user.set_password(password)
            user.save()
            messages.success(request, 'Password Reset Successfully')
            return redirect(reverse('index'))


class SendVerificationLink(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        current_site = get_current_site(request)
        token = account_activation_token.make_token(user)
        site = "{}://{}".format(self.request.scheme, self.request.get_host())
        message = render_to_string('jobs/verify_email_template.html', {
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.email)).decode(),
            'token': token,
            'site': site
        })
        send_mail('Welcome to Leader Terminal', message, settings.EMAIL_HOST_USER, [user.email],
                  html_message=message, fail_silently=True)
        print('verification email sent')
        messages.success(request, "verification email sent, Check your email")
        return redirect(reverse('job-list'))


class ChangePasswordView(View):
    def post(self, request):
        user = request.user
        if user.check_password(request.POST['current_password']):
            if request.POST['password'] == request.POST['confirm_password']:
                user.set_password(request.POST['password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully")
                return redirect(reverse('profile'))
            messages.error(request, "Password and Confirm password did not match")
            return redirect(reverse('profile'))
        messages.error(request, "Current password is not correct")
        return redirect(reverse('profile'))


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8001"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': 'price_1IkX7lJF0XNUJISgYutdSiFa',
                'quantity': 1
            }],
            success_url=YOUR_DOMAIN + '/payment-success/',
            cancel_url=YOUR_DOMAIN + '/payment-fail/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class PremiumView(TemplateView):
    template_name = "premium.html"


@login_required
def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1LME43JF0XNUJISgv8U1LHlE',
            'quantity': 1,
        }],
        customer_email=request.user.email,
        mode='payment',
        success_url=request.build_absolute_uri(reverse("signup")) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse("index")),
    )
    return JsonResponse({
        'session_id': session.id,
        'stripe_public_id': settings.STRIPE_PUBLIC_KEY
    })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        payment_intent = session["payment_intent"]

        # TODO - send an email to the customer
        user = get_user_model().objects.get(email=customer_email)
        user.is_paid = True
        user.save()

        # message = render_to_string('payment_success_email.html', {'link': reverse('signup')})
        # send_mail(
        #     'Welcome to Leader Terminal',
        #     message,
        #     settings.EMAIL_HOST_USER,
        #     [user.email],
        #     html_message=message,
        #     fail_silently=True
        # )

    return HttpResponse(status=200)
