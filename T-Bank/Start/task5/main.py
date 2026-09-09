n = int(input())
a = list(map(int, input().split()))

if all(x == a[0] for x in a):
    print(' '.join(['0'] * n))
else:
    min_val = min(a)
    max_val = max(a)
    distinct_count = len(set(a))
    freq = {}

    for x in a:
        freq[x] = freq.get(x, 0) + 1

    result = []
    for x in a:
        if x == min_val or x == max_val:
            result.append(str(n - freq[x]))
        else:
            result.append(str(distinct_count))

    print(' '.join(result))