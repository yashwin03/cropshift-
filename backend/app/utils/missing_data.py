"""
missing_data.py -- Utilities for graceful handling of absent data.

Every value that was NOT in the database is tracked here so the decision
engine and explainability layer can surface honest confidence levels and
farmer-readable notes. This is a first-class feature, not an edge case.

Rules:
- Missing data never raises an exception.
- Missing data lowers confidence and adds an explanatory note.
- Every resolved value knows whether it was defaulted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple


# ---------------------------------------------------------------------------
# Single-value resolution
# ---------------------------------------------------------------------------

def resolve(
    value: Any,
    fallback: Any,
    field_name: str,
) -> Tuple[Any, bool, str]:
    """Return (effective_value, was_defaulted, note).

    If *value* is None the fallback is used and was_defaulted is True.
    The note is a human-readable explanation suitable for a farmer-facing UI.
    """
    if value is not None:
        return value, False, ""

    note = (
        f"{field_name.replace('_', ' ').capitalize()} information was not "
        f"available, so a regional average was used."
    )
    return fallback, True, note


# ---------------------------------------------------------------------------
# Confidence tracker
# ---------------------------------------------------------------------------

@dataclass
class DataConfidence:
    """Accumulates defaulted fields and derives an overall confidence level.

    Confidence degrades as more fields fall back to defaults:
        0 defaults  -> HIGH
        1 default   -> MEDIUM
        2+ defaults -> LOW
    """

    defaults: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def record_default(self, field_name: str, note: str) -> None:
        """Register a single defaulted field."""
        if field_name not in self.defaults:
            self.defaults.append(field_name)
        if note and note not in self.notes:
            self.notes.append(note)

    def apply(
        self,
        value: Any,
        fallback: Any,
        field_name: str,
    ) -> Any:
        """Resolve *value* and automatically record any default taken."""
        effective, was_defaulted, note = resolve(value, fallback, field_name)
        if was_defaulted:
            self.record_default(field_name, note)
        return effective

    @property
    def level(self) -> str:
        """Return 'HIGH', 'MEDIUM', or 'LOW'."""
        n = len(self.defaults)
        if n == 0:
            return "HIGH"
        if n == 1:
            return "MEDIUM"
        return "LOW"

    def summary(self) -> dict:
        """Return a serialisable summary for API responses."""
        return {
            "confidence": self.level,
            "defaulted_fields": list(self.defaults),
            "notes": list(self.notes),
        }
