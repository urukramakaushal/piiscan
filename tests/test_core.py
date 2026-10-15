import pandas as pd
from piiscan.core import find_pii, luhn_ok, mask, scan


def test_email():
    assert find_pii("mail me at a.b@example.com") == ["email"]


def test_pan_not_phone():
    assert find_pii("ABCDE1234F") == ["pan"]


def test_ip():
    assert find_pii("host 192.168.1.10") == ["ipv4"]


def test_luhn_valid_card():
    assert luhn_ok("4539 1488 0343 6467")
    assert find_pii("4539 1488 0343 6467") == ["credit_card"]


def test_random_digits_not_card():
    assert "credit_card" not in find_pii("1234 5678 9012 3456")


def test_phone():
    assert find_pii("+91 98765 43210") == ["phone"]


def test_clean_text():
    assert find_pii("hello world 2024") == []


def test_scan_and_mask():
    df = pd.DataFrame({"note": ["x@y.com", "fine"], "n": ["1", "2"]})
    assert scan(df) == {"note": {"email": 1}}
    assert mask(df)["note"].tolist() == ["[EMAIL]", "fine"]
