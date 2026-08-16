"""
Toddler Lunch Planning Assistant
Web UI (Streamlit) — same modules and logic as app.py, adapted from CLI input()
prompts to browser widgets so it can be deployed as a shareable web app.
"""

import streamlit as st

from safety_filter import SafetyFilter
from preference_model import PreferenceModel
from meal_assembler import MealAssembler
from transcription_handler import TranscriptionHandler

st.set_page_config(page_title="Toddler Lunch Assistant", page_icon="🍽️", layout="centered")


def get_modules():
    if "safety_filter" not in st.session_state:
        st.session_state.safety_filter = SafetyFilter()
    if "preference_model" not in st.session_state:
        st.session_state.preference_model = PreferenceModel()
    if "meal_assembler" not in st.session_state:
        st.session_state.meal_assembler = MealAssembler()
    if "transcription_handler" not in st.session_state:
        st.session_state.transcription_handler = TranscriptionHandler()
    return (
        st.session_state.safety_filter,
        st.session_state.preference_model,
        st.session_state.meal_assembler,
        st.session_state.transcription_handler,
    )


safety_filter, preference_model, meal_assembler, transcription_handler = get_modules()

if "step" not in st.session_state:
    st.session_state.step = "input"
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []
if "meal" not in st.session_state:
    st.session_state.meal = None


def reset_flow():
    st.session_state.step = "input"
    st.session_state.ingredients = []
    st.session_state.meal = None
    st.session_state.pop("raw_ingredients", None)


def render_meal_card(meal):
    meal_with_portions = meal_assembler.verify_portions(meal)
    cols = st.columns(5)
    for col, (component, info) in zip(cols, meal_with_portions.items()):
        with col:
            st.markdown(f"**{component.title()}**")
            st.write(info["ingredient"])
            st.caption(info["portion"])


st.title("🍽️ Toddler Lunch Planning Assistant")
st.caption("A smarter, faster way to plan healthy, age-appropriate lunches for picky toddlers.")

page = st.sidebar.radio(
    "Menu",
    [
        "🌅 Morning Lunch Planning",
        "📊 Run Evaluation",
        "🔧 Test Safety Filter",
        "📋 View/Adjust Preferences",
        "🍽️ Fallback Meal",
    ],
)

