# Memory0verwrite

A Pygame-based educational cybersecurity escape game. Eight puzzle rooms, each hiding a stolen memory fragment. Solve the puzzles, recover the fragments, and defeat the virus that has rewritten your identity.

---

## Story

A memory-stealing virus has infiltrated the network. Your identity — your name, your skills, your past — has been encrypted and scattered across eight corrupted rooms.

Each room contains a stolen memory fragment. Solve its puzzle. Recover the fragment. Weaken the virus.

But the fragments tell a larger story. Early recoveries raise questions. Mid-game fragments reveal contradictions. The final fragments expose the truth — about the virus, about the experiment, and about your own role in what happened.

---

## Rooms

| # | Room | Tier | Concept |
|---|------|------|---------|
| 1 | Phishing Lab | 1 — Entry Point | Social engineering via email |
| 2 | OSINT Investigator | 1 — Entry Point | Open-source intelligence gathering |
| 3 | Password Vault | 2 — Technical | Password cracking, hashing, and salting |
| 4 | Cipher Chamber | 2 — Technical | Encryption: Caesar, Vigenère, XOR |
| 5 | Network Recon | 3 — Hacker Mindset | Port scanning and service enumeration |
| 6 | Script Foundry | 3 — Hacker Mindset | Python scripting for security automation |
| 7 | Reverse Engineering | 4 — Deep Dive | Reading assembly and pseudocode |
| 8 | Binary Breach | 4 — Deep Dive | Buffer overflow and memory exploitation |

Rooms 2 and 3 are fully implemented. Rooms 4–8 are coming soon.

---

## Gameplay Loop

```
Main Menu
  └─ Story Intro
       └─ World Map  (permanent hub)
            ├─ Mission Briefing → Room → Results → World Map
            ├─ Memory Archive  (fragment journal, accessible any time)
            └─ Ending Sequence  (unlocked after all rooms cleared)
```

- Rooms unlock sequentially — complete a room to unlock the next.
- Completed rooms remain permanently accessible for replay.
- Replaying a room preserves all progress: only the highest score is stored.
- The World Map is always the return point after any room action.
- The Start screen is only reached by explicitly choosing Main Menu or New Game.

---

## Memory Fragments

Each recovered fragment is part of a connected eight-part mystery:

| Fragment | Title | Arc |
|----------|-------|-----|
| 1 | Recall: Identity | A name. Yours. The first thing you remember. |
| 2 | Recall: The Experiment | You volunteered for something. |
| 3 | Recall: The Accident | A typo no one escalated. |
| 4 | Recall: The Modification | Someone made a change that wasn't in the spec. |
| 5 | Recall: Alteration | Your memories aren't stolen — they're rewritten. |
| 6 | Recall: Complicity | The blueprint was yours. |
| 7 | Recall: Adaptation | It's learning. It's becoming you. |
| 8 | Recall: Origin | It was never an external threat. |

Fragments are logged in the **Memory Archive**, accessible at any time from the World Map.

---

## Features

- **Scene-based state machine** — main menu, intro, world map, mission briefing, room game, results, archive, ending
- **Sequential room unlock** — each room unlocks only after the previous is cleared
- **Replay system** — any completed room can be replayed; high score is preserved, no progression is re-awarded
- **Four room status states** — Locked, Available, Completed, High Score
- **Memory Archive** — full fragment journal with story text, recovery location, and teaser text for locked fragments
- **Virus containment bar** — visual indicator of overall progress across all screens
- **Fragment tracker** — 8-dot progress display in results and archive
- **Mission Briefing** — narrative context before each room, with replay detection and previous score display
- **Room Results** — score bar, fragment dots, virus weakening indicator, newly-unlocked room notification
- **Ending sequence** — five-stage cinematic: fragment convergence animation, three story stages, statistics screen
- **Save system** — JSON save file; highest score per room, cross-room artefacts, full reset for new game
- **Audio manager** — ambient, SFX, and mute toggle (`M`)
- **Debug logging** — all navigation transitions, room entry/exit/completion logged to `memory0verwrite.log`
- **Error recovery** — unhandled scene exceptions are caught, logged, and recovered to the World Map without crashing the process

---

## Controls

| Key | Action |
|-----|--------|
| `SPACE` / `ENTER` | Advance / confirm |
| `ESC` | Back / return to World Map (or Main Menu from World Map) |
| `M` | Toggle audio mute |
| Mouse | Click room cards, buttons, and UI elements |

---

## Project Structure

```
memory0verwrite/
├── main.py                  # entry point
├── core/
│   ├── game.py              # main loop, scene registration, error recovery
│   ├── state_machine.py     # scene transitions with logging
│   ├── save_manager.py      # JSON save/load, high-score logic
│   ├── settings.py          # palette, room registry, fragment data
│   ├── audio.py             # audio manager
│   └── fx.py                # shared visual effects (scanlines, etc.)
├── scenes/
│   ├── base_scene.py
│   ├── main_menu.py
│   ├── intro.py             # animated story intro
│   ├── world_map.py         # persistent hub, sequential unlock, status badges
│   ├── context.py           # mission briefing / replay briefing
│   ├── room_game.py         # room host, timer, completion detection
│   ├── room_result.py       # score, fragment tracker, unlock notification
│   ├── archive.py           # memory fragment journal
│   └── ending.py            # five-stage ending sequence
└── rooms/
    ├── osint/               # Room 2 — OSINT Investigator
    │   ├── room.py
    │   └── data.py
    └── password/            # Room 3 — Password Vault
        ├── room.py
        └── data.py
```

---

## Requirements

```
python >= 3.10
pygame-ce >= 2.5
```

Install dependencies:

```bash
pip install pygame-ce
```

Run the game:

```bash
python main.py
```

Save data is written to `memory0verwrite_save.json` in the project root.  
Debug logs are written to `memory0verwrite.log`.

---

## Development Notes

- All colour constants are defined in `core/settings.py` and must be explicitly imported in each scene file.
- Room state is fully reset on each `setup()` call — replay safety is the room module's responsibility.
- The `StateMachine.transition()` method calls `on_exit()` on the current scene then `on_enter(**kwargs)` on the next. No fallback or error swallowing occurs inside the SM itself; the game loop in `game.py` provides the recovery layer.
- `SaveManager.mark_cleared()` uses `max(previous, new)` — a lower replay score never overwrites the high score.
