def solve():
    MOD = 10**9 + 7
    n, k = map(int, input().split())

    if k > n * n:
        print(0)
        return

    prev_states = {((), ()): 1}

    for r in range(n):
        for c in range(n):
            d1 = r - c + n - 1
            d2 = r + c

            new_states = {}
            for (d1_tuple, d2_tuple), cnt in prev_states.items():
                key = (d1_tuple, d2_tuple)
                new_states[key] = (new_states.get(key, 0) + cnt) % MOD
                d1_used = d1 in d1_tuple
                d2_used = d2 in d2_tuple

                if not d1_used and not d2_used:
                    new_d1 = tuple(x for x in d1_tuple if x < d1) + (d1,) + tuple(x for x in d1_tuple if x > d1)
                    new_d2 = tuple(x for x in d2_tuple if x < d2) + (d2,) + tuple(x for x in d2_tuple if x > d2)
                    new_key = (new_d1, new_d2)
                    new_states[new_key] = (new_states.get(new_key, 0) + cnt) % MOD
            prev_states = new_states
    result = 0

    for (d1_tuple, d2_tuple), cnt in prev_states.items():
        if len(d1_tuple) == k:
            result = (result + cnt) % MOD

    print(result)

solve()