import math
from typing import List, Tuple, cast

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from PVCalculatorApp.models import *
from .forms import CalculatorForm, InverterForm, MyUserRegistrationForm, PanelForm


# Create your views here.

# Calculator class calculates optimal string length based on panel and inverter parameters - user input
# or database selection
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
        error_messages = []
        result_user_input_string_length = []

        if 'manual_input' in request.POST:
            # Manual form input from user
            form = CalculatorForm(request.POST)

            if form.is_valid():
                opt_input_voltage = form.cleaned_data['opt_input_voltage']
                min_input_voltage = form.cleaned_data['min_input_voltage']
                max_input_voltage = form.cleaned_data['max_input_voltage']
                max_mppt_count = form.cleaned_data['max_mppt_count']
                uoc_mod = form.cleaned_data['uoc_mod_volt']
                tmod = form.cleaned_data['tmod_percent']
                ummp_mod = form.cleaned_data['ummp_mod_volt']
                tmod_p_max = form.cleaned_data['tmod_p_max_percent']
                isc = form.cleaned_data['isc_amper']
                tmod_short = form.cleaned_data['tmod_short_percent']
                panel_count = form.cleaned_data['panel_count']
                user_string_length = form.cleaned_data['user_string_length']
                project_name = form.cleaned_data['project_name']

            else:
                print(form.errors)
                return render(request, 'calculator.html', {'form': form})

        # User selects panel and inverter from the database
        elif 'model_selection' in request.POST:
            panel_id = request.POST.get('panel_db')
            inverter_id = request.POST.get('inverter_db')

            panel = get_object_or_404(Panel, pk=panel_id)
            inverter = get_object_or_404(Inverter, pk=inverter_id)

            uoc_mod = float(panel.uoc_mod_volt)
            tmod = float(panel.tmod_percent)
            ummp_mod = float(panel.ummp_mod_volt)
            tmod_p_max = float(panel.tmod_p_max_percent)
            max_input_voltage = float(inverter.max_input_voltage)
            min_input_voltage = float(inverter.min_input_voltage)
            opt_input_voltage = float(inverter.opt_input_voltage)
            max_mppt_count = int(inverter.max_mppt_count)

            panel_count = int(request.POST.get('panel_count'))
            project_name = str(request.POST.get('project_name'))
            user_string_length = request.POST.get('user_string_length')
            try:
                user_string_length = int(user_string_length)
            except ValueError:
                user_string_length = None

            initial_data = {
                'opt_input_voltage': inverter.opt_input_voltage,
                'min_input_voltage': inverter.min_input_voltage,
                'max_input_voltage': inverter.max_input_voltage,
                'max_mppt_count': inverter.max_mppt_count,
                'uoc_mod_volt': panel.uoc_mod_volt,
                'tmod_percent': panel.tmod_percent,
                'ummp_volt': panel.ummp_mod_volt,
                'tmod_p_max_percent': panel.tmod_p_max_percent,
                'isc_amper': panel.isc_amper,
                'tmod_short_percent': panel.tmod_short_percent,
                'panel_count': panel_count,
                'user_string_length': user_string_length if user_string_length else 0,
            }

            form = CalculatorForm(initial=initial_data)
            if form.is_valid():
                project_name = request.POST.get('project_name')

        else:
            form = CalculatorForm(request.POST)
            return render(request, 'calculator.html', {'form': form})

        udc_max_mod = count_udc_max_mod(uoc_mod, tmod)
        udc_min_mod = count_udc_min_mod(ummp_mod, tmod_p_max)
        ndc_max_inv = count_max_panel(max_input_voltage, udc_max_mod)
        ndc_min_inv = count_min_panel(min_input_voltage, udc_min_mod)
        ndc_opt_inv = count_optimal_panel(opt_input_voltage, ummp_mod)

        result_low_mppts = count_strings_for_lowest_mppts(uoc_mod, tmod, ummp_mod, tmod_p_max, max_input_voltage,
                                                          min_input_voltage, max_mppt_count, panel_count)

        if user_string_length is not None:
            result_user_input_string_length = count_panels_for_user_string_length(user_string_length, panel_count,
                                                                                  max_mppt_count, ndc_max_inv,
                                                                                  ndc_min_inv)
            results.append(result_user_input_string_length)

        results.append(result_low_mppts)

        if result_low_mppts is None:
            error_messages.append('Wrong input data - the calculation could not be performed')
            return render(request, 'calculator.html', {'form': form, 'error_messages': error_messages})

        # After calculation is done, data are saved to the database
        project = Project.objects.create(project_name=project_name)
        solution = Solution.objects.create(ndc_max_inv=ndc_max_inv, ndc_min_inv=ndc_min_inv,
                                           ndc_opt_inv=ndc_opt_inv, owner=request.user)

        for result in result_low_mppts:
            StringPair.objects.create(string1=result[0], string2=result[1],
                                      result=StringPair.LOW_MPPT, solution=solution)

        for result in result_user_input_string_length:
            StringPair.objects.create(string1=result[0], string2=result[1], result=StringPair.USER_STRING,
                                      solution=solution)

        SolutionProject.objects.create(project=project, solution=solution)

        request.session['project_id'] = project.id
        request.session['solution_id'] = solution.id

        return redirect('results')


