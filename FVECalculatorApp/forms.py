from django import forms

class CalculatorForm(forms.Form):
    opt_input_voltage = forms.FloatField(required=True)
    min_input_voltage =forms.FloatField(required=True)
    max_input_voltage = forms.FloatField(required=True)
    max_mppt_count = forms.IntegerField(required=True)

    UocMOD = forms.FloatField(required=True)
    TMOD = forms.FloatField(required=True)
    UmmpMOD = forms.FloatField(required=True)
    TMOD_pMax = forms.FloatField(required=True)
    ISC = forms.FloatField(required=True)
    TMOD_short = forms.FloatField(required=True)

    panel_count = forms.IntegerField(required=True)