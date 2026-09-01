import re
from datetime import timedelta
from django.utils import timezone

from .models import OTPRecord

# Mapping English number words to digit strings
WORD_TO_DIGIT: dict[str, str] = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}

# Mapping Bengali digits to ASCII digits
BENGALI_DIGITS: dict[str, str] = {
    "০": "0",
    "১": "1",
    "২": "2",
    "৩": "3",
    "৪": "4",
    "৫": "5",
    "৬": "6",
    "৭": "7",
    "৮": "8",
    "৯": "9",
}

# Regex to match 4 to 8 spelled-out number words separated by hyphens, spaces, or commas
# e.g., 'Seven-One-Nine-Three-Two-One', 'seven one nine three two one'
SPELLED_OUT_SEQUENCE_REGEX = re.compile(
    r"(?i)\b(?:zero|one|two|three|four|five|six|seven|eight|nine)"
    r"(?:[\s\-,]+(?:zero|one|two|three|four|five|six|seven|eight|nine)){3,7}\b"
)

# Numeric context patterns
NUMERIC_FORWARD_CONTEXT_REGEX = re.compile(
    r"(?i)(?:otp|code|pin|passcode|verification|password|sequence|is|use|type)[\s:=-]+(?:[A-Za-z]-)?(\d{4,8})\b"
)
NUMERIC_REVERSE_CONTEXT_REGEX = re.compile(
    r"(?i)\b(\d{4,8})\b\s+(?:is\s+your|is\s+the|code|otp|pin|verification|to\s+verify|sequence)"
)
NUMERIC_STANDALONE_REGEX = re.compile(r"\b\d{4,8}\b")


def extract_spelled_out_otp(message: str) -> str | None:
    """
    Finds sequences of 4 to 8 spelled-out number words
    (e.g., 'Seven-One-Nine-Three-Two-One') and converts them to digits (e.g., '719321').
    """
    match = SPELLED_OUT_SEQUENCE_REGEX.search(message)
    if not match:
        return None

    raw_sequence = match.group(0)
    tokens = re.split(r"[\s\-,]+", raw_sequence.strip())
    digits = [WORD_TO_DIGIT[token.lower()] for token in tokens if token.lower() in WORD_TO_DIGIT]

    if 4 <= len(digits) <= 8:
        return "".join(digits)
    return None


def normalize_bengali_digits(text: str) -> str:
    """Replaces any Bengali numeral characters with ASCII digits."""
    return "".join(BENGALI_DIGITS.get(char, char) for char in text)


def extract_otp(message: str) -> str | None:
    """
    Extracts an OTP (as numeric string) from an SMS message.
    Supports:
    1. Spelled-out number words: 'Seven-One-Nine-Three-Two-One' -> '719321'
    2. Contextual numeric OTPs: 'code: 739201', 'sequence 739201' -> '739201'
    3. Standalone 4 to 8 digit numbers: '482931' -> '482931'
    4. Bengali digits normalization: '৭৩৯২০১' -> '739201'
    """
    if not message or not isinstance(message, str):
        return None

    cleaned_message = message.strip()
    if not cleaned_message:
        return None

    # 1. Check for spelled-out word sequence first (e.g. IVAC BD format)
    spelled_out_otp = extract_spelled_out_otp(cleaned_message)
    if spelled_out_otp:
        return spelled_out_otp

    # 2. Normalize Bengali digits if present
    normalized_message = normalize_bengali_digits(cleaned_message)

    # 3. Look for forward contextual numeric OTP (e.g. 'type sequence 719321')
    forward_match = NUMERIC_FORWARD_CONTEXT_REGEX.search(normalized_message)
    if forward_match:
        return forward_match.group(1)

    # 4. Look for reverse contextual numeric OTP (e.g. '719321 is your code')
    reverse_match = NUMERIC_REVERSE_CONTEXT_REGEX.search(normalized_message)
    if reverse_match:
        return reverse_match.group(1)

    # 5. Fallback: Standalone 4 to 8 digit numbers
    candidates = NUMERIC_STANDALONE_REGEX.findall(normalized_message)
    if candidates:
        return candidates[0]

    return None


def store_otp(
    phone_number: str,
    otp: str,
    sender: str = "",
    deduplicate_window_seconds: int = 120,
) -> OTPRecord:
    """
    Stores phone_number, sender, and otp in the database.
    If the same phone_number and otp were saved within deduplicate_window_seconds,
    reuses the recent record to prevent duplicate entries from SMS retries.
    """
    recent_cutoff = timezone.now() - timedelta(seconds=deduplicate_window_seconds)
    existing = (
        OTPRecord.objects.filter(
            phone_number=phone_number,
            otp=otp,
            created_at__gte=recent_cutoff,
        )
        .order_by("-created_at")
        .first()
    )

    if existing is not None:
        if sender and not existing.sender:
            existing.sender = sender
            existing.save(update_fields=["sender"])
        return existing

    return OTPRecord.objects.create(
        phone_number=phone_number,
        sender=sender,
        otp=otp,
    )


def process_otp_sms(
    phone_number: str,
    message: str,
    sender: str = "",
) -> tuple[OTPRecord | None, str | None]:
    """
    Extracts OTP and persists the record with phone_number and sender.
    Returns (OTPRecord, otp_string) if successful, or (None, None) if no OTP was found.
    """
    otp = extract_otp(message)
    if not otp:
        return None, None

    record = store_otp(phone_number=phone_number, otp=otp, sender=sender)
    return record, otp


def get_latest_otps(limit: int = 20):
    """
    Returns latest OTP records ordered by created_at descending.
    """
    return OTPRecord.objects.all().order_by("-created_at")[:limit]
