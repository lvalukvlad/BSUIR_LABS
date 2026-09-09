s = input().strip()
n = len(s)

A = "tbank"
B = "study"

def calc_cost(pat, i):
    cost = 0
    for j in range(len(pat)):
        if s[i + j] != pat[j]:
            cost += 1
    return cost

cost_a = []
cost_b = []

for i in range(n - 4):
    cost_a.append(calc_cost(A, i))
    cost_b.append(calc_cost(B, i))

m = len(cost_b)  # m = n - 4
min_left = [float('inf')] * m
min_right = [float('inf')] * m

min_so_far = float('inf')
for i in range(m):
    if cost_b[i] < min_so_far:
        min_so_far = cost_b[i]
    min_left[i] = min_so_far

min_so_far = float('inf')
for i in range(m - 1, -1, -1):
    if cost_b[i] < min_so_far:
        min_so_far = cost_b[i]
    min_right[i] = min_so_far

ans = float('inf')

for i in range(len(cost_a)):
    cur_cost = cost_a[i]
    best = float('inf')
    if i - 5 >= 0:
        best = min(best, min_left[i - 5])
    if i + 5 < m:
        best = min(best, min_right[i + 5])
    if best != float('inf'):
        ans = min(ans, cur_cost + best)

print(ans)