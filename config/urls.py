"""config URL Configuration

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
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.api_urls")),  # API REST endpoints
    path("api/exercises/", include("apps.exercises.api_urls")),  # API REST endpoints
    path("api/routines/", include("apps.routines.api_urls")),  # API REST endpoints
    path("api/sessions/", include("apps.sessions.api_urls")),  # API REST endpoints
    path("users/", include("apps.users.web_urls")),  # Web endpoints
    path("exercises/", include("apps.exercises.web_urls")),  # Web endpoints
    path("routines/", include("apps.routines.web_urls")),  # Web endpoints
    path("sessions/", include("apps.sessions.web_urls")),  # Web endpoints
]
