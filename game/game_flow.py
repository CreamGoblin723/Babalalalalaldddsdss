"""Shared flow helpers used by multiple states: starting a new run, saving,
resuming, and ending a playthrough (bankrupt or victorious)."""
from game import constants as C
from game import save_manager
from game.player import Player


def start_new_game(app, name: str, skin: str):
    app.player = Player(name=name, skin=skin)
    app.player.map_name = "home"
    app.player.x = C.INTERNAL_WIDTH // 2
    app.player.y = C.INTERNAL_HEIGHT // 2 + 20
    app.active_slot = save_manager.find_free_slot()
    save_current(app)
    app.switch_state("overworld", map_name="home")


def resume_playthrough(app, slot: int):
    data = save_manager.load_playthrough(slot)
    if data is None:
        app.switch_state("main_menu")
        return
    app.player = Player.from_dict(data)
    app.active_slot = slot
    app.switch_state("overworld", map_name=app.player.map_name)


def save_current(app):
    if app.player is None or app.active_slot is None:
        return
    save_manager.save_playthrough(app.active_slot, app.player.to_dict())


def check_run_end(app) -> bool:
    """Call after any chip change from a minigame. If the run just ended
    (bankrupt or hit the 1,000,000 chip win condition), transitions to the
    run-end screen and returns True."""
    player = app.player
    if player is None:
        return False
    if player.won_game:
        end_run(app, victory=True)
        return True
    if player.busted:
        end_run(app, victory=False)
        return True
    return False


def end_run(app, victory: bool):
    """Called when the player busts (chips hit 0) or reaches 1,000,000 chips.
    Converts the run's peak chips into Blood Money and clears the save
    slot so the run cannot be continued."""
    player = app.player
    if player is None:
        app.switch_state("main_menu")
        return
    earned = C.blood_money_from_peak(player.peak_chips)
    if victory:
        earned *= 3
    app.meta["blood_money"] = app.meta.get("blood_money", 0) + earned
    save_manager.save_meta(app.meta)
    if app.active_slot is not None:
        save_manager.delete_playthrough(app.active_slot)
        meta = save_manager.load_meta()
        if meta.get("last_slot") == app.active_slot:
            meta["last_slot"] = None
            save_manager.save_meta(meta)
    app.switch_state("run_end", victory=victory, blood_money_earned=earned, player=player)
