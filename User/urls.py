from django.urls import path

from User import views

urlpatterns = [
    path('signup', views.Signup.as_view(), name='signup'),
    path('employer-signup', views.EmployerSignupView.as_view(), name='employer_signup'),
    path('premium', views.PremiumView.as_view(), name="premium"),
    path('checkout', views.checkout, name="checkout"),
    path('webhook/', views.stripe_webhook, name="stripe_webhook"),
    path('employer-signup-success', views.EmployerSignupSuccessView.as_view(), name='employer_signup_success'),
    path('activate-account/<uid>/<token>', views.VerifyEmailView.as_view(), name='activate_account'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('profile', views.Profile.as_view(), name='profile'),
    path('demo-profile', views.DemoProfile.as_view(), name='demo-profile'),
    path('profile/edit', views.ProfileEdit.as_view(), name='profile-edit'),
    path('profile/delete', views.ProfileDelete.as_view(), name='profile-delete'),
    path('reset-password/<uid>/<token>', views.ResetPasswordValidateTokenView.as_view(),
         name='reset_password_template'),
    path('reset-password', views.ResetPasswordView.as_view(), name='reset_password'),
    path('send-verification-link', views.SendVerificationLink.as_view(), name='send_verification_link'),
    path('change-password', views.ChangePasswordView.as_view(), name='change_password'),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('payment-success/', views.SuccessView.as_view(), name='payment_success'),
    path('payment-fail/', views.CancelView.as_view(), name='payment_cancel'),

]
