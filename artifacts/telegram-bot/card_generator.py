import random
from typing import Optional

BINS_DB = {
    "US": {
        "name": "🇺🇸 United States",
        "banks": {
            "Chase": {
                "Visa": {"credit": ["414709", "414720", "414750", "426428", "426453"],
                         "debit": ["412263", "414570", "426691"]},
                "Mastercard": {"credit": ["513742", "514897", "515543", "519627"],
                               "debit": ["513700", "514200"]},
                "Amex": {"credit": ["378282", "371449"]},
            },
            "Bank of America": {
                "Visa": {"credit": ["418460", "418490", "426617", "448410"],
                         "debit": ["415428", "418444"]},
                "Mastercard": {"credit": ["540761", "541333", "552564"], "debit": ["519198"]},
            },
            "Wells Fargo": {
                "Visa": {"credit": ["448002", "448010", "448092", "448016"],
                         "debit": ["448001", "448015"]},
                "Mastercard": {"credit": ["524128", "524150"], "debit": ["524100"]},
            },
            "Citi": {
                "Visa": {"credit": ["423157", "427533", "437860"], "debit": ["404256"]},
                "Mastercard": {"credit": ["542418", "542432", "545616", "549283"],
                               "debit": ["542400"]},
            },
            "Capital One": {
                "Visa": {"credit": ["414740", "414748", "426451"], "debit": []},
                "Mastercard": {"credit": ["516793", "517805", "533432"], "debit": []},
            },
            "American Express": {
                "Amex": {"credit": ["378282", "371449", "340000", "370000"]},
            },
            "Discover": {
                "Discover": {"credit": ["601100", "601109", "601120", "601144", "644000"],
                             "debit": ["601111"]},
            },
        }
    },
    "UK": {
        "name": "🇬🇧 United Kingdom",
        "banks": {
            "Barclays": {
                "Visa": {"credit": ["450875", "462744", "465934", "475148"],
                         "debit": ["450895", "456789", "462200"]},
                "Mastercard": {"credit": ["520474", "524104"], "debit": []},
            },
            "HSBC": {
                "Visa": {"credit": ["454313", "454723", "491880"], "debit": ["403767", "450440"]},
                "Mastercard": {"credit": ["540404", "541010", "549400"], "debit": []},
            },
            "Lloyds Bank": {
                "Visa": {"credit": ["475938", "492182", "498824"],
                         "debit": ["447520", "476213"]},
                "Mastercard": {"credit": ["542603"], "debit": []},
            },
            "NatWest": {
                "Visa": {"credit": ["464510", "476620"], "debit": ["443069", "465328"]},
                "Mastercard": {"credit": ["540900", "541214"], "debit": []},
            },
            "Monzo": {
                "Mastercard": {"credit": [], "debit": ["532232", "535685"]},
            },
            "Revolut": {
                "Visa": {"credit": [], "debit": ["488455", "488457"]},
                "Mastercard": {"credit": [], "debit": ["531274", "533954"]},
            },
        }
    },
    "CA": {
        "name": "🇨🇦 Canada",
        "banks": {
            "RBC": {
                "Visa": {"credit": ["446200", "446213", "450032"], "debit": ["450044"]},
                "Mastercard": {"credit": [], "debit": []},
            },
            "TD Bank": {
                "Visa": {"credit": ["453614", "453627", "456321"], "debit": ["453600"]},
                "Mastercard": {"credit": ["521978", "522310"], "debit": []},
            },
            "Scotiabank": {
                "Visa": {"credit": ["452905", "452920", "453091"], "debit": ["452900"]},
                "Mastercard": {"credit": ["541744", "541766"], "debit": []},
            },
            "CIBC": {
                "Visa": {"credit": ["448529", "448570"], "debit": ["448500"]},
                "Mastercard": {"credit": ["534642", "540040"], "debit": []},
            },
        }
    },
    "AU": {
        "name": "🇦🇺 Australia",
        "banks": {
            "Commonwealth Bank": {
                "Visa": {"credit": ["459012", "462756", "482634"],
                         "debit": ["459000", "462760"]},
                "Mastercard": {"credit": ["528102", "539421"], "debit": []},
            },
            "ANZ": {
                "Visa": {"credit": ["403123", "413745"], "debit": ["403120"]},
                "Mastercard": {"credit": ["515078", "521022"], "debit": []},
            },
            "Westpac": {
                "Visa": {"credit": ["437962", "455683"], "debit": ["437960"]},
                "Mastercard": {"credit": ["512878", "527834"], "debit": []},
            },
        }
    },
    "DE": {
        "name": "🇩🇪 Germany",
        "banks": {
            "Deutsche Bank": {
                "Visa": {"credit": ["411858", "413004", "419427"], "debit": ["411850"]},
                "Mastercard": {"credit": ["521234", "536812"], "debit": []},
            },
            "Commerzbank": {
                "Visa": {"credit": ["434531", "439001"], "debit": ["434530"]},
                "Mastercard": {"credit": ["519050", "523498"], "debit": []},
            },
            "N26": {
                "Mastercard": {"credit": [], "debit": ["533300", "533301"]},
            },
        }
    },
    "FR": {
        "name": "🇫🇷 France",
        "banks": {
            "BNP Paribas": {
                "Visa": {"credit": ["408711", "426578", "432101"], "debit": ["408710"]},
                "Mastercard": {"credit": ["521783", "535016"], "debit": []},
            },
            "Crédit Agricole": {
                "Visa": {"credit": ["416590", "431560"], "debit": ["416591"]},
                "Mastercard": {"credit": ["533602", "540150"], "debit": []},
            },
            "Société Générale": {
                "Visa": {"credit": ["451416", "476012"], "debit": ["451415"]},
                "Mastercard": {"credit": ["524871", "531340"], "debit": []},
            },
        }
    },
    "IN": {
        "name": "🇮🇳 India",
        "banks": {
            "SBI": {
                "Visa": {"credit": ["414906", "437748", "459108"], "debit": ["414900", "437740"]},
                "Mastercard": {"credit": ["523414", "536001"], "debit": []},
                "Rupay": {"credit": ["607001", "607020"], "debit": ["607000", "607010"]},
            },
            "HDFC Bank": {
                "Visa": {"credit": ["439895", "456616", "461266"],
                         "debit": ["439890", "456610"]},
                "Mastercard": {"credit": ["522888", "531556"], "debit": []},
            },
            "ICICI Bank": {
                "Visa": {"credit": ["430000", "430001", "456017"], "debit": ["430000"]},
                "Mastercard": {"credit": ["512601", "527246"], "debit": []},
            },
            "Axis Bank": {
                "Visa": {"credit": ["415359", "438857"], "debit": ["415350"]},
                "Mastercard": {"credit": ["519474", "530993"], "debit": []},
            },
        }
    },
    "JP": {
        "name": "🇯🇵 Japan",
        "banks": {
            "MUFG": {
                "Visa": {"credit": ["417904", "441338"], "debit": ["417900"]},
                "JCB": {"credit": ["353011", "356600", "357811"], "debit": []},
            },
            "SMBC": {
                "Visa": {"credit": ["418012", "438421"], "debit": ["418010"]},
                "Mastercard": {"credit": ["528421", "537001"], "debit": []},
            },
            "Rakuten Bank": {
                "Visa": {"credit": ["417528"], "debit": ["417527"]},
                "JCB": {"credit": ["357900"], "debit": []},
            },
        }
    },
    "BR": {
        "name": "🇧🇷 Brazil",
        "banks": {
            "Banco do Brasil": {
                "Visa": {"credit": ["406655", "407308"], "debit": ["406650"]},
                "Mastercard": {"credit": ["513480", "536741"], "debit": []},
                "Elo": {"credit": ["636368", "636297"], "debit": ["636368"]},
            },
            "Itaú": {
                "Visa": {"credit": ["403783", "438411"], "debit": ["403780"]},
                "Mastercard": {"credit": ["528032", "530012"], "debit": []},
            },
            "Nubank": {
                "Mastercard": {"credit": ["534432", "535720"], "debit": []},
            },
        }
    },
    "SG": {
        "name": "🇸🇬 Singapore",
        "banks": {
            "DBS Bank": {
                "Visa": {"credit": ["411690", "457861"], "debit": ["411691"]},
                "Mastercard": {"credit": ["520888", "539001"], "debit": []},
            },
            "OCBC": {
                "Visa": {"credit": ["404784", "438090"], "debit": ["404780"]},
                "Mastercard": {"credit": ["524532", "531600"], "debit": []},
            },
        }
    },
    "AE": {
        "name": "🇦🇪 UAE",
        "banks": {
            "Emirates NBD": {
                "Visa": {"credit": ["403040", "435617"], "debit": ["403041"]},
                "Mastercard": {"credit": ["521730", "532891"], "debit": []},
            },
            "Abu Dhabi Islamic": {
                "Visa": {"credit": ["414456", "427812"], "debit": []},
                "Mastercard": {"credit": ["533720"], "debit": []},
            },
        }
    },
    "MX": {
        "name": "🇲🇽 Mexico",
        "banks": {
            "BBVA Mexico": {
                "Visa": {"credit": ["413711", "424568"], "debit": ["413710"]},
                "Mastercard": {"credit": ["524031", "530460"], "debit": []},
            },
            "Banamex": {
                "Visa": {"credit": ["407832", "412302"], "debit": ["407831"]},
                "Mastercard": {"credit": ["519012", "527340"], "debit": []},
            },
        }
    },
    "NL": {
        "name": "🇳🇱 Netherlands",
        "banks": {
            "ING": {
                "Visa": {"credit": ["432923", "471149"], "debit": ["432920"]},
                "Mastercard": {"credit": ["531022", "540300"], "debit": []},
            },
            "ABN AMRO": {
                "Visa": {"credit": ["434901", "451602"], "debit": ["434900"]},
                "Mastercard": {"credit": ["523010", "531660"], "debit": []},
            },
        }
    },
    "SE": {
        "name": "🇸🇪 Sweden",
        "banks": {
            "Swedbank": {
                "Visa": {"credit": ["427788", "432010"], "debit": ["427780"]},
                "Mastercard": {"credit": ["519400", "535010"], "debit": []},
            },
            "Klarna": {
                "Visa": {"credit": [], "debit": ["489020", "489021"]},
            },
        }
    },
    "ES": {
        "name": "🇪🇸 Spain",
        "banks": {
            "Santander": {
                "Visa": {"credit": ["403116", "423005"], "debit": ["403110"]},
                "Mastercard": {"credit": ["519370", "530980"], "debit": []},
            },
            "BBVA Spain": {
                "Visa": {"credit": ["414542", "424009"], "debit": ["414540"]},
                "Mastercard": {"credit": ["523906", "533110"], "debit": []},
            },
        }
    },
    "IT": {
        "name": "🇮🇹 Italy",
        "banks": {
            "Intesa Sanpaolo": {
                "Visa": {"credit": ["425617", "448003"], "debit": ["425610"]},
                "Mastercard": {"credit": ["524678", "537012"], "debit": []},
            },
            "UniCredit": {
                "Visa": {"credit": ["421302", "434712"], "debit": ["421300"]},
                "Mastercard": {"credit": ["520003", "531004"], "debit": []},
            },
        }
    },
    "KR": {
        "name": "🇰🇷 South Korea",
        "banks": {
            "KB Kookmin": {
                "Visa": {"credit": ["413002", "438510"], "debit": ["413000"]},
                "Mastercard": {"credit": ["523892", "536402"], "debit": []},
            },
            "Kakao Bank": {
                "Visa": {"credit": [], "debit": ["461212", "461213"]},
                "Mastercard": {"credit": [], "debit": ["533080"]},
            },
        }
    },
    "TR": {
        "name": "🇹🇷 Turkey",
        "banks": {
            "Garanti BBVA": {
                "Visa": {"credit": ["415022", "438821"], "debit": ["415020"]},
                "Mastercard": {"credit": ["531222", "540088"], "debit": []},
            },
            "Akbank": {
                "Visa": {"credit": ["403340", "424200"], "debit": ["403341"]},
                "Mastercard": {"credit": ["519601", "530044"], "debit": []},
            },
        }
    },
    "SA": {
        "name": "🇸🇦 Saudi Arabia",
        "banks": {
            "Al Rajhi": {
                "Visa": {"credit": ["412450", "443012"], "debit": ["412451"]},
                "Mastercard": {"credit": ["524190", "533680"], "debit": []},
            },
            "NCB": {
                "Visa": {"credit": ["413800", "426311"], "debit": ["413801"]},
                "Mastercard": {"credit": ["519820", "530201"], "debit": []},
            },
        }
    },
    "ZA": {
        "name": "🇿🇦 South Africa",
        "banks": {
            "Standard Bank": {
                "Visa": {"credit": ["428012", "451603"], "debit": ["428010"]},
                "Mastercard": {"credit": ["523012", "537802"], "debit": []},
            },
            "FNB": {
                "Visa": {"credit": ["414218", "438002"], "debit": ["414210"]},
                "Mastercard": {"credit": ["521301", "530812"], "debit": []},
            },
        }
    },
}

