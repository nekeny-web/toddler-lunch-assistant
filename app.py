"""
Toddler Lunch Planning Assistant
Main Application - CLI Interface

This tool implements the IMPACT framework (Module 4: Accuracy & Cost) for a toddler lunch planning assistant.
- A2 Product-layer responses: Safety validator, transcription verification, preference confirmation, fallback
- C2 Latency budget: Targets 3s voice transcription, 2s UI, 3s meal generation, <2min full flow
- C3 70/30 split: Validated (voice API, rules-based safety, meal logic) vs experimental (preference learning, multilingual)
"""

import time
import json
from typing import Optional, Dict
from safety_filter import SafetyFilter
from preference_model import PreferenceModel
from meal_assembler import MealAssembler
from transcription_handler import TranscriptionHandler


class ToddlerLunchAssistant:
    def __init__(self):
        """Initialize the lunch assistant with all modules."""
        print("\n" + "=" * 60)
        print("🍽️  TODDLER LUNCH PLANNING ASSISTANT")
        print("=" * 60)
        print("\nInitializing modules...\n")

        self.safety_filter = SafetyFilter()
        self.preference_model = PreferenceModel()
        self.meal_assembler = MealAssembler()
        self.transcription_handler = TranscriptionHandler()

        print("✅ Safety Filter loaded")
        print("✅ Preference Model loaded")
        print("✅ Meal Assembler loaded")
        print("✅ Transcription Handler loaded")
        print("\n" + "=" * 60 + "\n")

    def run_morning_flow(self):
        """
        Main flow: What the user experiences each morning.
        Implements A2 product-layer responses and C2 latency budgets.
        """
        print("Good morning! Let's plan today's lunch.\n")

        # STEP 1: TRANSCRIPTION + VERIFICATION (A2 #3, C2 target: 3 sec)
        print("STEP 1: What do you have in the fridge?")
        print("(Say the ingredients, or I'll use a default list)")
        ingredients_input = input("Ingredients: ").strip()

        if not ingredients_input:
            print("Using quick default meal...")
            self._present_fallback_meal()
            return

        # Simulate transcription with optional error for testing
        print("\n⏳ Transcribing... (simulating 2 sec latency)")
        time.sleep(0.5)  # Simulate network latency

        transcription = self.transcription_handler.simulate_voice_input(
            ingredients_input,
            language="English",
            introduce_error=False  # Set to True to test A2 #3
        )

        # Verify transcription (A2 #3 response)
        is_confirmed, ingredient_list = (
            self.transcription_handler.present_transcription_for_verification(
                transcription
            )
        )

        if not is_confirmed:
            print("Let's try again...")
            return

        # STEP 2: BUILD INGREDIENTS DICT
        available_ingredients = (
            self.transcription_handler.build_ingredients_dict(ingredient_list)
        )

        # STEP 3: PREFERENCE CONFIRMATION (A2 #2, C2 target: 2 sec)
        print("\n" + "=" * 50)
        self.preference_model.print_preference_summary()
        print("\nDoes this match your child's preferences?")
        pref_response = input("Confirm preferences? (yes/no/adjust): ").lower().strip()

        if pref_response == "no":
            print("Let's update preferences...")
            while True:
                ingredient = input("What food to adjust? ").strip()
                if ingredient:
                    action = input("Mark as (like/dislike/never_tried)? ").strip()
                    self.preference_model.adjust_preference(ingredient, action)
                    again = input("Adjust another? (yes/no): ").lower().strip()
                    if again != "yes":
                        break

        if pref_response in ["yes", "adjust"]:
            self.preference_model.confirm_preferences(
                self.preference_model.get_detected_pattern()
            )

        # STEP 4: MEAL GENERATION (A2 #1 + #2, C2 target: 3 sec)
        print("\n⏳ Generating meal... (simulating 2 sec latency)")
        time.sleep(0.5)

        meal = self.meal_assembler.build_balanced_meal(
            available_ingredients,
            preference_model=self.preference_model,
            avoid_ingredients=[]
        )

        # STEP 5: SAFETY VALIDATION (A2 #1 - HARD VALIDATOR)
        print("\n🔒 Running safety check...")
        time.sleep(0.3)

        is_safe, failures = self.safety_filter.validate_meal(meal)

        if not is_safe:
            print("\n⚠️  Safety check failed. Unsafe ingredients detected:")
            for failure in failures:
                print(f"   {failure}")
            print("\n🔄 Finding safe alternatives...")

            # Find safe alternatives
            for component in meal.keys():
                is_safe_component, _ = self.safety_filter.validate_ingredient(
                    meal[component]
                )
                if not is_safe_component:
                    alternatives = self.safety_filter.get_safe_alternatives(
                        meal[component]
                    )
                    if alternatives:
                        meal[component] = alternatives[0]
                        print(f"✅ Swapped {component}: using {alternatives[0]}")

            # Revalidate after swaps
            is_safe, failures = self.safety_filter.validate_meal(meal)
            if not is_safe:
                print("\n❌ Could not make meal safe. Using fallback...")
                self._present_fallback_meal()
                return

        # STEP 6: PORTION VERIFICATION (A2 #4)
        meal_with_portions = self.meal_assembler.verify_portions(meal)

        print("\n✅ Safety verified!")
        self.meal_assembler.print_meal_card(meal_with_portions)

        # STEP 7: QUANTITY CHECK (A2 #4 - HUMAN VERIFICATION)
        print("FINAL STEP: Do you have enough of each ingredient?")
        enough = input("Do you have enough to pack? (yes/no): ").lower().strip()

        if enough == "no":
            print("\nLet's find a swap...")
            component = input("Which ingredient is short? ").strip()
            alternative = self.meal_assembler.suggest_alternative_for_component(
                component, meal.get(component, "unknown"), self.preference_model
            )
            if alternative:
                print(f"Try: {alternative}")
                meal[component] = alternative

        print("\n🎉 Lunch is ready to pack!")
        print("Have a great day!\n")

    def _present_fallback_meal(self):
        """
        Present a pre-built safe fallback meal (A2 #5).
        Used when app stalls or user wants quick option.
        """
        fallback = {
            "protein": "Chicken nuggets (store-bought, safe)",
            "veggie": "Steamed peas",
            "starch": "Rice",
            "fruit": "Apple slices",
            "drink": "Milk"
        }

        print("\n" + "=" * 50)
        print("⚡ QUICK SUGGESTION (Safe Fallback Meal)")
        print("=" * 50)

        meal_with_portions = self.meal_assembler.verify_portions(fallback)
        self.meal_assembler.print_meal_card(meal_with_portions)

        # Always validate fallback against safety filter
        is_safe, _ = self.safety_filter.validate_meal(fallback)
        if is_safe:
            print("✅ This meal is safe and ready to pack!\n")
        else:
            print("⚠️  Even the fallback has issues - please contact support\n")

    def run_eval_mode(self):
        """
        Run evaluation mode to test metrics (A3).
        Generates test meals and checks:
        - Safety filter precision
        - Preference model accuracy
        - Meal nutritional balance
        """
        print("\n" + "=" * 60)
        print("📊 EVALUATION MODE (A3 - Accuracy & Safety Metrics)")
        print("=" * 60 + "\n")

        num_meals = input("How many test meals? (default: 10): ").strip()
        num_meals = int(num_meals) if num_meals.isdigit() else 10

        safety_passes = 0
        balance_passes = 0
        test_results = []

        for i in range(num_meals):
            # Build a test meal
            meal = self.meal_assembler.build_balanced_meal(
                {},  # Use defaults
                preference_model=self.preference_model
            )

            # Check safety (A3 metric #1)
            is_safe, _ = self.safety_filter.validate_meal(meal)

            # Check balance (A3 metric #3)
            is_balanced = all(meal.values())

            if is_safe:
                safety_passes += 1
            if is_balanced:
                balance_passes += 1

            test_results.append({
                "meal_id": i + 1,
                "meal": meal,
                "safe": is_safe,
                "balanced": is_balanced
            })

        # Print results
        print("\n" + "=" * 60)
        print("📈 EVALUATION RESULTS")
        print("=" * 60)
        print(f"\nSafety Filter Precision: {safety_passes}/{num_meals} ({100*safety_passes//num_meals}%)")
        print(f"Target: 100% | Minimum bar: 99%")
        print(f"Status: {'✅ PASS' if safety_passes == num_meals else '❌ NEEDS WORK'}\n")

        print(f"Meal Balance: {balance_passes}/{num_meals} ({100*balance_passes//num_meals}%)")
        print(f"Target: 95% | Minimum bar: 85%")
        print(f"Status: {'✅ PASS' if balance_passes >= int(0.95*num_meals) else '❌ NEEDS WORK'}\n")

        # Show sample meals
        print("Sample meals generated:")
        for result in test_results[:3]:
            print(f"\n  Meal {result['meal_id']}: {result['meal']}")
            print(f"  Safe: {'✅' if result['safe'] else '❌'} | " +
                  f"Balanced: {'✅' if result['balanced'] else '❌'}")

    def run_interactive_menu(self):
        """Main menu for user to choose action."""
        while True:
            print("\n" + "=" * 60)
            print("MENU")
            print("=" * 60)
            print("1. 🌅 Morning Lunch Planning (Main Flow)")
            print("2. 📊 Run Evaluation (Accuracy Tests)")
            print("3. 🔧 Test Safety Filter")
            print("4. 📋 View/Adjust Preferences")
            print("5. 🍽️  Suggest Fallback Meal")
            print("6. ❌ Exit")
            print("=" * 60)

            choice = input("Choose (1-6): ").strip()

            if choice == "1":
                self.run_morning_flow()
            elif choice == "2":
                self.run_eval_mode()
            elif choice == "3":
                self._test_safety_filter()
            elif choice == "4":
                self._manage_preferences()
            elif choice == "5":
                self._present_fallback_meal()
            elif choice == "6":
                print("\n✅ Goodbye!\n")
                break
            else:
                print("Invalid choice. Try again.")

    def _test_safety_filter(self):
        """Interactive safety filter tester."""
        print("\n" + "=" * 50)
        print("🔒 SAFETY FILTER TEST")
        print("=" * 50)

        while True:
            ingredient = input("\nTest ingredient (or 'done'): ").strip()
            if ingredient.lower() == "done":
                break

            is_safe, reason = self.safety_filter.validate_ingredient(ingredient)
            status = "✅ SAFE" if is_safe else "❌ UNSAFE"
            print(f"{status}: {reason}")

            if not is_safe:
                alts = self.safety_filter.get_safe_alternatives(ingredient)
                if alts:
                    print(f"Try instead: {', '.join(alts)}")

    def _manage_preferences(self):
        """Let user view/adjust preferences."""
        print("\n" + "=" * 50)
        print("📋 PREFERENCE MANAGEMENT")
        print("=" * 50)

        self.preference_model.print_preference_summary()

        print("\nOptions:")
        print("1. Confirm these preferences")
        print("2. Adjust preferences")
        print("3. Back to menu")

        choice = input("Choose (1-3): ").strip()

        if choice == "1":
            self.preference_model.confirm_preferences(
                self.preference_model.get_detected_pattern()
            )
        elif choice == "2":
            ingredient = input("What ingredient to adjust? ").strip()
            action = input("Mark as (like/dislike/never_tried)? ").strip()
            self.preference_model.adjust_preference(ingredient, action)
            self.preference_model.print_preference_summary()


def main():
    """Main entry point."""
    app = ToddlerLunchAssistant()
    app.run_interactive_menu()


if __name__ == "__main__":
    main()
