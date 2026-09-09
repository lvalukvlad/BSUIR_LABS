n, q = map(int, input().split())
s = input().strip()

base = s
ops = []

for _ in range(q):
    data = list(map(int, input().split()))
    if data[0] == 1:
        l = data[1]
        r = data[2]
        ops.append((l, r))
    else:
        pos = data[1]  
        cur = pos

        for i in range(len(ops) - 1, -1, -1):
            l, r = ops[i]
            seg_len = r - l + 1
            new_end = l + 2 * seg_len - 1

            if cur < l:
                continue
            elif cur <= new_end:
                offset = cur - l
                cur = l + offset // 2
            else:
                cur = cur - seg_len
        print(base[cur - 1])