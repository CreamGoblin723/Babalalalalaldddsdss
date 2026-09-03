"""Consumable items sold by the Shady Man, purchased with Chips."""

ITEMS = {
    "emergency_loan": {
        "name": "Emergency Loan",
        "cost": 50,
        "desc": "A grubby envelope of chips. Use it when you're about to go bust.",
        "chips_value": 150,
    },
    "rabbits_foot": {
        "name": "Rabbit's Foot",
        "cost": 200,
        "desc": "Use before a hand: guarantees your next blackjack/coin/roll push is a win instead.",
    },
    "marked_deck": {
        "name": "Marked Deck",
        "cost": 250,
        "desc": "Use before a blackjack hand: your first two cards are guaranteed 19 or better.",
    },
}

ITEM_ORDER = ["emergency_loan", "rabbits_foot", "marked_deck"]
