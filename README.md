# Itestra Hackathon — Autonomous Snake Bot

**Result: 1st Place**  
**Team Name: Titanaboa**     
**Team:** Vishnucharan Saravanamoorthy, Saimothish Ramalingam, Yasashwini  Gutta    
**Event:** Itestra x Bonding Hackathon, Aachen

---

## Overview

A competitive autonomous bot built for a multiplayer Snake arena where all teams' bots compete simultaneously in real-time. The challenge spanned multiple rounds, each introducing different game mechanics and special abilities. The final round carried the highest weightage and is where our strategy performed best.

The server-client architecture was provided by the organizers. Our responsibility was designing and implementing the full decision-making logic — pathfinding, survival, ability management, and enemy prediction — from scratch.

---

## Final Round Strategy

The core philosophy was **survival over aggression**: stay alive the longest rather than chase eliminations. Abilities were treated as emergency tools, not defaults.

### Pathfinding
Navigation used a **risk-aware BFS** on a toroidal (wrapping) grid. Rather than simply finding the shortest path, each candidate path was evaluated against:
- Enemy predicted positions (1, 2, and 3-step lookahead)
- Sword and boost threat zones from opponents
- Flood fill space estimation to avoid trapping into dead ends

### Move Scoring
Every legal move was scored across multiple factors simultaneously:

| Factor | Description |
|--------|-------------|
| **Flood fill space** | How much open area is reachable from the next cell (primary survival signal) |
| **Enemy danger** | Proximity to predicted enemy head positions, sword range, boost threat zones |
| **Body exposure** | How exposed our own body is to enemy threats after the move |
| **Item value** | Apples, swords, boosts, stacks, stars — weighted by safety and contestedness |
| **Anti-loop** | Penalises revisiting recent positions to prevent oscillation |
| **Directional continuity** | Slight preference for maintaining current direction unless a better option exists |

### Ability Management
All four abilities were activated conditionally, not reactively:

- **Sword** — triggered only when an adjacent enemy body segment could be cleanly cut, or when positioned for a 2-step setup cut
- **Boost** — used only when both steps ahead were safe, and the situation involved escaping danger, racing for a key item, or a large open escape corridor
- **Stack** — activated as a panic reset when space dropped below a threshold or body exposure became critical
- **Star** — deployed when moving through a high-risk zone or when close contested items needed to be claimed safely

---

## Sub-Challenge Strategies

Each earlier round had distinct mechanics requiring separate strategy implementations:

| File | Challenge | Approach |
|------|-----------|----------|
| `strategycut3.py` / `main_cut.py` | Cut round | BFS-based path interception; navigates toward enemy body segments to cut them off using sword |
| `strategyfight1.py` / `main_fight.py` | Fight round | Collect-and-strike mode; accumulates swords and boosts, enters attack state when enemy is within range, uses flood fill for safe repositioning |
| `strategyStacky1.py` / `main_stacky1.py` | Stack round | Stack-safe combat survival; activates stack defensively when body exposure crosses a threat threshold, scores moves against multi-step enemy prediction |

---

## Repository Structure

```
SnakePythonClient/
└── src/
    ├── strategy_final_updated.py   # Final round — BFS + scored move selection
    ├── main_final.py               # Entry point for final round
    ├── strategyStacky1.py          # Stacking round strategy
    ├── main_stacky1.py             # Entry point for stacking round
    ├── strategyfight1.py           # Fight round strategy
    ├── main_fight.py               # Entry point for fight round
    ├── strategycut3.py             # Cut round strategy
    ├── main_strategycut3.py         # CV-assisted round
    └── data_structures.py          # Shared data structures

pythonClient/                       # Base client provided by organizers
server_windows/                     # Local server for testing (Windows)
Game.pdf                            # Game rules and mechanics
Hackathon_Introduction.pdf          # Hackathon overview
```

---

## How to Run

### Prerequisites
- Python 3.8+
- No external dependencies — strategy files use Python standard library only

### Start the local server
Use the provided `server_windows` binary to run the game server locally, or connect to the event server.

### Run the final round bot
```bash
cd SnakePythonClient/src
python main_final.py <team_name> <game_name> --password <password> --base_url http://localhost:3030
```

### Run other round bots
```bash
# Fight round
python main_fight.py <team_name> <game_name>

# Stacking round
python main_stacky1.py <team_name> <game_name>
```

---

## Match Recording

> Final round match recording
<video controls src="end-game.mp4" title="Title"></video>
<video controls src="040_End-Game-Faster.mp4" title="Title"></video>
https://github.com/VishnucharanS/Itestra_Hackathon/blob/main/end-game.mp4
---

## Connection to Autonomous Systems

Building a competitive snake bot is fundamentally an autonomous decision-making problem. Each tick, the bot perceives its environment (grid state, enemy positions, item locations), predicts future states (enemy movement zones, collision risk), and acts under real-time constraints — the same loop that drives any robotic agent. The flood-fill-based space evaluation is closely related to occupancy grid reasoning in mobile robotics. The multi-factor move scoring and conditional ability triggers are a simplified but real implementation of behaviour-based planning. The iterative strategy development across rounds — each introducing new constraints — mirrors how robotic systems are progressively stress-tested in changing environments.
