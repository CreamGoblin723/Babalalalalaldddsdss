"""Luck-manipulation abilities sold by the Shady Man for Chips.

Each ability is a passive or once-per-hand effect that nudges the RNG in
the casino minigames. The minigame states check `player.has_effect` (owns
the ability permanently, OR a bar drink granted a temporary version of it
for this visit) and call the small helper functions below rather than each
re-implementing the probability math.
"""
import random

ABILITIES = {
    "sharp_eyes": {
        "name": "Sharp Eyes",
        "game": "blackjack",
        "cost": 60,
        "desc": "See the dealer's face-down card before you decide to hit or stand.",
    },
    "card_counter": {
        "name": "Card Counter",
        "game": "blackjack",
        "cost": 130,
        "desc": "The shoe is quietly weighted in your favor. Fewer bust-cards come your way.",
    },
    "second_chance": {
        "name": "Second Chance",
        "game": "blackjack",
        "cost": 160,
        "desc": "The first time you bust each casino visit, it's a push instead of a loss.",
    },
    "lucky_coin": {
        "name": "Lucky Coin",
        "game": "coinflip",
        "cost": 90,
        "desc": "Your coin lands your way about 58% of the time instead of 50%.",
    },
    "double_take": {
        "name": "Double Take",
        "game": "coinflip",
        "cost": 110,
        "desc": "Once per casino visit, a lost flip can be called again for free.",
    },
    "loaded_dice": {
        "name": "Loaded Dice",
        "game": "overunder",
        "cost": 100,
        "desc": "The roll leans toward whichever side of 7 you bet on.",
    },
    "true_sight": {
        "name": "True Sight",
        "game": "overunder",
        "cost": 140,
        "desc": "Peek at the first die before locking in your over/under bet.",
    },
    "insurance_hustle": {
        "name": "Insurance Hustle",
        "game": "blackjack",
        "cost": 80,
        "desc": "If the dealer draws blackjack, you quietly get half your bet back.",
    },
    "rigged_reels": {
        "name": "Rigged Reels",
        "game": "slots",
        "cost": 150,
        "desc": "The reels quietly like to agree with each other. More matches, more often.",
    },
    "wheel_whisperer": {
        "name": "Wheel Whisperer",
        "game": "roulette",
        "cost": 170,
        "desc": "The ball leans toward whatever you bet on, red, black, or anything between.",
    },
}

ABILITY_ORDER = [
    "sharp_eyes", "card_counter", "second_chance", "insurance_hustle",
    "lucky_coin", "double_take", "loaded_dice", "true_sight",
    "rigged_reels", "wheel_whisperer",
]


def biased_coin(player, base_prob_player_side=0.5) -> float:
    """Return the probability the coin lands on the side the player picked."""
    if player.has_effect("lucky_coin"):
        return min(0.95, base_prob_player_side + 0.08)
    return base_prob_player_side


def biased_die(player, favor_high: bool) -> list:
    """Return a weighted list of die faces (1-6) for random.choice, nudged
    toward high rolls (favor_high=True) or low rolls (False) when the
    player owns Loaded Dice."""
    faces = [1, 2, 3, 4, 5, 6]
    if not player.has_effect("loaded_dice"):
        return faces
    weights = []
    for f in faces:
        if favor_high:
            weights.append(1.0 + (f - 3.5) * 0.18)
        else:
            weights.append(1.0 + (3.5 - f) * 0.18)
        weights[-1] = max(0.15, weights[-1])
    bag = []
    for f, w in zip(faces, weights):
        bag.extend([f] * max(1, round(w * 10)))
    return bag


def draw_die(player, favor_high=None) -> int:
    bag = biased_die(player, favor_high) if favor_high is not None else [1, 2, 3, 4, 5, 6]
    return random.choice(bag)


def card_counter_bust_reduction(player) -> float:
    """Extra probability weight subtracted from high-value (bust-risk) cards
    when the player owns Card Counter, applied by the blackjack shoe."""
    return 0.35 if player.has_effect("card_counter") else 0.0


def rigged_reels_bias(player) -> float:
    """Correlation strength passed to slots_logic.spin_reels when the
    player owns (or is buzzed on) Rigged Reels."""
    return 0.28 if player.has_effect("rigged_reels") else 0.0


def wheel_whisperer_bias(player) -> float:
    """Bias strength passed to roulette_logic.spin when the player owns
    (or is buzzed on) Wheel Whisperer."""
    return 0.35 if player.has_effect("wheel_whisperer") else 0.0