NETWORK_LENGTHS = {
    "Visa": 16,
    "Mastercard": 16,
    "Amex": 15,
    "Discover": 16,
    "JCB": 16,
    "UnionPay": 16,
    "Rupay": 16,
    "Elo": 16,
    "Diners Club": 14,
}

CARD_CATEGORIES = ["Classic", "Gold", "Platinum", "Business", "World", "Infinite", "Signature", "Standard"]

ALL_NETWORKS = ["Visa", "Mastercard", "Amex", "Discover", "JCB", "UnionPay", "Rupay", "Elo", "Diners Club"]


def luhn_complete(partial: str) -> Optional[str]:
    partial = partial.rstrip()
    for check_digit in range(10):
        candidate = partial + str(check_digit)
        total = 0
        reverse = candidate[::-1]
        for i, digit in enumerate(reverse):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        if total % 10 == 0:
            return candidate
    return None


def generate_card_number(bin_prefix: str, length: int) -> str:
    while True:
        padding_length = length - len(bin_prefix) - 1
        middle = "".join(str(random.randint(0, 9)) for _ in range(padding_length))
        partial = bin_prefix + middle
        result = luhn_complete(partial)
        if result:
            return result


def generate_expiry() -> str:
    month = random.randint(1, 12)
    year = random.randint(2026, 2030)
    return f"{month:02d}/{year % 100:02d}"


