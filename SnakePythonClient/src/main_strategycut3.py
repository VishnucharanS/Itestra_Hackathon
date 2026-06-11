import argparse
import time

from api import SnakeFieldAPI
from strategycut3 import choose_next_move   # <-- updated strategy

def is_valid_coord(c):
    return isinstance(c, (list, tuple)) and len(c) >= 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("team_name")
    parser.add_argument("game_name")
    parser.add_argument("--password", default="test")
    parser.add_argument("--base_url", default="http://localhost:3030")
    args = parser.parse_args()

    api = SnakeFieldAPI(
        args.base_url,
        args.team_name,
        args.game_name,
        args.password
    )

    current_direction = "NORTH"
    api.set_direction(current_direction)

    print("Bot started.")

    while True:
        time.sleep(0.5)

        field = api.get_field()
        if not field:
            continue

        snake = field.snakes.get(args.team_name)
        if not snake or not snake.alive or not snake.body:
            continue

        head = snake.body[0]

        if not is_valid_coord(head):
            continue

        my_head = (int(head[0]), int(head[1]))

        # ---------------- OBSTACLES ----------------
        obstacles = set()
        snakes_info = []

        for name, s in field.snakes.items():
            body = [(int(x), int(y)) for x, y in s.body]

            obstacles.update(body)

            snakes_info.append({
                "name": name,
                "body": body,
                "head": body[0]
            })

        # ---------------- ITEMS (NO SPAM DEBUG) ----------------
        items = field.items

        # ONLY ONE SHORT DEBUG LINE
        print(f"[DBG] A:{len([i for i in items if 'apple' in str(i.kind).lower()])} "
              f"B:{len([i for i in items if 'bad' in str(i.kind).lower()])} "
              f"S:{len([i for i in items if 'sword' in str(i.kind).lower()])}")

        # ---------------- STRATEGY ----------------
        new_dir, activate = choose_next_move(
            my_head,
            obstacles,
            snakes_info,
            field.size,
            items,
            current_direction,
        )

        # ---------------- SWORD ACTIVATION ----------------
        if activate:
            try:
                api.activate_item("Sword")   # IMPORTANT HOOK
            except:
                pass

        current_direction = new_dir
        api.set_direction(current_direction)