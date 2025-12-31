import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime


URL_EN = input("Enter the English CWB earthquake URL: ").strip()
URL_ZH = URL_EN.replace("/E/E/EQ/", "/C/E/EQ/")

# --------------------
# Fetch pages
# --------------------
resp_en = requests.get(URL_EN, timeout=10)
resp_en.raise_for_status()
soup_en = BeautifulSoup(resp_en.text, "html.parser")

resp_zh = requests.get(URL_ZH, timeout=10)
resp_zh.raise_for_status()
soup_zh = BeautifulSoup(resp_zh.text, "html.parser")

# --------------------
# Extract English quake info
# --------------------
info = {}

def normalize_direction(text: str) -> str:
    def repl(match):
        abbr = match.group(1)
        return DIRECTION_MAP.get(abbr, abbr)

    pattern = r"\b(" + "|".join(sorted(DIRECTION_MAP.keys(), key=len, reverse=True)) + r")\b"
    return re.sub(pattern, repl, text)

DIRECTION_MAP = {
    "N": "north",
    "NNE": "north-northeast",
    "NE": "northeast",
    "ENE": "east-northeast",
    "E": "east",
    "ESE": "east-southeast",
    "SE": "southeast",
    "SSE": "south-southeast",
    "S": "south",
    "SSW": "south-southwest",
    "SW": "southwest",
    "WSW": "west-southwest",
    "W": "west",
    "WNW": "west-northwest",
    "NW": "northwest",
    "NNW": "north-northwest",
}

for li in soup_en.select("ul.quake_info li"):
    text = li.get_text(strip=True)

    if "Origin Time" in text:
        info["time"] = text.replace("Origin Time:", "").strip()

    elif "Epicenter" in text:
        span = li.find("span")
        epicenter_raw = span.get_text(strip=True) if span else ""
        info["epicenter"] = normalize_direction(epicenter_raw).replace("km", " kilometers")

    elif "Focal depth" in text:
        info["depth"] = text.replace("Focal depth:", "").strip()

    elif "Magnitude" in text:
        info["magnitude"] = text.split(":")[-1].strip()

# --------------------
# Parse datetime & weekday
# --------------------
dt = datetime.strptime(info["time"], "%Y/%m/%d %H:%M:%S")
date_str = dt.strftime("%b. %d")
time_str = dt.strftime("%I:%M %p").lstrip("0").lower()
weekday = dt.strftime("%A")

# --------------------
# Extract Chinese epicenter wording
# --------------------
def get_chinese_epicenter_text(soup):
    for li in soup.select("ul.quake_info li"):
        if li.find("i", class_="fa-map-marker"):
            return li.get_text(strip=True)
    return ""

zh_epicenter_text = get_chinese_epicenter_text(soup_zh)

# --------------------
# Decide "at sea" vs "in xxx"
# --------------------
if "近海" in zh_epicenter_text or "海域" in zh_epicenter_text:
    location_phrase = "at sea"
else:
    # minimal rule as requested
    location_phrase = "in XXX"

# --------------------
# Extract intensity info
# --------------------
panels = soup_en.select(".panel-title a")

highest_area = highest_intensity = None
second_area = second_intensity = None

for a in panels:
    text = a.get_text(" ", strip=True)
    if "Largest Intensity" not in text:
        continue

    area, intensity = text.split("Largest Intensity")
    area = area.replace("area", "").strip()
    intensity = intensity.strip()

    if highest_area is None:
        highest_area = area
        highest_intensity = intensity
    elif second_area is None:
        second_area = area
        second_intensity = intensity
        break

# --------------------
# CNA-style report
# --------------------
report = f"""Magnitude {info['magnitude']} earthquake shakes XXX Taiwan

Taipei, {date_str} (CNA) A magnitude {info['magnitude']} earthquake struck {location_phrase} off XXX Taiwan at {time_str} {weekday}, according to the Central Weather Administration (CWA).

There were no immediate reports of damage or injuries.

The epicenter of the temblor was located {location_phrase}, about {info['epicenter']}, at a depth of {info['depth']}, according to the administration.

The earthquake's intensity was highest in {highest_area}, where it measured {highest_intensity} on Taiwan's 7-tier intensity scale.
"""

if second_area:
    report += f"\nThe quake also measured an intensity of {second_intensity} in {second_area}, the CWA said."

report += "\n\n(By NAME)\nEnditem"

print(report)
