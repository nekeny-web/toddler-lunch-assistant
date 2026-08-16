"""
Transcription Handler Module
Simulates voice-to-text transcription with VERIFICATION.
Grandma reviews what the app heard and confirms/edits it.
This is the product-layer response to transcription errors (A2 response #3).
"""

import json
from typing import Dict, List, Tuple


class TranscriptionHandler:
    def __init__(self):
        """Initialize the transcription handler."""
        self.last_transcription = None
        self.languages_supported = ["English", "Chinese (Mandarin)"]

    def simulate_voice_input(
        self,
        user_input: str,
        language: str = "English",
        introduce_error: bool = False
    ) -> str:
        """
        Simulate voice transcription (for testing).
        In production, this would call Google Cloud Speech-to-Text or similar.

        Args:
            user_input: What the user said (simulated voice)
            language: Language spoken
            introduce_error: For testing, deliberately introduce a transcription error

        Returns:
            Transcribed text (may contain errors)
        """
        # In real implementation, this would:
        # 1. Send audio to speech-to-text API
        # 2. Receive transcript
        # 3. Return the text

        transcription = user_input

        # Simulate occasional transcription errors (for testing A2 response #3)
        if introduce_error:
            common_mishears = {
                "chicken": ["kitchen", "chiffon"],
                "apple": ["maple", "apple"],
                "carrot": ["karate", "carrot"],
                "peas": ["peace", "bees"],
            }

            for correct, errors in common_mishears.items():
                if correct in user_input.lower():
                    transcription = user_input.lower().replace(
                        correct, errors[0]
                    )
                    break

        self.last_transcription = transcription
        return transcription

    def present_transcription_for_verification(
        self,
        transcription: str
    ) -> Tuple[bool, List[str]]:
        """
        Present what the app heard to Grandma.
        She reviews and either confirms or corrects.
        This implements A2 response #3: Transcription Verification.

        Args:
            transcription: Raw transcription from voice input

        Returns:
            (is_confirmed: bool, ingredient_list: List[str])
        """
        print("\n" + "=" * 50)
        print("🎤 TRANSCRIPTION REVIEW")
        print("=" * 50)
        print(f"\nI heard you say:\n  '{transcription}'")
        print("\nPlease review the ingredients list below:")
        print("=" * 50)

        # Parse ingredients from transcription
        ingredients = self._parse_ingredients(transcription)

        for i, ingredient in enumerate(ingredients, 1):
            print(f"  {i}. {ingredient}")

        print("\n" + "=" * 50)
        response = input("Is this correct? (yes/no/edit): ").lower().strip()

        if response == "yes":
            return True, ingredients
        elif response == "edit":
            ingredients = self._get_manual_edits(ingredients)
            return True, ingredients
        else:
            # Grandma wants to re-record
            return False, ingredients

    def _parse_ingredients(self, transcription: str) -> List[str]:
        """
        Parse a list of ingredients from transcription.
        Simple split by comma, "and", or "or".

        Args:
            transcription: Raw transcription text

        Returns:
            List of ingredient strings
        """
        # Replace common separators
        text = transcription.replace(" and ", ", ")
        text = text.replace(" or ", ", ")

        # Split by comma and clean up
        ingredients = [ing.strip() for ing in text.split(",")]
        ingredients = [ing for ing in ingredients if ing]

        return ingredients

    def _get_manual_edits(self, ingredients: List[str]) -> List[str]:
        """
        Let Grandma manually edit the ingredient list.

        Args:
            ingredients: Current list to edit

        Returns:
            Updated ingredient list
        """
        print("\nEdit mode:")
        print("  - Type ingredient number to delete (e.g., '2')")
        print("  - Type new ingredient to add (e.g., 'rice')")
        print("  - Type 'done' when finished")
        print()

        while True:
            command = input("Edit > ").lower().strip()

            if command == "done":
                break
            elif command.isdigit():
                idx = int(command) - 1
                if 0 <= idx < len(ingredients):
                    removed = ingredients.pop(idx)
                    print(f"✅ Removed '{removed}'")
            else:
                # Add new ingredient
                ingredients.append(command)
                print(f"✅ Added '{command}'")

        return ingredients

    def verify_multilingual_transcription(
        self,
        audio_language: str,
        transcription: str
    ) -> Dict[str, any]:
        """
        For Chinese + English multilingual support (C1 tradeoff #3).
        Return confidence metrics for the transcription.

        Args:
            audio_language: Language detected
            transcription: Transcribed text

        Returns:
            Dict with language info and confidence
        """
        # Simulate language detection
        if any(char.ord() > 127 for char in transcription):
            detected_language = "Chinese"
            confidence = 0.92
        else:
            detected_language = "English"
            confidence = 0.95

        return {
            "expected_language": audio_language,
            "detected_language": detected_language,
            "confidence": confidence,
            "transcription": transcription,
            "status": "high_confidence" if confidence > 0.85 else "needs_review"
        }

    def build_ingredients_dict(self, ingredient_list: List[str]) -> Dict[str, List[str]]:
        """
        Convert ingredient list to categorized dictionary for meal assembly.
        Simple heuristic: if ingredient sounds like a protein/veggie/etc, categorize it.

        Args:
            ingredient_list: List of ingredients Grandma confirmed

        Returns:
            Dict with categories
        """
        ingredient_dict = {
            "protein": [],
            "veggie": [],
            "starch": [],
            "fruit": [],
            "drink": []
        }

        # Simple categorization heuristic
        proteins = ["chicken", "turkey", "beef", "fish", "egg", "yogurt", "cheese", "tofu"]
        veggies = ["carrot", "peas", "corn", "broccoli", "spinach", "squash", "beans"]
        starches = ["rice", "pasta", "bread", "potato", "oatmeal"]
        fruits = ["apple", "banana", "orange", "berry", "peach", "pear"]
        drinks = ["milk", "water", "juice", "coconut"]

        for ingredient in ingredient_list:
            ingredient_lower = ingredient.lower().strip()

            if any(p in ingredient_lower for p in proteins):
                ingredient_dict["protein"].append(ingredient)
            elif any(v in ingredient_lower for v in veggies):
                ingredient_dict["veggie"].append(ingredient)
            elif any(s in ingredient_lower for s in starches):
                ingredient_dict["starch"].append(ingredient)
            elif any(f in ingredient_lower for f in fruits):
                ingredient_dict["fruit"].append(ingredient)
            elif any(d in ingredient_lower for d in drinks):
                ingredient_dict["drink"].append(ingredient)

        return ingredient_dict

    def print_transcription_summary(self, ingredients: List[str]) -> None:
        """Print a summary of confirmed ingredients."""
        print("\n" + "=" * 50)
        print("✅ INGREDIENTS CONFIRMED")
        print("=" * 50)
        for ing in ingredients:
            print(f"  • {ing}")
        print("=" * 50 + "\n")
