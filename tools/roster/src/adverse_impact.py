"""
Core adverse-impact analysis for hiring/promotion data.

Implements the EEOC "four-fifths (80%) rule" plus a two-proportion z-test for
statistical significance. No scipy dependency: the normal survival function is
computed with math.erfc.

This is a screening/monitoring aid, NOT legal advice and NOT a compliance
certification. A four-fifths flag is a trigger for review, not a verdict.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd

POSITIVE_TOKENS = {
    "1", "1.0", "true", "t", "yes", "y", "hired", "hire", "selected",
    "select", "pass", "passed", "advance", "advanced", "offer", "offered",
}


def coerce_outcome(series: pd.Series) -> pd.Series:
    """Coerce an outcome column to 0/1 integers."""
    def to_bin(v) -> int:
        if pd.isna(v):
            return 0
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return 1 if float(v) >= 0.5 else 0
        return 1 if str(v).strip().lower() in POSITIVE_TOKENS else 0

    return series.map(to_bin).astype(int)


def _normal_sf(z: float) -> float:
    """Survival function P(Z > z) for the standard normal."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def two_proportion_ztest(s1: int, n1: int, s2: int, n2: int) -> tuple[float, float]:
    """Pooled two-proportion z-test. Returns (z, two-sided p-value)."""
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
    p1, p2 = s1 / n1, s2 / n2
    p_pool = (s1 + s2) / (n1 + n2)
    se = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    p_value = 2.0 * _normal_sf(abs(z))
    return z, p_value


@dataclass
class GroupResult:
    group: str
    n: int
    selected: int
    selection_rate: float
    impact_ratio: float          # selection_rate / reference_rate
    is_reference: bool
    four_fifths_flag: bool       # impact_ratio < 0.80 (non-reference groups)
    z_stat: float | None         # vs reference group
    p_value: float | None
    significant: bool            # p < 0.05
    small_sample: bool           # n < 30 -> ratios unreliable


@dataclass
class AttributeResult:
    attribute: str
    outcome: str
    reference_group: str
    groups: list[GroupResult] = field(default_factory=list)

    @property
    def any_flag(self) -> bool:
        return any(g.four_fifths_flag for g in self.groups)

    @property
    def any_significant_flag(self) -> bool:
        return any(g.four_fifths_flag and g.significant for g in self.groups)

    def to_frame(self) -> pd.DataFrame:
        rows = []
        for g in self.groups:
            rows.append(
                {
                    "Group": g.group,
                    "N": g.n,
                    "Selected": g.selected,
                    "Selection rate": round(g.selection_rate, 4),
                    "Impact ratio": round(g.impact_ratio, 4),
                    "Reference": "\u2605" if g.is_reference else "",
                    "4/5 flag": "\u26a0\ufe0f" if g.four_fifths_flag else "",
                    "p-value": (None if g.p_value is None else round(g.p_value, 4)),
                    "Significant": "yes" if g.significant else "",
                    "Small N": "yes" if g.small_sample else "",
                }
            )
        return pd.DataFrame(rows)


def analyze_attribute(
    df: pd.DataFrame,
    attribute: str,
    outcome_col: str,
    *,
    min_group_n: int = 1,
) -> AttributeResult:
    """Run a four-fifths + significance analysis for one protected attribute."""
    work = df[[attribute, outcome_col]].copy()
    work["_outcome"] = coerce_outcome(work[outcome_col])

    grouped = (
        work.groupby(attribute)["_outcome"]
        .agg(["count", "sum"])
        .rename(columns={"count": "n", "sum": "selected"})
    )
    grouped = grouped[grouped["n"] >= min_group_n]
    if grouped.empty:
        return AttributeResult(attribute, outcome_col, reference_group="", groups=[])

    grouped["rate"] = grouped["selected"] / grouped["n"]

    # Reference = highest selection-rate group (EEOC convention).
    reference_group = grouped["rate"].idxmax()
    ref_rate = grouped.loc[reference_group, "rate"]
    ref_sel = int(grouped.loc[reference_group, "selected"])
    ref_n = int(grouped.loc[reference_group, "n"])

    results: list[GroupResult] = []
    for group, row in grouped.iterrows():
        n = int(row["n"])
        selected = int(row["selected"])
        rate = float(row["rate"])
        is_ref = group == reference_group
        impact_ratio = 1.0 if ref_rate == 0 else rate / ref_rate

        if is_ref:
            z = p = None
            significant = False
        else:
            z, p = two_proportion_ztest(selected, n, ref_sel, ref_n)
            significant = bool(p < 0.05)

        results.append(
            GroupResult(
                group=str(group),
                n=int(n),
                selected=int(selected),
                selection_rate=float(rate),
                impact_ratio=float(impact_ratio),
                is_reference=bool(is_ref),
                four_fifths_flag=bool((not is_ref) and impact_ratio < 0.80),
                z_stat=(None if z is None else float(z)),
                p_value=(None if p is None else float(p)),
                significant=significant,
                small_sample=bool(n < 30),
            )
        )

    results.sort(key=lambda g: g.selection_rate, reverse=True)
    return AttributeResult(attribute, outcome_col, str(reference_group), results)


def analyze(
    df: pd.DataFrame,
    attributes: Iterable[str],
    outcome_col: str,
    *,
    min_group_n: int = 1,
) -> list[AttributeResult]:
    return [
        analyze_attribute(df, attr, outcome_col, min_group_n=min_group_n)
        for attr in attributes
    ]
