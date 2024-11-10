"""blogicum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from blog import views as blog_views
from pages import views as page_views


urlpatterns = [
    path('auth/login/', blog_views.MyLoginView.as_view(), name='login'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', blog_views.UserRegistrationView.as_view(), name='registration'),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
]

handler404 = 'pages.views.handler404'
handler500 = 'pages.views.handler500'
handler403 = 'pages.views.handler403'
