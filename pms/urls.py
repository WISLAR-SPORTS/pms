"""
URL configuration for pms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path

# pms/urls.py
from django.contrib import admin
from django.urls import path, include
from Auth.views import landing_page
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
   
    path('', landing_page, name='landing'),
    path('auth/', include('Auth.urls', namespace='auth')),  # use the same namespace
    path('supervisor/', include('Supervisor.urls', namespace='supervisor')),
    path('project/', include('project.urls', namespace='project')),
    path('chaining/', include('smart_selects.urls')),
    path('submission/', include('submission.urls', namespace='submission')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
