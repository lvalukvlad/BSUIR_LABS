n, m = map(int, input().split())

for L in range(28, 32):
    if ((m + 14 - 1) % L) + 1 == n:
        x = ((m + 7 - 1) % L) + 1
        print(x)
        break