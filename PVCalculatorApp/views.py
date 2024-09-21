from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CalculatorForm, InverterForm, MyUserRegistrationForm, PanelForm
import math

from PVCalculatorApp.models import *


# Create your views here.
class CalculatorView(LoginRequiredMixin, View):
    def get(self, request):
        form = CalculatorForm()
        panels = Panel.objects.all()
        inverters = Inverter.objects.all()

        return render(request, 'calculator.html', {"form": form,
                                                                        "panels": panels,
                                                                        "inverters": inverters})

    def post(self, request):
        results = []
        result_low_mppts = []
        error_messages = []

        if 'manual_input' in request.POST:
            form = CalculatorForm(request.POST)

        # Zkontroluje, zda uživatel vyplnil všechny potřebné údaje
            if form.is_valid():
                opt_input_voltage = form.cleaned_data['opt_input_voltage']
                min_input_voltage = form.cleaned_data['min_input_voltage']
                max_input_voltage = form.cleaned_data['max_input_voltage']
                max_mppt_count = form.cleaned_data['max_mppt_count']
                UocMOD_volt = form.cleaned_data['UocMOD_volt']
                TMOD = form.cleaned_data['TMOD_percent']
                UmmpMOD = form.cleaned_data['UmmpMOD_volt']
                TMOD_pMax = form.cleaned_data['TMOD_pMax_percent']
                ISC = form.cleaned_data['ISC_amper']
                TMOD_short = form.cleaned_data['TMOD_short_percent']
                panel_count = form.cleaned_data['panel_count']
                project_name = form.cleaned_data['project_name']

            else:
                print(form.errors)
                return render(request, 'calculator.html', {'form': form})

        elif 'model_selection' in request.POST:
            # Získání ID panelu a střídače
            panel_id = request.POST.get('panel_db')
            inverter_id = request.POST.get('inverter_db')

            panel = get_object_or_404(Panel, pk=panel_id)
            inverter = get_object_or_404(Inverter, pk=inverter_id)

            UocMOD_volt = float(panel.UocMOD_volt)
            TMOD = float(panel.TMOD_percent)
            UmmpMOD = float(panel.UmmpMOD_volt)
            TMOD_pMax = float(panel.TMOD_pMax_percent)
            max_input_voltage = float(inverter.max_input_voltage)
            min_input_voltage = float(inverter.min_input_voltage)
            opt_input_voltage = float(inverter.opt_input_voltage)
            max_mppt_count = int(inverter.max_mppt_count)

            panel_count = int(request.POST.get('panel_count'))
            project_name = str(request.POST.get('project_name'))

            initial_data = {
                        'opt_input_voltage': inverter.opt_input_voltage,
                        'min_input_voltage': inverter.min_input_voltage,
                        'max_input_voltage': inverter.max_input_voltage,
                        'max_mppt_count': inverter.max_mppt_count,
                        'UocMOD_volt': panel.UocMOD_volt,
                        'TMOD_percent': panel.TMOD_percent,
                        'UmmpMOD_volt': panel.UmmpMOD_volt,
                        'TMOD_pMax_percent': panel.TMOD_pMax_percent,
                        'ISC_amper': panel.ISC_amper,
                        'TMOD_short_percent': panel.TMOD_short_percent,
                        'panel_count': panel_count,
                    }

            form = CalculatorForm(initial=initial_data)
            if form.is_valid():
                project_name = request.POST.get('project_name')

        else:
            form = CalculatorForm(request.POST)
            print(form.errors)
            return render(request, 'calculator.html', {'form': form})

        result_low_mppts = count_strings_for_lowest_mppts(UocMOD_volt, TMOD, UmmpMOD, TMOD_pMax, max_input_voltage,
                                                          min_input_voltage, max_mppt_count, panel_count)

        UDC_max_MOD = count_UDC_max_MOD(UocMOD_volt, TMOD)
        UDC_min_MOD = count_UDC_min_MOD(UmmpMOD, TMOD_pMax)
        nDCmaxINV = count_max_panel(max_input_voltage, UDC_max_MOD)
        nDCminINV = count_min_panel(min_input_voltage, UDC_min_MOD)
        nDCoptINV = count_optimal_panel(opt_input_voltage, UmmpMOD)

        results.append(result_low_mppts)

        if result_low_mppts is None:
            error_messages.append('Wrong input data - the calculation could not be performed')
            return render(request, 'calculator.html', {'form': form, 'error_messages': error_messages})

        # Uložení výsledků do databáze
        project = Project.objects.create(project_name=project_name)
        solution = Solution.objects.create(nDCmaxINV=nDCmaxINV, nDCminINV=nDCminINV,
                                           nDCoptINV=nDCoptINV, owner=request.user)

        for result in result_low_mppts:
            StringPair.objects.create(string1=result[0], string2=result[1],
                                      result=StringPair.LOW_MPPT, solution=solution)

        SolutionProject.objects.create(project=project, solution=solution)

        request.session['results'] = results

        request.session['project_id'] = project.id
        request.session['solution_id'] = solution.id



        return redirect('results')


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
def count_strings_for_lowest_mppts(UocMOD, TMOD, UmmpMOD, TMOD_pMax, max_input_voltage,
                                   min_input_voltage, max_inverter_count, panel_count):
    # Typical mppt count for one inverter, can be different if Sungrow inverters are used
    mppt_count = 2
    result_low_mppts = []

    UDC_max_MOD = count_UDC_max_MOD(UocMOD, TMOD)
    UDC_min_MOD = count_UDC_min_MOD(UmmpMOD, TMOD_pMax)
    # IDC_max_STR = count_IDC_max_STR(ISC, TMOD_short)

    max_panel = count_max_panel(max_input_voltage, UDC_max_MOD)
    min_panel = count_min_panel(min_input_voltage, UDC_min_MOD)
    # opt_panel = count_optimal_panel(opt_input_voltage, UmmpMOD)

    # Create alert in js for this exception??
    # Panel count can't be bigger than maximal string multiplied by count of all mppts
    if panel_count > max_panel * mppt_count * max_inverter_count:
        return None

    # List to be filled based on minimal and maximal count of mppts, reversed - every tuple should be filled from
    # the biggest number, than move to the lower
    panel_range = list(range(min_panel, max_panel + 1))[::-1]

    remainder_panel = panel_count

    i = 0

    for _ in range(max_inverter_count):
        if remainder_panel >= max_panel * mppt_count:
            result_low_mppts.append((max_panel,) * mppt_count)
            remainder_panel -= max_panel * mppt_count
        elif remainder_panel >= min_panel * mppt_count:
            optimal_panels_per_string = remainder_panel // mppt_count
            result_low_mppts.append((optimal_panels_per_string,) * mppt_count)
            remainder_panel -= optimal_panels_per_string * mppt_count
        else:
            result_low_mppts.append((remainder_panel // mppt_count,) * mppt_count)
            remainder_panel = 0

    i = 0
    while remainder_panel > 0:
        current_tuple = list(result_low_mppts[i])
        if current_tuple[0] < max_panel:
            current_tuple[0] += 1
            remainder_panel -= 1
        if mppt_count > 1 and current_tuple[1] < max_panel and remainder_panel > 0:
            current_tuple[1] += 1
            remainder_panel -= 1
        result_low_mppts[i] = tuple(current_tuple)
        i = (i + 1) % max_inverter_count

    return result_low_mppts


# Count strings for optimal string length
# def count_user_input_mttp(UocMOD, TMOD, UmmpMOD, TMOD_pMax, ISC, TMOD_short, max_input_voltage,
#                           min_input_voltage, opt_input_voltage, max_inverter_count, panel_count, panel_max, panel_min):
#     remainder_panel = panel_count
#     mppt_count = 2
#     result_user_input = []
#
# #     Pokud je zbytek 0, rozpočítat optimální string do všech tuples; zbytek > 0 přidat do všech stringů + 1 nebo zaplnit první;
# #     zbytek < 0 ubrat ze všech stringů - 1 nebo zkráti poslední
#     rest_of_panels = remainder_panel - (max_inverter_count * mppt_count * panel_count)
#     full_optimal_string_inverters = remainder_panel // (panel_count * mppt_count)
#
#     for _ in range(full_optimal_string_inverters):
#         result_user_input.append((panel_count, panel_count))
#
#     i = 0
#     while remainder_panel > 0:
#
#
#
#
#     while len(result_user_input) < max_inverter_count:
#         if rest_of_panels == 0:
#             for x in range(max_inverter_count):
#                 result_user_input.append((panel_count, panel_count))
#                 remainder_panel = 0
#         elif rest_of_panels < 0:
#             for x in range(max_inverter_count):
#                 result_user_input.append((panel_count, panel_count))
#                 remainder_panel -= panel_count * 2
#             while remainder_panel < 0:
#                 for y in range(max_inverter_count - 1, -1, -1):
#                     if result_user_input[y][0] == panel_min:
#                         continue
#                     else:
#                         result_user_input[y] = tuple(val - 1 for val in result_user_input[y])
#                         remainder_panel += 2
#                         break
#             a = 0
#             while a < max_inverter_count - 1:
#                 index_b = a + 1
#                 if result_user_input[index_b][0] == 0:
#                     break
#                 elif (result_user_input[a][0] < panel_count) and (result_user_input[a][0] + result_user_input[index_b][0] < panel_max):
#                     new_tuple = tuple(
#                         val_a + val_b for val_a, val_b in zip(result_user_input[a], result_user_input[index_b]))
#                     result_user_input[a] = new_tuple
#                     result_user_input[index_b] = (0, 0)
#                     result_user_input.sort(reverse=True)
#                     a = 0
#                 else:
#                     a += 1
#
#         elif rest_of_panels > 0:
#             for x in range(max_inverter_count):
#                 result_user_input.append((panel_count, panel_count))
#                 remainder_panel -= panel_count * mppt_count
#             while remainder_panel > 0:
#                 for y in range(max_inverter_count):
#                     if result_user_input[y][0] == panel_max:
#                         continue
#                     else:
#                         result_user_input[y] = tuple(val + 1 for val in result_user_input[y])
#                         remainder_panel -= 2
#                         break
#             a = 0
#             while a < max_inverter_count - 1:
#                 index_b = a + 1
#                 if result_user_input[index_b][0] == 0:
#                     break
#                 elif (result_user_input[a][0] < panel_count) and (
#                         result_user_input[a][0] + result_user_input[index_b][0] < panel_max):
#                     new_tuple = tuple(
#                         val_a + val_b for val_a, val_b in zip(result_user_input[a], result_user_input[index_b]))
#                     result_user_input[a] = new_tuple
#                     result_user_input[index_b] = (0, 0)
#                     result_user_input.sort(reverse=True)
#                     a = 0
#                 else:
#                     a += 1


class ResultsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        results = request.session.get('results', [])
        project_id = request.session.get('project_id')
        solution_id = request.session.get('solution_id')

        print(project_id, solution_id)

        project = Project.objects.get(pk=project_id)
        solution = Solution.objects.get(pk=solution_id)
        string_pairs = StringPair.objects.filter(solution=solution)

        return render(request, "results.html", {"results": results, "string_pairs": string_pairs,
                                                "project": project, "solution": solution})


class AddInverterView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'add_inverter.html')

    def post(self, request):
        form = InverterForm(request.POST)
        if form.is_valid():
            # print("valid")
            name = form.cleaned_data['name']
            opt_input_voltage = form.cleaned_data['opt_input_voltage']
            min_input_voltage = form.cleaned_data['min_input_voltage']
            max_input_voltage = form.cleaned_data['max_input_voltage']
            max_mppt_count = form.cleaned_data['max_mppt_count']

            Inverter.objects.create(name=name, opt_input_voltage=opt_input_voltage,
                                             min_input_voltage=min_input_voltage,
                                             max_input_voltage=max_input_voltage, max_mppt_count=max_mppt_count)
            return redirect('inverters')
        else:
            print(form.errors)
            return render(request, 'add_inverter.html', {'form': form})


class InvertersView(LoginRequiredMixin, View):
    def get(self, request):
        inverters = Inverter.objects.all()
        return render(request, "inverters.html", {"inverters": inverters})


class AddPanelView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'add_panel.html')

    def post(self,request):
        form = PanelForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            UocMOD_volt = form.cleaned_data['UocMOD_volt']
            TMOD_percent = form.cleaned_data['TMOD_percent']
            UmmpMOD_volt = form.cleaned_data['UmmpMOD_volt']
            TMOD_pMax_percent = form.cleaned_data['TMOD_pMax_percent']
            ISC_amper = form.cleaned_data['ISC_amper']
            TMOD_short_percent = form.cleaned_data['TMOD_short_percent']

            Panel.objects.create(name=name, UocMOD_volt=UocMOD_volt, TMOD_percent=TMOD_percent,
                                 UmmpMOD_volt=UmmpMOD_volt, TMOD_pMax_percent=TMOD_pMax_percent,
                                 ISC_amper=ISC_amper, TMOD_short_percent=TMOD_short_percent)
            return redirect('panels')
        else:
            print(form.errors)
            return render(request, 'add_panel.html', {'form': form})


