import logging
import requests
import re
from bs4 import BeautifulSoup

url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
res = requests.get(url)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, "html.parser")

def twd2usd(twdINT):
    """Convert TWD to USD using the exchange rate."""

    usd_rate = get_usd_rate()
    usd_value = int(twdINT / usd_rate)

    #usdSTR = "{:,}".format(usd_value)

    return usd_value


def get_usd_rate():
    try:
        # Find the <tr> that contains "美金 (USD)"
        usd_row = None
        for row in soup.select("table tbody tr"):
            if "美金" in row.text:
                usd_row = row
                break
        
        if usd_row:
                # Extract "本行現金賣出" (cash sell rate)
                cash_sell_td = usd_row.find("td", {"data-table": "本行現金賣出"})
                if cash_sell_td:
                    # print("USD Cash Sell Rate:", cash_sell_td.text.strip())
                    return float(cash_sell_td.text.strip())
                else:
                    print("Couldn't find the cash sell cell in USD row.")
        else:
            raise ValueError("Couldn't find the USD row in the table.")

    except Exception as e:
        print(f"An error occurred while fetching the USD rates: {e}")

def _remove_extra_usd(inputSTR):
    """
    Remove all but the first '(US$xxx)' annotation followed by optional unit terms.
    """
    # Pattern: Match (US$xxx) with optional unit (cents, million, billion, trillion)
    pattern = r'\s?\(US\$[0-9\.,]+\)(?: (cents|million|billion|trillion))?\s?'

    # Find all matches
    matches = list(re.finditer(pattern, inputSTR))

    # If more than one match, remove all but the first
    if len(matches) > 1:
        # Keep the first one
        first_match_end = matches[0].end()
        # Reconstruct string excluding other matches
        result = inputSTR[:first_match_end]
        remaining = inputSTR[first_match_end:]

        # Remove subsequent matches from the remaining string
        remaining_cleaned = re.sub(pattern, ' ', remaining)
        remaining_cleaned = re.sub(r'(?<=\d)\s+(?=\W)', '', remaining_cleaned)  # Clean up extra spaces
        result += remaining_cleaned
        return result
    else:
        return inputSTR