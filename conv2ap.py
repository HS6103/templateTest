import math

def month_to_ap(month: str) -> str:
    """
    Convert a month name to its AP Style abbreviation.
    """
    month_abbr = {
        "January": "Jan.",
        "February": "Feb.",
        "March": "March",
        "April": "April",
        "May": "May",
        "June": "June",
        "July": "July",
        "August": "Aug.",
        "September": "Sept.",
        "October": "Oct.",
        "November": "Nov.",
        "December": "Dec."
    }
    return month_abbr.get(month, month)

def number_to_ap(num: float) -> str:
    """
    Convert a number into AP Style formatting.
    Handles thousands, millions, billions, trillions.
    Preserves decimals instead of rounding up.
    """
    if num < 1_000:
        return str(int(num)) if num.is_integer() else str(num)
    elif num < 1_000_000:  # thousands
        return f"{num:,.0f}"
    elif num < 1_000_000_000:  # millions
        val = num / 1_000_000
        val = math.floor(val * 100) / 100  # truncate to 2 decimals
        return f"{val}".rstrip("0").rstrip(".") + " million"
    elif num < 1_000_000_000_000:  # billions
        val = num / 1_000_000_000
        val = math.floor(val * 100) / 100
        return f"{val}".rstrip("0").rstrip(".") + " billion"
    else:  # trillions
        val = num / 1_000_000_000_000
        val = math.floor(val * 100) / 100
        return f"{val}".rstrip("0").rstrip(".") + " trillion"

if __name__ == "__main__":
    test_numbers = [500, 1500, 2500000, 4300000000, 7200000000000]
    for number in test_numbers:
        print(f"{number} -> {number_to_ap(number)}")