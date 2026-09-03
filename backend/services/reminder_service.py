import re
from datetime import datetime

DATE_CONTEXT_KEYWORDS = [
    'expiry', 'expires', 'expire', 'expiration', 'valid until', 'valid till',
    'due date', 'due by', 'renewal', 'renew by', 'last date',
    'deadline', 'submission date', 'exam date', 'appointment'
]

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7,
    'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
}


def find_reminders(text):
    if not text:
        return []

    reminders = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    seen_dates = set()

    # First, try the normal approach: keyword and date close together
    for i, line in enumerate(lines):
        line_lower = line.lower()

        for keyword in DATE_CONTEXT_KEYWORDS:
            if keyword in line_lower:
                search_window = ' '.join(lines[max(0, i - 2):i + 5])
                parsed_date = _extract_date_from_line(search_window)

                if parsed_date:
                    date_key = parsed_date.date().isoformat()
                    if date_key not in seen_dates:
                        seen_dates.add(date_key)
                        reminders.append({
                            'label': keyword.title(),
                            'due_date': parsed_date.date()
                        })
                break

    # Fallback: if no reminder found yet, but a keyword AND a date
    # both exist somewhere in the document (common with scrambled multi-column
    # layouts from OCR), link the keyword to the nearest date found.
    if not reminders:
        has_keyword = any(k in text.lower() for k in DATE_CONTEXT_KEYWORDS)
        if has_keyword:
            all_dates = []
            for line in lines:
                d = _extract_date_from_line(line)
                if d:
                    all_dates.append(d)
            if all_dates:
                matched_keyword = next((k for k in DATE_CONTEXT_KEYWORDS if k in text.lower()), 'Deadline')
                reminders.append({
                    'label': matched_keyword.title(),
                    'due_date': min(all_dates).date()
                })

    return reminders


def _extract_date_from_line(line):
    match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', line)
    if match:
        day, month_name, year = match.groups()
        month = MONTHS.get(month_name.lower())
        if month:
            try:
                return datetime(int(year), month, int(day))
            except ValueError:
                pass

    match = re.search(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', line)
    if match:
        month_name, day, year = match.groups()
        month = MONTHS.get(month_name.lower())
        if month:
            try:
                return datetime(int(year), month, int(day))
            except ValueError:
                pass

    match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', line)
    if match:
        day, month, year = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            pass

    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', line)
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            pass

    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2})\b', line)
    if match:
        day, month, year = match.groups()
        try:
            return datetime(2000 + int(year), int(month), int(day))
        except ValueError:
            pass

    return None