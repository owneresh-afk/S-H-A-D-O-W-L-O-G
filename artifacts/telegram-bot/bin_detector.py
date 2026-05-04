"""
BIN auto-detection: network, card type, and country hints.
"""

COUNTRY_HINTS = {
    # US ranges
    "4": {"US": ["40", "41", "42", "43", "44", "45", "46", "47", "48"]},
}

NETWORK_RULES = [
    # (check_fn, network_name)
    (lambda b: b[:2] in ("34", "37"), "Amex"),
    (lambda b: 3528 <= int(b[:4]) <= 3589 if len(b) >= 4 and b[:4].isdigit() else False, "JCB"),
    (lambda b: b[:2] in ("36", "38") or (len(b) >= 3 and b[:3].isdigit() and 300 <= int(b[:3]) <= 305), "Diners Club"),
    (lambda b: b[:4] == "6011" or b[:2] == "65" or (len(b) >= 3 and b[:3].isdigit() and 644 <= int(b[:3]) <= 649), "Discover"),
    (lambda b: b[:2] == "62", "UnionPay"),
    (lambda b: b[:4] in ("6070", "6071", "6072", "6073", "6074", "6075", "6076", "6079", "6080", "6081", "6082", "6083", "6084", "6085"), "Rupay"),
    (lambda b: b[:6] in ("636368", "636297", "509040", "509070", "627780", "636369") or b[:3] == "509", "Elo"),
    (lambda b: b[:2] in ("51", "52", "53", "54", "55"), "Mastercard"),
    (lambda b: len(b) >= 4 and b[:4].isdigit() and 2221 <= int(b[:4]) <= 2720, "Mastercard"),
    (lambda b: b[:1] == "4", "Visa"),
]

COUNTRY_BIN_RANGES = {
    # Format: (start, end, country_code, country_name)
    # US
    (400000, 409999, "US", "🇺🇸 United States"),
    (410000, 419999, "US", "🇺🇸 United States"),
    (420000, 429999, "US", "🇺🇸 United States"),
    (430000, 439999, "US", "🇺🇸 United States"),
    (440000, 449999, "US", "🇺🇸 United States"),
    (450000, 459999, "US", "🇺🇸 United States"),
    (460000, 469999, "US", "🇺🇸 United States"),
    (470000, 479999, "US", "🇺🇸 United States"),
    (480000, 489999, "US", "🇺🇸 United States"),
    (510000, 519999, "US", "🇺🇸 United States"),
    (520000, 529999, "US", "🇺🇸 United States"),
    (530000, 539999, "US", "🇺🇸 United States"),
    (540000, 549999, "US", "🇺🇸 United States"),
    (550000, 559999, "US", "🇺🇸 United States"),
    # UK
    (450000, 459999, "GB", "🇬🇧 United Kingdom"),
    (462000, 465999, "GB", "🇬🇧 United Kingdom"),
    (475000, 476999, "GB", "🇬🇧 United Kingdom"),
    # India  
    (607000, 608999, "IN", "🇮🇳 India"),
    # China
    (621000, 625999, "CN", "🇨🇳 China"),
    (626000, 627999, "CN", "🇨🇳 China"),
    # Brazil
    (636000, 636999, "BR", "🇧🇷 Brazil"),
    (509000, 509999, "BR", "🇧🇷 Brazil"),
    (627780, 627780, "BR", "🇧🇷 Brazil"),
}

