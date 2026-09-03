import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from game import constants as C


@pytest.fixture
def temp_saves(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr(C, "SAVES_DIR", tmpdir)
    monkeypatch.setattr(C, "META_SAVE_PATH", os.path.join(tmpdir, "meta.json"))
    monkeypatch.setattr(C, "SETTINGS_PATH", os.path.join(tmpdir, "settings.json"))
    monkeypatch.setattr(C, "SAVE_SLOT_TEMPLATE", os.path.join(tmpdir, "slot_{}.json"))
    # save_manager imported C by reference at module scope, so patch there too
    from game import save_manager
    monkeypatch.setattr(save_manager.C, "SAVES_DIR", tmpdir)
    monkeypatch.setattr(save_manager.C, "META_SAVE_PATH", os.path.join(tmpdir, "meta.json"))
    monkeypatch.setattr(save_manager.C, "SAVE_SLOT_TEMPLATE", os.path.join(tmpdir, "slot_{}.json"))
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_meta_roundtrip(temp_saves):
    from game import save_manager
    meta = save_manager.load_meta()
    assert meta["blood_money"] == 0
    meta["blood_money"] = 42
    save_manager.save_meta(meta)
    reloaded = save_manager.load_meta()
    assert reloaded["blood_money"] == 42


def test_save_and_load_playthrough(temp_saves):
    from game import save_manager
    from game.player import Player

    p = Player(name="Ace", skin="red_suit")
    p.chips = 12345
    save_manager.save_playthrough(0, p.to_dict())

    loaded = save_manager.load_playthrough(0)
    assert loaded["name"] == "Ace"
    assert loaded["chips"] == 12345

    p2 = Player.from_dict(loaded)
    assert p2.chips == 12345
    assert p2.skin == "red_suit"


def test_list_slots_reports_occupied(temp_saves):
    from game import save_manager
    from game.player import Player

    slots = save_manager.list_slots()
    assert len(slots) == C.NUM_SAVE_SLOTS
    assert all(not s["occupied"] for s in slots)

    save_manager.save_playthrough(1, Player().to_dict())
    slots = save_manager.list_slots()
    assert slots[1]["occupied"]
    assert not slots[0]["occupied"]


def test_find_free_slot_and_continue(temp_saves):
    from game import save_manager
    from game.player import Player

    assert save_manager.find_free_slot() == 0
    save_manager.save_playthrough(0, Player().to_dict())
    assert save_manager.find_free_slot() == 1
    assert save_manager.get_continue_slot() == 0


def test_delete_playthrough(temp_saves):
    from game import save_manager
    from game.player import Player

    save_manager.save_playthrough(2, Player().to_dict())
    assert save_manager.load_playthrough(2) is not None
    save_manager.delete_playthrough(2)
    assert save_manager.load_playthrough(2) is None
