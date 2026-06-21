from pathlib import Path

from app.tools.spreadsheet import PricingAnalysisTool


def test_three_year_tco_reconciles_expected_vendor_costs() -> None:
    path = Path(__file__).resolve().parents[1] / "data" / "demo" / "vendor_pricing.csv"
    results = PricingAnalysisTool(path).calculate_three_year_tco()
    values = {item.vendor: item for item in results}

    assert values["Northstar"].three_year_tco == 498180.0
    assert values["BluePeak"].three_year_tco == 443130.0
    assert values["Veridian"].three_year_tco == 480620.0
    assert results[0].vendor == "BluePeak"
