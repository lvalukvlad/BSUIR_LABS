n, k = map(int, input().split())
a = [0] + list(map(int, input().split()))
INF = -10**9
dp = [[INF] * (k+1) for _ in range(n+1)]
dp[0][0] = 0
for used in range(k+1):
    for i in range(n):
        if dp[i][used] == INF:
            continue
        if i+1 <= n:
            dp[i+1][used] = max(dp[i+1][used], dp[i][used] + a[i+1])
        if i+2 <= n:
            dp[i+2][used] = max(dp[i+2][used], dp[i][used] + a[i+2])
        if used < k:
            for j in range(i+1, n+1):
                dp[j][used+1] = max(dp[j][used+1], dp[i][used] + a[j])

ans = max(dp[n])
print(ans)