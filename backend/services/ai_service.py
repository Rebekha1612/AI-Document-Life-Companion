from transformers import pipeline
import re
import json

print("Loading AI models... this may take a minute on first run.")

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

CATEGORIES = ['Education', 'Finance', 'Medical', 'Legal', 'Identity', 'Insurance', 'Other']


# Strong, unambiguous keyword signals per category - checked before the AI model
CATEGORY_KEYWORDS = {
    'Finance': [
        'bank statement', 'account number', 'account holder', 'opening balance',
        'closing balance', 'salary credit', 'debit', 'credit', 'transaction',
        'ifsc', 'upi payment', 'bank account'
    ],
    'Insurance': [
        'policy number', 'premium', 'insurer', 'insured', 'coverage amount',
        'sum insured', 'policy holder', 'claim', 'network hospitals'
    ],
    'Medical': [
        'diagnosis', 'prescription', 'patient name', 'doctor', 'hospital',
        'blood group', 'lab report', 'medical report', 'symptoms'
    ],
    'Education': [
        'roll number', 'marksheet', 'cgpa', 'semester', 'grade', 'university',
        'college', 'exam', 'certificate of completion', 'course'
    ],
    'Identity': [
        'aadhaar', 'passport number', 'date of birth', 'nationality',
        'identity card', 'voter id', 'driving license'
    ],
    'Legal': [
        'agreement', 'contract', 'party of the first part', 'witness',
        'notary', 'affidavit', 'clause'
    ],
}


def classify_document(text):
    if not text or len(text.strip()) < 10:
        return "Other"

    text_lower = text.lower()

    # Check for strong keyword matches first - count matches per category
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            scores[category] = count

    if scores:
        best_category = max(scores, key=scores.get)
        # Only trust the keyword match if it's a clear winner (2+ matches,
        # or the only category matched at all)
        if scores[best_category] >= 2 or len(scores) == 1:
            return best_category

    # Fallback to AI model when keywords are weak/ambiguous
    result = classifier(text[:1000], CATEGORIES)
    return result['labels'][0]


def summarize_document(text):
    if not text or len(text.strip()) < 30:
        return text

    word_count = len(text.split())

    # If the text is already short, showing it as-is is clearer
    # than forcing an AI summary that can sound awkward on tiny inputs
    if word_count < 40:
        return text.strip()

    truncated = text[:1024]

    try:
        # Keep max_length reasonably below input length to avoid the
        # "output longer than input" warning on medium-length texts
        max_len = min(100, max(20, word_count - 5))
        result = summarizer(truncated, max_length=max_len, min_length=15, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        print(f"Summarization error: {e}")
        return text[:200] + "..."

def extract_key_details(text):
    details = {}

    # Amounts (₹5,00,000 or $500)
    amounts = re.findall(r'[₹$]\s?[\d,]+(?:\.\d+)?', text)
    if amounts:
        details['amounts'] = list(set(amounts))[:5]

    # Policy / reference / ID numbers (look for a label followed by a code)
    id_patterns = re.findall(
        r'(?:policy\s*number|reference\s*number|id\s*number|account\s*number|certificate\s*number|roll\s*number)\s*[:\-]?\s*([A-Z0-9\-\/]{4,})',
        text, re.IGNORECASE
    )
    if id_patterns:
        details['id_numbers'] = list(set(id_patterns))[:5]

    # Fallback: any standalone alphanumeric code that looks like an ID
    if not id_patterns:
        ref_numbers = re.findall(r'\b[A-Z]{2,}[0-9]{3,}\b', text)
        if ref_numbers:
            details['id_numbers'] = list(set(ref_numbers))[:5]

    # Dates mentioned anywhere in the document (various formats)
    dates = re.findall(
        r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b|\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        text, re.IGNORECASE
    )
    if dates:
        details['dates_mentioned'] = list(set(dates))[:5]

    # Possible names (capitalized word pairs, e.g. "Riya Sharma") - heuristic only
    name_matches = re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text)
    # Filter out common false positives (category-like words)
    ignore_words = {'Policy Number', 'Insurance Company', 'Health Insurance', 'Coverage Details'}
    names = [n for n in name_matches if n not in ignore_words]
    if names:
        details['possible_names'] = list(set(names))[:3]

    return json.dumps(details)