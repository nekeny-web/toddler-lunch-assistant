# Toddler Lunch Planning Assistant

A smarter, faster way for caregivers to plan healthy, age-appropriate lunches for picky 22-month-olds.

## Overview

This tool solves a specific problem: **"It's 8am, I need to pack lunch, and I can't decide what to make."**

Built on the **IMPACT Framework** (Module 4: Accuracy & Cost), this assistant focuses on:

- 🔒 **Safety First** — Hard validator ensures only age-appropriate foods are suggested
- 🎯 **Preference Learning** — Learns what your toddler likes and dislikes
- ⚡ **Speed** — Generates a complete meal suggestion in under 2 minutes
- 🌍 **Multilingual** — Supports English and Chinese voice input

## Features

### Core Functionality

1. **Voice Input** (Simulated in v1)
   - Say what you have in the fridge
   - System transcribes and asks you to verify
   - Human-in-the-loop transcription verification

2. **Safety Filter** (Hard Validator)
   - Rules-based check for unsafe foods (choking hazards, allergens, toxins)
   - Blocks any meal containing unsafe ingredients
   - Suggests safe alternatives automatically

3. **Preference Learning**
   - Detects food preferences from past meals
   - Shows pattern to caregiver for confirmation
   - Learns likes, dislikes, and never-tried foods

4. **Meal Assembly**
   - Builds complete, balanced meals
   - One item from each category: protein + veggie + starch + fruit + drink
   - Prioritizes preferred foods

5. **Fallback Meal** (For App Stalls)
   - Pre-built safe meal if the app is slow
   - Always validated against safety filter
   - Gets the job done in the morning rush

## Product Architecture

### Modules

| Module | Purpose | A2 Response |
|---|---|---|
| `safety_filter.py` | Rules-based safety validator | Hard filter validates before meal suggestion |
| `preference_model.py` | Preference learning & confirmation | Human confirmation gates preference model |
| `meal_assembler.py` | Balanced meal building | Builds from available ingredients + preferences |
| `transcription_handler.py` | Voice transcription verification | User reviews & confirms transcribed ingredients |
| `app.py` | Main CLI application | Orchestrates full morning flow |

### Autonomy Levels

- **Validator** (Safety Filter): Non-negotiable, runs before any output
- **Recommend** (Preferences): AI detects pattern, human confirms before acting
- **Act** (Meal Assembly): AI generates meal autonomously after preferences confirmed
- **Human** (Quantity Verification): Caregiver manually checks fridge

## Running the Tool

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/toddler-lunch-assistant.git
cd toddler-lunch-assistant

# No external dependencies needed for v1
# Python 3.8+ only
```

### Usage

```bash
# Run the interactive menu
python app.py
```

### Menu Options

1. **🌅 Morning Lunch Planning** — Run the main flow (what you use every day)
2. **📊 Run Evaluation** — Test A3 accuracy metrics (safety, balance)
3. **🔧 Test Safety Filter** — Try individual ingredients
4. **📋 View/Adjust Preferences** — Review and edit preferences
5. **🍽️  Suggest Fallback Meal** — See the quick safe meal
6. **❌ Exit**

## IMPACT Framework Integration

This tool implements decisions from Sections 1-5 of the IMPACT Living Document:

### Section 4: Accuracy & Safety

- **A1 Failure Modes** ✅
  - Safety filter misses choking hazard
  - Preference model learns wrong
  - Transcription errors corrupt list
  - Portion estimates way off
  - App timing fails in morning rush

- **A2 Product-Layer Responses** ✅
  - Hard validator + "Safety verified" badge
  - Human preference confirmation before acting
  - Transcription verification before use
  - Fallback meal for app stalls
  - Cached quick meal option

- **A3 Eval Plan** ✅
  - **Metric:** Meal nutritional balance
  - **Target:** 95% (all 5 categories + portions)
  - **Minimum bar:** 85%
  - **Measurement:** 50-meal pilot review

- **A4 Uncomfortable Question** ✅
  - Worst case: Safety filter fails → toddler chokes → emergency ER visit
  - Response: Non-negotiable validator, 99%+ precision, human oversight

### Section 5: Cost & Constraints

- **C1 Tradeoffs** ✅
  - Accuracy over speed (manual preference confirmation)
  - Consistency over variety (smaller trusted meal set)
  - Multilingual from day one (added dev overhead)

- **C2 Latency Budget** ✅
  - Voice transcription: 3 seconds
  - Preference UI: 2 seconds
  - Meal generation: 3 seconds
  - Full flow: <2 minutes
  - App launch: 5 seconds

- **C3 70/30 Split** ✅
  - **70% Validated:** Voice API, rules-based safety, meal logic, UI patterns
  - **30% Experimental:** Preference learning model, multilingual accuracy, preference shifts

- **C4 Cut List** ✅
  - Feedback loop (Step 6) — v2
  - Inventory tracking (Step 7) — v2
  - Grocery shopping (Step 8) — v2

## File Structure

```
toddler-lunch-assistant/
├── app.py                    # Main CLI application
├── safety_filter.py          # Safety validator module
├── preference_model.py        # Preference learning module
├── meal_assembler.py          # Meal assembly module
├── transcription_handler.py   # Transcription verification module
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git configuration
└── data/
    ├── unsafe_foods.json      # (Optional) Unsafe foods list
    ├── safe_meals.json        # (Optional) Pre-built meals
    └── preferences.json       # (Optional) Sample preferences
