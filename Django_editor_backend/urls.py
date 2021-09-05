"""Django_editor_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.contrib import admin
from django.conf.urls import  include, url
from homeApp.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name = 'home'), #添加各级目录
    path('V1/courseApp/', include('courseApp.urls')),
    path('V1/execriseApp/', include('execriseApp.urls')),
    path('V1/commitApp/', include('commitApp.urls')),
    path('V1/ueditor/',include('DjangoUeditor.urls')),
    # path('V1/search/', include('haystack.urls')),
    path(r'V1/editor/', include('online_editor.urls')),
    path(r'V1/user/', include('identity.urls')),
    # path('online_editor/', include('online_editor.urls')),

]
