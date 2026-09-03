"""Pure European-wheel roulette logic (single zero, numbers 0-36), kept
separate from the pygame state so it can be unit tested without a display."""
import random

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NUMBERS = list(range(37))

BET_TYPES = ("red", "black", "odd", "even", "low", "high", "green")
PAYOUT_MULTIPLIER = {
    "red": 1, "black": 1, "odd": 1, "even": 1, "low": 1, "high": 1, "green": 35,
}


def number_color(number: int) -> str:
    if number == 0:
        return "green"
    return "red" if number in RED_NUMBERS else "black"


def bet_wins(bet_type: str, number: int) -> bool:
    if bet_type == "red":
        return number_color(number) == "red"
    if bet_type == "black":
        return number_color(number) == "black"
    if bet_type == "odd":
        return number != 0 and number % 2 == 1
    if bet_type == "even":
        return number != 0 and number % 2 == 0
    if bet_type == "low":
        return 1 <= number <= 18
    if bet_type == "high":
        return 19 <= number <= 36
    if bet_type == "green":
        return number == 0
    return False


def spin(bet_type: str = None, bias_strength: float = 0.0) -> int:
    """Spin the wheel, returning a number 0-36. When bias_strength > 0 and
    a bet_type is given (Wheel Whisperer), numbers that would win that bet
    are weighted more heavily without ever excluding the rest of the wheel."""
    if bias_strength <= 0 or bet_type is None:
        return random.choice(NUMBERS)
    weights = [1.0 + (bias_strength * 6 if bet_wins(bet_type, n) else 0.0) for n in NUMBERS]
    return random.choices(NUMBERS, weights=weights, k=1)[0]
