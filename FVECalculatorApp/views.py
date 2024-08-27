
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View


from .forms import CalculatorForm
import math

from FVECalculatorApp.models import *

# Create your views here.
class CalculatorView(View):
    def get(self, request):
        form = CalculatorForm()
        return render(request, 'calculator.html', {"form": form})

    def post(self, request):
        form = CalculatorForm(request.POST)
        if form.is_valid():
            results = []

            opt_input_voltage = form.cleaned_data['opt_input_voltage']
            min_input_voltage = form.cleaned_data['min_input_voltage']
            max_input_voltage = form.cleaned_data['max_input_voltage']
            max_mppt_count = form.cleaned_data['max_mppt_count']

            UocMOD = form.cleaned_data['UocMOD']
            TMOD = form.cleaned_data['TMOD']
            UmmpMOD = form.cleaned_data['UmmpMOD']
            TMOD_pMax = form.cleaned_data['TMOD_pMax']
            ISC = form.cleaned_data['ISC']
            TMOD_short = form.cleaned_data['TMOD_short']

            panel_count = form.cleaned_data['panel_count']

            try:
                result_low_mppts = count_strings_for_lowest_mppts(UocMOD, TMOD, UmmpMOD, TMOD_pMax, ISC, TMOD_short,
                                                                  max_input_voltage, min_input_voltage, opt_input_voltage,
                                                                  max_mppt_count, panel_count)

                results.append(result_low_mppts)
            except Exception as e:
                messages.error(request, f"Error in  calculation {e}")
                return redirect('calculator')

            request.session['results'] = results
            return redirect('results')
        else:
            return render(request, 'calculator.html', {"form": form})


# Stanoveni maximalniho napeti naprazdno
def count_UDC_max_MOD(UocMOD, TMOD):
    UDC_max_MOD = UocMOD * (1 + TMOD * (-20-25) /100)
    return  UDC_max_MOD

# Stanovení minimálního napětí
def count_UDC_min_MOD(UmmpMOD, TMOD_Pmax):
    UDC_min_MOD = UmmpMOD * (1 + (TMOD_Pmax * (70-25) / 100))
    return UDC_min_MOD

# Výpočet maximálního zkratového proudu
def count_IDC_max_STR(ISC, TMOD_short):
    IDC_max_STR = ISC * (1 + (TMOD_short * (70-25)) / 100)
    return IDC_max_STR

#Výpočet maximálního počtu panelů na string
def count_max_panel(max_input_voltage, UDC_max_MOD):
    panel_max_fl = max_input_voltage / UDC_max_MOD
    panel_max = math.floor(panel_max_fl)
    return panel_max

# Výpočet minimálního počtu panelů na string
def count_min_panel(min_input_voltage, UDC_min_MOD):
    panel_min_fl = min_input_voltage / UDC_min_MOD
    panel_min = math.ceil(panel_min_fl)
    return panel_min

# Výpočet optimálního počtu panelů na string
def count_optimal_panel(opt_input_voltage, UmmpMOD):
    panel_optimal_fl = opt_input_voltage / UmmpMOD
    panel_optimal = round(panel_optimal_fl)
    return panel_optimal


# Count strings for lowest possible count of mppts
def count_strings_for_lowest_mppts(UocMOD, TMOD, UmmpMOD, TMOD_pMax, ISC, TMOD_short, max_input_voltage,
                                   min_input_voltage, opt_input_voltage, max_mppt_count, panel_count):
    # Typical mppt count for one inverter, can be different if Sungrow inverters are used
    mppt_count = 2
    result_low_mppts = []

    UDC_max_MOD = count_UDC_max_MOD(UocMOD, TMOD)
    UDC_min_MOD = count_UDC_min_MOD(UmmpMOD, TMOD_pMax)
    IDC_max_STR = count_IDC_max_STR(ISC, TMOD_short)

    max_panel = count_max_panel(max_input_voltage, UDC_max_MOD)
    min_panel = count_min_panel(min_input_voltage, UDC_min_MOD)
    opt_panel = count_optimal_panel(opt_input_voltage, UmmpMOD)

    # Create alert in js for this exception??
    # Panel count can't be bigger than maximal string multiplied by count of all mppts
    if panel_count // max_panel // mppt_count > max_mppt_count:
        return JsonResponse("Too many panels for this count of mppts!")

    # List to be filled based on minimal and maximal count of mppts, reversed - every tuple should be filled from
    # the biggest number, than move to the lower
    panel_range = list(range(min_panel, max_panel + 1))[::-1]

    remainder_panel = panel_count

    while len(result_low_mppts) < max_mppt_count:
        for x in panel_range:
            tuple_found = True
            if len(result_low_mppts) == max_mppt_count:
                break
            if remainder_panel <= 0:
                for y in range(max_mppt_count - len(result_low_mppts)):
                    result_low_mppts.append((0,) * mppt_count)
                break
            while tuple_found:
                # Fill the most tuples with maximum panel count per string till possible
                if remainder_panel - x * mppt_count == 0:
                    result_low_mppts.append((x,) * mppt_count)
                    break
                # Fill tuple with the biggest number possible till you reach minimum panel count for string
                if remainder_panel - x * mppt_count > min_panel:
                    result_low_mppts.append((x,) * mppt_count)
                    remainder_panel -= x * mppt_count
                # Till panel count is bigger than zero and current number is bigger than remaining panel count
                # or remaining panel count is bigger than zero
                elif x > remainder_panel > 0 or x > remainder_panel // mppt_count > 0:
                    # if remaining panels are lower than current number fill the last string with this number
                    if remainder_panel < x:
                        result_low_mppts.append((remainder_panel, 0))
                        remainder_panel -= x
                    #     (0, 0)
                    else:
                        result_low_mppts.append((remainder_panel, 0))
                # no remaining panels, ends the loop
                else:
                    tuple_found = False
    return result_low_mppts


class ResultsView(View):
    def get(self, request, *args, **kwargs):
        results = request.session.get('results', [])
        return render(request, "results.html", {"results": results})


class InverterView(View):
    def get(self, request):
        return render(request, 'inverter.html')