# ---------------------------------------------------------------------------
# 1. Morning Lunch Planning
# ---------------------------------------------------------------------------
if page == "🌅 Morning Lunch Planning":
    st.header("Good morning! Let's plan today's lunch.")

    if st.session_state.step == "input":
        st.subheader("Step 1: What do you have in the fridge?")
        with st.form("ingredients_form"):
            text = st.text_input(
                "Ingredients (comma separated)",
                placeholder="chicken, peas, rice, apple, milk",
            )
            submitted = st.form_submit_button("Continue")
        if submitted:
            if not text.strip():
                st.session_state.meal = meal_assembler.build_balanced_meal(
                    {}, preference_model=preference_model
                )
                is_safe, _ = safety_filter.validate_meal(st.session_state.meal)
                st.session_state.step = "result"
                st.session_state.safety_ok = is_safe
            else:
                transcription = transcription_handler.simulate_voice_input(
                    text, language="English"
                )
                st.session_state.raw_ingredients = transcription_handler._parse_ingredients(
                    transcription
                )
                st.session_state.step = "review"
            st.rerun()

    elif st.session_state.step == "review":
        st.subheader("🎤 Step 2: Transcription Review")
        raw = st.session_state.get("raw_ingredients", [])
        st.write("I heard:")
        for i, ing in enumerate(raw, 1):
            st.write(f"{i}. {ing}")
        edited = st.text_area(
            "Edit if anything looks wrong (comma separated)", value=", ".join(raw)
        )
        col1, col2 = st.columns(2)
        if col1.button("✅ Confirm ingredients", use_container_width=True):
            st.session_state.ingredients = [i.strip() for i in edited.split(",") if i.strip()]
            st.session_state.step = "preferences"
            st.rerun()
        if col2.button("🔄 Start over", use_container_width=True):
            reset_flow()
            st.rerun()

    elif st.session_state.step == "preferences":
        st.subheader("📋 Step 3: Preference Check")
        pattern = preference_model.get_detected_pattern()
        st.write(f"**Likes:** {', '.join(pattern['likes'])}")
        st.write(f"**Dislikes:** {', '.join(pattern['dislikes'])}")
        st.write(f"**Never tried:** {', '.join(pattern['never_tried'])}")
        st.caption(
            "✅ Confirmed"
            if preference_model.confirmed
            else "⏳ Pending your confirmation"
        )

        if st.button("✅ Looks right — confirm preferences"):
            preference_model.confirm_preferences(pattern)
            st.session_state.step = "generate"
            st.rerun()

        with st.expander("Adjust a preference"):
            ing = st.text_input("Ingredient", key="adj_ing")
            action = st.selectbox(
                "Mark as", ["likes", "dislikes", "never_tried"], key="adj_action"
            )
            if st.button("Apply adjustment") and ing.strip():
                preference_model.adjust_preference(ing, action)
                st.success(f"'{ing}' moved to '{action}'")
                st.rerun()

    elif st.session_state.step == "generate":
        st.subheader("⏳ Step 4: Generating meal...")
        available = transcription_handler.build_ingredients_dict(st.session_state.ingredients)
        meal = meal_assembler.build_balanced_meal(available, preference_model=preference_model)

        is_safe, failures = safety_filter.validate_meal(meal)
        if not is_safe:
            st.warning("Unsafe ingredients detected — swapping for safe alternatives:")
            for failure in failures:
                st.write(f"- {failure}")
            for component in list(meal.keys()):
                ok, _ = safety_filter.validate_ingredient(meal[component])
                if not ok:
                    alts = safety_filter.get_safe_alternatives(meal[component])
                    if alts:
                        meal[component] = alts[0]
            is_safe, failures = safety_filter.validate_meal(meal)

        if not is_safe:
            st.error("Could not make this meal safe — using fallback instead.")
            meal = {
                "protein": "Chicken nuggets (store-bought, safe)",
                "veggie": "Steamed peas",
                "starch": "Rice",
                "fruit": "Apple slices",
                "drink": "Milk",
            }

        st.session_state.meal = meal
        st.session_state.safety_ok = is_safe
        st.session_state.step = "result"
        st.rerun()

    elif st.session_state.step == "result":
        meal = st.session_state.meal
        if st.session_state.get("safety_ok", True):
            st.success("✅ Safety verified!")
        st.subheader("Today's Lunch Suggestion")
        render_meal_card(meal)

        st.subheader("Final Step: Quantity Check")
        enough = st.radio(
            "Do you have enough of each ingredient to pack?", ["Yes", "No"], horizontal=True
        )
        if enough == "No":
            component = st.selectbox("Which ingredient is short?", list(meal.keys()))
            if st.button("Find a swap"):
                alternative = meal_assembler.suggest_alternative_for_component(
                    component, meal.get(component, "unknown"), preference_model
                )
                if alternative:
                    meal[component] = alternative
                    st.session_state.meal = meal
                    st.success(f"Swapped {component} → {alternative}")
                    st.rerun()

        if st.button("🎉 Lunch is packed — plan another"):
            reset_flow()
            st.rerun()

