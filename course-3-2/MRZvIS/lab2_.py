#   Лабораторная работа №2 по дисциплине МРЗвИС
#   Задача: реализовать и исследовать модель решения на ОКМД архитектуре задачи
#   вычисления матрицы значений             
#   Вариант: 17. (~) = x /3\ y = max({x+y-1} U {0}); /~\ = x /3\ y = max({x+y-1} U {0});  x ~> y = min({1-x+y}U{1})
#      
#   Автор: Титов А. В. (321703)
#   Дата: 24.02.2026
#
#   Используемые источники: https://libeldoc.bsuir.by/handle/123456789/42611

import random

def generate_matrix(rows: int, cols: int):
    return [[round(random.uniform(-1,1), 4) for _ in range(cols)] for _ in range(rows)]


p = int(input("Введите p "))
q = int(input("Введите q "))
m = int(input("Введите m "))

operation3_time = int(input("Введите время для  x /~\ y  и  x (~) y "))
sum_time =  int(input("Введите время для суммы "))
implication_time =  int(input("Введите время для импликации "))
product_time =  int(input("Введите время для произведения "))
negation_time =  int(input("Введите время для разности "))

k_product_time = product_time * (m-1) # время для (/~\k x[k])
neg_k_product_time = product_time * (m-1) + m * negation_time + negation_time # время для произведения (\~/k x[k]) 

one_element_count_time = operation3_time + operation3_time * m + sum_time * 2 * m + 2 * sum_time + product_time * 7 * m + 7 * product_time +\
                         negation_time * 3*m + 3 * negation_time + k_product_time + neg_k_product_time + implication_time * 2 * m

print(f"Время для вычисления Сij = {one_element_count_time}")


random.seed(1)
A = generate_matrix(p, m)
B = generate_matrix(m, q)
E = generate_matrix(1, m)
G = generate_matrix(p, q)
C = [[0 for _ in range(q)] for _ in range(p)]


def print_matrix(matrix, name: str):
    print(f"{name} = ")
    for row in matrix:
        print(row)
    print("\n")

print_matrix(A, "A")
print_matrix(B, "B")
print_matrix(E, "E")
print_matrix(G, "G")
#print_matrix(C, "C")


def implication(x, y):   # x ~> y
    return min(1 - x + y, 1)


def operation3(x, y):   # x /~\ y  и  x (~) y
    return max(x + y - 1, 0)


def k_product_operation(values: list):  # (/~\k x[k])
    product = 1
    for item in values:
        product *= item

    return product


def k_negation_product_operation(values: list): # (\~/k x[k])
    product = 1
    for item in values:
        product *= (1 - item)

    return 1 - product

import time
start = time.time()
for i in range(p):
    for j in range(q):
        f_list = []
        d_list = []
        for k in range(m):
            a = A[i][k]
            b = B[k][j]
            e = E[0][k]

            d = operation3(a, b)
            d_list.append(d)

            impl_ab = implication(a, b)
            impl_ba = implication(b, a)

            part1 = impl_ab * (2 * e - 1) * e                        #(a[i][k] ~> b[k][j])* (2* e[k] - 1) * e[k]
            part2 = impl_ba * (1 + (4* impl_ab - 2) * e ) * (1 - e)  # (b[k][j] ~> a[i][k])* (1 + (4*(a[i][k] ~> b[k][j]) - 2) * e[k]) * (1-e[k])

            f_ijk =  part1 + part2
            f_list.append(f_ijk)

        

        g = G[i][j]
        d_ij = k_negation_product_operation(d_list)  # (\~/k d)
        f_prod = k_product_operation(f_list)  # (/~\k f)
        
        temp = operation3(f_prod, d_ij)  #((/~\k f(i,j,k)) (~) d[i][j])
        
        part_c_1 = f_prod * (3* g - 2) * g                        # (/~\k f(i,j,k)) * (3* g[i][j] - 2) * g[i][j]            
        part_c_2 = (1 - g) * (d_ij + (4*temp - 3* d_ij) * g)      # (1 - g[i][j]) * (d[i][j] + (4*((/~\k f(i,j,k)) (~) d[i][j]) - 3* d[i][j]) * g[i][j])

        C[i][j] = part_c_1 + part_c_2
end = time.time()
print(end-start)
print_matrix(C, "Результат C")     