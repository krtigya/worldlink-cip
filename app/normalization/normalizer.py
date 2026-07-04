"""
Converts raw scraped strings into clean, typed, structured plan data.
Speed → Mbps int. Price → NPR float. Bundles → typed list.
"""
import re
from dataclasses import dataclass, field
from typing import Optional
from app.logger import get_logger

logger = get_logger(__name__)



SPEED_PATTERNS = [
    (re.compile(r"(\d+(?:\.\d+)?)\s*gbps?", re.I), lambda m: int(float(m.group(1)) * 1000)),
    (re.compile(r"(\d+(?:\.\d+)?)\s*mbps?", re.I), lambda m: int(float(m.group(1)))),
    (re.compile(r"(\d+(?:\.\d+)?)\s*kbps?", re.I), lambda m: max(1, int(float(m.group(1)) / 1000))),
    (re.compile(r"upto?\s*(\d+)\s*mbps?", re.I),    lambda m: int(m.group(1))),
    (re.compile(r"(\d+)\s*g\b", re.I),               lambda m: int(m.group(1)) * 1000),
    (re.compile(r"(\d+)\s*m\b", re.I),               lambda m: int(m.group(1))),
]

def normalize_speed(raw: str) -> tuple[int, Optional[int]]:
    """Returns (download_mbps, upload_mbps). upload_mbps may be None."""
    cleaned = raw.strip().replace(",", "")

    
    split_match = re.match(r"^(\d+)/(\d+)\s*(?:mbps?)?$", cleaned, re.I)
    if split_match:
        return int(split_match.group(1)), int(split_match.group(2))

    for pattern, converter in SPEED_PATTERNS:
        m = pattern.search(cleaned)
        if m:
            return converter(m), None

    
    num = re.search(r"(\d+)", cleaned)
    if num:
        n = int(num.group(1))
        return (n * 1000 if n < 10 else n), None

    raise ValueError(f"Cannot parse speed: {raw!r}")




def normalize_price(raw: str) -> float:
    """Extract NPR float from any price string."""
    cleaned = re.sub(r"rs\.?|npr\.?|रु\.?|₨", "", raw, flags=re.I)
    cleaned = cleaned.replace(",", "").strip().lower()

    # "799/mo" or "799 per month"
    mo = re.search(r"(\d+(?:\.\d+)?)\s*(?:/mo|per\s*month|monthly)", cleaned, re.I)
    if mo:
        return float(mo.group(1))

    num = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    if not num:
        raise ValueError(f"Cannot parse price: {raw!r}")
    return float(num.group(1))




BUNDLE_RULES = [
    {
        "flags": ["iptv"],
        "pattern": re.compile(r"iptv|ip\s*tv|live\s*tv|digital\s*tv|cable\s*tv|television", re.I),
        "type": "iptv", "canonical": "IPTV",
    },
    {
        "flags": ["ott"],
        "pattern": re.compile(r"netflix|youtube\s*premium|amazon\s*prime|disney\+?|hotstar|hbo|zee5", re.I),
        "type": "ott", "canonical": "OTT Streaming",
    },
    {
        "flags": ["router"],
        "pattern": re.compile(r"free\s*router|router\s*included|wi-?fi\s*router|modem", re.I),
        "type": "router", "canonical": "Free Router",
    },
    {
        "flags": ["phone"],
        "pattern": re.compile(r"landline|telephone|free\s*calls?|voip|unlimited\s*calls?", re.I),
        "type": "phone", "canonical": "Landline",
    },
    {
        "flags": ["antivirus"],
        "pattern": re.compile(r"antivirus|kaspersky|norton|mcafee|security\s*suite", re.I),
        "type": "antivirus", "canonical": "Antivirus",
    },
]

def normalize_bundles(raw_bundles: list[str]) -> tuple[list[dict], list[str]]:
    """Returns (bundles, bundle_flags)."""
    all_text = " | ".join(raw_bundles)
    bundles, flags = [], set()

    for rule in BUNDLE_RULES:
        if rule["pattern"].search(all_text):
            match_text = next(
                (b for b in raw_bundles if rule["pattern"].search(b)),
                rule["canonical"]
            )
            bundles.append({"type": rule["type"], "name": match_text.strip()})
            flags.update(rule["flags"])

    return bundles, sorted(flags)