def generate_cvv(network: str) -> str:
    length = 4 if network == "Amex" else 3
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def get_bin_prefix(country_code: str, bank: Optional[str], network: Optional[str], card_type: str) -> Optional[tuple]:
    country_data = BINS_DB.get(country_code)
    if not country_data:
        return None

    banks = country_data["banks"]
    if bank and bank not in banks:
        return None

    candidate_banks = {bank: banks[bank]} if bank else banks
    candidates = []

    for bname, bdata in candidate_banks.items():
        for net, types in bdata.items():
            if network and net != network:
                continue
            bins_list = types.get(card_type, [])
            if not bins_list:
                bins_list = types.get("credit", []) + types.get("debit", [])
            for b in bins_list:
                candidates.append((bname, net, b))

    if not candidates:
        return None
    return random.choice(candidates)


def generate_cards(
    countries: list,
    banks: Optional[list],
    networks: Optional[list],
    card_type: str,
    count: int
) -> list:
    cards = []
    attempts = 0
    max_attempts = count * 20

    while len(cards) < count and attempts < max_attempts:
        attempts += 1
        country_code = random.choice(countries)
        bank = random.choice(banks) if banks else None
        network = random.choice(networks) if networks else None

        result = get_bin_prefix(country_code, bank, network, card_type)
        if not result:
            bank_data = BINS_DB.get(country_code, {}).get("banks", {})
            for bname, bdata in bank_data.items():
                for net, types in bdata.items():
                    if network and net != network:
                        continue
                    bins_list = types.get(card_type, []) + types.get("credit", [])
                    if bins_list:
                        result = (bname, net, random.choice(bins_list))
                        break
                if result:
                    break

        if not result:
            continue

        bname, net, bin_prefix = result
        length = NETWORK_LENGTHS.get(net, 16)
        number = generate_card_number(bin_prefix, length)
        expiry = generate_expiry()
        cvv = generate_cvv(net)

        cards.append({
            "number": number,
            "expiry": expiry,
            "cvv": cvv,
            "network": net,
            "bank": bname,
            "country": BINS_DB[country_code]["name"],
            "type": card_type,
        })

    return cards


def format_card(card: dict) -> str:
    return f"`{card['number']}|{card['expiry']}|{card['cvv']}`"


def get_countries_list() -> list:
    return [(code, data["name"]) for code, data in BINS_DB.items()]


def get_banks_for_countries(country_codes: list) -> list:
    banks = set()
    for code in country_codes:
        country = BINS_DB.get(code)
        if country:
            for bank in country["banks"]:
                banks.add(bank)
    return sorted(banks)


def get_networks_for_countries(country_codes: list, bank: Optional[str] = None) -> list:
    networks = set()
    for code in country_codes:
        country = BINS_DB.get(code)
        if not country:
            continue
        bank_data = country["banks"]
        if bank:
            bank_data = {bank: bank_data[bank]} if bank in bank_data else {}
        for bdata in bank_data.values():
            for net in bdata:
                networks.add(net)
    return sorted(networks)
