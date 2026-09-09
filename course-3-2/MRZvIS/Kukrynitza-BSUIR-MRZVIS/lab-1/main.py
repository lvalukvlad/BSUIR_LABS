# Лабораторная работа #1 по предмету "Методы решения задач в интеллектуальных системах"
#
# Автор:
# студент гр. 321701
# Политыко И.А.
#
# Задание:
# (6) алгоритм вычисления целочисленного частного пары 4-разрядных чисел делением без восстановления частичного остатка.
#
# Источники:
# (1) Интеграционная платформа
import os

def to_bin(val, bits):
    return bin(val & (2 ** bits - 1))[2:].zfill(bits)


def bitwise_add(bin_a, bin_b, bits=5):
    a = int(bin_a, 2)
    b = int(bin_b, 2)
    mask = (1 << bits) - 1
    res = (a + b) & mask
    return to_bin(res, bits)


def bitwise_sub(bin_a, bin_b, bits=5):
    a = int(bin_a, 2)
    b = int(bin_b, 2)
    mask = (1 << bits) - 1
    res = (a - b) & mask
    return to_bin(res, bits)


def division_step_bin(A, Q, M):
    combined = A + Q
    combined = combined[1:] + '0'
    A = combined[:5]
    Q = combined[5:]

    if A[0] == '0':
        A = bitwise_sub(A, M, bits=5)
        op = "-M"
    else:
        A = bitwise_add(A, M, bits=5)
        op = "+M"

    bit = '1' if A[0] == '0' else '0'
    Q = Q[:-1] + bit
    return A, Q, op, bit



def render_pipeline(current_time, stages, results_log):
    current_time = current_time - 1
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('')
    print(f"=== ТАКТ: {current_time} ".ljust(75, "="))
    print(f"{'ЭТАП':<8} | {'№':<3} | {'A (5б)':<6} | {'Q (4б)':<6} | {'M (4б)':<6} | {'СТАТУС'}")
    print("-" * 75)
    for i in range(4):
        st = stages[i]
        if st:
            print(f"Этап {i + 1:<4} | {st['idx']:<3} | {st['A']:<6} | {st['Q']:<6} | {st['M'][1:]:<6} | {st['status']}")
        else:
            print(f"Этап {i + 1:<4} | {'-':<3} | {'-':<6} | {'-':<6} | {'-':<6} | [ Свободен ]")
    print("-" * 75)
    print("ВЫПОЛНЕННЫЕ ПАРЫ:")
    for res in results_log:
        print(f"  √ {res}")


def pipeline_division_bin(pairs_input, ti):
    pairs = pairs_input.copy()
    stages = [None] * 4
    step_counters = [0] * 4
    current_time = 0
    results_log = []
    final_results = []

    while pairs or any(stages):
        current_time += 1

        for i in reversed(range(4)):
            curr = stages[i]
            if not curr: continue

            if curr.get('last_finished_stage', -1) < i:
                if step_counters[i] < ti[i]:
                    step_counters[i] += 1
                    curr['status'] = f"Задержка {step_counters[i]}/{ti[i]}"
                else:
                    A, Q, op, bit = division_step_bin(curr['A'], curr['Q'], curr['M'])
                    curr.update({'A': A, 'Q': Q, 'status': f"{op}, bit={bit}", 'last_finished_stage': i})

                    if i == 3:
                        if curr['A'][0] == '1':
                            curr['A'] = bitwise_add(curr['A'], curr['M'], bits=5)
                            curr['status'] += " + Коррекция"

                        res_val = {
                            'idx': curr['idx'],
                            'Q_bin': curr['Q'], 'R_bin': curr['A'], 'M_bin': curr['M'],
                            'Q_dec': int(curr['Q'], 2), 'R_dec': int(curr['A'], 2), 'M_dec': int(curr['M'], 2),
                            'time': current_time
                        }
                        final_results.append(res_val)
                        results_log.append(
                            f"Пара {res_val['idx']}: Q={res_val['Q_dec']}, R={res_val['R_dec']}, M={res_val['M_dec']}, (такт {current_time - 1})")

            if curr.get('last_finished_stage') == i:
                if i < 3:
                    if stages[i + 1] is None:
                        stages[i + 1] = curr
                        stages[i] = None
                        step_counters[i + 1] = 0
                    else:
                        curr['status'] = "Ожидание (след. этап занят)"
                else:
                    stages[i] = None

        if pairs and stages[0] is None:
            idx, (a, b) = pairs.pop(0)
            stages[0] = {
                'idx': idx, 'A': '00000', 'Q': to_bin(a, 4),
                'M': to_bin(b, 5), 'status': "Загрузка",
                'last_finished_stage': -1
            }
            step_counters[0] = 0

        render_pipeline(current_time, stages, results_log)
        input("\n>>> [ENTER]")

    print("\n" + " ИТОГОВЫЕ РЕЗУЛЬТАТЫ ".center(75, "="))
    print(f"{'№':<3} | {'Q (bin)':<8} | {'Q (dec)':<8} | {'R (bin)':<8} | {'R (dec)':<8} | {'M (bin)':<8} | {'M (dec)':<8}| {'Такт'}")
    print("-" * 75)
    for res in sorted(final_results, key=lambda x: x['idx']):
        print(
            f"{res['idx']:<3} | {res['Q_bin']:<8} | {res['Q_dec']:<8} | {res['R_bin']:<8} | {res['R_dec']:<8} | {res['M_bin'][1:]:<8} | {res['M_dec']:<8} | {res['time'] - 1}")
    print("=" * 75)


if __name__ == "__main__":
    ti_config = [0, 0, 0, 0]
    data= []
    count = 0
    choice = 0
    while int(choice) == 0:
        dividend = input("Введите делимое\n")
        divisor = input("Ввести делитель\n")
        data.append((count, (int(dividend), int(divisor))))
        count += 1
        choice = input("Ввести новую пару - 0, Приступить к выполнению - 1\n")
        os.system('cls' if os.name == 'nt' else 'clear')
        os.system('')

    pipeline_division_bin(data, ti_config)