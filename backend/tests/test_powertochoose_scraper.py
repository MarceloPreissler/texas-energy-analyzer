"""Unit tests for the PowerToChoose scraper."""
from __future__ import annotations

from typing import Any, Dict

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pytest
import requests

from backend.app.scrapers.powertochoose import scrape_power_to_choose


class _DummyResponse:
    def __init__(self, json_data: Dict[str, Any] | None = None, text: str = "") -> None:
        self._json = json_data
        self.text = text

    def raise_for_status(self) -> None:  # pragma: no cover - no-op
        return None

    def json(self) -> Dict[str, Any]:
        if self._json is None:
            raise ValueError("No JSON payload")
        return self._json


def test_scrape_power_to_choose_uses_api_when_available(monkeypatch):
    """The scraper should prefer the JSON API when it returns data."""

    sample_plan = {
        "providerName": "Reliable Energy",
        "planName": "Solar Saver 12",
        "planType": "Fixed",
        "termValue": 12,
        "renewableValue": 100,
        "cancellationFee": "$150",
        "rate_500": 12.0,
        "rate_1000": 11.5,
        "rate_2000": 11.2,
        "planUrl": "https://example.com/plan",
        "specialFeatures": "100% renewable",
    }

    def fake_get(url, params=None, headers=None, timeout=None):  # noqa: ANN001
        assert "zip_code" in params
        assert params["page_size"] == 99999
        return _DummyResponse({"data": [sample_plan]})

    monkeypatch.setattr("backend.app.scrapers.powertochoose.requests.get", fake_get)

    plans = scrape_power_to_choose("75214")
    assert len(plans) == 1
    plan = plans[0]
    assert plan.plan_name == "Solar Saver 12"
    assert plan.provider_name == "Reliable Energy"
    assert plan.rate_1000_cents == pytest.approx(11.5)
    assert plan.renewable_percent == 100
    assert plan.cancellation_fee == pytest.approx(150.0)


def test_scrape_power_to_choose_falls_back_to_html(monkeypatch):
    """When the API errors, the HTML parser should still return plans."""

    html_page_one = """
    <html>
        <body>
            <table>
                <tbody>
                    <tr>
                        <td data-label="Provider">TimeCo</td>
                        <td data-label="Plan Name">Free Nights 12</td>
                        <td data-label="Type">Time of Use</td>
                        <td data-label="Term">12</td>
                        <td data-label="Renewable Content">80%</td>
                        <td data-label="Cancellation Fee">$200</td>
                        <td data-label="500 kWh">11.1¢</td>
                        <td data-label="1000 kWh">10.5¢</td>
                        <td data-label="2000 kWh">10.0¢</td>
                        <td data-label="Features">Free nights from 8pm-6am</td>
                    </tr>
                </tbody>
            </table>
            <div data-total-pages="1"></div>
        </body>
    </html>
    """

    def fake_get(url, params=None, headers=None, timeout=None):  # noqa: ANN001
        if "api.powertochoose.org" in url:
            raise requests.RequestException("API unavailable")
        return _DummyResponse(text=html_page_one)

    monkeypatch.setattr("backend.app.scrapers.powertochoose.requests.get", fake_get)

    plans = scrape_power_to_choose("77001")
    assert len(plans) == 1
    plan = plans[0]
    assert plan.plan_type == "Time of Use"
    assert plan.rate_1000_cents == pytest.approx(10.5)
    assert plan.cancellation_fee == pytest.approx(200.0)
    assert plan.renewable_percent == 80
