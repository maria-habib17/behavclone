"""Scaled deterministic cohort for false-positive evaluation."""

from dataclasses import dataclass

from experiments.models import (
    BenchmarkPair,
    TransformationKind,
)
from experiments.synthetic import SyntheticSubmission

SCALED_FAMILIES: dict[str, tuple[str, ...]] = {
    "PRICE": (
        "PRICE_BASE",
        "PRICE_RENAMED",
        "PRICE_REORDERED",
        "PRICE_SPLIT",
    ),
    "SCORE": (
        "SCORE_BASE",
        "SCORE_RENAMED",
        "SCORE_REORDERED",
        "SCORE_SPLIT",
    ),
    "STOCK": (
        "STOCK_BASE",
        "STOCK_RENAMED",
        "STOCK_REORDERED",
        "STOCK_SPLIT",
    ),
    "TEMP": (
        "TEMP_BASE",
        "TEMP_RENAMED",
        "TEMP_REORDERED",
        "TEMP_SPLIT",
    ),
}


@dataclass(frozen=True)
class ScaledCohort:
    """Submissions and predeclared provenance-positive pairs."""

    submissions: tuple[SyntheticSubmission, ...]
    related_pairs: tuple[BenchmarkPair, ...]


def _price_family() -> tuple[SyntheticSubmission, ...]:
    return (
        SyntheticSubmission(
            submission_id="PRICE_BASE",
            files={
                "PriceCalculator.java": """
class PriceCalculator {
    int addServiceFee(int price) {
        int adjusted = price + 7;
        return adjusted;
    }

    int applyMultiplier(int price) {
        int adjusted = price * 4;
        return adjusted;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="PRICE_RENAMED",
            files={
                "PriceCalculator.java": """
class PriceCalculator {
    int addServiceFee(int amount) {
        int result = amount + 7;
        return result;
    }

    int applyMultiplier(int amount) {
        int result = amount * 4;
        return result;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="PRICE_REORDERED",
            files={
                "PriceCalculator.java": """
class PriceCalculator {
    int applyMultiplier(int price) {
        int adjusted = price * 4;
        return adjusted;
    }

    int addServiceFee(int price) {
        int adjusted = price + 7;
        return adjusted;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="PRICE_SPLIT",
            files={
                "FeeCalculator.java": """
class FeeCalculator {
    int addServiceFee(int price) {
        int adjusted = price + 7;
        return adjusted;
    }
}
""",
                "PriceMultiplier.java": """
class PriceMultiplier {
    int applyMultiplier(int price) {
        int adjusted = price * 4;
        return adjusted;
    }
}
""",
            },
        ),
    )


def _score_family() -> tuple[SyntheticSubmission, ...]:
    return (
        SyntheticSubmission(
            submission_id="SCORE_BASE",
            files={
                "ScoreRules.java": """
class ScoreRules {
    int addBonus(int score) {
        int updated = score + 12;
        return updated;
    }

    int doubleScore(int score) {
        int updated = score * 2;
        return updated;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="SCORE_RENAMED",
            files={
                "ScoreRules.java": """
class ScoreRules {
    int addBonus(int points) {
        int outcome = points + 12;
        return outcome;
    }

    int doubleScore(int points) {
        int outcome = points * 2;
        return outcome;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="SCORE_REORDERED",
            files={
                "ScoreRules.java": """
class ScoreRules {
    int doubleScore(int score) {
        int updated = score * 2;
        return updated;
    }

    int addBonus(int score) {
        int updated = score + 12;
        return updated;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="SCORE_SPLIT",
            files={
                "BonusRule.java": """
class BonusRule {
    int addBonus(int score) {
        int updated = score + 12;
        return updated;
    }
}
""",
                "DoubleRule.java": """
class DoubleRule {
    int doubleScore(int score) {
        int updated = score * 2;
        return updated;
    }
}
""",
            },
        ),
    )


def _stock_family() -> tuple[SyntheticSubmission, ...]:
    return (
        SyntheticSubmission(
            submission_id="STOCK_BASE",
            files={
                "StockMath.java": """
class StockMath {
    int addRestock(int units) {
        int total = units + 5;
        return total;
    }

    int packCases(int units) {
        int total = units * 6;
        return total;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="STOCK_RENAMED",
            files={
                "StockMath.java": """
class StockMath {
    int addRestock(int quantity) {
        int changed = quantity + 5;
        return changed;
    }

    int packCases(int quantity) {
        int changed = quantity * 6;
        return changed;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="STOCK_REORDERED",
            files={
                "StockMath.java": """
class StockMath {
    int packCases(int units) {
        int total = units * 6;
        return total;
    }

    int addRestock(int units) {
        int total = units + 5;
        return total;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="STOCK_SPLIT",
            files={
                "RestockMath.java": """
class RestockMath {
    int addRestock(int units) {
        int total = units + 5;
        return total;
    }
}
""",
                "CaseMath.java": """
class CaseMath {
    int packCases(int units) {
        int total = units * 6;
        return total;
    }
}
""",
            },
        ),
    )


def _temperature_family() -> tuple[SyntheticSubmission, ...]:
    return (
        SyntheticSubmission(
            submission_id="TEMP_BASE",
            files={
                "TemperatureRules.java": """
class TemperatureRules {
    int raiseMinimum(int temperature) {
        if (temperature < 10) {
            return 10;
        }
        return temperature;
    }

    int distanceFromFreezing(int temperature) {
        int distance = temperature - 32;
        return distance;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="TEMP_RENAMED",
            files={
                "TemperatureRules.java": """
class TemperatureRules {
    int raiseMinimum(int value) {
        if (value < 10) {
            return 10;
        }
        return value;
    }

    int distanceFromFreezing(int value) {
        int difference = value - 32;
        return difference;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="TEMP_REORDERED",
            files={
                "TemperatureRules.java": """
class TemperatureRules {
    int distanceFromFreezing(int temperature) {
        int distance = temperature - 32;
        return distance;
    }

    int raiseMinimum(int temperature) {
        if (temperature < 10) {
            return 10;
        }
        return temperature;
    }
}
""",
            },
        ),
        SyntheticSubmission(
            submission_id="TEMP_SPLIT",
            files={
                "MinimumRule.java": """
class MinimumRule {
    int raiseMinimum(int temperature) {
        if (temperature < 10) {
            return 10;
        }
        return temperature;
    }
}
""",
                "FreezingDistance.java": """
class FreezingDistance {
    int distanceFromFreezing(int temperature) {
        int distance = temperature - 32;
        return distance;
    }
}
""",
            },
        ),
    )


def _family_related_pairs(
    prefix: str,
) -> tuple[BenchmarkPair, ...]:
    base = f"{prefix}_BASE"

    return (
        BenchmarkPair(
            left_submission_id=base,
            right_submission_id=f"{prefix}_RENAMED",
            related=True,
            transformation=(
                TransformationKind.IDENTIFIER_RENAME
            ),
        ),
        BenchmarkPair(
            left_submission_id=base,
            right_submission_id=f"{prefix}_REORDERED",
            related=True,
            transformation=(
                TransformationKind.METHOD_REORDER
            ),
        ),
        BenchmarkPair(
            left_submission_id=base,
            right_submission_id=f"{prefix}_SPLIT",
            related=True,
            transformation=(
                TransformationKind.CLASS_SPLIT
            ),
        ),
    )


def scaled_cohort() -> ScaledCohort:
    """Return the fixed 16-submission scaled evaluation cohort."""
    submissions = (
        *_price_family(),
        *_score_family(),
        *_stock_family(),
        *_temperature_family(),
    )

    related_pairs = (
        *_family_related_pairs("PRICE"),
        *_family_related_pairs("SCORE"),
        *_family_related_pairs("STOCK"),
        *_family_related_pairs("TEMP"),
    )

    return ScaledCohort(
        submissions=submissions,
        related_pairs=related_pairs,
    )
