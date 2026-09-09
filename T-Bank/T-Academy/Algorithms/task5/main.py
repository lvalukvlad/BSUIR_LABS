def solve():
    N, Q = map(int, input().split())
    adj = [[] for _ in range(N + 1)]

    for _ in range(Q):
        l, r = map(int, input().split())
        adj[l - 1].append(r)
        adj[r].append(l - 1)

    dist = [-1] * (N + 1)
    dist[0] = 0
    queue = [0]
    front = 0

    while front < len(queue):
        u = queue[front]
        front += 1
        if u == N:
            break

        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)

    if dist[N] == -1:
        print("No")
    else:
        print("Yes")
        print(dist[N])

if __name__ == "__main__":
    solve()