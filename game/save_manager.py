"""Handles persistence: per-playthrough save slots and the cross-run meta
save (Blood Money, unlocked skins, last-played slot)."""
import json
import os
import time

from game import constants as C


def ensure_saves_dir():
    os.makedirs(C.SAVES_DIR, exist_ok=True)


# --- Meta save (persists across playthroughs / character deaths) ---------
DEFAULT_META = {
    "blood_money": 0,
    "unlocked_skins": ["drifter"],
    "last_slot": None,
}


def load_meta() -> dict:
    ensure_saves_dir()
    if not os.path.exists(C.META_SAVE_PATH):
        return dict(DEFAULT_META)
    try:
        with open(C.META_SAVE_PATH, "r") as f:
            data = json.load(f)
        merged = dict(DEFAULT_META)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_META)


def save_meta(meta: dict):
    ensure_saves_dir()
    with open(C.META_SAVE_PATH, "w") as f:
        json.dump(meta, f, indent=2)


# --- Per-playthrough save slots -------------------------------------------
def slot_path(slot: int) -> str:
    return C.SAVE_SLOT_TEMPLATE.format(slot)


def list_slots() -> list:
    """Return metadata for every save slot, whether occupied or not."""
    ensure_saves_dir()
    slots = []
    for i in range(C.NUM_SAVE_SLOTS):
        path = slot_path(i)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                slots.append({
                    "slot": i,
                    "occupied": True,
                    "character": data.get("character", "?"),
                    "chips": data.get("chips", 0),
                    "map_name": data.get("map_name", "home"),
                    "saved_at": data.get("saved_at", 0),
                })
            except (json.JSONDecodeError, OSError):
                slots.append({"slot": i, "occupied": False})
        else:
            slots.append({"slot": i, "occupied": False})
    return slots


def save_playthrough(slot: int, data: dict):
    ensure_saves_dir()
    data = dict(data)
    data["saved_at"] = time.time()
    with open(slot_path(slot), "w") as f:
        json.dump(data, f, indent=2)

    meta = load_meta()
    meta["last_slot"] = slot
    save_meta(meta)


def load_playthrough(slot: int) -> dict:
    path = slot_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def delete_playthrough(slot: int):
    path = slot_path(slot)
    if os.path.exists(path):
        os.remove(path)


def find_free_slot() -> int:
    for s in list_slots():
        if not s["occupied"]:
            return s["slot"]
    return 0  # overwrite the oldest slot if all are full


def get_continue_slot():
    """Return the slot number to resume via the 'Continue' button, or None."""
    meta = load_meta()
    last = meta.get("last_slot")
    if last is not None and os.path.exists(slot_path(last)):
        return last
    # fall back to the most recently saved occupied slot
    occupied = [s for s in list_slots() if s["occupied"]]
    if not occupied:
        return None
    occupied.sort(key=lambda s: s["saved_at"], reverse=True)
    return occupied[0]["slot"]
