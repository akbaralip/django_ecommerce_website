from django.urls import path, include
from . import views

urlpatterns = [
    path('signin/', views.signin,name='signin'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('reset_password/<uidb64>/<token>',views.reset_password,name='reset_password'),
    path('update_password/', views.update_password, name='update_password'),
    path('signup/', views.signup,name='signup'),
    path('otp_login/', views.otp_login,name='otp_login'),
    path('signout/', views.signout,name='signout'),
    path('activate/<uidb64>/<token>', views.activate,name='activate'),
    path('send_otp_sms/', views.send_otp_sms,name='send_otp_sms'),

]