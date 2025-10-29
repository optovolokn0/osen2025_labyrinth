import sys
from collections import deque
from functools import lru_cache

def canonical_edge(u, v):
    return (u, v) if u <= v else (v, u)

def build_adj(edges_tuple):
    adj = {}
    for u, v in edges_tuple:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    return adj

def bfs(start, adj):
    dist = {start: 0}
    dq = deque([start])
    while dq:
        u = dq.popleft()
        for w in adj.get(u, ()):
            if w not in dist:
                dist[w] = dist[u] + 1
                dq.append(w)
    return dist

def solve(edges_input):
    edges_set = set(canonical_edge(u, v) for u, v in edges_input)
    start_virus = 'a'

    @lru_cache(maxsize=None)
    def dfs(virus_node, edges_tuple):
        edges = tuple(edges_tuple)
        edges_set_local = set(edges)

        candidates = []
        for u, v in edges:
            if u.isupper() and v.islower():
                candidates.append((u, v))
            elif v.isupper() and u.islower():
                candidates.append((v, u))
        candidates.sort(key=lambda x: (x[0], x[1]))

        for gateway, node in candidates:
            rem = canonical_edge(gateway, node)
            new_edges = edges_set_local.copy()
            new_edges.remove(rem)
            new_edges_tuple = tuple(sorted(new_edges))

            adj_new = build_adj(new_edges_tuple)

            dist_from_virus = bfs(virus_node, adj_new)
            reachable_gateways = [
                (g, dist_from_virus[g]) for g in adj_new.keys()
                if g.isupper() and g in dist_from_virus
            ]
            if not reachable_gateways:
                return [f"{gateway}-{node}"]

            min_dist = min(d for _, d in reachable_gateways)
            candidates_gateways = sorted([g for g, d in reachable_gateways if d == min_dist])
            target_gateway = candidates_gateways[0]

            dist_to_target = bfs(target_gateway, adj_new)
            d_current = dist_to_target.get(virus_node)
            if d_current is None:
                continue

            next_candidates = [
                nb for nb in sorted(adj_new.get(virus_node, []))
                if nb in dist_to_target and dist_to_target[nb] == d_current - 1
            ]
            if not next_candidates:
                continue
            next_node = next_candidates[0]

            if next_node.isupper():
                continue

            result = dfs(next_node, new_edges_tuple)
            if result is not None:
                return [f"{gateway}-{node}"] + result

        return None

    edges_tuple0 = tuple(sorted(edges_set))
    res = dfs(start_virus, edges_tuple0)
    return res if res is not None else []

def main():
    edges = []
    for line in sys.stdin:
        s = line.strip()
        if not s:
            continue
        u, sep, v = s.partition('-')
        if not sep:
            continue
        edges.append((u, v))
    ans = solve(edges)
    for item in ans:
        print(item)

if __name__ == "__main__":
    main()