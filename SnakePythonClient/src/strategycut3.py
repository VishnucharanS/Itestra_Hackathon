from collections import deque

# ==========================================================
# MOVES
# ==========================================================

DIRECTIONS = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "WEST": (-1, 0),
    "EAST": (1, 0),
}

OPPOSITE = {
    "NORTH": "SOUTH",
    "SOUTH": "NORTH",
    "WEST": "EAST",
    "EAST": "WEST",
}

# ==========================================================
# HELPERS
# ==========================================================

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def wrap(p, w, h):
    return (p[0] % w, p[1] % h)

def dist(a, b, w, h):
    return min(abs(a[0]-b[0]), w-abs(a[0]-b[0])) + \
           min(abs(a[1]-b[1]), h-abs(a[1]-b[1]))

# ==========================================================
# ITEMS
# ==========================================================

def classify(items):
    apples, bad, swords = [], [], []

    for it in items:
        kind = str(it.kind).lower()
        pos = it.position

        if "sword" in kind:
            swords.append(pos)
        elif "bad" in kind:
            bad.append(pos)
        elif "apple" in kind:
            apples.append(pos)

    return apples, bad, swords

# ==========================================================
# FLOOD FILL
# ==========================================================

def flood_fill(start, blocked, size, limit=350):
    if start in blocked:
        return 0

    w, h = size
    q = deque([start])
    seen = {start}
    c = 0

    while q and c < limit:
        cur = q.popleft()
        c += 1

        for d in DIRECTIONS.values():
            nxt = wrap(add(cur, d), w, h)
            if nxt in blocked or nxt in seen:
                continue
            seen.add(nxt)
            q.append(nxt)

    return c

# ==========================================================
# ENEMY PRESSURE
# ==========================================================

def enemy_zones(snakes, me, size):
    w, h = size
    danger = set()

    for s in snakes:
        if s["head"] == me:
            continue

        hx, hy = s["head"]

        for dx, dy in DIRECTIONS.values():
            danger.add(wrap((hx + dx, hy + dy), w, h))

    return danger

# ==========================================================
# SURVIVAL CHECK
# ==========================================================

def safe_move(nxt, blocked, size):
    return flood_fill(nxt, blocked, size) > 8

# ==========================================================
# NEW: WOULD WE DIE NEXT TURN?
# ==========================================================

def would_die_next(my_head, blocked, size):
    w, h = size

    for d in DIRECTIONS.values():
        nxt = wrap(add(my_head, d), w, h)
        if nxt not in blocked:
            return False
    return True

# ==========================================================
# NEW: FIND VALID CUT MOVE
# ==========================================================

def find_cut_move(my_head, snakes, blocked, size):
    w, h = size

    for s in snakes:
        if s["head"] == my_head:
            continue

        body = s.get("body", [])

        for i in range(1, len(body)):  # avoid head
            cell = body[i]

            # try moving into cut cell
            for move, d in DIRECTIONS.items():
                nxt = wrap(add(my_head, d), w, h)

                if nxt == cell and nxt not in blocked:
                    return move, s

    return None, None

def enemy_can_reach(cell, snakes, size):
    w, h = size

    for s in snakes:
        head = s["head"]
        d = dist(head, cell, w, h)

        # enemy can reach within 2 steps advantage
        if d <= 2:
            return True

    return False

# ==========================================================
# MAIN STRATEGY
# ==========================================================

_sword_used = 0


def choose_next_move(my_head, obstacles, snakes, size, items, direction):
    global _sword_used

    w, h = size

    my_snake = next((s for s in snakes if s["head"] == my_head), None)
    body = set(my_snake.get("body", [])) if my_snake else set()

    apples, bad, swords = classify(items)
    danger = enemy_zones(snakes, my_head, size)

    blocked = obstacles | body

    best_move = direction
    best_score = -1e18
    activate = False

    sword_phase = _sword_used < 3

    # ======================================================
    # HARD SURVIVAL TRIGGER FOR SWORD
    # ======================================================

    no_escape = would_die_next(my_head, blocked, size)

    cut_move, cut_target = None, None

    if sword_phase:
        cut_move, cut_target = find_cut_move(my_head, snakes, blocked, size)

    if no_escape and cut_move:
        # only activate if cut cell is NOT instant death trap
        cut_nxt = wrap(add(my_head, DIRECTIONS[cut_move]), w, h)

        if cut_nxt not in danger:
            activate = True
            return cut_move, activate

    # ======================================================
    # NORMAL MOVE SELECTION
    # ======================================================

    for move, d in DIRECTIONS.items():

        if move == OPPOSITE.get(direction):
            continue

        nxt = wrap(add(my_head, d), w, h)

        if nxt in blocked:
            continue

        score = 0

        if nxt in danger:
            score -= 600

        space = flood_fill(nxt, blocked, size)
        score += space * 12

        if space < 10:
            score -= 900

        # sword chasing (SAFE ONLY)
        if sword_phase and swords:
            target = min(swords, key=lambda s: dist(my_head, s, w, h))

            enemy_threat = enemy_can_reach(target, snakes, size)

            # HARD RULE: do not contest sword if unsafe
            if not enemy_threat:
                score += max(0, 120 - dist(nxt, target, w, h) * 10)

        # apples still useful
        if apples:
            nearest = min(dist(nxt, a, w, h) for a in apples)
            score += max(0, 35 - nearest * 2)

        if nxt in bad:
            score -= 300

        if move == direction:
            score += 5

        if not safe_move(nxt, blocked, size):
            score -= 1200

        if score > best_score:
            best_score = score
            best_move = move

    return best_move, False