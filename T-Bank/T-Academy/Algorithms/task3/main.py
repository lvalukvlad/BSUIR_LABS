N = int(input())
S = input().strip()
left = [-1] * (N + 2)
right = [-1] * (N + 2)

for i in range(1, N + 1):
    if S[i-1] == 'L':
        l = left[i-1]
        left[i] = l
        right[i] = i-1
        left[i-1] = i
        if l != -1:
            right[l] = i
    else:
        r = right[i-1]
        right[i] = r
        left[i] = i-1
        right[i-1] = i
        if r != -1:
            left[r] = i

start = 0
for x in range(N + 1):
    if left[x] == -1:
        start = x
        break

result = []
cur = start
while cur != -1:
    result.append(cur)
    cur = right[cur]

print(' '.join(map(str, result)))