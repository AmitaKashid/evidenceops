from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class VendorCostResult:
    vendor: str
    implementation_cost: float
    recurring_annual_cost: float
    first_year_subtotal: float
    contingency: float
    three_year_tco: float
    assumptions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vendor": self.vendor,
            "implementation_cost": round(self.implementation_cost, 2),
            "recurring_annual_cost": round(self.recurring_annual_cost, 2),
            "first_year_subtotal": round(self.first_year_subtotal, 2),
            "contingency": round(self.contingency, 2),
            "three_year_tco": round(self.three_year_tco, 2),
            "assumptions": self.assumptions,
        }


class PricingAnalysisTool:
    """Deterministic pricing analysis used by the workflow and numeric verifier."""

    REQUIRED_COLUMNS = {
        "vendor",
        "named_users",
        "implementation_cost",
        "annual_license_per_user",
        "annual_support_cost",
        "annual_add_on_cost",
        "currency",
    }

    def __init__(self, pricing_file: Path) -> None:
        self.pricing_file = pricing_file

    def load(self) -> pd.DataFrame:
        frame = pd.read_csv(self.pricing_file)
        missing = self.REQUIRED_COLUMNS.difference(frame.columns)
        if missing:
            raise ValueError(f"Pricing dataset is missing required columns: {sorted(missing)}")
        if frame["currency"].nunique() != 1:
            raise ValueError("Reference tool expects a single currency to avoid unsupported FX assumptions.")
        return frame

    def calculate_three_year_tco(self, contingency_rate: float = 0.10) -> list[VendorCostResult]:
        if not 0 <= contingency_rate <= 0.5:
            raise ValueError("Contingency rate must be between 0 and 0.5.")
        frame = self.load()
        results: list[VendorCostResult] = []
        for record in frame.to_dict(orient="records"):
            license_cost = float(record["named_users"]) * float(record["annual_license_per_user"])
            recurring = license_cost + float(record["annual_support_cost"]) + float(record["annual_add_on_cost"])
            implementation = float(record["implementation_cost"])
            first_year_subtotal = implementation + recurring
            contingency = first_year_subtotal * contingency_rate
            total = implementation + contingency + (3 * recurring)
            results.append(
                VendorCostResult(
                    vendor=str(record["vendor"]),
                    implementation_cost=implementation,
                    recurring_annual_cost=recurring,
                    first_year_subtotal=first_year_subtotal,
                    contingency=contingency,
                    three_year_tco=total,
                    assumptions=[
                        f"{int(record['named_users'])} named users remain constant for three years.",
                        f"A {contingency_rate:.0%} contingency applies to the first-year subtotal.",
                        "No foreign-exchange, tax, renewal uplift, or usage-overage assumptions are included.",
                    ],
                )
            )
        return sorted(results, key=lambda result: result.three_year_tco)

    def best_cost_option(self) -> VendorCostResult:
        results = self.calculate_three_year_tco()
        if not results:
            raise ValueError("Pricing analysis returned no vendor rows.")
        return results[0]
