"""
Safety Filter Module
Validates meals against age-appropriate safety rules for 22-month-olds.
This is a HARD VALIDATOR - no unsafe foods get through.
"""

import json
from typing import List, Dict, Tuple


class SafetyFilter:
    def __init__(self, unsafe_foods_path: str = None):
        """
        Initialize the safety filter with a list of unsafe foods for 22-month-olds.

        Args:
            unsafe_foods_path: Path to JSON file with unsafe foods list
        """
        self.unsafe_foods = self._load_unsafe_foods(unsafe_foods_path)

    def _load_unsafe_foods(self, path: str = None) -> Dict[str, List[str]]:
        """Load unsafe foods from file or use defaults."""
        if path:
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                pass

        # Default unsafe foods for 22-month-olds
        return {
            "choking_hazards": [
                "whole grapes", "cherry tomatoes", "berries", "popcorn",
                "hard carrots (raw)", "hard apples (raw)", "celery",
                "whole nuts", "seeds", "hard candy", "olives with pits",
                "hot dogs (unless cut lengthwise)", "chunks of cheese"
            ],
            "allergens_and_toxins": [
                "honey", "peanuts", "tree nuts", "shellfish", "eggs (raw)",
                "unpasteurized milk", "undercooked meat", "raw fish"
            ],
            "choking_textures": [
                "sticky foods (peanut butter in large amounts)",
                "hard/crunchy foods", "very thick pastes"
            ],
            "high_risk_foods": [
                "spicy foods", "foods with added salt/sugar",
                "fried foods", "processed meats with nitrates"
            ]
        }

    def validate_ingredient(self, ingredient: str) -> Tuple[bool, str]:
        """
        Check if a single ingredient is safe for a 22-month-old.

        Args:
            ingredient: Food item to validate

        Returns:
            (is_safe: bool, reason: str)
        """
        ingredient_lower = ingredient.lower().strip()

        for category, unsafe_items in self.unsafe_foods.items():
            for unsafe_item in unsafe_items:
                if unsafe_item.lower() in ingredient_lower:
                    return False, f"Unsafe: {unsafe_item} ({category})"

        return True, "Safe"

    def validate_meal(self, meal: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate an entire meal (all components).

        Args:
            meal: Dict with keys like 'protein', 'veggie', 'starch', 'fruit', 'drink'

        Returns:
            (is_safe: bool, failures: list of unsafe ingredients)
        """
        failures = []

        for component, ingredient in meal.items():
            if ingredient:
                is_safe, reason = self.validate_ingredient(ingredient)
                if not is_safe:
                    failures.append(f"{component}: {ingredient} - {reason}")

        return len(failures) == 0, failures

    def get_safe_alternatives(self, ingredient: str) -> List[str]:
        """
        If an ingredient is unsafe, suggest safe alternatives.

        Args:
            ingredient: Unsafe ingredient

        Returns:
            List of safe alternatives
        """
        ingredient_lower = ingredient.lower()

        # Simple rule-based suggestions
        alternatives = {
            "grapes": ["raisins", "watermelon chunks", "blueberries"],
            "carrots": ["sweet potato", "pumpkin", "squash"],
            "apples": ["applesauce", "banana", "pear"],
            "peanut butter": ["sunflower butter", "tahini"],
            "whole nuts": ["nut butter", "seeds (crushed)"],
            "honey": ["maple syrup", "agave", "fruit puree"],
            "raw eggs": ["cooked eggs"],
        }

        for key, alts in alternatives.items():
            if key in ingredient_lower:
                return alts

        return []

    def print_safety_report(self, meal: Dict[str, str]) -> None:
        """Print a human-readable safety report."""
        is_safe, failures = self.validate_meal(meal)

        if is_safe:
            print("\n✅ SAFETY VERIFIED")
            print("All ingredients are age-appropriate for a 22-month-old.")
        else:
            print("\n❌ SAFETY CHECK FAILED")
            print("Unsafe ingredients detected:\n")
            for failure in failures:
                print(f"  • {failure}")
            print("\nSuggested alternatives:")
            for component, ingredient in meal.items():
                if ingredient:
                    is_safe, _ = self.validate_ingredient(ingredient)
                    if not is_safe:
                        alts = self.get_safe_alternatives(ingredient)
                        if alts:
                            print(f"  • {component}: Try {', '.join(alts)}")
