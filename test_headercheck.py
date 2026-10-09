import pytest
import requests
from unittest.mock import patch, Mock
from requests.structures import CaseInsensitiveDict

from headercheck import check_headers, main, SECURITY_HEADERS

def fake_response(headers):
    response = Mock()
    response.headers = CaseInsensitiveDict(headers)
    return response


@patch("headercheck.requests.get")
def test_all_headers_present(mock_get):
    mock_get.return_value = fake_response(
        {header: "some-value" for header in SECURITY_HEADERS}
    )

    results = check_headers("https://example.com")

    assert all(results.values())

@patch("headercheck.requests.get")
def test_some_headers_missing(mock_get):
    mock_get.return_value = fake_response({
        "Strict-Transport-Security": "max-age=31536000",
        "X-Frame-Options": "DENY",
    })

    results = check_headers("https://example.com")

    assert results["Strict-Transport-Security"] is True
    assert results["X-Frame-Options"] is True
    assert results["Content-Security-Policy"] is False
    assert results["X-Content-Type-Options"] is False
    assert results["Referrer-Policy"] is False

@patch("headercheck.requests.get")
def test_headers_are_case_insensitive(mock_get):
    mock_get.return_value = fake_response({
        "strict-transport-security": "max-age=31536000",
        "CONTENT-SECURITY-POLICY": "default-src 'self'",
        "x-frame-options": "DENY",
        "X-CONTENT-TYPE-OPTIONS": "nosniff",
        "referrer-policy": "no-referrer",
    })

    results = check_headers("https://example.com")

    assert all(results.values())

@pytest.mark.parametrize("headers, expected_code", [
    ({header: "x" for header in SECURITY_HEADERS}, 0),
    ({"X-Frame-Options": "DENY"}, 1),
])
@patch("headercheck.requests.get")
def test_exit_codes(mock_get, monkeypatch, headers, expected_code):
    mock_get.return_value = fake_response(headers)
    monkeypatch.setattr("sys.argv", ["headercheck.py", "https://example.com"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == expected_code


def test_usage_error_without_url(monkeypatch):
    monkeypatch.setattr("sys.argv", ["headercheck.py"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2

@patch("headercheck.requests.get")
def test_unreachable_site_exits_cleanly(mock_get, monkeypatch, capsys):
    mock_get.side_effect = requests.exceptions.ConnectionError("connection refused")
    monkeypatch.setattr("sys.argv", ["headercheck.py", "https://unreachable.example"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 3
    assert "Error" in capsys.readouterr().out