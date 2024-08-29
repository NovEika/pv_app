import math

# User input:
optimal_napeti_vstup_stridac_V = int(input("Optimální napětí na vstupu střídače: "))
min_napeti_vstup_stridace_V = int(input("Min napětí na vstupu střídače nebo MPPT: "))
max_napeti_vstup_stridace_V = int(input("Max napětí na vstupu střídače nebo MPPT: "))
max_mttp_count = int(input("Vložte maximální počet mttp trackerů: "))
panel_count = int(input("Vložte celkový počet panelů: "))
napeti_naprazdno_FV_modul = float(input("Napětí naprázdno FV modulu: "))
teplotni_koef_FV_modul = float(input("Teplotní koeficient modulu: "))
napeti_max_vykon_FV_modul = float(input("Napětí FV modulu při max. výkonu: "))
teplotni_koef_pmax_modul = float(input("Teplotní koeficient modulu Pmax: "))
proud_nakratko_FV_modul_A = float(input("Proud nakrátko FV modulu: "))
teplotni_koef_modul_nakratko = float(input("Teplotní koeficient modulu nakrátko: "))
# User input or app will calculate the best length of string
user_panel_count_per_string = int(input("Vložte optimální počet panelů pro string: "))

# Basic setting
mttp_input_count = 2
result_low_mttp = []
result_user_input = []
result_optimal = []
result_optimal_autocalculated = []
optimal_str_len = 0
last_string = 0
remainder_panel = panel_count
UDC_max_MOD = float()
UDC_min_MOD = float()
IDC_max_STR = float()

panel_max = int()
panel_min = int()
panel_optimal = int()


# Stanoveni maximalniho napeti naprazdno
def count_UDC_max_MOD():
    UDC_max_MOD = napeti_naprazdno_FV_modul * (1 + teplotni_koef_FV_modul * (-20-25) /100)
    return  UDC_max_MOD

# Stanovení minimálního napětí
def count_UDC_min_MOD():
    UDC_min_MOD = napeti_max_vykon_FV_modul * (1 + (teplotni_koef_pmax_modul * (70-25) / 100))
    return UDC_min_MOD

# Výpočet maximálního zkratového proudu
def count_IDC_max_STR():
    IDC_max_STR = proud_nakratko_FV_modul_A * (1 + (teplotni_koef_modul_nakratko*(70-25)) / 100)
    return IDC_max_STR

def count_max_panel():
    panel_max_fl = max_napeti_vstup_stridace_V / UDC_max_MOD
    panel_max = math.floor(panel_max_fl)
    return panel_max

def count_min_panel():
    panel_min_fl = min_napeti_vstup_stridace_V / UDC_min_MOD
    panel_min = math.ceil(panel_min_fl)
    return panel_min

def count_optimal_panel():
    panel_optimal_fl = optimal_napeti_vstup_stridac_V / napeti_max_vykon_FV_modul
    panel_optimal = round(panel_optimal_fl)
    return panel_optimal