```

## Data Format

### Preference Model (JSON)

```json
{
  "likes": ["chicken", "pasta", "apples", "banana"],
  "dislikes": ["broccoli", "spinach"],
  "never_tried": ["salmon", "avocado"]
}
```

### Safety Filter (JSON)

```json
{
  "choking_hazards": ["whole grapes", "nuts", "hard carrots"],
  "allergens_and_toxins": ["honey", "peanuts", "shellfish"],
  "choking_textures": ["sticky foods", "hard foods"],
  "high_risk_foods": ["spicy foods", "fried foods"]
}
```

### Meal Database (JSON)

```json
{
  "proteins": ["chicken", "beef", "fish", "eggs"],
  "veggies": ["peas", "corn", "carrots", "squash"],
  "starches": ["rice", "pasta", "bread", "potato"],
  "fruits": ["apple", "banana", "watermelon"],
  "drinks": ["milk", "water", "diluted juice"]
}
```

## v1 Scope (What's Included)

✅ Step 3 of caregiver journey: "Decide what to make from what we have"

✅ Safety validator (hard filter for age-appropriate foods)

✅ Preference learning & confirmation (human gates AI)

✅ Balanced meal assembly (5 components)

✅ Transcription verification (human reviews before use)

✅ Fallback meal for app stalls

✅ CLI interface for testing

## v2 Roadmap (Not in v1)

- Real voice-to-text integration (Google Cloud Speech-to-Text)
- Step 6: Lunchbox feedback loop (track what he ate)
- Step 7: Inventory tracking (know when to restock)
- Step 8: Grocery shopping assistance
- Web/mobile app UI
- Multi-child support
- Nutritional tracking over time
- Daycare menu integration

## Testing

Run the evaluation mode to test accuracy metrics:

```bash
python app.py
# Choose option 2: Run Evaluation
```

This generates test meals and measures:
- Safety filter precision
- Meal nutritional balance
- Other A3 metrics

## Latency Performance

Target latencies (C2):

| Operation | Budget | Current |
|---|---|---|
| Voice transcription | 3s | ~0.5s (simulated) |
| Preference UI | 2s | Instant |
| Meal generation | 3s | ~0.5s |
| Full flow | <2 min | ~1-2 min |
| App launch | 5s | Instant |

## Safety Guarantees

🔒 **The safety filter is non-negotiable.**

- Runs on every meal before it reaches the user
- Blocks unsafe foods (choking hazards, allergens, toxins)
- Suggests safe alternatives automatically
- Target precision: 100% (zero unsafe foods slip through)
- Minimum bar: 99%

If the safety filter ever fails, do not use the meal suggestion.

## Contributing

This is a prototype built for the IMPACT Framework Module 4. Contributions welcome!

Areas for improvement:
- Real voice transcription (currently simulated)
- Machine learning for preference prediction
- Multilingual support beyond Chinese/English
- Mobile app frontend
- Real-time nutrition calculation

## License

MIT License — See LICENSE file

## Contact

Built as part of TMMBA 522 (Builder OS project).

Questions? Check the IMPACT Living Document (Sections 1-5) for product decisions.

---

**Last Updated:** August 15, 2026

**Version:** 0.1 (MVP)

**Status:** 🚀 Ready for testing