# ---------------------------------------------------------------------------
# 2. Run Evaluation
# ---------------------------------------------------------------------------
elif page == "📊 Run Evaluation":
    st.header("📊 Evaluation Mode")
    st.caption("Tests A3 accuracy metrics: safety filter precision and meal balance.")

    num_meals = st.number_input("How many test meals?", min_value=1, max_value=100, value=10)

    if st.button("Run evaluation"):
        safety_passes = 0
        balance_passes = 0
        test_results = []

        for i in range(num_meals):
            meal = meal_assembler.build_balanced_meal({}, preference_model=preference_model)
            is_safe, _ = safety_filter.validate_meal(meal)
            is_balanced = all(meal.values())

            if is_safe:
                safety_passes += 1
            if is_balanced:
                balance_passes += 1

            test_results.append({"meal_id": i + 1, "meal": meal, "safe": is_safe, "balanced": is_balanced})

        col1, col2 = st.columns(2)
        with col1:
            pct = 100 * safety_passes // num_meals
            st.metric("Safety Filter Precision", f"{safety_passes}/{num_meals} ({pct}%)")
            st.caption("Target: 100% | Minimum bar: 99%")
            st.write("✅ PASS" if safety_passes == num_meals else "❌ NEEDS WORK")
        with col2:
            pct_b = 100 * balance_passes // num_meals
            st.metric("Meal Balance", f"{balance_passes}/{num_meals} ({pct_b}%)")
            st.caption("Target: 95% | Minimum bar: 85%")
            st.write("✅ PASS" if balance_passes >= int(0.95 * num_meals) else "❌ NEEDS WORK")

        st.subheader("Sample meals")
        for result in test_results[:3]:
            st.write(
                f"**Meal {result['meal_id']}**: {result['meal']} — "
                f"Safe: {'✅' if result['safe'] else '❌'} | Balanced: {'✅' if result['balanced'] else '❌'}"
            )

# ---------------------------------------------------------------------------
# 3. Test Safety Filter
# ---------------------------------------------------------------------------
elif page == "🔧 Test Safety Filter":
    st.header("🔒 Safety Filter Test")
    ingredient = st.text_input("Test ingredient")
    if ingredient:
        is_safe, reason = safety_filter.validate_ingredient(ingredient)
        if is_safe:
            st.success(f"✅ SAFE: {reason}")
        else:
            st.error(f"❌ UNSAFE: {reason}")
            alts = safety_filter.get_safe_alternatives(ingredient)
            if alts:
                st.info(f"Try instead: {', '.join(alts)}")

# ---------------------------------------------------------------------------
# 4. View/Adjust Preferences
# ---------------------------------------------------------------------------
elif page == "📋 View/Adjust Preferences":
    st.header("📋 Preference Management")
    pattern = preference_model.get_detected_pattern()
    st.write(f"**Likes:** {', '.join(pattern['likes'])}")
    st.write(f"**Dislikes:** {', '.join(pattern['dislikes'])}")
    st.write(f"**Never tried:** {', '.join(pattern['never_tried'])}")
    st.caption("✅ Confirmed" if preference_model.confirmed else "⏳ Pending confirmation")

    if st.button("Confirm these preferences"):
        preference_model.confirm_preferences(pattern)
        st.rerun()

    st.subheader("Adjust a preference")
    ing = st.text_input("Ingredient to adjust")
    action = st.selectbox("Mark as", ["likes", "dislikes", "never_tried"])
    if st.button("Apply") and ing.strip():
        preference_model.adjust_preference(ing, action)
        st.rerun()

# ---------------------------------------------------------------------------
# 5. Fallback Meal
# ---------------------------------------------------------------------------
elif page == "🍽️ Fallback Meal":
    st.header("⚡ Quick Suggestion (Safe Fallback Meal)")
    st.caption("Pre-built safe meal for when the app stalls or you just need a fast answer.")

    fallback = {
        "protein": "Chicken nuggets (store-bought, safe)",
        "veggie": "Steamed peas",
        "starch": "Rice",
        "fruit": "Apple slices",
        "drink": "Milk",
    }
    render_meal_card(fallback)

    is_safe, _ = safety_filter.validate_meal(fallback)
    if is_safe:
        st.success("✅ This meal is safe and ready to pack!")
    else:
        st.error("⚠️ Even the fallback has issues — please contact support.")
