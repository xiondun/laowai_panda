from django.conf.urls import url
from .views import *
from rest_framework.authtoken import views as restviews

app_name = "accounts"
urlpatterns = [
    url(r'^language/$', LanguageView.as_view(), name="language"),
    url(r'^signup/$', Signup.as_view(), name="signup_api"),
    url(r'^logout/', Logout.as_view(), name="logout"),
    url(r'^login/$', Login.as_view(), name="login"),
    url(r'^profile/', Profile.as_view(), name="profile"),
    url(r'^other-user-profile/(?P<user_id>\w+)', OtherUserProfile.as_view(), name="other_user_profile"),
    url(r'^sociallogin/$', SocialLogin.as_view(), name="social_login"),
    url(r'^forget-password/$', SendTempPasswordApi.as_view(), name='forget_password'),
    url(r'^change-password/$', ChangePasswordApi.as_view(), name='change_password'),
    url(r'^rest-password/$', RestPasswordApi.as_view(), name='reset_password'),
    url(r'^app-verify-code/$', AppVerifyCodeApi.as_view(), name='verify_code'),
    url(r'^my-blocked-users/$',MyBlockedUsersView.as_view(),name="blocked_users"),
    url(r'^block-unblock/$', BlockUnBlockUsers.as_view(), name="block_unblock"),
    url(r'^resend-verification-email/$',
        ResendVerificationEmail.as_view(), name='resend_verification'),
    url(r'^verify/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<code>\w+)/$',
        EmailVerification.as_view(), name='email_verification'),
    url(r'^follow-unfollow/$', FollowUnFollowUsers.as_view(), name="follow_unfollow"),
    url('followers/$',FollowersView.as_view(),name="followers_users"),
    url(r'^my-following-users/$',MyFollowingUsersView.as_view(),name="following_users"),
]
