from app.utils.pii import redact_pii


def test_redact_pii_masks_common_patterns():
    raw = "Email test@example.com phone 9876543210 PAN ABCDE1234F Aadhaar 1234 5678 9012"
    out = redact_pii(raw)
    assert "[REDACTED_EMAIL]" in out
    assert "[REDACTED_PHONE]" in out
    assert "[REDACTED_PAN]" in out
    assert "[REDACTED_AADHAAR]" in out
