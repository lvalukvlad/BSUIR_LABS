s = input().strip()
count_a = 0
count_ab = 0
count_abc = 0

for ch in s:
    if ch == 'a':
        count_a += 1
    elif ch == 'b':
        count_ab += count_a
    elif ch == 'c':
        count_abc += count_ab

print(count_abc)