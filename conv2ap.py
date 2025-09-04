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

def number_to_ap(num: int) -> str:
    """
    Convert a number into AP Style formatting.
    Handles millions, billions, trillions.
    """
    if num < 1_000:  # 1–999
        return str(num)
    elif num < 1_000_000:  # thousands
        return f"{num:,}"  # keep as comma-separated
    elif num < 1_000_000_000:  # millions
        return f"{num / 1_000_000:.2f}".rstrip("0").rstrip(".") + " million"
    elif num < 1_000_000_000_000:  # billions
        return f"{num / 1_000_000_000:.2f}".rstrip("0").rstrip(".") + " billion"
    else:  # trillions
        return f"{num / 1_000_000_000_000:.2f}".rstrip("0").rstrip(".") + " trillion"

if __name__ == "__main__":
    test_numbers = [500, 1500, 2500000, 4300000000, 7200000000000]
    for number in test_numbers:
        print(f"{number} -> {number_to_ap(number)}")