COUNTRY_CODE_MAP = {
    "US": "🇺🇸 United States",
    "GB": "🇬🇧 United Kingdom",
    "UK": "🇬🇧 United Kingdom",
    "DE": "🇩🇪 Germany",
    "FR": "🇫🇷 France",
    "IT": "🇮🇹 Italy",
    "ES": "🇪🇸 Spain",
    "NL": "🇳🇱 Netherlands",
    "BE": "🇧🇪 Belgium",
    "CH": "🇨🇭 Switzerland",
    "AT": "🇦🇹 Austria",
    "PL": "🇵🇱 Poland",
    "SE": "🇸🇪 Sweden",
    "NO": "🇳🇴 Norway",
    "DK": "🇩🇰 Denmark",
    "FI": "🇫🇮 Finland",
    "PT": "🇵🇹 Portugal",
    "GR": "🇬🇷 Greece",
    "IE": "🇮🇪 Ireland",
    "RU": "🇷🇺 Russia",
    "UA": "🇺🇦 Ukraine",
    "CZ": "🇨🇿 Czech Republic",
    "HU": "🇭🇺 Hungary",
    "RO": "🇷🇴 Romania",
    "TR": "🇹🇷 Turkey",
    "CA": "🇨🇦 Canada",
    "MX": "🇲🇽 Mexico",
    "BR": "🇧🇷 Brazil",
    "AR": "🇦🇷 Argentina",
    "CL": "🇨🇱 Chile",
    "CO": "🇨🇴 Colombia",
    "PE": "🇵🇪 Peru",
    "IN": "🇮🇳 India",
    "CN": "🇨🇳 China",
    "JP": "🇯🇵 Japan",
    "KR": "🇰🇷 South Korea",
    "SG": "🇸🇬 Singapore",
    "HK": "🇭🇰 Hong Kong",
    "TW": "🇹🇼 Taiwan",
    "MY": "🇲🇾 Malaysia",
    "TH": "🇹🇭 Thailand",
    "ID": "🇮🇩 Indonesia",
    "PH": "🇵🇭 Philippines",
    "VN": "🇻🇳 Vietnam",
    "PK": "🇵🇰 Pakistan",
    "BD": "🇧🇩 Bangladesh",
    "KZ": "🇰🇿 Kazakhstan",
    "AE": "🇦🇪 UAE",
    "SA": "🇸🇦 Saudi Arabia",
    "IL": "🇮🇱 Israel",
    "EG": "🇪🇬 Egypt",
    "KW": "🇰🇼 Kuwait",
    "QA": "🇶🇦 Qatar",
    "JO": "🇯🇴 Jordan",
    "ZA": "🇿🇦 South Africa",
    "NG": "🇳🇬 Nigeria",
    "KE": "🇰🇪 Kenya",
    "GH": "🇬🇭 Ghana",
    "MA": "🇲🇦 Morocco",
    "TZ": "🇹🇿 Tanzania",
    "ET": "🇪🇹 Ethiopia",
    "AU": "🇦🇺 Australia",
    "NZ": "🇳🇿 New Zealand",
}


def detect_network(bin_code: str) -> str:
    bin_code = bin_code.strip()
    for check_fn, network in NETWORK_RULES:
        try:
            if check_fn(bin_code):
                return network
        except Exception:
            continue
    return "Unknown"


def detect_card_length(network: str) -> int:
    lengths = {
        "Amex": 15,
        "Diners Club": 14,
    }
    return lengths.get(network, 16)


def get_country_name(country_code: str) -> str:
    return COUNTRY_CODE_MAP.get(country_code.upper(), country_code.upper())


def parse_bin_file(content: str) -> list:
    """
    Parse a BIN file. Supports:
    1. Simple: one BIN per line (digits only)
    2. CSV: BIN,BANK_NAME,COUNTRY_CODE,CARD_TYPE
    3. With #comments

    Returns list of dicts: {bin, bank_name, country_code, card_type}
    """
    results = []
    lines = content.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split(",")]
        bin_code = parts[0].replace(" ", "").replace("-", "")

        if not bin_code.isdigit() or not (6 <= len(bin_code) <= 8):
            continue

        bank_name = parts[1] if len(parts) > 1 and parts[1] else "Custom Bank"
        country_code = parts[2].upper() if len(parts) > 2 and parts[2] else "US"
        card_type = parts[3].lower() if len(parts) > 3 and parts[3] else "credit"

        if card_type not in ("credit", "debit", "both"):
            card_type = "credit"

        results.append({
            "bin": bin_code,
            "bank_name": bank_name,
            "country_code": country_code,
            "card_type": card_type,
        })

    return results
