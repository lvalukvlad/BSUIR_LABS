n, m = map(int, input().split())
adj = [[] for _ in range(n)]
edges = []

for i in range(m):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    adj[a].append(b)
    adj[b].append(a)
    edges.append((a, b))

INF = 10 ** 9
best_cycle = INF

for u, v in edges:
    dist = [-1] * n
    queue = [u]
    dist[u] = 0
    idx = 0
    found = False

    while idx < len(queue) and not found:
        cur = queue[idx]
        idx += 1
        for nxt in adj[cur]:
            if (cur == u and nxt == v) or (cur == v and nxt == u):
                continue
            if dist[nxt] == -1:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
                if nxt == v:
                    found = True
                    break

    if dist[v] != -1:
        cycle_len = dist[v] + 1
        if cycle_len < best_cycle:
            best_cycle = cycle_len

if best_cycle == INF:
    print(-1)
else:
    print(best_cycle)