# Blood & Chips

A 2D top-down, pixel-art gambling roguelite written in pure Python with
[pygame](https://www.pygame.org/). Walk your gambler around, hop in the van
down to the strip, hit the casino floor for Blackjack, Coin Flip, Over &
Under, Slots, or Roulette, grab a drink at the bar, and buy luck-bending
abilities from the Shady Man out back. Bust out and it's over — reach
**1,000,000 chips** and you beat the house.

## Running it

```bash
pip install -r requirements.txt
python3 main.py
```

Controls: **WASD / Arrow Keys** to move, **E / Enter / Space** to interact,
**Esc** to pause, mouse to click UI buttons, **F11** to toggle fullscreen
(also available in Options). Menus are fully keyboard-navigable with
Up/Down + Enter too.

The game renders at a fixed low internal resolution and scales that up to
fill whatever window or fullscreen size you're on, **letterboxed** to the
correct aspect ratio (black bars, never stretched or distorted) — so it
looks crisp and correct on any monitor, including ultrawide.

## The loop

- **Main Menu**: Continue, Load Game, New Game, Options, Exit.
- **New Game** opens **Character Select**, where you name your gambler and
  pick a skin (more skins unlock permanently with **Blood Money**).
- You start on your **Home Lot** with 500 chips. Walk into the **van** to
  drive down to **The Strip**, where the casino, the **Shady Man**, and the
  **bar** all wait.
- Inside the casino are five tables — **Blackjack**, **Coin Flip**,
  **Over/Under**, **Slots**, and **Roulette** — each a full betting
  minigame with its own odds.
- The **Shady Man** sells permanent-for-this-run **abilities** (Sharp Eyes,
  Card Counter, Second Chance, Lucky Coin, Loaded Dice, True Sight, Rigged
  Reels, Wheel Whisperer, and more) and one-shot **items** (Rabbit's Foot,
  Marked Deck, Emergency Loan), all purchased with **Chips**.
- The **bar** sells cheap **drinks** that grant a *temporary* version of an
  ability for the rest of your current visit to The Strip — a shorter-lived,
  cheaper alternative to buying the real thing.
- Chips are the run's stakes: hit **0** and the run ends (bankrupt); hit
  **1,000,000** and you win. Either way, the run converts into **Blood
  Money** (scaled off your peak chip count, tripled on a win) — a
  permanent, cross-run currency spent on character skins back at Character
  Select.
- **Esc** in the world opens the pause menu: Resume, Save Game (to your
  current slot), Options, or Quit to Menu. **Continue** on the main menu
  always resumes your most recently saved run; **Load Game** lets you pick
  from the 3 save slots directly.

## Project layout

```
main.py                    entry point / state registry
game/
  app.py                    window + internal surface + letterboxed scaling + state stack
  constants.py               palette, sizes, economy tuning
  player.py                  the run's state (chips, abilities, position...)
  save_manager.py            save-slot + meta (Blood Money) persistence
  settings_manager.py        options persistence
  game_flow.py                shared new-game / resume / run-end helpers
  sprites.py                  procedural pixel-art generation (no image assets)
  ui.py                       Button/Slider/text/panel widgets, keyboard nav, word-wrap
  blackjack_logic.py          pure blackjack rules (unit tested)
  slots_logic.py              pure slot-machine rules (unit tested)
  roulette_logic.py           pure roulette rules (unit tested)
  abilities.py / shop_data.py / bar_data.py   ability, item, and drink definitions
  states/                     one module per screen (see below)
tests/                        pytest unit tests for the pure game logic
scripts/smoke_test.py         headless end-to-end run through every screen
```

All art is generated at runtime from small pixel grids and shapes drawn
with pygame and scaled up with nearest-neighbour scaling — there are no
external image assets to ship.

### Screens (`game/states/`)

`main_menu`, `character_select`, `load_menu`, `options`, `overworld` (Home
Lot / The Strip), `casino_interior`, `shop`, `bar`, `blackjack`, `coinflip`,
`overunder`, `slots`, `roulette`, `pause_menu`, `run_end`.

## Testing

```bash
pip install pytest
python3 -m pytest tests/ -v                 # unit tests for game logic
SDL_VIDEODRIVER=dummy python3 scripts/smoke_test.py   # full headless playthrough
```

Both run cleanly without a display, using SDL's dummy video driver.
