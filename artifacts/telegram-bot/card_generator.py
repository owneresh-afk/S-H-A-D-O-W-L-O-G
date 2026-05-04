import random
from typing import Optional

BINS_DB = {
    # ═══════════════ AMERICAS ═══════════════
    "US": {
        "name": "🇺🇸 United States",
        "banks": {
            "Chase": {
                "Visa": {"credit": ["414709", "414720", "414750", "426428", "426453", "476776"], "debit": ["412263", "414570", "426691", "476797"]},
                "Mastercard": {"credit": ["513742", "514897", "515543", "519627", "524285"], "debit": ["513700", "514200", "524200"]},
                "Amex": {"credit": ["378282", "371449"]},
            },
            "Bank of America": {
                "Visa": {"credit": ["418460", "418490", "426617", "448410", "472363"], "debit": ["415428", "418444", "472347"]},
                "Mastercard": {"credit": ["540761", "541333", "552564", "553201"], "debit": ["519198", "540700"]},
            },
            "Wells Fargo": {
                "Visa": {"credit": ["448002", "448010", "448092", "448016", "482198"], "debit": ["448001", "448015", "482111"]},
                "Mastercard": {"credit": ["524128", "524150", "537822"], "debit": ["524100", "537800"]},
            },
            "Citi": {
                "Visa": {"credit": ["423157", "427533", "437860", "472456"], "debit": ["404256", "423100"]},
                "Mastercard": {"credit": ["542418", "542432", "545616", "549283", "558129"], "debit": ["542400", "545600"]},
            },
            "Capital One": {
                "Visa": {"credit": ["414740", "414748", "426451", "476215"], "debit": ["414741"]},
                "Mastercard": {"credit": ["516793", "517805", "533432", "545085"], "debit": ["516790"]},
            },
            "American Express": {
                "Amex": {"credit": ["378282", "371449", "340000", "370000", "378734", "371144"]},
            },
            "Discover": {
                "Discover": {"credit": ["601100", "601109", "601120", "601144", "644000", "650000"], "debit": ["601111", "644001"]},
            },
            "US Bank": {
                "Visa": {"credit": ["403714", "410936", "411042"], "debit": ["403710", "410930"]},
                "Mastercard": {"credit": ["517563", "530001", "538301"], "debit": ["517560"]},
            },
            "PNC Bank": {
                "Visa": {"credit": ["426981", "455714", "485932"], "debit": ["426980", "455710"]},
                "Mastercard": {"credit": ["520301", "531428"], "debit": ["520300"]},
            },
            "TD Bank": {
                "Visa": {"credit": ["424631", "456821", "476502"], "debit": ["424630", "456820"]},
                "Mastercard": {"credit": ["520845", "535621"], "debit": ["520840"]},
            },
            "Truist": {
                "Visa": {"credit": ["437614", "476321"], "debit": ["437610"]},
                "Mastercard": {"credit": ["521634", "537421"], "debit": ["521630"]},
            },
            "Goldman Sachs (Marcus)": {
                "Mastercard": {"credit": ["522163", "533561"], "debit": []},
            },
            "Chime": {
                "Visa": {"credit": [], "debit": ["423220", "448542", "498503"]},
            },
            "Cash App": {
                "Visa": {"credit": [], "debit": ["445783", "461321", "493814"]},
            },
        }
    },
    "CA": {
        "name": "🇨🇦 Canada",
        "banks": {
            "RBC Royal Bank": {
                "Visa": {"credit": ["446200", "446213", "450032", "450051", "476891"], "debit": ["450044", "476890"]},
                "Mastercard": {"credit": ["513051", "521200"], "debit": ["513050"]},
            },
            "TD Canada Trust": {
                "Visa": {"credit": ["453614", "453627", "456321", "476554"], "debit": ["453600", "476550"]},
                "Mastercard": {"credit": ["521978", "522310", "536421"], "debit": ["521970"]},
            },
            "Scotiabank": {
                "Visa": {"credit": ["452905", "452920", "453091", "476012"], "debit": ["452900", "476010"]},
                "Mastercard": {"credit": ["541744", "541766", "552101"], "debit": ["541740"]},
            },
            "CIBC": {
                "Visa": {"credit": ["448529", "448570", "457821"], "debit": ["448500", "457820"]},
                "Mastercard": {"credit": ["534642", "540040", "551201"], "debit": ["534640"]},
            },
            "BMO": {
                "Mastercard": {"credit": ["514632", "527431", "540921"], "debit": ["514630", "527430"]},
                "Visa": {"credit": ["402718", "437521"], "debit": ["402710"]},
            },
            "National Bank": {
                "Mastercard": {"credit": ["521634", "535401"], "debit": ["521630"]},
                "Visa": {"credit": ["423541", "456712"], "debit": ["423540"]},
            },
            "Desjardins": {
                "Visa": {"credit": ["403215", "457631"], "debit": ["403210", "457630"]},
                "Mastercard": {"credit": ["514201", "527901"], "debit": ["514200"]},
            },
            "Tangerine": {
                "Mastercard": {"credit": ["525641", "537821"], "debit": []},
            },
            "HSBC Canada": {
                "Mastercard": {"credit": ["526401", "540541"], "debit": ["526400"]},
                "Visa": {"credit": ["434521", "463201"], "debit": ["434520"]},
            },
        }
    },
    "MX": {
        "name": "🇲🇽 Mexico",
        "banks": {
            "BBVA Mexico": {
                "Visa": {"credit": ["413711", "424568", "476321"], "debit": ["413710", "476320"]},
                "Mastercard": {"credit": ["524031", "530460", "542101"], "debit": ["524030"]},
            },
            "Banamex (Citi)": {
                "Visa": {"credit": ["407832", "412302", "451321"], "debit": ["407831", "451320"]},
                "Mastercard": {"credit": ["519012", "527340", "538201"], "debit": ["519010"]},
            },
            "Santander Mexico": {
                "Visa": {"credit": ["421301", "448021"], "debit": ["421300", "448020"]},
                "Mastercard": {"credit": ["515421", "530121"], "debit": ["515420"]},
            },
            "Banorte": {
                "Visa": {"credit": ["414521", "438921"], "debit": ["414520"]},
                "Mastercard": {"credit": ["519241", "530881"], "debit": ["519240"]},
            },
            "HSBC Mexico": {
                "Visa": {"credit": ["403741", "451621"], "debit": ["403740"]},
                "Mastercard": {"credit": ["521461", "535201"], "debit": ["521460"]},
            },
            "Inbursa": {
                "Visa": {"credit": ["434201", "457321"], "debit": []},
                "Mastercard": {"credit": ["520141", "531281"], "debit": []},
            },
            "Banregio": {
                "Visa": {"credit": ["437801", "462341"], "debit": ["437800"]},
                "Mastercard": {"credit": ["522441"], "debit": []},
            },
        }
    },
    "BR": {
        "name": "🇧🇷 Brazil",
        "banks": {
            "Banco do Brasil": {
                "Visa": {"credit": ["406655", "407308", "451481"], "debit": ["406650", "451480"]},
                "Mastercard": {"credit": ["513480", "536741", "548201"], "debit": ["513481"]},
                "Elo": {"credit": ["636368", "636297", "636369"], "debit": ["636368"]},
            },
            "Itaú Unibanco": {
                "Visa": {"credit": ["403783", "438411", "476501"], "debit": ["403780", "476500"]},
                "Mastercard": {"credit": ["528032", "530012", "547321"], "debit": ["528030"]},
                "Amex": {"credit": ["376181"], "debit": []},
            },
            "Bradesco": {
                "Visa": {"credit": ["402827", "427491", "465821"], "debit": ["402820", "465820"]},
                "Mastercard": {"credit": ["516321", "527891", "545601"], "debit": ["516320"]},
                "Amex": {"credit": ["376451"], "debit": []},
                "Elo": {"credit": ["636297", "509070"], "debit": ["636297"]},
            },
            "Caixa Econômica": {
                "Visa": {"credit": ["404541", "451921"], "debit": ["404540", "451920"]},
                "Mastercard": {"credit": ["517641", "531441"], "debit": ["517640"]},
                "Elo": {"credit": ["509040", "627780"], "debit": ["509040"]},
            },
            "Santander Brazil": {
                "Visa": {"credit": ["403111", "443021", "456211"], "debit": ["403110", "456210"]},
                "Mastercard": {"credit": ["512901", "530311", "545801"], "debit": ["512900"]},
            },
            "Nubank": {
                "Mastercard": {"credit": ["534432", "535720", "548001"], "debit": ["535721"]},
                "Visa": {"credit": ["448811"], "debit": []},
            },
            "Inter Bank": {
                "Mastercard": {"credit": ["522301", "537021"], "debit": ["522300"]},
                "Visa": {"credit": ["455211"], "debit": ["455210"]},
            },
            "C6 Bank": {
                "Mastercard": {"credit": ["536101", "547601"], "debit": []},
            },
        }
    },
    "AR": {
        "name": "🇦🇷 Argentina",
        "banks": {
            "Banco Nación": {
                "Visa": {"credit": ["404211", "451201"], "debit": ["404210", "451200"]},
                "Mastercard": {"credit": ["516201", "530011"], "debit": ["516200"]},
            },
            "Banco Galicia": {
                "Visa": {"credit": ["407611", "438201"], "debit": ["407610", "438200"]},
                "Mastercard": {"credit": ["519301", "531201"], "debit": ["519300"]},
            },
            "Santander Argentina": {
                "Visa": {"credit": ["421101", "451601"], "debit": ["421100"]},
                "Mastercard": {"credit": ["521101", "534701"], "debit": ["521100"]},
            },
            "BBVA Argentina": {
                "Visa": {"credit": ["414101", "437501"], "debit": ["414100"]},
                "Mastercard": {"credit": ["519801", "530701"], "debit": ["519800"]},
            },
            "Mercado Pago": {
                "Visa": {"credit": ["437611"], "debit": ["437612"]},
                "Mastercard": {"credit": ["522611"], "debit": []},
            },
        }
    },
    "CL": {
        "name": "🇨🇱 Chile",
        "banks": {
            "Banco de Chile": {
                "Visa": {"credit": ["403621", "451321"], "debit": ["403620", "451320"]},
                "Mastercard": {"credit": ["516401", "531501"], "debit": ["516400"]},
            },
            "BancoEstado": {
                "Visa": {"credit": ["405101", "448401"], "debit": ["405100", "448400"]},
                "Mastercard": {"credit": ["518301", "530401"], "debit": ["518300"]},
            },
            "Santander Chile": {
                "Visa": {"credit": ["421201", "456401"], "debit": ["421200"]},
                "Mastercard": {"credit": ["521201", "534801"], "debit": ["521200"]},
            },
            "Scotiabank Chile": {
                "Visa": {"credit": ["418701", "453201"], "debit": ["418700"]},
                "Mastercard": {"credit": ["520301", "533601"], "debit": ["520300"]},
            },
            "Falabella": {
                "Visa": {"credit": ["462401", "476901"], "debit": []},
                "Mastercard": {"credit": ["527401", "540601"], "debit": []},
            },
        }
    },
    "CO": {
        "name": "🇨🇴 Colombia",
        "banks": {
            "Bancolombia": {
                "Visa": {"credit": ["404501", "451701"], "debit": ["404500", "451700"]},
                "Mastercard": {"credit": ["516501", "530201"], "debit": ["516500"]},
            },
            "Davivienda": {
                "Visa": {"credit": ["406901", "449801"], "debit": ["406900", "449800"]},
                "Mastercard": {"credit": ["518401", "531601"], "debit": ["518400"]},
            },
            "BBVA Colombia": {
                "Visa": {"credit": ["414201", "438101"], "debit": ["414200"]},
                "Mastercard": {"credit": ["519901", "531001"], "debit": ["519900"]},
            },
            "Banco de Bogotá": {
                "Visa": {"credit": ["404101", "448201"], "debit": ["404100"]},
                "Mastercard": {"credit": ["517101", "530601"], "debit": ["517100"]},
            },
        }
    },
    "PE": {
        "name": "🇵🇪 Peru",
        "banks": {
            "BCP": {
                "Visa": {"credit": ["404401", "451901"], "debit": ["404400", "451900"]},
                "Mastercard": {"credit": ["516601", "530301"], "debit": ["516600"]},
            },
            "BBVA Peru": {
                "Visa": {"credit": ["414301", "438301"], "debit": ["414300"]},
                "Mastercard": {"credit": ["520001", "531101"], "debit": ["520000"]},
            },
            "Interbank": {
                "Visa": {"credit": ["434101", "463501"], "debit": ["434100"]},
                "Mastercard": {"credit": ["522101", "535401"], "debit": ["522100"]},
            },
            "Scotiabank Peru": {
                "Visa": {"credit": ["418801", "453401"], "debit": ["418800"]},
                "Mastercard": {"credit": ["520501", "533801"], "debit": ["520500"]},
            },
        }
    },
    # ═══════════════ EUROPE ═══════════════
    "GB": {
        "name": "🇬🇧 United Kingdom",
        "banks": {
            "Barclays": {
                "Visa": {"credit": ["450875", "462744", "465934", "475148", "492143"], "debit": ["450895", "456789", "462200", "492100"]},
                "Mastercard": {"credit": ["520474", "524104", "539321"], "debit": ["520470"]},
            },
            "HSBC UK": {
                "Visa": {"credit": ["454313", "454723", "491880", "476321"], "debit": ["403767", "450440", "476320"]},
                "Mastercard": {"credit": ["540404", "541010", "549400", "552301"], "debit": ["540400"]},
            },
            "Lloyds Bank": {
                "Visa": {"credit": ["475938", "492182", "498824", "476411"], "debit": ["447520", "476213", "492100"]},
                "Mastercard": {"credit": ["542603", "551201"], "debit": ["542600"]},
            },
            "NatWest": {
                "Visa": {"credit": ["464510", "476620", "491201"], "debit": ["443069", "465328", "491200"]},
                "Mastercard": {"credit": ["540900", "541214", "553401"], "debit": ["540901"]},
            },
            "Halifax": {
                "Visa": {"credit": ["459821", "476101"], "debit": ["459820", "476100"]},
                "Mastercard": {"credit": ["521301", "534101"], "debit": ["521300"]},
            },
            "Santander UK": {
                "Visa": {"credit": ["451721", "476811"], "debit": ["451720", "476810"]},
                "Mastercard": {"credit": ["524301", "537601"], "debit": ["524300"]},
            },
            "Monzo": {
                "Mastercard": {"credit": [], "debit": ["532232", "535685", "543206"]},
            },
            "Revolut UK": {
                "Visa": {"credit": [], "debit": ["488455", "488457", "498621"]},
                "Mastercard": {"credit": [], "debit": ["531274", "533954", "548911"]},
            },
            "Starling Bank": {
                "Mastercard": {"credit": [], "debit": ["536811", "548201"]},
            },
            "TSB": {
                "Visa": {"credit": ["461201", "475901"], "debit": ["461200", "475900"]},
                "Mastercard": {"credit": ["522401", "535801"], "debit": ["522400"]},
            },
            "Metro Bank": {
                "Visa": {"credit": ["461401"], "debit": ["461400"]},
                "Mastercard": {"credit": ["524501"], "debit": ["524500"]},
            },
            "Nationwide": {
                "Visa": {"credit": ["462901", "476701"], "debit": ["462900", "476700"]},
                "Mastercard": {"credit": ["524701"], "debit": ["524700"]},
            },
        }
    },
    "DE": {
        "name": "🇩🇪 Germany",
        "banks": {
            "Deutsche Bank": {
                "Visa": {"credit": ["411858", "413004", "419427", "476201"], "debit": ["411850", "476200"]},
                "Mastercard": {"credit": ["521234", "536812", "548401"], "debit": ["521230"]},
            },
            "Commerzbank": {
                "Visa": {"credit": ["434531", "439001", "463101"], "debit": ["434530", "463100"]},
                "Mastercard": {"credit": ["519050", "523498", "536101"], "debit": ["519051"]},
            },
            "Sparkasse": {
                "Visa": {"credit": ["447201", "463801"], "debit": ["447200", "463800"]},
                "Mastercard": {"credit": ["524801", "538201"], "debit": ["524800"]},
            },
            "DZ Bank / VR": {
                "Visa": {"credit": ["434901", "463201"], "debit": ["434900", "463200"]},
                "Mastercard": {"credit": ["521401", "535601"], "debit": ["521400"]},
            },
            "ING Germany": {
                "Visa": {"credit": ["432923", "471149"], "debit": ["432920", "471140"]},
                "Mastercard": {"credit": ["531022", "540300", "552101"], "debit": ["531021"]},
            },
            "N26": {
                "Mastercard": {"credit": [], "debit": ["533300", "533301", "548101"]},
            },
            "Comdirect": {
                "Visa": {"credit": ["416101", "451901"], "debit": ["416100"]},
                "Mastercard": {"credit": ["519101", "530901"], "debit": ["519100"]},
            },
            "Postbank": {
                "Visa": {"credit": ["448101", "463901"], "debit": ["448100", "463900"]},
                "Mastercard": {"credit": ["525101", "539601"], "debit": ["525100"]},
            },
            "HypoVereinsbank": {
                "Visa": {"credit": ["425801", "451701"], "debit": ["425800"]},
                "Mastercard": {"credit": ["521501", "535001"], "debit": ["521500"]},
            },
        }
    },
    "FR": {
        "name": "🇫🇷 France",
        "banks": {
            "BNP Paribas": {
                "Visa": {"credit": ["408711", "426578", "432101", "476101"], "debit": ["408710", "476100"]},
                "Mastercard": {"credit": ["521783", "535016", "548201"], "debit": ["521780"]},
            },
            "Crédit Agricole": {
                "Visa": {"credit": ["416590", "431560", "456101"], "debit": ["416591", "456100"]},
                "Mastercard": {"credit": ["533602", "540150", "552401"], "debit": ["533601"]},
            },
            "Société Générale": {
                "Visa": {"credit": ["451416", "476012", "491101"], "debit": ["451415", "491100"]},
                "Mastercard": {"credit": ["524871", "531340", "545201"], "debit": ["524870"]},
            },
            "Crédit Mutuel": {
                "Visa": {"credit": ["407401", "438101", "456201"], "debit": ["407400", "456200"]},
                "Mastercard": {"credit": ["517301", "531501"], "debit": ["517300"]},
            },
            "La Banque Postale": {
                "Visa": {"credit": ["413801", "451001"], "debit": ["413800", "451000"]},
                "Mastercard": {"credit": ["519201", "532201"], "debit": ["519200"]},
            },
            "Boursorama (BoursoBank)": {
                "Visa": {"credit": ["403901", "438201"], "debit": ["403900", "438200"]},
                "Mastercard": {"credit": ["516901", "530501"], "debit": ["516900"]},
            },
            "Fortuneo": {
                "Mastercard": {"credit": [], "debit": ["519801", "534501"]},
                "Visa": {"credit": ["403901"], "debit": ["403900"]},
            },
            "Orange Bank": {
                "Visa": {"credit": [], "debit": ["462901", "476901"]},
                "Mastercard": {"credit": [], "debit": ["524901", "537501"]},
            },
        }
    },
    "IT": {
        "name": "🇮🇹 Italy",
        "banks": {
            "Intesa Sanpaolo": {
                "Visa": {"credit": ["425617", "448003", "476101"], "debit": ["425610", "476100"]},
                "Mastercard": {"credit": ["524678", "537012", "549201"], "debit": ["524670"]},
            },
            "UniCredit": {
                "Visa": {"credit": ["421302", "434712", "463201"], "debit": ["421300", "463200"]},
                "Mastercard": {"credit": ["520003", "531004", "545301"], "debit": ["520001"]},
            },
            "Banco BPM": {
                "Visa": {"credit": ["407201", "438101"], "debit": ["407200", "438100"]},
                "Mastercard": {"credit": ["518101", "531201"], "debit": ["518100"]},
            },
            "Monte dei Paschi": {
                "Visa": {"credit": ["412101", "451201"], "debit": ["412100", "451200"]},
                "Mastercard": {"credit": ["519901", "532201"], "debit": ["519900"]},
            },
            "Fineco Bank": {
                "Visa": {"credit": ["416301", "451401"], "debit": ["416300", "451400"]},
                "Mastercard": {"credit": ["520601", "534001"], "debit": ["520600"]},
            },
            "Hype": {
                "Mastercard": {"credit": [], "debit": ["527501", "541201"]},
            },
            "N26 Italy": {
                "Mastercard": {"credit": [], "debit": ["533302", "548102"]},
            },
        }
    },
    "ES": {
        "name": "🇪🇸 Spain",
        "banks": {
            "Santander Spain": {
                "Visa": {"credit": ["403116", "423005", "456101"], "debit": ["403110", "456100"]},
                "Mastercard": {"credit": ["519370", "530980", "545401"], "debit": ["519371"]},
            },
            "BBVA Spain": {
                "Visa": {"credit": ["414542", "424009", "451701"], "debit": ["414540", "451700"]},
                "Mastercard": {"credit": ["523906", "533110", "548301"], "debit": ["523900"]},
            },
            "CaixaBank": {
                "Visa": {"credit": ["404101", "438301", "456501"], "debit": ["404100", "456500"]},
                "Mastercard": {"credit": ["517401", "531601"], "debit": ["517400"]},
            },
            "Bankia (now CaixaBank)": {
                "Visa": {"credit": ["406701", "451801"], "debit": ["406700"]},
                "Mastercard": {"credit": ["517901", "530401"], "debit": ["517900"]},
            },
            "Banco Sabadell": {
                "Visa": {"credit": ["407601", "439101"], "debit": ["407600"]},
                "Mastercard": {"credit": ["518401", "531801"], "debit": ["518400"]},
            },
            "ING Spain": {
                "Visa": {"credit": ["432924", "471150"], "debit": ["432921", "471141"]},
                "Mastercard": {"credit": ["531023", "540301"], "debit": ["531022"]},
            },
            "Bankinter": {
                "Visa": {"credit": ["404201", "438501"], "debit": ["404200"]},
                "Mastercard": {"credit": ["518601", "532401"], "debit": ["518600"]},
            },
        }
    },
    "NL": {
        "name": "🇳🇱 Netherlands",
        "banks": {
            "ING Netherlands": {
                "Visa": {"credit": ["432923", "471149", "491301"], "debit": ["432920", "491300"]},
                "Mastercard": {"credit": ["531022", "540300", "552201"], "debit": ["531021"]},
            },
            "ABN AMRO": {
                "Visa": {"credit": ["434901", "451602", "476201"], "debit": ["434900", "476200"]},
                "Mastercard": {"credit": ["523010", "531660", "545501"], "debit": ["523011"]},
            },
            "Rabobank": {
                "Visa": {"credit": ["444101", "463001"], "debit": ["444100", "463000"]},
                "Mastercard": {"credit": ["524201", "538401"], "debit": ["524200"]},
            },
            "Bunq": {
                "Mastercard": {"credit": [], "debit": ["519401", "534601"]},
                "Visa": {"credit": [], "debit": ["451901", "476401"]},
            },
            "ASN Bank": {
                "Visa": {"credit": ["404301"], "debit": ["404300"]},
                "Mastercard": {"credit": ["517501"], "debit": ["517500"]},
            },
        }
    },
    "BE": {
        "name": "🇧🇪 Belgium",
        "banks": {
            "BNP Paribas Fortis": {
                "Visa": {"credit": ["407301", "438601", "456601"], "debit": ["407300", "456600"]},
                "Mastercard": {"credit": ["517601", "531901"], "debit": ["517600"]},
            },
            "ING Belgium": {
                "Visa": {"credit": ["432925", "471151"], "debit": ["432922", "471142"]},
                "Mastercard": {"credit": ["531024", "540302"], "debit": ["531023"]},
            },
            "KBC": {
                "Visa": {"credit": ["422101", "456701"], "debit": ["422100", "456700"]},
                "Mastercard": {"credit": ["521601", "535101"], "debit": ["521600"]},
            },
            "Belfius": {
                "Visa": {"credit": ["404401", "451501"], "debit": ["404400", "451500"]},
                "Mastercard": {"credit": ["517701", "531301"], "debit": ["517700"]},
            },
            "Argenta": {
                "Visa": {"credit": ["401601", "438701"], "debit": ["401600"]},
                "Mastercard": {"credit": ["516101", "530601"], "debit": ["516100"]},
            },
        }
    },
    "CH": {
        "name": "🇨🇭 Switzerland",
        "banks": {
            "UBS": {
                "Visa": {"credit": ["447601", "463601"], "debit": ["447600", "463600"]},
                "Mastercard": {"credit": ["524401", "538601"], "debit": ["524400"]},
            },
            "Credit Suisse": {
                "Visa": {"credit": ["416601", "451601"], "debit": ["416600"]},
                "Mastercard": {"credit": ["520101", "533001"], "debit": ["520100"]},
            },
            "Raiffeisen CH": {
                "Visa": {"credit": ["444201", "463101"], "debit": ["444200"]},
                "Mastercard": {"credit": ["524301", "538501"], "debit": ["524301"]},
            },
            "PostFinance": {
                "Visa": {"credit": ["448301"], "debit": ["448300"]},
                "Mastercard": {"credit": ["525201"], "debit": ["525200"]},
            },
            "Neon": {
                "Mastercard": {"credit": [], "debit": ["527601", "541401"]},
            },
            "Revolut CH": {
                "Visa": {"credit": [], "debit": ["488456", "498622"]},
                "Mastercard": {"credit": [], "debit": ["531275", "548912"]},
            },
        }
    },
    "AT": {
        "name": "🇦🇹 Austria",
        "banks": {
            "Erste Bank": {
                "Visa": {"credit": ["416701", "451701"], "debit": ["416700", "451700"]},
                "Mastercard": {"credit": ["520201", "533101"], "debit": ["520200"]},
            },
            "Raiffeisen Austria": {
                "Visa": {"credit": ["444301", "463201"], "debit": ["444300"]},
                "Mastercard": {"credit": ["524401", "538701"], "debit": ["524401"]},
            },
            "BAWAG P.S.K.": {
                "Visa": {"credit": ["403501", "438801"], "debit": ["403500"]},
                "Mastercard": {"credit": ["516201", "530701"], "debit": ["516200"]},
            },
            "UniCredit Austria": {
                "Visa": {"credit": ["421401", "451801"], "debit": ["421400"]},
                "Mastercard": {"credit": ["520301", "533201"], "debit": ["520301"]},
            },
        }
    },
    "PL": {
        "name": "🇵🇱 Poland",
        "banks": {
            "PKO BP": {
                "Visa": {"credit": ["424801", "452001"], "debit": ["424800", "452000"]},
                "Mastercard": {"credit": ["523201", "537001"], "debit": ["523200"]},
            },
            "Bank Pekao": {
                "Visa": {"credit": ["413901", "451901"], "debit": ["413900", "451900"]},
                "Mastercard": {"credit": ["519301", "532301"], "debit": ["519301"]},
            },
            "mBank": {
                "Visa": {"credit": ["412201", "451001"], "debit": ["412200"]},
                "Mastercard": {"credit": ["519401", "532401"], "debit": ["519400"]},
            },
            "ING Poland": {
                "Visa": {"credit": ["432926", "471152"], "debit": ["432923", "471143"]},
                "Mastercard": {"credit": ["531025", "540303"], "debit": ["531024"]},
            },
            "Santander Poland": {
                "Visa": {"credit": ["421501", "451001"], "debit": ["421500"]},
                "Mastercard": {"credit": ["521701", "535201"], "debit": ["521700"]},
            },
        }
    },
    "SE": {
        "name": "🇸🇪 Sweden",
        "banks": {
            "Swedbank": {
                "Visa": {"credit": ["427788", "432010", "456401"], "debit": ["427780", "456400"]},
                "Mastercard": {"credit": ["519400", "535010", "548501"], "debit": ["519401"]},
            },
            "SEB": {
                "Visa": {"credit": ["447701", "463701"], "debit": ["447700", "463700"]},
                "Mastercard": {"credit": ["524501", "538801"], "debit": ["524500"]},
            },
            "Handelsbanken": {
                "Visa": {"credit": ["425801", "452001"], "debit": ["425800", "452000"]},
                "Mastercard": {"credit": ["523301", "537101"], "debit": ["523300"]},
            },
            "Nordea Sweden": {
                "Visa": {"credit": ["413101", "451101"], "debit": ["413100", "451100"]},
                "Mastercard": {"credit": ["519501", "532501"], "debit": ["519500"]},
            },
            "Klarna": {
                "Visa": {"credit": [], "debit": ["489020", "489021", "498701"]},
                "Mastercard": {"credit": [], "debit": ["527901", "541501"]},
            },
            "Revolut SE": {
                "Visa": {"credit": [], "debit": ["488458", "498623"]},
                "Mastercard": {"credit": [], "debit": ["531276", "548913"]},
            },
        }
    },
    "NO": {
        "name": "🇳🇴 Norway",
        "banks": {
            "DNB": {
                "Visa": {"credit": ["417101", "451101"], "debit": ["417100", "451100"]},
                "Mastercard": {"credit": ["519601", "532601"], "debit": ["519600"]},
            },
            "Sparebank 1": {
                "Visa": {"credit": ["447801", "463801"], "debit": ["447800", "463800"]},
                "Mastercard": {"credit": ["524601", "538901"], "debit": ["524600"]},
            },
            "Nordea Norway": {
                "Visa": {"credit": ["413201", "451201"], "debit": ["413200", "451200"]},
                "Mastercard": {"credit": ["519701", "532701"], "debit": ["519700"]},
            },
            "Sbanken": {
                "Visa": {"credit": ["447901", "463901"], "debit": ["447900"]},
                "Mastercard": {"credit": ["524701", "539001"], "debit": ["524700"]},
            },
        }
    },
    "DK": {
        "name": "🇩🇰 Denmark",
        "banks": {
            "Danske Bank": {
                "Visa": {"credit": ["410101", "451301"], "debit": ["410100", "451300"]},
                "Mastercard": {"credit": ["519801", "532801"], "debit": ["519800"]},
            },
            "Nordea Denmark": {
                "Visa": {"credit": ["413301", "451401"], "debit": ["413300", "451400"]},
                "Mastercard": {"credit": ["519901", "532901"], "debit": ["519901"]},
            },
            "Jyske Bank": {
                "Visa": {"credit": ["421601", "456101"], "debit": ["421600"]},
                "Mastercard": {"credit": ["521801", "535301"], "debit": ["521800"]},
            },
            "Lunar": {
                "Visa": {"credit": [], "debit": ["488459", "498624"]},
                "Mastercard": {"credit": [], "debit": ["527801", "541601"]},
            },
        }
    },
    "FI": {
        "name": "🇫🇮 Finland",
        "banks": {
            "OP Financial": {
                "Visa": {"credit": ["421701", "451501"], "debit": ["421700", "451500"]},
                "Mastercard": {"credit": ["521901", "535401"], "debit": ["521901"]},
            },
            "Nordea Finland": {
                "Visa": {"credit": ["413401", "451601"], "debit": ["413400", "451600"]},
                "Mastercard": {"credit": ["520001", "533001"], "debit": ["520001"]},
            },
            "Danske Bank FI": {
                "Visa": {"credit": ["410201", "451701"], "debit": ["410200", "451700"]},
                "Mastercard": {"credit": ["520101", "533101"], "debit": ["520101"]},
            },
            "S-Bank": {
                "Visa": {"credit": ["447101", "463401"], "debit": ["447100"]},
                "Mastercard": {"credit": ["524101", "538001"], "debit": ["524101"]},
            },
        }
    },
    "PT": {
        "name": "🇵🇹 Portugal",
        "banks": {
            "Caixa Geral": {
                "Visa": {"credit": ["404601", "438901"], "debit": ["404600", "438900"]},
                "Mastercard": {"credit": ["517801", "531401"], "debit": ["517800"]},
            },
            "Millennium BCP": {
                "Visa": {"credit": ["412301", "451101"], "debit": ["412300", "451100"]},
                "Mastercard": {"credit": ["520201", "533201"], "debit": ["520201"]},
            },
            "Banco Santander PT": {
                "Visa": {"credit": ["403201", "438601"], "debit": ["403200"]},
                "Mastercard": {"credit": ["516301", "530801"], "debit": ["516300"]},
            },
            "Novo Banco": {
                "Visa": {"credit": ["413501", "451801"], "debit": ["413500"]},
                "Mastercard": {"credit": ["519201", "532101"], "debit": ["519201"]},
            },
        }
    },
    "GR": {
        "name": "🇬🇷 Greece",
        "banks": {
            "National Bank of Greece": {
                "Visa": {"credit": ["413601", "451901"], "debit": ["413600", "451900"]},
                "Mastercard": {"credit": ["519301", "532201"], "debit": ["519301"]},
            },
            "Alpha Bank": {
                "Visa": {"credit": ["401701", "438701"], "debit": ["401700"]},
                "Mastercard": {"credit": ["515301", "530001"], "debit": ["515300"]},
            },
            "Piraeus Bank": {
                "Visa": {"credit": ["424101", "456201"], "debit": ["424100"]},
                "Mastercard": {"credit": ["521001", "534201"], "debit": ["521000"]},
            },
            "Eurobank": {
                "Visa": {"credit": ["416801", "451901"], "debit": ["416800"]},
                "Mastercard": {"credit": ["520401", "533301"], "debit": ["520401"]},
            },
        }
    },
    "IE": {
        "name": "🇮🇪 Ireland",
        "banks": {
            "AIB": {
                "Visa": {"credit": ["401801", "438801"], "debit": ["401800", "438800"]},
                "Mastercard": {"credit": ["515401", "530101"], "debit": ["515400"]},
            },
            "Bank of Ireland": {
                "Visa": {"credit": ["407101", "451601"], "debit": ["407100", "451600"]},
                "Mastercard": {"credit": ["517101", "531001"], "debit": ["517101"]},
            },
            "Ulster Bank": {
                "Visa": {"credit": ["447201", "463501"], "debit": ["447200"]},
                "Mastercard": {"credit": ["524201", "538101"], "debit": ["524201"]},
            },
            "N26 Ireland": {
                "Mastercard": {"credit": [], "debit": ["533303", "548103"]},
            },
        }
    },
    "RU": {
        "name": "🇷🇺 Russia",
        "banks": {
            "Sberbank": {
                "Visa": {"credit": ["427901", "452201"], "debit": ["427900", "452200"]},
                "Mastercard": {"credit": ["521101", "534901"], "debit": ["521100"]},
            },
            "VTB": {
                "Visa": {"credit": ["447301", "463601"], "debit": ["447300", "463600"]},
                "Mastercard": {"credit": ["524101", "538201"], "debit": ["524101"]},
            },
            "Alfa Bank RU": {
                "Visa": {"credit": ["401901", "438901"], "debit": ["401900"]},
                "Mastercard": {"credit": ["515501", "530201"], "debit": ["515500"]},
            },
            "Tinkoff": {
                "Visa": {"credit": ["437401", "462601"], "debit": ["437400", "462600"]},
                "Mastercard": {"credit": ["521201", "535001"], "debit": ["521200"]},
            },
            "Gazprombank": {
                "Visa": {"credit": ["416901", "452001"], "debit": ["416900"]},
                "Mastercard": {"credit": ["520501", "533401"], "debit": ["520501"]},
            },
        }
    },
    "UA": {
        "name": "🇺🇦 Ukraine",
        "banks": {
            "PrivatBank": {
                "Visa": {"credit": ["424201", "456301"], "debit": ["424200", "456300"]},
                "Mastercard": {"credit": ["521301", "534401"], "debit": ["521300"]},
            },
            "Monobank": {
                "Visa": {"credit": [], "debit": ["488461", "498625"]},
                "Mastercard": {"credit": [], "debit": ["531277", "548914"]},
            },
            "Oschadbank": {
                "Visa": {"credit": ["413701", "451901"], "debit": ["413700", "451900"]},
                "Mastercard": {"credit": ["519401", "532301"], "debit": ["519401"]},
            },
            "Raiffeisen UA": {
                "Visa": {"credit": ["444401", "463301"], "debit": ["444400"]},
                "Mastercard": {"credit": ["524501", "538801"], "debit": ["524501"]},
            },
        }
    },
    "CZ": {
        "name": "🇨🇿 Czech Republic",
        "banks": {
            "Česká spořitelna": {
                "Visa": {"credit": ["409101", "452301"], "debit": ["409100", "452300"]},
                "Mastercard": {"credit": ["517201", "530901"], "debit": ["517200"]},
            },
            "ČSOB": {
                "Visa": {"credit": ["410301", "451801"], "debit": ["410300"]},
                "Mastercard": {"credit": ["518201", "531501"], "debit": ["518200"]},
            },
            "Komerční banka": {
                "Visa": {"credit": ["422201", "456401"], "debit": ["422200"]},
                "Mastercard": {"credit": ["521401", "534801"], "debit": ["521400"]},
            },
            "Fio banka": {
                "Visa": {"credit": ["416201"], "debit": ["416200"]},
                "Mastercard": {"credit": ["519501"], "debit": ["519500"]},
            },
        }
    },
    "HU": {
        "name": "🇭🇺 Hungary",
        "banks": {
            "OTP Bank": {
                "Visa": {"credit": ["421801", "452401"], "debit": ["421800", "452400"]},
                "Mastercard": {"credit": ["521501", "534901"], "debit": ["521500"]},
            },
            "K&H Bank": {
                "Visa": {"credit": ["410401", "451901"], "debit": ["410400"]},
                "Mastercard": {"credit": ["518301", "531601"], "debit": ["518300"]},
            },
            "Raiffeisen HU": {
                "Visa": {"credit": ["444501", "463401"], "debit": ["444500"]},
                "Mastercard": {"credit": ["524601", "538901"], "debit": ["524601"]},
            },
        }
    },
    "RO": {
        "name": "🇷🇴 Romania",
        "banks": {
            "Banca Transilvania": {
                "Visa": {"credit": ["403301", "452501"], "debit": ["403300", "452500"]},
                "Mastercard": {"credit": ["516401", "531001"], "debit": ["516400"]},
            },
            "BCR": {
                "Visa": {"credit": ["407201", "451501"], "debit": ["407200", "451500"]},
                "Mastercard": {"credit": ["517301", "531101"], "debit": ["517300"]},
            },
            "BRD": {
                "Visa": {"credit": ["404701", "451601"], "debit": ["404700"]},
                "Mastercard": {"credit": ["517401", "531201"], "debit": ["517400"]},
            },
        }
    },
    "TR": {
        "name": "🇹🇷 Turkey",
        "banks": {
            "Garanti BBVA": {
                "Visa": {"credit": ["415022", "438821", "476401"], "debit": ["415020", "476400"]},
                "Mastercard": {"credit": ["531222", "540088", "549801"], "debit": ["531221"]},
            },
            "Akbank": {
                "Visa": {"credit": ["403340", "424200", "456401"], "debit": ["403341", "456400"]},
                "Mastercard": {"credit": ["519601", "530044", "545601"], "debit": ["519602"]},
            },
            "İş Bankası": {
                "Visa": {"credit": ["434101", "462601"], "debit": ["434100", "462600"]},
                "Mastercard": {"credit": ["521601", "535101"], "debit": ["521600"]},
            },
            "Yapı Kredi": {
                "Visa": {"credit": ["447401", "463701"], "debit": ["447400", "463700"]},
                "Mastercard": {"credit": ["524701", "539001"], "debit": ["524701"]},
            },
            "Ziraat Bankası": {
                "Visa": {"credit": ["448401", "463801"], "debit": ["448400", "463800"]},
                "Mastercard": {"credit": ["524801", "539101"], "debit": ["524801"]},
            },
            "Halkbank": {
                "Visa": {"credit": ["421901", "452601"], "debit": ["421900"]},
                "Mastercard": {"credit": ["521701", "535201"], "debit": ["521701"]},
            },
            "VakıfBank": {
                "Visa": {"credit": ["447501", "463901"], "debit": ["447500"]},
                "Mastercard": {"credit": ["524901", "539201"], "debit": ["524901"]},
            },
        }
    },
    # ═══════════════ ASIA ═══════════════
    "IN": {
        "name": "🇮🇳 India",
        "banks": {
            "SBI": {
                "Visa": {"credit": ["414906", "437748", "459108", "476501"], "debit": ["414900", "437740", "476500"]},
                "Mastercard": {"credit": ["523414", "536001", "548601"], "debit": ["523413"]},
                "Rupay": {"credit": ["607001", "607020", "607300"], "debit": ["607000", "607010", "607200"]},
            },
            "HDFC Bank": {
                "Visa": {"credit": ["439895", "456616", "461266", "476601"], "debit": ["439890", "456610", "476600"]},
                "Mastercard": {"credit": ["522888", "531556", "548701"], "debit": ["522881"]},
                "Rupay": {"credit": ["607400", "607500"], "debit": ["607401", "607501"]},
            },
            "ICICI Bank": {
                "Visa": {"credit": ["430000", "430001", "456017", "476701"], "debit": ["430000", "476700"]},
                "Mastercard": {"credit": ["512601", "527246", "548801"], "debit": ["512600"]},
                "Amex": {"credit": ["376201"], "debit": []},
                "Rupay": {"credit": ["607600", "607700"], "debit": ["607601", "607701"]},
            },
            "Axis Bank": {
                "Visa": {"credit": ["415359", "438857", "476801"], "debit": ["415350", "476800"]},
                "Mastercard": {"credit": ["519474", "530993", "548901"], "debit": ["519470"]},
                "Rupay": {"credit": ["607800", "607900"], "debit": ["607801", "607901"]},
            },
            "Kotak Mahindra": {
                "Visa": {"credit": ["422301", "456501"], "debit": ["422300"]},
                "Mastercard": {"credit": ["521801", "535501"], "debit": ["521800"]},
                "Rupay": {"credit": ["608001", "608101"], "debit": ["608002", "608102"]},
            },
            "Yes Bank": {
                "Visa": {"credit": ["448501", "463201"], "debit": ["448500"]},
                "Mastercard": {"credit": ["524901", "538001"], "debit": ["524901"]},
                "Rupay": {"credit": ["608201"], "debit": ["608202"]},
            },
            "IndusInd Bank": {
                "Visa": {"credit": ["434201", "462701"], "debit": ["434200"]},
                "Mastercard": {"credit": ["522001", "535601"], "debit": ["522000"]},
            },
            "RBL Bank": {
                "Visa": {"credit": ["427101", "456601"], "debit": ["427100"]},
                "Mastercard": {"credit": ["521901", "535701"], "debit": ["521901"]},
            },
            "Paytm Payments": {
                "Visa": {"credit": [], "debit": ["488462", "498626"]},
                "Mastercard": {"credit": [], "debit": ["531278", "548915"]},
                "Rupay": {"credit": [], "debit": ["608301", "608401"]},
            },
        }
    },
    "CN": {
        "name": "🇨🇳 China",
        "banks": {
            "ICBC": {
                "Visa": {"credit": ["424401", "456701"], "debit": ["424400", "456700"]},
                "Mastercard": {"credit": ["521901", "535001"], "debit": ["521901"]},
                "UnionPay": {"credit": ["621783", "625802", "627081"], "debit": ["621782", "625800", "627080"]},
            },
            "China Construction Bank": {
                "Visa": {"credit": ["404801", "451001"], "debit": ["404800", "451000"]},
                "Mastercard": {"credit": ["515601", "531101"], "debit": ["515600"]},
                "UnionPay": {"credit": ["621225", "625803", "627006"], "debit": ["621224", "625801", "627005"]},
            },
            "Agricultural Bank of China": {
                "Visa": {"credit": ["401001", "438901"], "debit": ["401000"]},
                "Mastercard": {"credit": ["514801", "530001"], "debit": ["514800"]},
                "UnionPay": {"credit": ["621668", "625804", "627200"], "debit": ["621667", "625802", "627201"]},
            },
            "Bank of China": {
                "Visa": {"credit": ["404901", "451201"], "debit": ["404900", "451200"]},
                "Mastercard": {"credit": ["515701", "531201"], "debit": ["515700"]},
                "UnionPay": {"credit": ["621785", "625805", "627060"], "debit": ["621784", "625803", "627061"]},
            },
            "Bank of Communications": {
                "Visa": {"credit": ["410501", "451301"], "debit": ["410500", "451300"]},
                "Mastercard": {"credit": ["517501", "531301"], "debit": ["517500"]},
                "UnionPay": {"credit": ["621002", "625806", "627026"], "debit": ["621001", "625804", "627025"]},
            },
            "China Merchants Bank": {
                "Visa": {"credit": ["409201", "451401"], "debit": ["409200"]},
                "Mastercard": {"credit": ["517601", "531401"], "debit": ["517600"]},
                "UnionPay": {"credit": ["621483", "625807"], "debit": ["621482", "625805"]},
            },
            "Postal Savings Bank": {
                "UnionPay": {"credit": ["621096", "625808"], "debit": ["621095", "625806"]},
            },
            "WeBank (WeChat Pay)": {
                "Visa": {"credit": [], "debit": ["488463", "498627"]},
                "UnionPay": {"credit": [], "debit": ["621900", "625809"]},
            },
        }
    },
    "JP": {
        "name": "🇯🇵 Japan",
        "banks": {
            "MUFG (Bank of Tokyo)": {
                "Visa": {"credit": ["417904", "441338", "476901"], "debit": ["417900", "476900"]},
                "JCB": {"credit": ["353011", "356600", "357811"], "debit": []},
                "Mastercard": {"credit": ["521001", "534001"], "debit": ["521000"]},
            },
            "SMBC": {
                "Visa": {"credit": ["418012", "438421", "477001"], "debit": ["418010", "477000"]},
                "Mastercard": {"credit": ["528421", "537001", "549101"], "debit": ["528420"]},
                "JCB": {"credit": ["353501", "356700"], "debit": []},
            },
            "Mizuho Bank": {
                "Visa": {"credit": ["412401", "451101"], "debit": ["412400", "451100"]},
                "Mastercard": {"credit": ["520101", "534201"], "debit": ["520100"]},
                "JCB": {"credit": ["354001", "356800"], "debit": []},
            },
            "Rakuten Bank": {
                "Visa": {"credit": ["417528", "451201"], "debit": ["417527", "451200"]},
                "JCB": {"credit": ["357900", "356900"], "debit": []},
                "Mastercard": {"credit": ["520201", "534301"], "debit": []},
            },
            "Sony Bank": {
                "Visa": {"credit": ["427201", "456901"], "debit": ["427200"]},
                "Mastercard": {"credit": ["521101", "535001"], "debit": ["521100"]},
            },
            "PayPay Bank": {
                "Visa": {"credit": [], "debit": ["488464", "498628"]},
                "JCB": {"credit": [], "debit": ["354501"]},
            },
            "Aeon Bank": {
                "Visa": {"credit": ["401101", "438001"], "debit": ["401100"]},
                "JCB": {"credit": ["354101"], "debit": []},
            },
            "Seven Bank": {
                "Visa": {"credit": [], "debit": ["447001", "463101"]},
                "Mastercard": {"credit": [], "debit": ["523801"]},
            },
        }
    },
    "KR": {
        "name": "🇰🇷 South Korea",
        "banks": {
            "KB Kookmin": {
                "Visa": {"credit": ["413002", "438510", "476401"], "debit": ["413000", "476400"]},
                "Mastercard": {"credit": ["523892", "536402", "548401"], "debit": ["523890"]},
            },
            "Shinhan Bank": {
                "Visa": {"credit": ["421001", "452901"], "debit": ["421000", "452900"]},
                "Mastercard": {"credit": ["521201", "534501"], "debit": ["521200"]},
            },
            "Woori Bank": {
                "Visa": {"credit": ["447801", "463901"], "debit": ["447800"]},
                "Mastercard": {"credit": ["524801", "539001"], "debit": ["524801"]},
            },
            "KEB Hana Bank": {
                "Visa": {"credit": ["422401", "456901"], "debit": ["422400"]},
                "Mastercard": {"credit": ["521301", "534601"], "debit": ["521300"]},
            },
            "NH NongHyup": {
                "Visa": {"credit": ["413301", "451401"], "debit": ["413300", "451400"]},
                "Mastercard": {"credit": ["519701", "532901"], "debit": ["519700"]},
            },
            "Kakao Bank": {
                "Visa": {"credit": [], "debit": ["461212", "461213", "498629"]},
                "Mastercard": {"credit": [], "debit": ["533080", "548916"]},
            },
            "Toss Bank": {
                "Visa": {"credit": [], "debit": ["488465", "498630"]},
                "Mastercard": {"credit": [], "debit": ["531279", "548917"]},
            },
        }
    },
    "SG": {
        "name": "🇸🇬 Singapore",
        "banks": {
            "DBS Bank": {
                "Visa": {"credit": ["411690", "457861", "476501"], "debit": ["411691", "476500"]},
                "Mastercard": {"credit": ["520888", "539001", "549201"], "debit": ["520889"]},
            },
            "OCBC": {
                "Visa": {"credit": ["404784", "438090", "476601"], "debit": ["404780", "476600"]},
                "Mastercard": {"credit": ["524532", "531600", "549301"], "debit": ["524531"]},
            },
            "UOB Singapore": {
                "Visa": {"credit": ["447901", "464001"], "debit": ["447900", "464000"]},
                "Mastercard": {"credit": ["524901", "539101"], "debit": ["524901"]},
            },
            "Standard Chartered SG": {
                "Visa": {"credit": ["427301", "456901"], "debit": ["427300"]},
                "Mastercard": {"credit": ["521401", "534701"], "debit": ["521400"]},
            },
            "HSBC Singapore": {
                "Visa": {"credit": ["454314", "476701"], "debit": ["454310", "476700"]},
                "Mastercard": {"credit": ["540405", "549401"], "debit": ["540401"]},
            },
            "Revolut SG": {
                "Visa": {"credit": [], "debit": ["488466", "498631"]},
                "Mastercard": {"credit": [], "debit": ["531280", "548918"]},
            },
        }
    },
    "HK": {
        "name": "🇭🇰 Hong Kong",
        "banks": {
            "HSBC Hong Kong": {
                "Visa": {"credit": ["454315", "476801"], "debit": ["454311", "476800"]},
                "Mastercard": {"credit": ["540406", "549402"], "debit": ["540402"]},
            },
            "Hang Seng": {
                "Visa": {"credit": ["426101", "456801"], "debit": ["426100"]},
                "Mastercard": {"credit": ["521601", "534901"], "debit": ["521600"]},
            },
            "Bank of China HK": {
                "Visa": {"credit": ["404901", "451301"], "debit": ["404901", "451300"]},
                "UnionPay": {"credit": ["621786", "625810"], "debit": ["621785", "625808"]},
                "Mastercard": {"credit": ["515801", "531501"], "debit": ["515800"]},
            },
            "Standard Chartered HK": {
                "Visa": {"credit": ["427401", "457001"], "debit": ["427400"]},
                "Mastercard": {"credit": ["521501", "534801"], "debit": ["521500"]},
            },
            "ZA Bank": {
                "Visa": {"credit": [], "debit": ["488467", "498632"]},
                "Mastercard": {"credit": [], "debit": ["531281", "548919"]},
            },
        }
    },
    "TW": {
        "name": "🇹🇼 Taiwan",
        "banks": {
            "Cathay United": {
                "Visa": {"credit": ["408401", "452001"], "debit": ["408400", "452000"]},
                "Mastercard": {"credit": ["517001", "530901"], "debit": ["517000"]},
            },
            "CTBC Bank": {
                "Visa": {"credit": ["417201", "451601"], "debit": ["417200"]},
                "Mastercard": {"credit": ["519001", "532101"], "debit": ["519000"]},
            },
            "Fubon Bank": {
                "Visa": {"credit": ["416201", "451701"], "debit": ["416200"]},
                "Mastercard": {"credit": ["519101", "532201"], "debit": ["519100"]},
            },
            "E.SUN Bank": {
                "Visa": {"credit": ["410601", "451801"], "debit": ["410600"]},
                "Mastercard": {"credit": ["518701", "531801"], "debit": ["518700"]},
            },
        }
    },
    "MY": {
        "name": "🇲🇾 Malaysia",
        "banks": {
            "Maybank": {
                "Visa": {"credit": ["412501", "452101"], "debit": ["412500", "452100"]},
                "Mastercard": {"credit": ["520001", "533301"], "debit": ["520001"]},
            },
            "CIMB Bank": {
                "Visa": {"credit": ["408701", "451901"], "debit": ["408700"]},
                "Mastercard": {"credit": ["517101", "531901"], "debit": ["517100"]},
            },
            "Public Bank": {
                "Visa": {"credit": ["424901", "456801"], "debit": ["424900"]},
                "Mastercard": {"credit": ["521701", "535001"], "debit": ["521700"]},
            },
            "RHB Bank": {
                "Visa": {"credit": ["426301", "456901"], "debit": ["426300"]},
                "Mastercard": {"credit": ["521801", "535101"], "debit": ["521800"]},
            },
            "Hong Leong Bank": {
                "Visa": {"credit": ["425901", "456001"], "debit": ["425900"]},
                "Mastercard": {"credit": ["521901", "535201"], "debit": ["521901"]},
            },
        }
    },
    "TH": {
        "name": "🇹🇭 Thailand",
        "banks": {
            "Bangkok Bank": {
                "Visa": {"credit": ["403401", "452201"], "debit": ["403400", "452200"]},
                "Mastercard": {"credit": ["516501", "531001"], "debit": ["516500"]},
            },
            "Kasikorn Bank (KBank)": {
                "Visa": {"credit": ["421101", "452301"], "debit": ["421100", "452300"]},
                "Mastercard": {"credit": ["520101", "533401"], "debit": ["520101"]},
            },
            "Krungthai Bank": {
                "Visa": {"credit": ["422501", "456501"], "debit": ["422500"]},
                "Mastercard": {"credit": ["521001", "534401"], "debit": ["521000"]},
            },
            "SCB": {
                "Visa": {"credit": ["427601", "457101"], "debit": ["427600"]},
                "Mastercard": {"credit": ["521501", "534901"], "debit": ["521500"]},
            },
        }
    },
    "ID": {
        "name": "🇮🇩 Indonesia",
        "banks": {
            "Bank Mandiri": {
                "Visa": {"credit": ["412601", "452401"], "debit": ["412600", "452400"]},
                "Mastercard": {"credit": ["520201", "533501"], "debit": ["520200"]},
            },
            "BCA": {
                "Visa": {"credit": ["403501", "452501"], "debit": ["403500", "452500"]},
                "Mastercard": {"credit": ["516601", "531101"], "debit": ["516600"]},
            },
            "BNI": {
                "Visa": {"credit": ["404101", "452601"], "debit": ["404100"]},
                "Mastercard": {"credit": ["516701", "531201"], "debit": ["516700"]},
            },
            "BRI": {
                "Visa": {"credit": ["404201", "452701"], "debit": ["404200"]},
                "Mastercard": {"credit": ["516801", "531301"], "debit": ["516800"]},
            },
            "GoPay (Jago)": {
                "Visa": {"credit": [], "debit": ["488468", "498633"]},
                "Mastercard": {"credit": [], "debit": ["531282", "548920"]},
            },
        }
    },
    "PH": {
        "name": "🇵🇭 Philippines",
        "banks": {
            "BDO Unibank": {
                "Visa": {"credit": ["403601", "452801"], "debit": ["403600", "452800"]},
                "Mastercard": {"credit": ["516901", "531401"], "debit": ["516900"]},
            },
            "BPI": {
                "Visa": {"credit": ["404301", "452901"], "debit": ["404300", "452900"]},
                "Mastercard": {"credit": ["517001", "531501"], "debit": ["517000"]},
            },
            "Metrobank": {
                "Visa": {"credit": ["412701", "452901"], "debit": ["412700"]},
                "Mastercard": {"credit": ["520301", "533601"], "debit": ["520300"]},
            },
            "GCash (Mynt)": {
                "Visa": {"credit": [], "debit": ["488469", "498634"]},
                "Mastercard": {"credit": [], "debit": ["531283", "548921"]},
            },
        }
    },
    "VN": {
        "name": "🇻🇳 Vietnam",
        "banks": {
            "Vietcombank": {
                "Visa": {"credit": ["447101", "463501"], "debit": ["447100", "463500"]},
                "Mastercard": {"credit": ["524201", "538301"], "debit": ["524201"]},
            },
            "VietinBank": {
                "Visa": {"credit": ["412801", "453001"], "debit": ["412800"]},
                "Mastercard": {"credit": ["520401", "533701"], "debit": ["520400"]},
            },
            "Techcombank": {
                "Visa": {"credit": ["437301", "462501"], "debit": ["437300"]},
                "Mastercard": {"credit": ["521001", "534501"], "debit": ["521000"]},
            },
            "MoMo": {
                "Mastercard": {"credit": [], "debit": ["531284", "548922"]},
            },
        }
    },
    "PK": {
        "name": "🇵🇰 Pakistan",
        "banks": {
            "HBL": {
                "Visa": {"credit": ["425301", "457101"], "debit": ["425300", "457100"]},
                "Mastercard": {"credit": ["521101", "534601"], "debit": ["521100"]},
            },
            "MCB Bank": {
                "Visa": {"credit": ["412901", "453101"], "debit": ["412900"]},
                "Mastercard": {"credit": ["520501", "533801"], "debit": ["520500"]},
            },
            "UBL": {
                "Visa": {"credit": ["447201", "463601"], "debit": ["447200"]},
                "Mastercard": {"credit": ["524301", "538401"], "debit": ["524301"]},
            },
        }
    },
    "BD": {
        "name": "🇧🇩 Bangladesh",
        "banks": {
            "Dutch-Bangla Bank": {
                "Visa": {"credit": ["410701", "453201"], "debit": ["410700", "453200"]},
                "Mastercard": {"credit": ["518001", "532001"], "debit": ["518000"]},
            },
            "BRAC Bank": {
                "Visa": {"credit": ["404401", "451001"], "debit": ["404400"]},
                "Mastercard": {"credit": ["516001", "530001"], "debit": ["516000"]},
            },
            "bKash": {
                "Mastercard": {"credit": [], "debit": ["531285", "548923"]},
            },
        }
    },
    "KZ": {
        "name": "🇰🇿 Kazakhstan",
        "banks": {
            "Kaspi Bank": {
                "Visa": {"credit": ["421201", "452401"], "debit": ["421200", "452400"]},
                "Mastercard": {"credit": ["521201", "534501"], "debit": ["521200"]},
            },
            "Halyk Bank": {
                "Visa": {"credit": ["416001", "451401"], "debit": ["416000", "451400"]},
                "Mastercard": {"credit": ["519801", "533201"], "debit": ["519800"]},
            },
            "Jusan Bank": {
                "Visa": {"credit": ["422601", "456601"], "debit": ["422600"]},
                "Mastercard": {"credit": ["521301", "534701"], "debit": ["521300"]},
            },
        }
    },
    # ═══════════════ MIDDLE EAST ═══════════════
    "AE": {
        "name": "🇦🇪 UAE",
        "banks": {
            "Emirates NBD": {
                "Visa": {"credit": ["403040", "435617", "476201"], "debit": ["403041", "476200"]},
                "Mastercard": {"credit": ["521730", "532891", "548201"], "debit": ["521731"]},
            },
            "Abu Dhabi Commercial Bank": {
                "Visa": {"credit": ["414456", "427812", "476301"], "debit": ["414457", "476300"]},
                "Mastercard": {"credit": ["533720", "545201"], "debit": ["533721"]},
            },
            "First Abu Dhabi Bank": {
                "Visa": {"credit": ["416101", "451301"], "debit": ["416100"]},
                "Mastercard": {"credit": ["519301", "533001"], "debit": ["519300"]},
            },
            "Mashreq Bank": {
                "Visa": {"credit": ["412201", "451401"], "debit": ["412200"]},
                "Mastercard": {"credit": ["519401", "533101"], "debit": ["519400"]},
            },
            "ENBD (Dubai Islamic)": {
                "Visa": {"credit": ["421301", "451501"], "debit": ["421300"]},
                "Mastercard": {"credit": ["519501", "533201"], "debit": ["519500"]},
            },
            "Liv. (Emirates NBD digital)": {
                "Mastercard": {"credit": [], "debit": ["531286", "548924"]},
                "Visa": {"credit": [], "debit": ["488470", "498635"]},
            },
        }
    },
    "SA": {
        "name": "🇸🇦 Saudi Arabia",
        "banks": {
            "Al Rajhi Bank": {
                "Visa": {"credit": ["412450", "443012", "476401"], "debit": ["412451", "476400"]},
                "Mastercard": {"credit": ["524190", "533680", "548301"], "debit": ["524191"]},
            },
            "NCB (Al Ahli)": {
                "Visa": {"credit": ["413800", "426311", "476501"], "debit": ["413801", "476500"]},
                "Mastercard": {"credit": ["519820", "530201", "548401"], "debit": ["519821"]},
            },
            "Riyad Bank": {
                "Visa": {"credit": ["427001", "456401"], "debit": ["427000"]},
                "Mastercard": {"credit": ["521501", "534901"], "debit": ["521500"]},
            },
            "SABB (HSBC SA)": {
                "Visa": {"credit": ["454401", "476601"], "debit": ["454400", "476600"]},
                "Mastercard": {"credit": ["540501", "549501"], "debit": ["540500"]},
            },
            "Alinma Bank": {
                "Visa": {"credit": ["401201", "438101"], "debit": ["401200"]},
                "Mastercard": {"credit": ["515001", "530001"], "debit": ["515000"]},
            },
            "STC Pay": {
                "Visa": {"credit": [], "debit": ["488471", "498636"]},
                "Mastercard": {"credit": [], "debit": ["531287", "548925"]},
            },
        }
    },
    "IL": {
        "name": "🇮🇱 Israel",
        "banks": {
            "Bank Hapoalim": {
                "Visa": {"credit": ["425401", "457201"], "debit": ["425400", "457200"]},
                "Mastercard": {"credit": ["521401", "534801"], "debit": ["521400"]},
            },
            "Bank Leumi": {
                "Visa": {"credit": ["413001", "451001"], "debit": ["413000", "451000"]},
                "Mastercard": {"credit": ["519001", "532001"], "debit": ["519000"]},
            },
            "Discount Bank": {
                "Visa": {"credit": ["410801", "453301"], "debit": ["410800"]},
                "Mastercard": {"credit": ["518101", "532101"], "debit": ["518100"]},
            },
            "Bit (Bank Hapoalim digital)": {
                "Mastercard": {"credit": [], "debit": ["531288", "548926"]},
            },
        }
    },
    "EG": {
        "name": "🇪🇬 Egypt",
        "banks": {
            "CIB Egypt": {
                "Visa": {"credit": ["408801", "452201"], "debit": ["408800", "452200"]},
                "Mastercard": {"credit": ["517201", "532101"], "debit": ["517200"]},
            },
            "Banque Misr": {
                "Visa": {"credit": ["403701", "451901"], "debit": ["403700"]},
                "Mastercard": {"credit": ["516201", "531001"], "debit": ["516200"]},
            },
            "National Bank of Egypt": {
                "Visa": {"credit": ["413801", "452001"], "debit": ["413800"]},
                "Mastercard": {"credit": ["519801", "532901"], "debit": ["519800"]},
            },
        }
    },
    "KW": {
        "name": "🇰🇼 Kuwait",
        "banks": {
            "NBK": {
                "Visa": {"credit": ["413901", "452101"], "debit": ["413900"]},
                "Mastercard": {"credit": ["519901", "533001"], "debit": ["519900"]},
            },
            "Kuwait Finance House": {
                "Visa": {"credit": ["422701", "456701"], "debit": ["422700"]},
                "Mastercard": {"credit": ["521401", "534901"], "debit": ["521400"]},
            },
        }
    },
    "QA": {
        "name": "🇶🇦 Qatar",
        "banks": {
            "QNB": {
                "Visa": {"credit": ["424301", "456801"], "debit": ["424300"]},
                "Mastercard": {"credit": ["521501", "535001"], "debit": ["521500"]},
            },
            "Commercial Bank Qatar": {
                "Visa": {"credit": ["408901", "452301"], "debit": ["408900"]},
                "Mastercard": {"credit": ["517301", "532201"], "debit": ["517300"]},
            },
        }
    },
    "JO": {
        "name": "🇯🇴 Jordan",
        "banks": {
            "Arab Bank": {
                "Visa": {"credit": ["401301", "438201"], "debit": ["401300"]},
                "Mastercard": {"credit": ["515101", "530101"], "debit": ["515100"]},
            },
            "Bank of Jordan": {
                "Visa": {"credit": ["407301", "451601"], "debit": ["407300"]},
                "Mastercard": {"credit": ["517401", "532301"], "debit": ["517400"]},
            },
        }
    },
    # ═══════════════ AFRICA ═══════════════
    "ZA": {
        "name": "🇿🇦 South Africa",
        "banks": {
            "Standard Bank SA": {
                "Visa": {"credit": ["428012", "451603", "476201"], "debit": ["428010", "476200"]},
                "Mastercard": {"credit": ["523012", "537802", "548501"], "debit": ["523011"]},
            },
            "FNB": {
                "Visa": {"credit": ["414218", "438002", "476301"], "debit": ["414210", "476300"]},
                "Mastercard": {"credit": ["521301", "530812", "548601"], "debit": ["521300"]},
            },
            "ABSA": {
                "Visa": {"credit": ["401401", "438301", "476401"], "debit": ["401400", "476400"]},
                "Mastercard": {"credit": ["515201", "531001"], "debit": ["515200"]},
            },
            "Nedbank": {
                "Visa": {"credit": ["413201", "451101"], "debit": ["413200", "451100"]},
                "Mastercard": {"credit": ["519201", "532101"], "debit": ["519200"]},
            },
            "Capitec": {
                "Mastercard": {"credit": [], "debit": ["531289", "548927"]},
                "Visa": {"credit": [], "debit": ["488472", "498637"]},
            },
            "Investec": {
                "Visa": {"credit": ["434301", "463001"], "debit": ["434300"]},
                "Mastercard": {"credit": ["522101", "535301"], "debit": ["522100"]},
            },
        }
    },
    "NG": {
        "name": "🇳🇬 Nigeria",
        "banks": {
            "Access Bank": {
                "Visa": {"credit": ["401501", "438401"], "debit": ["401500", "438400"]},
                "Mastercard": {"credit": ["515301", "530201"], "debit": ["515300"]},
            },
            "GTBank": {
                "Visa": {"credit": ["408101", "452401"], "debit": ["408100", "452400"]},
                "Mastercard": {"credit": ["517501", "532401"], "debit": ["517500"]},
            },
            "Zenith Bank": {
                "Visa": {"credit": ["448601", "463101"], "debit": ["448600"]},
                "Mastercard": {"credit": ["524901", "539201"], "debit": ["524901"]},
            },
            "First Bank NG": {
                "Visa": {"credit": ["416301", "451301"], "debit": ["416300"]},
                "Mastercard": {"credit": ["519301", "532501"], "debit": ["519300"]},
            },
            "Opay": {
                "Mastercard": {"credit": [], "debit": ["531290", "548928"]},
            },
        }
    },
    "KE": {
        "name": "🇰🇪 Kenya",
        "banks": {
            "KCB": {
                "Visa": {"credit": ["421501", "452501"], "debit": ["421500", "452500"]},
                "Mastercard": {"credit": ["521601", "535101"], "debit": ["521600"]},
            },
            "Equity Bank": {
                "Visa": {"credit": ["409301", "452601"], "debit": ["409300"]},
                "Mastercard": {"credit": ["517601", "532601"], "debit": ["517600"]},
            },
            "M-PESA (Safaricom)": {
                "Mastercard": {"credit": [], "debit": ["531291", "548929"]},
                "Visa": {"credit": [], "debit": ["488473", "498638"]},
            },
            "Cooperative Bank": {
                "Visa": {"credit": ["409401", "452701"], "debit": ["409400"]},
                "Mastercard": {"credit": ["517701", "532701"], "debit": ["517700"]},
            },
        }
    },
    "GH": {
        "name": "🇬🇭 Ghana",
        "banks": {
            "GCB Bank": {
                "Visa": {"credit": ["417301", "452801"], "debit": ["417300"]},
                "Mastercard": {"credit": ["519401", "532801"], "debit": ["519400"]},
            },
            "Ecobank Ghana": {
                "Visa": {"credit": ["409501", "452901"], "debit": ["409500"]},
                "Mastercard": {"credit": ["517801", "532901"], "debit": ["517800"]},
            },
            "MTN Mobile Money": {
                "Mastercard": {"credit": [], "debit": ["531292", "548930"]},
            },
        }
    },
    "MA": {
        "name": "🇲🇦 Morocco",
        "banks": {
            "Attijariwafa Bank": {
                "Visa": {"credit": ["403801", "452001"], "debit": ["403800"]},
                "Mastercard": {"credit": ["515901", "530801"], "debit": ["515900"]},
            },
            "BMCE Bank": {
                "Visa": {"credit": ["407401", "451801"], "debit": ["407400"]},
                "Mastercard": {"credit": ["517001", "531801"], "debit": ["517000"]},
            },
            "CIH Bank": {
                "Visa": {"credit": ["409601", "453001"], "debit": ["409600"]},
                "Mastercard": {"credit": ["517901", "533001"], "debit": ["517900"]},
            },
        }
    },
    "TZ": {
        "name": "🇹🇿 Tanzania",
        "banks": {
            "CRDB Bank": {
                "Visa": {"credit": ["409701", "453101"], "debit": ["409700"]},
                "Mastercard": {"credit": ["518001", "533101"], "debit": ["518000"]},
            },
            "NMB Bank": {
                "Visa": {"credit": ["413501", "451801"], "debit": ["413500"]},
                "Mastercard": {"credit": ["519501", "533201"], "debit": ["519500"]},
            },
        }
    },
    "ET": {
        "name": "🇪🇹 Ethiopia",
        "banks": {
            "Commercial Bank of Ethiopia": {
                "Visa": {"credit": ["409801", "453201"], "debit": ["409800"]},
                "Mastercard": {"credit": ["518101", "533301"], "debit": ["518100"]},
            },
            "Dashen Bank": {
                "Visa": {"credit": ["410901", "453301"], "debit": ["410900"]},
                "Mastercard": {"credit": ["518201", "533401"], "debit": ["518200"]},
            },
        }
    },
    # ═══════════════ OCEANIA ═══════════════
    "AU": {
        "name": "🇦🇺 Australia",
        "banks": {
            "Commonwealth Bank": {
                "Visa": {"credit": ["459012", "462756", "482634", "476101"], "debit": ["459000", "462760", "476100"]},
                "Mastercard": {"credit": ["528102", "539421", "549001"], "debit": ["528101"]},
            },
            "ANZ": {
                "Visa": {"credit": ["403123", "413745", "476201"], "debit": ["403120", "476200"]},
                "Mastercard": {"credit": ["515078", "521022", "549101"], "debit": ["515079"]},
            },
            "Westpac": {
                "Visa": {"credit": ["437962", "455683", "476301"], "debit": ["437960", "476300"]},
                "Mastercard": {"credit": ["512878", "527834", "549201"], "debit": ["512879"]},
            },
            "NAB": {
                "Visa": {"credit": ["413201", "452201"], "debit": ["413200", "452200"]},
                "Mastercard": {"credit": ["520101", "534001"], "debit": ["520100"]},
            },
            "Macquarie Bank": {
                "Visa": {"credit": ["412301", "452301"], "debit": ["412300"]},
                "Mastercard": {"credit": ["520201", "534101"], "debit": ["520200"]},
            },
            "Up Bank": {
                "Visa": {"credit": [], "debit": ["488474", "498639"]},
            },
            "ING Australia": {
                "Visa": {"credit": ["432927", "471153"], "debit": ["432924", "471144"]},
                "Mastercard": {"credit": ["531026", "540304"], "debit": ["531025"]},
            },
            "Bendigo Bank": {
                "Visa": {"credit": ["403401", "451001"], "debit": ["403400", "451000"]},
                "Mastercard": {"credit": ["516101", "531501"], "debit": ["516100"]},
            },
        }
    },
    "NZ": {
        "name": "🇳🇿 New Zealand",
        "banks": {
            "ANZ NZ": {
                "Visa": {"credit": ["403201", "452401"], "debit": ["403200", "452400"]},
                "Mastercard": {"credit": ["515201", "530301"], "debit": ["515200"]},
            },
            "BNZ": {
                "Visa": {"credit": ["407501", "452501"], "debit": ["407500", "452500"]},
                "Mastercard": {"credit": ["517301", "531401"], "debit": ["517300"]},
            },
            "ASB Bank": {
                "Visa": {"credit": ["401601", "438501"], "debit": ["401600"]},
                "Mastercard": {"credit": ["515401", "530401"], "debit": ["515400"]},
            },
            "Westpac NZ": {
                "Visa": {"credit": ["437963", "455684"], "debit": ["437961", "455683"]},
                "Mastercard": {"credit": ["512879", "527835"], "debit": ["512880"]},
            },
            "Kiwibank": {
                "Visa": {"credit": ["421801", "452601"], "debit": ["421800"]},
                "Mastercard": {"credit": ["521201", "534401"], "debit": ["521200"]},
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
    for _ in range(20):
        padding_length = length - len(bin_prefix) - 1
        middle = "".join(str(random.randint(0, 9)) for _ in range(padding_length))
        partial = bin_prefix + middle
        result = luhn_complete(partial)
        if result:
            return result
    return bin_prefix + "0" * (length - len(bin_prefix))


def generate_expiry() -> tuple:
    month = random.randint(1, 12)
    year = random.randint(2026, 2030)
    return (f"{month:02d}", f"{year % 100:02d}")


def generate_cvv(network: str) -> str:
    length = 4 if network == "Amex" else 3
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def _find_bin(country_code: str, bank: Optional[str], network: Optional[str], card_type: str) -> Optional[tuple]:
    country_data = BINS_DB.get(country_code)
    if not country_data:
        return None
    banks = country_data["banks"]
    candidate_banks = {bank: banks[bank]} if (bank and bank in banks) else banks
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
    return random.choice(candidates) if candidates else None


def generate_cards(
    countries: list,
    banks: Optional[list],
    networks: Optional[list],
    card_type: str,
    count: int
) -> list:
    cards = []
    attempts = 0
    max_attempts = count * 30

    while len(cards) < count and attempts < max_attempts:
        attempts += 1
        country_code = random.choice(countries)
        bank = random.choice(banks) if banks else None
        network = random.choice(networks) if networks else None

        result = _find_bin(country_code, bank, network, card_type)
        if not result:
            result = _find_bin(country_code, None, network, card_type)
        if not result:
            result = _find_bin(country_code, None, None, card_type)
        if not result:
            result = _find_bin(country_code, None, None, "credit")
        if not result:
            continue

        bname, net, bin_prefix = result
        length = NETWORK_LENGTHS.get(net, 16)
        number = generate_card_number(bin_prefix, length)
        month, year = generate_expiry()
        cvv = generate_cvv(net)

        cards.append({
            "number": number,
            "month": month,
            "year": year,
            "cvv": cvv,
            "network": net,
            "bank": bname,
            "country": BINS_DB[country_code]["name"],
            "type": card_type,
        })

    return cards


def format_card(card: dict) -> str:
    return f"{card['number']}|{card['month']}|{card['year']}|{card['cvv']}"


def format_card_inline(card: dict) -> str:
    return f"`{card['number']}|{card['month']}|{card['year']}|{card['cvv']}`"


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


def generate_cards_with_custom(
    countries: list,
    banks: Optional[list],
    networks: Optional[list],
    card_type: str,
    count: int,
    custom_bins_list: Optional[list] = None
) -> list:
    """Generate cards including custom BINs from the database."""
    cards = []

    # Build custom BIN candidates filtered by countries/networks/type
    custom_candidates = []
    if custom_bins_list:
        for cb in custom_bins_list:
            if countries and cb["country_code"] not in countries:
                continue
            if networks and cb["network"] not in networks:
                continue
            ct = cb.get("card_type", "credit")
            if card_type != "both" and ct != "both" and ct != card_type:
                continue
            custom_candidates.append(cb)

    # Merge pool: 30% chance to pick custom BIN if available
    attempts = 0
    max_attempts = count * 30

    while len(cards) < count and attempts < max_attempts:
        attempts += 1

        use_custom = custom_candidates and random.random() < 0.3

        if use_custom:
            cb = random.choice(custom_candidates)
            bin_prefix = cb["bin"]
            net = cb["network"]
            bname = cb["bank_name"]
            country_name = cb["country_name"]
        else:
            country_code = random.choice(countries)
            bank = random.choice(banks) if banks else None
            network = random.choice(networks) if networks else None

            result = _find_bin(country_code, bank, network, card_type)
            if not result:
                result = _find_bin(country_code, None, network, card_type)
            if not result:
                result = _find_bin(country_code, None, None, card_type)
            if not result:
                result = _find_bin(country_code, None, None, "credit")
            if not result:
                continue

            bname, net, bin_prefix = result
            country_name = BINS_DB[country_code]["name"]

        length = NETWORK_LENGTHS.get(net, 16)
        number = generate_card_number(bin_prefix, length)
        month, year = generate_expiry()
        cvv = generate_cvv(net)

        cards.append({
            "number": number,
            "month": month,
            "year": year,
            "cvv": cvv,
            "network": net,
            "bank": bname,
            "country": country_name,
            "type": card_type,
        })

    return cards