# Calculates maximum open-circuit voltage/Stanoveni maximalniho napeti naprazdno
def count_udc_max_mod(uoc_mod, tmod):
    udc_max_mod = uoc_mod * (1 + tmod * (-20 - 25) / 100)
    return udc_max_mod


# Calculates minimum voltage/Stanovení minimálního napětí
def count_udc_min_mod(ummp_mod, tmod_p_max):
    udc_min_mod = ummp_mod * (1 + (tmod_p_max * (70 - 25) / 100))
    return udc_min_mod


# Calculates maximum short-circuit current/Výpočet maximálního zkratového proudu
def count_idc_max_str(isc, tmod_short):
    idc_max_str = isc * (1 + (tmod_short * (70 - 25)) / 100)
    return idc_max_str


# Calculates maximum panel count per string/Výpočet maximálního počtu panelů na string
def count_max_panel(max_input_voltage, udc_max_mod):
    panel_max_fl = max_input_voltage / udc_max_mod
    panel_max = math.floor(panel_max_fl)
    return panel_max


# Calculates minimum panel count per string/Výpočet minimálního počtu panelů na string
def count_min_panel(min_input_voltage, udc_min_mod):
    panel_min_fl = min_input_voltage / udc_min_mod
    panel_min = math.ceil(panel_min_fl)
    return panel_min


# Calculates optimal panel count per string/Výpočet optimálního počtu panelů na string
def count_optimal_panel(opt_input_voltage, ummp_mod):
    panel_optimal_fl = opt_input_voltage / ummp_mod
    panel_optimal = round(panel_optimal_fl)
    return panel_optimal


