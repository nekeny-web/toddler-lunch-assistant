"""
Preference Model Module
Learns and manages toddler food preferences.
Requires HUMAN CONFIRMATION before acting on preferences (Recommend autonomy).
"""

import json
from typing import Dict, List, Set
from datetime import datetime


class PreferenceModel:
    def __init__(self, preferences_path: str = None):
        """
        Initialize the preference model.

        Args:
            preferences_path: Path to JSON file with past preferences
        """
        self.preferences = self._load_preferences(preferences_path)
        self.confirmed = False  # Must be manually confirmed each session

    def _load_preferences(self, path: str = None) -> Dict[str, List[str]]:
        """Load preferences from file or start with defaults."""
        if path:
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                pass

        # Default preferences for a 22-month-old (typical picky eater)
        return {
            "likes": [
                "chicken", "pasta", "rice", "apples", "banana",
                "yogurt", "cheese", "bread", "sweet potato", "peas"
            ],
            "dislikes": [
                "broccoli", "spinach", "tomatoes", "beans", "mushrooms"
            ],
            "never_tried": [
                "salmon", "avocado", "kale", "lentils", "quinoa"
            ]
        }

    def get_detected_pattern(self) -> Dict[str, List[str]]:
        """
        Return the detected preference pattern.
        This is what Grandma will review and confirm.

        Returns:
            Dictionary of likes/dislikes/never_tried
        """
        return {
            "likes": self.preferences.get("likes", []),
            "dislikes": self.preferences.get("dislikes", []),
            "never_tried": self.preferences.get("never_tried", [])
        }

    def confirm_preferences(self, pattern: Dict[str, List[str]]) -> None:
        """
        Grandma reviews and confirms (or adjusts) the preference pattern.
        This is the RECOMMEND autonomy level - human judgment gates the model.

        Args:
            pattern: Dict with 'likes', 'dislikes', 'never_tried'
        """
        self.preferences = pattern
        self.confirmed = True
        print("\n✅ Preferences confirmed by Grandma")
        print(f"   Likes: {', '.join(self.preferences.get('likes', []))}")
        print(f"   Dislikes: {', '.join(self.preferences.get('dislikes', []))}")

    def adjust_preference(self, ingredient: str, action: str) -> None:
        """
        Grandma manually adjusts a preference (move ingredient between categories).

        Args:
            ingredient: Food item to adjust
            action: 'like', 'dislike', or 'never_tried'
        """
        ingredient = ingredient.lower().strip()

        # Remove from other categories
        for category in self.preferences.keys():
            if ingredient in self.preferences[category]:
                self.preferences[category].remove(ingredient)

        # Add to new category
        if action in self.preferences:
            if ingredient not in self.preferences[action]:
                self.preferences[action].append(ingredient)
                print(f"✅ {ingredient} moved to '{action}'")

    def predict_will_eat(self, ingredient: str) -> float:
        """
        Estimate probability the toddler will eat this ingredient (0-1).
        Only used if preferences are confirmed.

        Args:
            ingredient: Food item to predict

        Returns:
            Confidence score (0.0 = won't eat, 1.0 = will eat, 0.5 = unknown)
        """
        if not self.confirmed:
            return 0.5  # Unknown until confirmed

        ingredient_lower = ingredient.lower().strip()

        # Check likes
        for liked in self.preferences.get("likes", []):
            if liked.lower() in ingredient_lower or ingredient_lower in liked.lower():
                return 0.85  # High confidence he'll eat it

        # Check dislikes
        for disliked in self.preferences.get("dislikes", []):
            if disliked.lower() in ingredient_lower or ingredient_lower in disliked.lower():
                return 0.1  # Low confidence he'll eat it

        # Check never_tried
        for untried in self.preferences.get("never_tried", []):
            if untried.lower() in ingredient_lower or ingredient_lower in untried.lower():
                return 0.5  # Unknown - new food

        return 0.5  # Default: unknown

    def filter_by_preference(self, ingredients: List[str]) -> List[str]:
        """
        Filter a list of ingredients based on confirmed preferences.

        Args:
            ingredients: List of potential ingredients

        Returns:
            List of ingredients ranked by likelihood of being eaten
        """
        if not self.confirmed:
            return ingredients  # Can't filter without confirmation

        # Sort by predict_will_eat score
        ranked = sorted(
            ingredients,
            key=lambda x: self.predict_will_eat(x),
            reverse=True
        )

        return ranked

    def print_preference_summary(self) -> None:
        """Print a human-readable preference summary."""
        print("\n📋 DETECTED PREFERENCE PATTERN")
        print("=" * 50)
        print(f"\nLikes: {', '.join(self.preferences.get('likes', []))}")
        print(f"Dislikes: {', '.join(self.preferences.get('dislikes', []))}")
        print(f"Never tried: {', '.join(self.preferences.get('never_tried', []))}")
        print("\nStatus: ", end="")
        if self.confirmed:
            print("✅ CONFIRMED by Grandma")
        else:
            print("⏳ PENDING Grandma's approval")
        print("=" * 50)

    def save_preferences(self, path: str) -> None:
        """Save current preferences to a JSON file."""
        with open(path, 'w') as f:
            json.dump(self.preferences, f, indent=2)
        print(f"✅ Preferences saved to {path}")