def detect_fup(raw_bundles: list[str], description: str = "") -> tuple[Optional[int], bool]:
    """Returns (fup_gb, is_unlimited)."""
    text = " ".join(raw_bundles + [description]).lower()

    if re.search(r"unlimited|no\s*fup|no\s*data\s*cap|uncapped", text, re.I):
        return None, True

    m = (re.search(r"(\d+)\s*(?:gb|gigabyte)?\s*(?:fup|data\s*limit|data\s*cap)", text, re.I)
         or re.search(r"fup[:\s]+(\d+)\s*gb", text, re.I))
    if m:
        return int(m.group(1)), False

    return None, False


def detect_plan_type(name: str) -> str:
    n = name.lower()
    if re.search(r"enterprise|corporate|data\s*center", n): return "enterprise"
    if re.search(r"business|office|smb|commercial", n):      return "business"
    if re.search(r"fiber|fibre|ftth|pon", n):                return "fiber"
    if re.search(r"wireless|4g|lte|wimax|radio", n):        return "wireless"
    return "residential"




def normalize_plan_name(raw: str, isp_slug: str) -> str:
    name = re.sub(r"\s+", " ", raw).strip()
    name = re.sub(r"[^\w\s\-+.]", "", name)
    name = re.sub(r"\b(package|plan|pack|pkg|offer|scheme)\b", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip()
    return name or f"{isp_slug.upper()} Plan"


# ── Master normalised plan dataclass ───────────────────────────────────────

@dataclass
class NormalizedPlan:
    isp_id: int
    raw_name: str
    normalized_name: str
    plan_type: str
    download_mbps: int
    upload_mbps: Optional[int]
    speed_raw: str
    price_monthly: float
    price_raw: str
    vat_included: bool
    fup_gb: Optional[int]
    is_unlimited: bool
    contract_months: int
    bundles: list[dict]
    bundle_flags: list[str]
    description: Optional[str]
    scrape_url: str
    raw_data: dict
    price_quarterly: Optional[float] = None
    price_annual: Optional[float] = None
    setup_fee: float = 0.0


def normalize_plan(raw: dict, isp_slug: str) -> NormalizedPlan:
    """
    Convert a raw scraped dict into a fully normalized NormalizedPlan.
    Raises ValueError if speed or price cannot be parsed.
    """
    download_mbps, upload_mbps = normalize_speed(raw.get("raw_speed", "0 Mbps"))
    price_monthly = normalize_price(raw.get("raw_price", "0"))
    bundles, bundle_flags = normalize_bundles(raw.get("raw_bundles", []))
    fup_gb, is_unlimited = detect_fup(raw.get("raw_bundles", []), raw.get("raw_description", ""))
    normalized_name = normalize_plan_name(raw.get("raw_name", ""), isp_slug)
    plan_type = detect_plan_type(raw.get("raw_name", ""))

    # VAT: assume included unless explicitly marked exclusive
    raw_price_str = raw.get("raw_price", "")
    vat_included = not bool(re.search(r"excl|exclusive|without\s*vat|before\s*vat", raw_price_str, re.I))

    return NormalizedPlan(
        isp_id=raw["isp_id"],
        raw_name=raw.get("raw_name", ""),
        normalized_name=normalized_name,
        plan_type=plan_type,
        download_mbps=download_mbps,
        upload_mbps=upload_mbps,
        speed_raw=raw.get("raw_speed", ""),
        price_monthly=price_monthly,
        price_raw=raw.get("raw_price", ""),
        vat_included=vat_included,
        fup_gb=fup_gb,
        is_unlimited=is_unlimited,
        contract_months=1,
        bundles=bundles,
        bundle_flags=bundle_flags,
        description=raw.get("raw_description"),
        scrape_url=raw.get("source_url", ""),
        raw_data=raw,
    )