# Calculates strings for lowest possible count of mppts
def count_strings_for_lowest_mppts(uoc_mod, tmod, ummp_mod, tmod_p_max, max_input_voltage,
                                   min_input_voltage, max_inverter_count, panel_count):
    # Typical mppt count for one inverter, can be different if Sungrow inverters are used
    mppt_count = 2
    result = []

    udc_max_mod = count_udc_max_mod(uoc_mod, tmod)
    udc_min_mod = count_udc_min_mod(ummp_mod, tmod_p_max)
    # IDC_max_STR = count_IDC_max_STR(ISC, TMOD_short)

    max_panel = count_max_panel(max_input_voltage, udc_max_mod)
    min_panel = count_min_panel(min_input_voltage, udc_min_mod)
    # opt_panel = count_optimal_panel(opt_input_voltage, UmmpMOD)

    # Create alert in js for this exception??
    # Panel count can't be bigger than maximal string multiplied by count of all mppts
    if panel_count > max_panel * mppt_count * max_inverter_count:
        return None

    remaining_panels = panel_count

    for _ in range(max_inverter_count):
        if remaining_panels >= max_panel * mppt_count:
            result.append((max_panel,) * mppt_count)
            remaining_panels -= max_panel * mppt_count
        elif remaining_panels >= min_panel * mppt_count:
            optimal_panels_per_string = remaining_panels // mppt_count
            result.append((optimal_panels_per_string,) * mppt_count)
            remaining_panels -= optimal_panels_per_string * mppt_count
        else:
            result.append((remaining_panels // mppt_count,) * mppt_count)
            remaining_panels = 0

    i = 0
    while remaining_panels > 0:
        current_tuple = list(result[i])
        if current_tuple[0] < max_panel:
            current_tuple[0] += 1
            remaining_panels -= 1
        if mppt_count > 1 and current_tuple[1] < max_panel and remaining_panels > 0:
            current_tuple[1] += 1
            remaining_panels -= 1
        result[i] = tuple(current_tuple)
        i = (i + 1) % max_inverter_count

    return result


def count_panels_for_user_string_length(user_string_length, panel_count, max_inverter_count, panel_max, panel_min):
    mppt_count = 2
    remaining_panels = panel_count
    rest_of_panels = remaining_panels - (max_inverter_count * mppt_count * user_string_length)
    result: List[Tuple[int, int]] = []

    def clear_tuples(end_index):
        nonlocal rest_of_panels
        if end_index > 0:
            for i in range(end_index):
                result[i] = (0, 0)
            rest_of_panels += end_index * user_string_length

    def adjust_tuples(delta, comparator, reverse=False):
        nonlocal rest_of_panels
        idx_range = range(max_inverter_count - 1, -1, -1) if reverse else range(max_inverter_count)

        for i in idx_range:
            while result[i][0] > panel_min and result[i][1] > panel_min:
                if comparator(result[i][0]):
                    continue
                result[i] = tuple(val + delta for val in result[i])
                rest_of_panels -= 2 * delta
                if rest_of_panels == 0:
                    break
            if rest_of_panels == 0:
                break

            elif result[i][0] == panel_min and result[i][1] == panel_min:
                continue

    def merge_tuples():
        i = 0
        while i < max_inverter_count - 1:
            if result[i + 1][0] == 0:
                break
            if result[i][0] < user_string_length and result[i][0] + result[i + 1][0] < panel_max:
                result[i] = tuple(sum(x) for x in zip(cast(Tuple[int, int], result[i]), result[i + 1]))
                result[i + 1] = (0, 0)
                result.sort(reverse=True)
                i = 0
            else:
                i += 1

    def sort_tuples():
        result.sort(key=lambda x: (x[0], x[1]), reverse=True)

    for _ in range(max_inverter_count):
        result.append((user_string_length, user_string_length))

    end_index = rest_of_panels // user_string_length * -1
    clear_tuples(end_index)

    if rest_of_panels < 0:
        adjust_tuples(-1, lambda x: x == panel_min, reverse=True)
        merge_tuples()
        sort_tuples()

    elif rest_of_panels > 0:
        adjust_tuples(1, lambda x: x == panel_max)
        merge_tuples()
        sort_tuples()

    return result


# Displays latest results from database based on ids kept in sessions
class ResultsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        results = request.session.get('results', [])
        project_id = request.session.get('project_id')
        solution_id = request.session.get('solution_id')

        print(project_id, solution_id)

        project = Project.objects.get(pk=project_id)
        solution = Solution.objects.get(pk=solution_id)
        low_mppt_string_pairs = StringPair.objects.filter(solution=solution, result=StringPair.LOW_MPPT)
        user_string_pairs = StringPair.objects.filter(solution=solution, result=StringPair.USER_STRING)

        print(low_mppt_string_pairs.first(), user_string_pairs.first())

        return render(request, "results.html", {"results": results,
                                                "low_mppt_string_pairs": low_mppt_string_pairs,
                                                "user_string_pairs": user_string_pairs,
                                                "project": project, "solution": solution})


# View for saving new inverter to the database
class AddInverterView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'add_inverter.html')

    def post(self, request):
        form = InverterForm(request.POST)
        if form.is_valid():
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
            return render(request, 'add_inverter.html', {'form': form})


# Displays all inverters in database
class InvertersView(LoginRequiredMixin, View):
    def get(self, request):
        inverters = Inverter.objects.all()
        return render(request, "inverters.html", {"inverters": inverters})


# View for editing existing inverter in database
class InverterEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        inverter = Inverter.objects.get(pk=pk)
        form = InverterForm(initial={
            'name': inverter.name,
            'opt_input_voltage': inverter.opt_input_voltage,
            'min_input_voltage': inverter.min_input_voltage,
            'max_input_voltage': inverter.max_input_voltage,
            'max_mppt_count': inverter.max_mppt_count,
        })
        return render(request, 'edit_inverter.html', {'form': form})

    def post(self, request, pk):
        inverter = Inverter.objects.get(pk=pk)
        form = InverterForm(request.POST)
        if form.is_valid():
            inverter.name = form.cleaned_data['name']
            inverter.opt_input_voltage = form.cleaned_data['opt_input_voltage']
            inverter.min_input_voltage = form.cleaned_data['min_input_voltage']
            inverter.max_input_voltage = form.cleaned_data['max_input_voltage']
            inverter.max_mppt_count = form.cleaned_data['max_mppt_count']
            inverter.save()
            return redirect('inverters')
        else:
            print(form.errors)
            return render(request, 'edit_inverter.html', {'form': form})


# View for deleting existing inverter from database
class InverterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        inverter = get_object_or_404(Inverter, pk=pk)
        inverter.delete()
        return redirect('inverters')


# View for adding a new panel to the database
class AddPanelView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'add_panel.html')

    def post(self, request):
        form = PanelForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            uoc_mod_volt = form.cleaned_data['uoc_mod_volt']
            tmod_percent = form.cleaned_data['tmod_percent']
            ummp_mod_volt = form.cleaned_data['ummp_mod_volt']
            tmod_p_max_percent = form.cleaned_data['tmod_p_max_percent']
            isc_amper = form.cleaned_data['isc_amper']
            tmod_short_percent = form.cleaned_data['tmod_short_percent']

            Panel.objects.create(name=name, uoc_mod_volt=uoc_mod_volt, tmod_percent=tmod_percent,
                                 ummp_mod_volt=ummp_mod_volt, tmod_p_max_percent=tmod_p_max_percent,
                                 isc_amper=isc_amper, tmod_short_percent=tmod_short_percent)
            return redirect('panels')
        else:
            print(form.errors)
            return render(request, 'add_panel.html', {'form': form})


