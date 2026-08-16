"""
Meal Assembler Module
Builds balanced, nutritionally complete meals for 22-month-olds.
Ensures one item from each category: protein + veggie + starch + fruit + drink.
"""

import json
import random
from typing import Dict, List, Optional


class MealAssembler:
    def __init__(self, meals_path: str = None):
        """
        Initialize the meal assembler with available foods.

        Args:
            meals_path: Path to JSON file with meal database
        """
        self.meal_database = self._load_meal_database(meals_path)

    def _load_meal_database(self, path: str = None) -> Dict[str, List[str]]:
        """Load meal database from file or use defaults."""
        if path:
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                pass

        # Default age-appropriate foods for 22-month-olds
        return {
            "proteins": [
                "chicken", "ground turkey", "beef", "fish",
                "eggs", "cottage cheese", "yogurt", "tofu"
            ],
            "veggies": [
                "peas", "corn", "zucchini", "squash", "sweet potato",
                "pumpkin", "green beans", "carrots (soft)", "spinach"
            ],
            "starches": [
                "pasta", "rice", "bread", "potato", "sweet potato",
                "oatmeal", "cereal", "couscous"
            ],
            "fruits": [
                "apple", "banana", "watermelon", "cantaloupe", "pear",
                "peach", "orange", "strawberry", "blueberries"
            ],
            "drinks": [
                "milk", "water", "diluted juice", "unsweetened coconut milk"
            ]
        }

    def build_balanced_meal(
        self,
        available_ingredients: Dict[str, List[str]],
        preference_model=None,
        avoid_ingredients: List[str] = None
    ) -> Dict[str, str]:
        """
        Build a balanced meal using available ingredients.

        Args:
            available_ingredients: Dict with categories and what Grandma has
            preference_model: PreferenceModel to influence choices
            avoid_ingredients: List of ingredients to avoid

        Returns:
            Dict with 'protein', 'veggie', 'starch', 'fruit', 'drink'
        """
        avoid_ingredients = avoid_ingredients or []
        meal = {}

        for category in ['protein', 'veggie', 'starch', 'fruit', 'drink']:
            # Use available ingredients if provided, else use defaults
            candidates = available_ingredients.get(category, self.meal_database.get(
                self._map_category_to_db(category), []
            ))

            # Filter out avoided ingredients
            candidates = [
                ing for ing in candidates
                if ing.lower() not in [a.lower() for a in avoid_ingredients]
            ]

            if not candidates:
                candidates = self.meal_database.get(
                    self._map_category_to_db(category), []
                )

            # Sort by preference if model is provided
            if preference_model:
                candidates = preference_model.filter_by_preference(candidates)

            # Pick the first (most preferred) ingredient
            meal[category] = candidates[0] if candidates else "unknown"

        return meal

    def _map_category_to_db(self, category: str) -> str:
        """Map meal component to database category."""
        mapping = {
            'protein': 'proteins',
            'veggie': 'veggies',
            'starch': 'starches',
            'fruit': 'fruits',
            'drink': 'drinks'
        }
        return mapping.get(category, category)

    def get_meal_from_available(
        self,
        available_ingredients: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """
        Build a meal strictly from what Grandma says is available.

        Args:
            available_ingredients: What's in the fridge (from transcription)

        Returns:
            Balanced meal using only available ingredients
        """
        meal = {}

        for category in ['protein', 'veggie', 'starch', 'fruit', 'drink']:
            db_category = self._map_category_to_db(category)
            available = available_ingredients.get(category, [])

            if available:
                meal[category] = available[0]  # Use first available
            else:
                # Fallback to database default
                defaults = self.meal_database.get(db_category, [])
                meal[category] = defaults[0] if defaults else "unknown"

        return meal

    def verify_portions(self, meal: Dict[str, str]) -> Dict[str, str]:
        """
        Add age-appropriate portion sizes to a meal.

        Returns:
            Dict with portion sizes
        """
        portions = {
            "protein": "1-2 oz (finger-sized piece)",
            "veggie": "2-3 tablespoons",
            "starch": "1/4 to 1/2 cup cooked",
            "fruit": "1/4 cup or small handful",
            "drink": "4-6 oz cup"
        }

        meal_with_portions = {}
        for component, ingredient in meal.items():
            meal_with_portions[component] = {
                "ingredient": ingredient,
                "portion": portions.get(component, "age-appropriate")
            }

        return meal_with_portions

    def print_meal_card(self, meal: Dict[str, str]) -> None:
        """Print a formatted meal suggestion."""
        print("\n" + "=" * 50)
        print("🍽️  TODAY'S LUNCH SUGGESTION")
        print("=" * 50)

        for component, ingredient in meal.items():
            print(f"\n{component.upper()}:")
            if isinstance(ingredient, dict):
                print(f"  {ingredient.get('ingredient', 'unknown')}")
                print(f"  Portion: {ingredient.get('portion', 'age-appropriate')}")
            else:
                print(f"  {ingredient}")

        print("\n" + "=" * 50)
        print("✅ Balanced meal ready to pack!")
        print("=" * 50 + "\n")

    def suggest_alternative_for_component(
        self,
        component: str,
        current_ingredient: str,
        preference_model=None
    ) -> Optional[str]:
        """
        If Grandma wants to swap one component, suggest an alternative.

        Args:
            component: 'protein', 'veggie', 'starch', 'fruit', 'drink'
            current_ingredient: Current ingredient to replace
            preference_model: Optional preference model to guide suggestions

        Returns:
            Alternative ingredient
        """
        db_category = self._map_category_to_db(component)
        candidates = self.meal_database.get(db_category, [])

        # Remove current ingredient
        candidates = [
            ing for ing in candidates
            if ing.lower() != current_ingredient.lower()
        ]

        if not candidates:
            return None

        # Sort by preference if model provided
        if preference_model:
            candidates = preference_model.filter_by_preference(candidates)

        return candidates[0]