class PanelsView(LoginRequiredMixin, View):
    def get(self, request):
        panels = Panel.objects.all()
        return render(request, 'panels.html', {"panels": panels})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'login.html')


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'home.html')


class RegisterView(View):
    def get(self, request):
        form = MyUserRegistrationForm()
        return render(request, 'register.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = MyUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration was successful!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
        return render(request, 'register.html', {"form": form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        engineers = []
        solutions = []
        projects = []

        if user.role == 'group_leader':
            engineers = MyUser.objects.filter(group_leader_id=user.id)

        if user.role == 'engineer':
            solutions = Solution.objects.filter(owner_id=user.id)

            for solution in solutions:
                projects_id = SolutionProject.objects.filter(solution_id=solution.id).values_list('project_id',
                                                                                                  flat=True)
                projects.extend(Project.objects.filter(id__in=projects_id))

        return render(request, 'profile.html', {'engineers': engineers, 'solutions': solutions,
                                                'projects': projects})


class EngineerProjectView(LoginRequiredMixin, View):
    def get(self, request):
        engineer_id = request.GET.get('id')
        # print(engineer_id)
        solutions = Solution.objects.filter(owner_id=engineer_id)
        projects = []
        for _ in solutions:
            project_ids = SolutionProject.objects.filter(solution__in=solutions).values_list('project_id', flat=True)
            projects = Project.objects.filter(id__in=project_ids)

        return render(request, 'engineer_project.html', {'projects': projects})


class SolutionsView(LoginRequiredMixin, View):
    def get(self, request):
        project_id = request.GET.get('id')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
