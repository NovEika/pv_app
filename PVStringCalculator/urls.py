"""
URL configuration for PVStringCalculator project.

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
from django.views.generic import RedirectView

from PVCalculatorApp.models import Inverter
from PVCalculatorApp.views import CalculatorView, AddInverterView, ResultsView, InvertersView, LoginView, HomeView, \
    RegisterView, AddPanelView, PanelsView, ProfileView, LogoutView, EngineerProjectView, SolutionsView, \
    InverterEditView, InverterDeleteView, PanelEditView, PanelDeleteView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/home', permanent=True)),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('calculator/', CalculatorView.as_view(), name='calculator'),
    path('results/', ResultsView.as_view(), name='results'),
    path('add-inverter/', AddInverterView.as_view(), name='inverter'),
    path('inverters/', InvertersView.as_view(), name='inverters'),
    path('edit-inverter/<int:pk>/', InverterEditView.as_view(), name='edit_inverter'),
    path('delete-inverter/<int:pk>/', InverterDeleteView.as_view(), name='delete_inverter'),
    path('add-panel/', AddPanelView.as_view(), name='panel'),
    path('edit-panel/<int:pk>/', PanelEditView.as_view(), name='edit_panel'),
    path('delete-panel/<int:pk>/', PanelDeleteView.as_view(), name='delete_panel'),
    path('panels/', PanelsView.as_view(), name='panels'),
    path('profile/engineer/<int:eng_id>/', EngineerProjectView.as_view(), name='engineer_project'),
    path('profile/solutions/<int:proj_id>/', SolutionsView.as_view(), name='solutions'),
    path('profile/engineer/<int:eng_id>/solutions/<int:proj_id>/', SolutionsView.as_view(), name='solutions_engineer'),
]
