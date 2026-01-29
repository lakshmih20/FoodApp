import re
import easyocr
from datetime import datetime
from django.conf import settings

FSSAI_NUMBER_REGEX = r'\b\d{14}\b'
EXPIRY_DATE_REGEX = r'\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2})\b'

class FSSAIResult:
    def __init__(self, number=None, expiry=None, confidence=None, notes=None):
        self.number = number
        self.expiry = expiry
        self.confidence = confidence
        self.notes = notes


def extract_fssai_info(image_path, expected_number=None, expected_length=None, confidence_threshold=None):
    if expected_length is None:
        expected_length = getattr(settings, 'FSSAI_NUMBER_LENGTH', 14)
    if confidence_threshold is None:
        confidence_threshold = getattr(settings, 'FSSAI_OCR_CONFIDENCE_THRESHOLD', 0.6)
    reader = easyocr.Reader(['en'])
    try:
        result = reader.readtext(image_path)
    except Exception as e:
        return FSSAIResult(notes=f"OCR failed: {str(e)}"), 'high', 'flagged'

    text = ' '.join([r[1] for r in result])
    confidences = [r[2] for r in result]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    # Extract FSSAI number
    match_num = re.search(FSSAI_NUMBER_REGEX, text)
    fssai_num = match_num.group(0) if match_num else None
    if not fssai_num:
        # fallback: longest digit sequence
        digit_seqs = re.findall(r'\d{10,}', text)
        fssai_num = max(digit_seqs, key=len) if digit_seqs else None

    # Extract expiry date
    match_exp = re.search(EXPIRY_DATE_REGEX, text)
    expiry_raw = match_exp.group(0) if match_exp else None
    expiry_date = None
    if expiry_raw:
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                expiry_date = datetime.strptime(expiry_raw, fmt).date()
                break
            except Exception:
                continue

    # Risk assessment
    today = datetime.today().date()
    risk = 'low'
    status = 'verified'
    notes = []
    if not fssai_num or len(fssai_num) != expected_length or not fssai_num.isdigit():
        risk = 'high'
        status = 'flagged'
        notes.append('Invalid or missing FSSAI number.')
    if expiry_date and expiry_date < today:
        risk = 'high'
        status = 'flagged'
        notes.append('Certificate expired.')
    if avg_conf < confidence_threshold:
        risk = 'high'
        status = 'flagged'
        notes.append('Low OCR confidence.')
    if expected_number and fssai_num and expected_number != fssai_num:
        risk = 'high'
        status = 'flagged'
        notes.append('FSSAI number mismatch.')
    if not expiry_date:
        risk = 'medium'
        status = 'flagged'
        notes.append('Expiry date not found.')
    if risk == 'low' and (avg_conf < 0.75 or not expiry_date):
        risk = 'medium'
        status = 'flagged'
        notes.append('Moderate confidence or missing expiry.')
    return FSSAIResult(fssai_num, expiry_date, avg_conf, '; '.join(notes)), risk, status
