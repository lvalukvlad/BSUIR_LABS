t = int(input().strip())

for _ in range(t):
    s = input().strip()
    n = len(s)

    if '1' not in s:
        print(0)
        continue

    groups = []
    i = 0
    while i < n:
        if s[i] == '1':
            cnt = 0
            while i < n and s[i] == '1':
                cnt += 1
                i += 1
            groups.append(cnt)
        else:
            i += 1

    if sum(groups) == n:
        print(n * n)
        continue

    max_block = max(groups)
    if s[0] == '1' and s[-1] == '1' and len(groups) >= 2:
        max_block = max(max_block, groups[0] + groups[-1])

    L = max_block
    best = 0
    for h in range(1, L + 1):
        w = L - h + 1
        if w <= 0:
            break
        area = h * w
        if area > best:
            best = area

    print(best)