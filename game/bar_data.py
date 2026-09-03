"""Drinks sold at the bar on The Strip, purchased with Chips. Each drink
grants a *temporary* version of an ability for the rest of the current
visit to The Strip (it wears off once you take the van back home) - a
cheaper, shorter-lived alternative to buying the ability outright from
the Shady Man."""

DRINKS = {
    "whiskey_nerve": {
        "name": "Whiskey Nerve",
        "cost": 35,
        "grants": "lucky_coin",
        "desc": "Steadies your hand at the coin table.",
    },
    "steady_hands": {
        "name": "Steady Hands",
        "cost": 45,
        "grants": "card_counter",
        "desc": "Clears your head just enough to keep count.",
    },
    "house_special": {
        "name": "The House Special",
        "cost": 45,
        "grants": "loaded_dice",
        "desc": "Tastes like it shouldn't work. But it does.",
    },
    "reel_deal": {
        "name": "The Reel Deal",
        "cost": 55,
        "grants": "rigged_reels",
        "desc": "The bartender winks as she pours.",
    },
    "wheelhouse": {
        "name": "Wheelhouse",
        "cost": 60,
        "grants": "wheel_whisperer",
        "desc": "Something in the ice hums along with the wheel.",
    },
}

DRINK_ORDER = ["whiskey_nerve", "steady_hands", "house_special", "reel_deal", "wheelhouse"]