# View for editing existing panel in database
class PanelEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        panel = Panel.objects.get(pk=pk)
        form = PanelForm(initial={
            'name': panel.name,
            'uoc_mod_volt': panel.uoc_mod_volt,
            'tmod_percent': panel.tmod_percent,
            'ummp_mod_volt': panel.ummp_mod_volt,
            'tmod_p_max_percent': panel.tmod_p_max_percent,
            'isc_amper': panel.isc_amper,
            'tmod_short_percent': panel.tmod_short_percent,
        })
        return render(request, 'edit_panel.html', {'form': form})

    def post(self, request, pk):
        panel = Panel.objects.get(pk=pk)
        form = PanelForm(request.POST)
        if form.is_valid():
            panel.name = form.cleaned_data['name']
            panel.uoc_mod_volt = form.cleaned_data['uoc_mod_volt']
            panel.tmod_percent = form.cleaned_data['tmod_percent']
            panel.ummp_mod_volt = form.cleaned_data['ummp_mod_volt']
            panel.tmod_p_max_percent = form.cleaned_data['tmod_p_max_percent']
            panel.isc_amper = form.cleaned_data['isc_amper']
            panel.tmod_short_percent = form.cleaned_data['tmod_short_percent']
            panel.save()
            return redirect('panels')
        else:
            print(form.errors)
            return render(request, 'edit_panel.html', {'form': form})


# View for deleting existing panel from database
class PanelDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        panel = get_object_or_404(Panel, pk=pk)
        panel.delete()
        return redirect('panels')


# Displays all panels in database
class PanelsView(LoginRequiredMixin, View):
    def get(self, request):
        panels = Panel.objects.all()
        return render(request, 'panels.html', {"panels": panels})


# View for login
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


# Home view with tile navigation
class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'home.html')


# View for creating a new user
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


# Profile view shows list of engineers to group leaders, list of projects to engineers
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        solutions = []
        projects = []

        if user.role == 'group_leader':
            engineers = MyUser.objects.filter(group_leader_id=user.id)
            return render(request, 'profile.html', {'engineers': engineers, 'solutions': solutions,
                                                    'projects': projects})

        if user.role == 'engineer':
            solutions = Solution.objects.filter(owner_id=user.id)
            project_ids = SolutionProject.objects.filter(solution__in=solutions).values_list('project_id', flat=True)
            projects = Project.objects.filter(id__in=project_ids)
            return render(request, 'profile.html', {'solutions': solutions,
                                                    'projects': projects})


# View of specific engineer's projects for group leaders
class EngineerProjectView(LoginRequiredMixin, View):
    def get(self, request, eng_id):
        solutions = Solution.objects.filter(owner_id=eng_id)
        project_ids = SolutionProject.objects.filter(solution__in=solutions).values_list('project_id', flat=True)
        projects = Project.objects.filter(id__in=project_ids)

        return render(request, 'engineer_project.html', {'projects': projects, 'eng_id': eng_id})


# View of solutions for particular project
class SolutionsView(LoginRequiredMixin, View):
    def get(self, request, proj_id, eng_id=None):
        engineer = None
        if eng_id is not None:
            engineer = MyUser.objects.get(pk=eng_id)
        project = Project.objects.get(pk=proj_id)
        solution_ids = SolutionProject.objects.filter(project=project).values_list('solution_id', flat=True)
        solutions = Solution.objects.filter(id__in=solution_ids)

        string_pairs = StringPair.objects.filter(solution__in=solutions)

        return render(request, 'solutions.html', {
            'project': project,
            'solutions': solutions,
            'string_pairs': string_pairs,
            'engineer': engineer
        })


# Logout view
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
