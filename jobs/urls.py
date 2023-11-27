from django.urls import path

from jobs import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('terms', views.Terms.as_view(), name='terms'),
    path('about-us', views.AboutUs.as_view(), name='about'),
    path('news', views.News.as_view(), name='news'),
    path('faq', views.Faq.as_view(), name='faq'),
    path('privacy', views.Privacy.as_view(), name='privacy'),
    path('jobs', views.JobList.as_view(), name='job-list'),
    path('jobs/<int:pk>', views.JobDetail.as_view(), name='job-detail'),
    path('jobs/contact-info/<int:pk>', views.JobContactInfo.as_view(), name='job-contact-info'),
    path('jobs/company-name/<int:pk>', views.JobCompanyName.as_view(), name='job-company-name'),
    path('jobs/add', views.JobAdd.as_view(), name='job-add'),
    path('jobs/<int:pk>/edit', views.JobEdit.as_view(), name='job-edit'),
    path('jobs/<int:pk>/delete', views.JobDelete.as_view(), name='job-delete'),
    path('companies', views.CompanyList.as_view(), name='company-list'),
    path('companies/<int:pk>', views.CompanyDetail.as_view(), name='company-detail'),
    path('companies/add', views.CompanyAdd.as_view(), name='company-add'),
    path('companies/<int:pk>/edit', views.CompanyEdit.as_view(), name='company-edit'),
    path('companies/<int:pk>/delete', views.CompanyDelete.as_view(), name='company-delete'),
    path('companies/<int:pk>/rating/add', views.CompanyRatingAdd.as_view(), name='company-rating-add'),
    path('companies/<int:pk>/rating/<int:id>/edit', views.CompanyRatingEdit.as_view(), name='company-rating-edit'),
    path('video', views.VideoRoom.as_view(), name='video-room'),
    path('payment', views.Payment.as_view(), name='payment'),
    path('signalhire-api', views.SignalHireData.as_view(), name='signalhire-api'),
    path('job-search', views.JobSearchView.as_view(), name="job_search"),
    path('reset-password-token/', views.ResetPasswordRequestTokenView.as_view(), name='reset_password_token'),
    path('upload-jobs/', views.JobsUploadView.as_view(), name='upload_jobs'),
    path('start-campaign/', views.StartCampaignView.as_view(), name='start_campaign'),
    path('email-service-callback/', views.EmailServiceCallbackView.as_view(), name='email_service_callback')
]

