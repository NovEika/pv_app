import pytest
from django.urls import reverse

from .models import Inverter, MyUser, Panel, Project


# Create your tests here.
@pytest.mark.django_db
def test_inverter_creation(client):
    MyUser.objects.create_user(
        email="testuser@testuser.com",
        password="password1234",
    )
    client.login(email="testuser@testuser.com", password="password1234")

    url = reverse('inverter')

    data = {
        'name': "Test Inverter",
        'opt_input_voltage': 200.0,
        'max_input_voltage': 600.0,
        'min_input_voltage': 100.0,
        'max_mppt_count': 24
    }

    response = client.post(url, data)

    assert response.status_code == 302

    inverter = Inverter.objects.get(name="Test Inverter")


    assert inverter.name == "Test Inverter"
    assert inverter.opt_input_voltage == 200.0
    assert inverter.max_input_voltage == 600.0
    assert inverter.min_input_voltage == 100.0
    assert inverter.max_mppt_count == 24


@pytest.mark.django_db
def test_invalid_inverter_creation(client):
    MyUser.objects.create_user(
        email="testuser@testuser.com",
        password="password1234",
    )
    client.login(email="testuser@testuser.com", password="password1234")

    url = reverse('inverter')

    data = {
        'name': "Test Inverter",
        'opt_input_voltage': 'abcde',
        'max_input_voltage': 600.0,
        'min_input_voltage': 100.0,
        'max_mppt_count': 24
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert 'opt_input_voltage' in response.context['form'].errors


@pytest.mark.django_db
def test_create_myuser():
    user = MyUser.objects.create(
        email="testuser@testuser.com",
        password="password1234",
    )

    assert user.email == "testuser@testuser.com"
    assert user.password == "password1234"


@pytest.mark.django_db
def test_login_myuser(client):
    MyUser.objects.create_user(
        email="testuser@testuser.com",
        password="password1234",
    )

    response = client.post(reverse('login'), {'email': 'testuser@testuser.com', 'password': 'password1234'})

    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_calculator_view_post_manual_input(client):
    MyUser.objects.create_user(email="testuser@testuser.com", password="password1234")
    client.login(email="testuser@testuser.com", password="password1234")

    data = {
        'opt_input_voltage': 600.0,
        'min_input_voltage': 180.0,
        'max_input_voltage': 1100.0,
        'max_mppt_count': 12,
        'uoc_mod_volt': 37.5,
        'tmod_percent': -0.36,
        'ummp_mod_volt': 31.5,
        'tmod_p_max_percent': -0.29,
        'isc_amper': 13.93,
        'tmod_short_percent': 0.079,
        'panel_count': 386,
        'project_name': 'Test project',
        'manual_input': '1'
    }
    response = client.post(reverse('calculator'), data)

    assert response.status_code == 302
    assert Project.objects.filter(project_name='Test project').exists()




@pytest.mark.django_db
def test_calculator_view_post_model_selection(client):
    MyUser.objects.create_user(
        email="testuser@testuser.com",
        password="password1234",
    )
    client.login(email="testuser@testuser.com", password="password1234")

    panel = Panel.objects.create(
        uoc_mod_volt=37.5,
        tmod_percent=0.36,
        ummp_mod_volt=31.5,
        tmod_p_max_percent=0.29,
        isc_amper=13.93,
        tmod_short_percent=0.079,
    )

    inverter = Inverter.objects.create(
        opt_input_voltage=600.0,
        max_input_voltage=1100.0,
        min_input_voltage=100.0,
        max_mppt_count=12,
    )

    data = {
        'panel_db': panel.id,
        'inverter_db': inverter.id,
        'panel_count': 380,
        'project_name': 'Test project',
        'model_selection': '1',
    }

    response = client.post(reverse('calculator'), data)

    assert response.status_code == 302
    assert Project.objects.filter(project_name='Test project').exists()
