from django import forms
from django.contrib.auth.forms import UserCreationForm

from PVCalculatorApp.models import MyUser


class CalculatorForm(forms.Form):
    # Form used to input and validate data for various electrical calculations
    project_name = forms.CharField()

    opt_input_voltage = forms.FloatField(required=True)
    min_input_voltage = forms.FloatField(required=True)
    max_input_voltage = forms.FloatField(required=True)
    max_mppt_count = forms.IntegerField(required=True)

    uoc_mod_volt = forms.FloatField(required=True)
    tmod_percent = forms.FloatField(required=True)
    ummp_mod_volt = forms.FloatField(required=True)
    tmod_p_max_percent = forms.FloatField(required=True)
    isc_amper = forms.FloatField(required=True)
    tmod_short_percent = forms.FloatField(required=True)

    panel_count = forms.IntegerField(required=True)

    user_string_length = forms.IntegerField(required=False)


class InverterForm(forms.Form):
    # Form used to input and save data about inverters
    name = forms.CharField(required=True)
    opt_input_voltage = forms.FloatField(required=True)
    min_input_voltage = forms.FloatField(required=True)
    max_input_voltage = forms.FloatField(required=True)
    max_mppt_count = forms.IntegerField(required=True)


class PanelForm(forms.Form):
    # Form used to input send save data about PV panels
    name = forms.CharField(required=True)
    uoc_mod_volt = forms.FloatField(required=True)
    tmod_percent = forms.FloatField(required=True)
    ummp_mod_volt = forms.FloatField(required=True)
    tmod_p_max_percent = forms.FloatField(required=True)
    isc_amper = forms.FloatField(required=True)
    tmod_short_percent = forms.FloatField(required=True)


class MyUserRegistrationForm(UserCreationForm):
    # Form used to registrate a new user
    email = forms.EmailField(required=True)
    group_leader = forms.ModelChoiceField(queryset=MyUser.objects.filter(role=MyUser.GROUP_LEADER),
                                          required=False, label="Group Leader")

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'group_leader')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        group_leader = cleaned_data.get('group_leader')

        # if role is 'engineer', group_leader required
        if role == MyUser.ENGINEER and not group_leader:
            raise forms.ValidationError("If you select 'Engineer', you must choose your group leader!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.group_leader = self.cleaned_data.get('group_leader', None)
        if commit:
            user.save()
        return user
