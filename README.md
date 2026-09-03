# Blood & Chips

A 2D top-down, pixel-art gambling roguelite written in pure Python with
[pygame](https://www.pygame.org/). Walk your gambler around, hop in the van
down to the strip, hit the casino floor for Blackjack / Coin Flip / Over &
Under, and buy luck-bending abilities from the Shady Man behind the casino.
Bust out and it's over — reach **1,000,000 chips** and you beat the house.

## Running it

```bash
pip install -r requirements.txt
python3 main.py
```

Controls: **WASD / Arrow Keys** to move, **E / Enter / Space** to interact,
**Esc** to pause, mouse to click UI buttons.

## The loop

- **Main Menu**: Continue, Load Game, New Game, Options, Exit.
- **New Game** opens **Character Select**, where you name your gambler and
  pick a skin (more skins unlock permanently with **Blood Money**).
- You start on your **Home Lot** with 500 chips. Walk into the **van** to
  drive down to **The Strip**, where the casino and the **Shady Man** wait.
- Inside the casino are three tables — **Blackjack**, **Coin Flip**, and
  **Over/Under** — each a full betting minigame with its own odds.
- The **Shady Man** sells permanent-for-this-run **abilities** (Sharp Eyes,
  Card Counter, Second Chance, Lucky Coin, Loaded Dice, True Sight, and
  more) and one-shot **items** (Rabbit's Foot, Marked Deck, Emergency Loan),
  all purchased with **Chips**.
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
  app.py                   window + low-res internal surface + state stack
  constants.py              palette, sizes, economy tuning
  player.py                 the run's state (chips, abilities, position...)
  save_manager.py           save-slot + meta (Blood Money) persistence
  settings_manager.py       options persistence
  game_flow.py               shared new-game / resume / run-end helpers
  sprites.py                 procedural pixel-art generation (no image assets)
  ui.py                      Button/Slider/text/panel widgets
  blackjack_logic.py         pure blackjack rules (unit tested)
  abilities.py / shop_data.py  ability & item definitions
  states/                    one module per screen (see below)
tests/                       pytest unit tests for the pure game logic
scripts/smoke_test.py        headless end-to-end run through every screen
```

All art is generated at runtime from small pixel grids drawn with pygame
and scaled up with nearest-neighbour scaling — there are no external image
assets to ship.

### Screens (`game/states/`)

`main_menu`, `character_select`, `load_menu`, `options`, `overworld` (Home
Lot / The Strip), `casino_interior`, `shop`, `blackjack`, `coinflip`,
`overunder`, `pause_menu`, `run_end`.

## Testing

```bash
pip install pytest
python3 -m pytest tests/ -v                 # unit tests for game logic
SDL_VIDEODRIVER=dummy python3 scripts/smoke_test.py   # full headless playthrough
```

Both run cleanly without a display, using SDL's dummy video driver.