# Count strings for as little mppts as possible:
def count_low_mttp():
    remainder_panel = panel_count

    if panel_count // panel_max // 2 > max_mttp_count:
        print("Too many panels for this count of mttps.")
        quit()

    while len(result_low_mttp) < max_mttp_count:
        for x in panel_range:
            tuple_found = True
            if len(result_low_mttp) == max_mttp_count:
                break
            if remainder_panel <= 0:
                for z in range(max_mttp_count - len(result_low_mttp)):
                    result_low_mttp.append((0, ) * mttp_input_count)
                break
            while (tuple_found):
                # print(remainder_panel)
                if (remainder_panel - x * mttp_input_count == 0):
                    result_low_mttp.append((x,) * mttp_input_count)
                    break
                if (remainder_panel - x * mttp_input_count) > panel_min:
                    result_low_mttp.append((x, ) * mttp_input_count)
                    remainder_panel -= x * mttp_input_count
                elif remainder_panel < x  and remainder_panel > 0 or remainder_panel//2 < x and remainder_panel//2 > 0:
                    if remainder_panel < x:
                        result_low_mttp.append((remainder_panel, 0))
                        remainder_panel -= x
                    else:
                        result_low_mttp.append((remainder_panel//2, remainder_panel//2))
                        remainder_panel -= remainder_panel
                else:
                    tuple_found = False
    return result_low_mttp


# Count strings for optimal string length
def count_user_input_mttp(panel_input):
    remainder_panel = panel_count
#     Pokud je zbytek 0, rozpočítat optimální string do všech tuples; zbytek > 0 přidat do všech stringů + 1 nebo zaplnit první;
#     zbytek < 0 ubrat ze všech stringů - 1 nebo zkráti poslední
    rest_of_panels = remainder_panel - (max_mttp_count * mttp_input_count * panel_input)

    while len(result_user_input) < max_mttp_count:
        if rest_of_panels == 0:
            for x in range(max_mttp_count):
                result_user_input.append((panel_input, panel_input))
                remainder_panel = 0
        elif rest_of_panels < 0:
            for x in range(max_mttp_count):
                result_user_input.append((panel_input, panel_input))
                remainder_panel -= panel_input * 2
            while remainder_panel < 0:
                for y in range(max_mttp_count - 1, -1, -1):
                    if result_user_input[y][0] == panel_min:
                        continue
                    else:
                        result_user_input[y] = tuple(val - 1 for val in result_user_input[y])
                        remainder_panel += 2
                        break
            a = 0
            while a < max_mttp_count - 1:
                index_b = a + 1
                if result_user_input[index_b][0] == 0:
                    break
                elif (result_user_input[a][0] < panel_input) and (result_user_input[a][0] + result_user_input[index_b][0] < panel_max):
                    new_tuple = tuple(
                        val_a + val_b for val_a, val_b in zip(result_user_input[a], result_user_input[index_b]))
                    result_user_input[a] = new_tuple
                    result_user_input[index_b] = (0, 0)
                    result_user_input.sort(reverse=True)
                    a = 0
                else:
                    a += 1

        elif rest_of_panels > 0:
            for x in range(max_mttp_count):
                result_user_input.append((panel_input, panel_input))
                remainder_panel -= panel_input * 2
            while remainder_panel > 0:
                for y in range(max_mttp_count):
                    if result_user_input[y][0] == panel_max:
                        continue
                    else:
                        result_user_input[y] = tuple(val + 1 for val in result_user_input[y])
                        remainder_panel -= 2
                        break
            a = 0
            while a < max_mttp_count - 1:
                index_b = a + 1
                if result_user_input[index_b][0] == 0:
                    break
                elif (result_user_input[a][0] < panel_input) and (
                        result_user_input[a][0] + result_user_input[index_b][0] < panel_max):
                    new_tuple = tuple(
                        val_a + val_b for val_a, val_b in zip(result_user_input[a], result_user_input[index_b]))
                    result_user_input[a] = new_tuple
                    result_user_input[index_b] = (0, 0)
                    result_user_input.sort(reverse=True)
                    a = 0
                else:
                    a += 1


# Vypočítá stringy pro optimální délku zadanou uživatelem
def count_optimal_mttp():
    for r in panel_range:
        last_string = panel_count % (r * mttp_input_count * (max_mttp_count - 1))
        if (last_string > panel_min and last_string < panel_max or last_string // 2 > panel_min
                and last_string // 2 < panel_max):
            optimal_str_len = r
            c = max_mttp_count - 1
            for n in range(c):
                result_optimal.append((optimal_str_len, optimal_str_len))
            if last_string > panel_max:
                last_string //= 2
                result_optimal.append((last_string, last_string))
            else:
                result_optimal.append((last_string, 0))
            break
        else:
            continue


#   Vypočítá stringy pro optimální délku vypočtenou vzorcem
def count_autocalculated_optimal_mttp():
    remainder_panel = panel_count
    for x in range(max_mttp_count):
        result_optimal_autocalculated.append((panel_optimal, panel_optimal))
        remainder_panel -= panel_optimal * mttp_input_count
    return result_optimal_autocalculated


# Vypočítá stringy pro optimální délku zadanou uživatelem
def count_optimal_mttp():
    for r in panel_range:
        last_string = panel_count % (r * mttp_input_count * (max_mttp_count - 1))
        if panel_min < last_string < panel_max or panel_min < last_string // 2 < panel_max:
            optimal_str_len = r
            c = max_mttp_count - 1
            for nevim in range(c):
                result_optimal.append((optimal_str_len, optimal_str_len))
            if last_string > panel_max:
                last_string //= 2
                result_optimal.append((last_string, last_string))
            else:
                result_optimal.append((last_string, 0))
            break
        else:
            continue
    return result_optimal


# Main
UDC_max_MOD = count_UDC_max_MOD()
UDC_min_MOD = count_UDC_min_MOD()
IDC_max_STR = count_IDC_max_STR()
panel_min = count_min_panel()
panel_max = count_max_panel()
panel_optimal = count_optimal_panel()

panel_range_unreversed = list(range(panel_min, panel_max+1))
panel_range = panel_range_unreversed[::-1]

count_low_mttp()
count_user_input_mttp(user_panel_count_per_string)
count_user_input_mttp(panel_optimal)
count_optimal_mttp()

print(f"Minimum panelů: {count_min_panel()}")
print(f"Maximum panelů: {count_max_panel()}")
print(f"Optimum panelů: {count_optimal_panel()}")
print(f"Max napětí naprázdo: {UDC_max_MOD} V")
print(f"Min napětí MPP: {UDC_min_MOD} V")
print(f"Maximální zkratový proud: {IDC_max_STR} A")
print(f"Solution for lowest count of mttps: {result_low_mttp}")
print(f"Solution for optimal count of panels per string: {result_user_input}")
print(f"Solution for automatically calculated optimal string lenght z pohledu napětí: {result_optimal_autocalculated}")
print(f"Solution for automatically calculated optimal string length z pohledu celkového počtu panelů a střídačů:"
      f"{result_optimal}")
