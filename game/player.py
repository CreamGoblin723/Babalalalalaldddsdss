"""The Player class holds all state for the current playthrough (a 'run')."""
from game import constants as C


class Player:
    def __init__(self, name="Drifter", skin="drifter"):
        self.name = name
        self.skin = skin

        # currency
        self.chips = C.STARTING_CHIPS
        self.peak_chips = C.STARTING_CHIPS

        # abilities owned this run: list of ability ids
        self.abilities = []
        # consumable inventory: {item_id: count}
        self.inventory = {}

        # position in the current map, in internal-resolution pixels
        self.map_name = "home"
        self.x = 160.0
        self.y = 120.0
        self.direction = "down"
        self.walk_frame = 0
        self._walk_timer = 0.0

        # run stats
        self.hands_played = 0
        self.games_won = 0
        self.games_lost = 0
        self.busted = False
        self.won_game = False

        # one-shot ability charges consumed within minigames, reset each hand
        self.active_effects = {}

    # -- economy ------------------------------------------------------
    def add_chips(self, amount: int):
        self.chips = max(0, self.chips + amount)
        if self.chips > self.peak_chips:
            self.peak_chips = self.chips
        if self.chips >= C.WIN_CHIPS:
            self.won_game = True
        if self.chips <= 0:
            self.chips = 0
            self.busted = True

    def can_afford(self, amount: int) -> bool:
        return self.chips >= amount

    def has_ability(self, ability_id: str) -> bool:
        return ability_id in self.abilities

    def add_item(self, item_id: str, count: int = 1):
        self.inventory[item_id] = self.inventory.get(item_id, 0) + count

    def use_item(self, item_id: str) -> bool:
        if self.inventory.get(item_id, 0) > 0:
            self.inventory[item_id] -= 1
            if self.inventory[item_id] <= 0:
                del self.inventory[item_id]
            return True
        return False

    def item_count(self, item_id: str) -> int:
        return self.inventory.get(item_id, 0)

    # -- movement -------------------------------------------------------
    def update_walk_anim(self, dt, moving):
        if moving:
            self._walk_timer += dt
            if self._walk_timer > 0.18:
                self._walk_timer = 0.0
                self.walk_frame = 1 - self.walk_frame
        else:
            self.walk_frame = 0
            self._walk_timer = 0.0

    # -- serialization ----------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "skin": self.skin,
            "chips": self.chips,
            "peak_chips": self.peak_chips,
            "abilities": self.abilities,
            "inventory": self.inventory,
            "map_name": self.map_name,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "hands_played": self.hands_played,
            "games_won": self.games_won,
            "games_lost": self.games_lost,
            "busted": self.busted,
            "won_game": self.won_game,
            "character": self.skin,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        p = cls(name=data.get("name", "Drifter"), skin=data.get("skin", "drifter"))
        p.chips = data.get("chips", C.STARTING_CHIPS)
        p.peak_chips = data.get("peak_chips", p.chips)
        p.abilities = list(data.get("abilities", []))
        p.inventory = dict(data.get("inventory", {}))
        p.map_name = data.get("map_name", "home")
        p.x = data.get("x", 160.0)
        p.y = data.get("y", 120.0)
        p.direction = data.get("direction", "down")
        p.hands_played = data.get("hands_played", 0)
        p.games_won = data.get("games_won", 0)
        p.games_lost = data.get("games_lost", 0)
        p.busted = data.get("busted", False)
        p.won_game = data.get("won_game", False)
        return p
