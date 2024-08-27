"""
URL configuration for FVEStringCalculator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from FVECalculatorApp.views import CalculatorView, InverterView, ResultsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calculator/', CalculatorView.as_view(), name='calculator'),
    path('results/', ResultsView.as_view(), name='results'),
    path('inverter/', InverterView.as_view(), name='inverter'),
]
