import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime


URL_EN = input("Enter the English CWA earthquake URL: ").strip()
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
            epicenter_raw = li.get_text(strip=True)
            # Determine if epicenter is at sea or on land
            if "近海" in epicenter_raw or "海域" in epicenter_raw:
                location_tag = "sea"
            else:
                location_tag = "land"
            epicenterSTR= re.match(r".*of (.+) Hall", info["epicenter"]).group(1).strip()
            # Remove "City" for six special municipalities
            if epicenterSTR in ["Kaohsiung City", "New Taipei City", "Kaohsiung City", "Taichung City", "Tainan City", "Taoyuan City"]:
                epicenterSTR = epicenterSTR.replace(" City", "")

            return epicenterSTR, location_tag
    return ""

zh_epicenter_text = get_chinese_epicenter_text(soup_zh)
epicenterSTR = zh_epicenter_text[0] if zh_epicenter_text else ""
location_tag = zh_epicenter_text[1] if zh_epicenter_text else ""

# --------------------
# Region mappings (CNA-style)
# --------------------
EASTERN_COUNTIES = {
    "Hualien County",
}

SOUTHERN_COUNTIES = {
    "Kaohsiung",
    "Tainan",
    "Pingtung County",
}

NORTHERN_COUNTIES = {
    "Taipei",
    "New Taipei",
    "Keelung City",
    "Taoyuan",
    "Hsinchu",
    "Hsinchu County",
}

CENTRAL_COUNTIES = {
    "Taichung",
    "Changhua County",
    "Nantou County",
    "Yunlin County",
    "Miaoli County",
}

SOUTHEASTERN_COUNTIES = {
    "Taitung County",
}

NORTHEASTERN_COUNTIES = {
    "Yilan County",
}

ALL_COUNTIES = (
    EASTERN_COUNTIES
    | SOUTHERN_COUNTIES
    | NORTHERN_COUNTIES
    | CENTRAL_COUNTIES
    | SOUTHEASTERN_COUNTIES
    | NORTHEASTERN_COUNTIES
)

# --------------------
# Map county → region
# --------------------

def county_to_region(county: str | None) -> str | None:
    region = None
    if county in EASTERN_COUNTIES:
        region = "eastern Taiwan"
    if county in SOUTHERN_COUNTIES:
        region = "southern Taiwan"
    if county in NORTHERN_COUNTIES:
        region = "northern Taiwan"
    if county in CENTRAL_COUNTIES:
        region = "central Taiwan"
    if county in SOUTHEASTERN_COUNTIES:
        region = "southeastern Taiwan"
    if county in NORTHEASTERN_COUNTIES:
        region = "northeastern Taiwan"
    return region

region = county_to_region(zh_epicenter_text[0]) if zh_epicenter_text else None

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
    if area in ["Kaohsiung City area", "New Taipei City area", "Kaohsiung City area", "Taichung City area", "Tainan City area", "Taoyuan City area"]:
        area = area.replace(" City area", "")
    else:
        area = area.replace("area", "").strip()
    intensity = intensity.strip()

    if highest_area is None:
        highest_area = area
        highest_intensity = intensity
    elif second_area is None:
        second_area = area
        if second_area in ["Kaohsiung City", "New Taipei City", "Kaohsiung City", "Taichung City", "Tainan City", "Taoyuan City"]:
            second_area = second_area.replace(" City", "")
        second_intensity = intensity
        break

# --------------------
# CNA-style report
# --------------------
if region:
    if location_tag == "sea":
        report = f"""Magnitude {info['magnitude']} earthquake shakes {region}\n\nTaipei, {date_str} (CNA) A magnitude {info['magnitude']} earthquake struck off the coast of {region}'s {epicenterSTR} at {time_str} {weekday}, according to the Central Weather Administration (CWA).\n\nThere were no immediate reports of damage or injuries.\n\nThe epicenter of the temblor was located at sea, about {info['epicenter']}, at a depth of {info['depth']}, according to the administration.\n\nThe earthquake's intensity was highest in {highest_area}, where it measured {highest_intensity} on Taiwan's 7-tier intensity scale.
        """
    else:
        report = f"""Magnitude {info['magnitude']} earthquake shakes {region}\n\nTaipei, {date_str} (CNA) A magnitude {info['magnitude']} earthquake struck {epicenterSTR} in {region} at {time_str} {weekday}, according to the Central Weather Administration (CWA).\n\nThere were no immediate reports of damage or injuries.\n\nThe epicenter of the temblor was located in {epicenterSTR}, about {info['epicenter']}, at a depth of {info['depth']}, according to the administration.\n\nThe earthquake's intensity was highest in {highest_area}, where it measured {highest_intensity} on Taiwan's 7-tier intensity scale.
        """

    if second_area:
        report += f"\nThe quake also measured an intensity of {second_intensity} in {second_area}, the CWA said."

    report += "\n\n(By NAME)\nEnditem"

    print(report)
else:
    print("Epicenter not in target regions; no report generated.")
