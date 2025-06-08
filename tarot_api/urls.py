from django.contrib import admin
from django.urls import path

from authentication.views import GoogleLoginView, AppleLoginView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path("auth/apple/", AppleLoginView.as_view(), name="apple_login"),
    path("me/", MeView.as_view(), name="me"),
]
