import re
from datetime import datetime

from chalicelib.utils import truncate_preview


AMOUNT_PATTERN = re.compile(r"(?:[$€£]\s?)?\d{1,3}(?:,\d{3})*\.\d{2}(?!\d)")
DATE_PATTERNS = [
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), ["%Y-%m-%d"]),
    (re.compile(r"\b\d{4}/\d{2}/\d{2}\b"), ["%Y/%m/%d"]),
    (re.compile(r"\b\d{2}/\d{2}/\d{4}\b"), ["%m/%d/%Y", "%d/%m/%Y"]),
    (re.compile(r"\b\d{2}-\d{2}-\d{4}\b"), ["%m-%d-%Y", "%d-%m-%Y"]),
    (re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b", re.IGNORECASE), ["%B %d, %Y", "%b %d, %Y"]),
]


def classify_document_type(text: str) -> str:
    lower_text = text.lower()
    if any(keyword in lower_text for keyword in ["receipt", "subtotal", "cashier"]):
        return "receipt"
    if any(keyword in lower_text for keyword in ["invoice", "bill to", "invoice number"]):
        return "invoice"
    if any(
        keyword in lower_text
        for keyword in ["transaction", "available balance", "transferred", "payment sent"]
    ):
        return "transaction_screenshot"
    return "unknown"


_HIGH_PRIORITY_KEYWORDS = ["grand total", "balance due", "total"]
_LOW_PRIORITY_KEYWORDS = ["paid", "amount due"]
_SUMMARY_KEYWORDS = {
    # English
    "subtotal", "sub-total", "total", "hst", "gst", "pst", "vat", "tax",
    "balance", "paid", "card", "cash", "mastercard", "visa", "amex", "debit", "credit",
    # French
    "sous-total", "tvh", "tps", "tvq",
}


def _extract_amount_from_lines(lines: list[str]) -> str | None:
    # Tuple: (priority, line_index, numeric_amount, raw_amount)
    candidate_amounts: list[tuple[int, int, float, str]] = []

    for index, line in enumerate(lines):
        matches = AMOUNT_PATTERN.findall(line)
        if not matches:
            continue

        lower_line = line.lower()
        if any(keyword in lower_line for keyword in _HIGH_PRIORITY_KEYWORDS):
            priority_score = 2
        elif any(keyword in lower_line for keyword in _LOW_PRIORITY_KEYWORDS):
            priority_score = 1
        else:
            priority_score = 0

        for raw_amount in matches:
            numeric_amount = float(raw_amount.replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip())
            candidate_amounts.append((priority_score, index, numeric_amount, raw_amount))

    if not candidate_amounts:
        return None

    # Sort by priority first, then by line position (later lines win within same priority)
    best = sorted(candidate_amounts, key=lambda item: (item[0], item[1]), reverse=True)[0]
    return f"{best[2]:.2f}"


def extract_amount(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return _extract_amount_from_lines(lines)


def _try_parse_date(date_text: str, formats: list[str]) -> str | None:
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_text, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_date(text: str) -> str | None:
    for pattern, formats in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        parsed = _try_parse_date(match.group(0), formats)
        if parsed:
            return parsed
    return None


def _parse_amount(raw: str) -> float:
    return float(raw.replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip())


def extract_line_items(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    items = []
    summary = []

    for i, line in enumerate(lines):
        matches = AMOUNT_PATTERN.findall(line)
        if not matches:
            continue

        raw = matches[-1]
        amount_str = f"{_parse_amount(raw):.2f}"

        # Strip all amounts and currency symbols to get the descriptive text
        label = AMOUNT_PATTERN.sub("", line).strip().strip("$€£@:,. ")

        if not label or len(label) < 2:
            # Amount-only line — look back for a label on the previous non-amount line
            prev_label = None
            for j in range(i - 1, max(i - 3, -1), -1):
                prev = lines[j].strip()
                if prev and not AMOUNT_PATTERN.search(prev) and len(prev) > 2:
                    prev_label = prev
                    break
            if prev_label is None:
                continue  # no usable label nearby, skip
            label = prev_label

        entry = {"text": label, "amount": amount_str}
        if any(kw in label.lower() for kw in _SUMMARY_KEYWORDS):
            summary.append(entry)
        else:
            items.append(entry)

    return {"items": items, "summary": summary}


def extract_entity(text: str, comprehend_result: dict) -> str:
    entities = comprehend_result.get("entities", [])
    preferred_types = ["ORGANIZATION", "COMMERCIAL_ITEM", "PERSON"]

    for entity_type in preferred_types:
        matching = [e for e in entities if e.get("type") == entity_type and e.get("text")]
        if matching:
            best = sorted(matching, key=lambda e: e.get("score", 0), reverse=True)[0]
            return best["text"].strip()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:5]:
        if len(line) > 2 and not re.search(r"\d{3,}", line):
            return line

    return "Unknown entity"


def build_summary(document_type: str, amount: str | None, date: str | None, entity: str) -> str:
    readable_type = document_type.replace("_", " ")
    amount_text = amount if amount else "unknown amount"
    date_text = date if date else "unknown date"
    return f"{readable_type.title()} from {entity} for {amount_text} on {date_text}."


def parse_document_data(text: str, comprehend_result: dict) -> dict:
    document_type = classify_document_type(text)
    amount = extract_amount(text)
    date = extract_date(text)
    entity = extract_entity(text, comprehend_result)
    summary = build_summary(document_type, amount, date, entity)
    line_items = extract_line_items(text)

    return {
        "document_type": document_type,
        "amount": amount or "N/A",
        "date": date or "N/A",
        "entity": entity,
        "summary": summary,
        "line_items": line_items,
        "raw_text_preview": truncate_preview(text, max_length=400) or "No text extracted.",
    }
