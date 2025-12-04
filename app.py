import streamlit as st
from owlready2 import *
from pathlib import Path
import logging
import shutil
from typing import List, Dict, Set

# -------------------------------------------------
# Basic setup
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="Financial Analysis ITS", layout="wide")

# -------------------------------------------------
# Load Ontology
# -------------------------------------------------
ONTO_FILENAME = "financial_analysis_enhanced.owl"
ONTO_PATH = Path(__file__).resolve().parent / ONTO_FILENAME

try:
    onto_path.append(str(ONTO_PATH.parent))
    onto = get_ontology(str(ONTO_PATH)).load()
except Exception as e:
    st.error(f"Failed to load ontology: {e}")
    onto = None

# Optional reasoning (quiet)
if onto:
    try:
        if shutil.which("java"):
            try:
                sync_reasoner_pellet(
                    infer_property_values=True,
                    infer_data_property_values=True
                )
                logging.info("Pellet reasoning completed.")
            except Exception as e:
                logging.warning(f"Pellet reasoning failed: {e}. Continuing without reasoning.")
    except Exception as ex:
        logging.warning(f"Reasoning error: {ex}")


# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def get_literal(entity, prop_name: str):
    """Return first literal for a given data property on an individual, or None."""
    try:
        vals = getattr(entity, prop_name)
        if vals:
            return vals[0]
    except Exception:
        return None
    return None


def is_concept(individual) -> bool:
    """Check if an individual is an instance of the Concept class."""
    try:
        return any(cls.name == "Concept" for cls in individual.is_a)
    except Exception:
        return False


def list_concepts() -> List:
    if not onto:
        return []
    return [c for c in onto.individuals() if is_concept(c)]


def get_related(entity, prop: str) -> List:
    try:
        return list(getattr(entity, prop))
    except Exception:
        return []


def get_practices(entity) -> List:
    return get_related(entity, "hasPractice")


def get_cases(entity) -> List:
    return get_related(entity, "hasCaseStudy")


def get_quizzes(entity) -> List:
    return get_related(entity, "hasQuiz")


def concept_display_name(ind) -> str:
    """Convert CamelCase to 'Camel Case' for nicer UI labels."""
    name = ind.name
    out = ""
    for i, ch in enumerate(name):
        if i > 0 and ch.isupper() and not name[i - 1].isupper():
            out += " "
        out += ch
    return out


def get_level(entity) -> str:
    level = get_literal(entity, "hasLevel")
    return level if level else "Unspecified"


def group_concepts(concepts: List) -> Dict[str, List]:
    """Group concepts roughly into curriculum modules using their names."""
    groups: Dict[str, List] = {
        "Foundations: Financial Statements": [],
        "Profitability & Return Ratios": [],
        "Liquidity & Working Capital": [],
        "Asset Utilisation & Efficiency": [],
        "Leverage & Capital Structure": [],
        "Trend, Growth & Benchmarking": [],
        "Pyramid / DuPont Analysis": [],
        "Other Concepts": [],
    }
    for c in concepts:
        n = c.name.lower()
        if any(k in n for k in ["financialstatements", "balancesheet", "incomestatement", "cashflow"]):
            groups["Foundations: Financial Statements"].append(c)
        elif any(k in n for k in ["profitability", "returnon", "returnratios"]):
            groups["Profitability & Return Ratios"].append(c)
        elif any(k in n for k in ["liquidity", "currentratio", "quickratio", "workingcapital"]):
            groups["Liquidity & Working Capital"].append(c)
        elif any(k in n for k in ["assetutilization", "assetutilisation"]):
            groups["Asset Utilisation & Efficiency"].append(c)
        elif any(k in n for k in ["leverage", "debttoequity"]):
            groups["Leverage & Capital Structure"].append(c)
        elif any(k in n for k in ["trendanalysis", "growthratios", "benchmarking"]):
            groups["Trend, Growth & Benchmarking"].append(c)
        elif any(k in n for k in ["dupont"]):
            groups["Pyramid / DuPont Analysis"].append(c)
        else:
            groups["Other Concepts"].append(c)
    return groups


# -------------------------------------------------
# Progress tracking
# -------------------------------------------------
if "quiz_correct" not in st.session_state:
    st.session_state["quiz_correct"] = {}  # { quiz_name: bool }

if "visited_concepts" not in st.session_state:
    st.session_state["visited_concepts"] = set()  # type: ignore

if "last_concept" not in st.session_state:
    st.session_state["last_concept"] = None


def mark_quiz_result(quiz_name: str, is_correct: bool):
    st.session_state["quiz_correct"][quiz_name] = is_correct


def concept_mastered(concept) -> bool:
    qs = get_quizzes(concept)
    if not qs:
        return False
    return any(st.session_state["quiz_correct"].get(q.name, False) for q in qs)


def compute_progress(concepts: List) -> float:
    """% of concepts that have at least one quiz answered correctly."""
    with_quiz = [c for c in concepts if get_quizzes(c)]
    if not with_quiz:
        return 0.0
    mastered = [c for c in with_quiz if concept_mastered(c)]
    return 100.0 * len(mastered) / len(with_quiz)


def module_progress(module_concepts: List) -> float:
    if not module_concepts:
        return 0.0
    return compute_progress(module_concepts)


# -------------------------------------------------
# Recommendation engine
# -------------------------------------------------
def recommend_next(concepts: List, groups: Dict[str, List], k: int = 5) -> List:
    visited: Set[str] = set(st.session_state["visited_concepts"])  # type: ignore

    # 1) Prefer unvisited Beginner concepts
    beginner_candidates = [
        c for c in concepts
        if c.name not in visited and get_level(c).lower().startswith("beginner")
    ]

    # 2) Then concepts related to mastered ones
    mastered = [c for c in concepts if concept_mastered(c)]
    related_candidates = []
    for m in mastered:
        for r in get_related(m, "relatedTo"):
            if r not in related_candidates and not concept_mastered(r):
                related_candidates.append(r)

    recs: List = []
    for c in beginner_candidates:
        if c not in recs:
            recs.append(c)
        if len(recs) >= k:
            break

    for c in related_candidates:
        if c not in recs:
            recs.append(c)
        if len(recs) >= k:
            break

    # 3) Fill with any unmastered
    if len(recs) < k:
        for c in concepts:
            if c not in recs and not concept_mastered(c):
                recs.append(c)
            if len(recs) >= k:
                break

    return recs[:k]


# -------------------------------------------------
# Calculators
# -------------------------------------------------
def show_ratio_calculator(concept):
    name = concept.name.lower()
    st.markdown("### 🔢 Interactive Calculator")

    if "currentratio" in name:
        ca = st.number_input("Current Assets (₦)", min_value=0.0, step=1000.0, key="ca")
        cl = st.number_input("Current Liabilities (₦)", min_value=0.0, step=1000.0, key="cl")
        if cl > 0:
            ratio = ca / cl
            st.write(f"**Current Ratio = {ratio:.2f}x**")
            if ratio < 1:
                st.warning("Current ratio < 1 may indicate liquidity stress.")
            elif ratio < 1.5:
                st.info("Current ratio is modest. Many analysts prefer ≥ 1.5× depending on industry.")
            else:
                st.success("Comfortable liquidity, but examine quality of current assets as well.")
        else:
            st.info("Enter a positive value for current liabilities to compute the ratio.")

    elif "quickratio" in name:
        cash = st.number_input("Cash (₦)", min_value=0.0, step=1000.0, key="cash")
        sec = st.number_input("Marketable Securities (₦)", min_value=0.0, step=1000.0, key="sec")
        rec = st.number_input("Accounts Receivable (₦)", min_value=0.0, step=1000.0, key="rec")
        cl = st.number_input("Current Liabilities (₦)", min_value=0.0, step=1000.0, key="cl_q")
        if cl > 0:
            quick_assets = cash + sec + rec
            ratio = quick_assets / cl
            st.write(f"**Quick Ratio = {ratio:.2f}x**")
            if ratio < 1:
                st.warning("Quick ratio < 1 suggests reliance on inventory or refinancing.")
            else:
                st.success("Quick ratio ≥ 1 suggests strong coverage by liquid assets.")
        else:
            st.info("Enter a positive value for current liabilities to compute the ratio.")

    elif "returnonequity" in name or "return_on_equity" in name or "roe" in name:
        ni = st.number_input("Net Income (₦)", min_value=0.0, step=1000.0, key="ni_roe")
        beg_eq = st.number_input("Beginning Equity (₦)", min_value=0.0, step=1000.0, key="beg_eq")
        end_eq = st.number_input("Ending Equity (₦)", min_value=0.0, step=1000.0, key="end_eq")
        avg_eq = (beg_eq + end_eq) / 2 if (beg_eq + end_eq) > 0 else 0
        if avg_eq > 0:
            roe = ni / avg_eq * 100
            st.write(f"**ROE = {roe:.1f}%**")
            st.info("Compare ROE with the firm's cost of equity and industry peers.")
        else:
            st.info("Enter positive beginning and ending equity values to compute ROE.")

    elif "returnonassets" in name or "return_on_assets" in name or "roa" in name:
        ni = st.number_input("Net Income (₦)", min_value=0.0, step=1000.0, key="ni_roa")
        beg_a = st.number_input("Beginning Total Assets (₦)", min_value=0.0, step=1000.0, key="beg_a")
        end_a = st.number_input("Ending Total Assets (₦)", min_value=0.0, step=1000.0, key="end_a")
        avg_a = (beg_a + end_a) / 2 if (beg_a + end_a) > 0 else 0
        if avg_a > 0:
            roa = ni / avg_a * 100
            st.write(f"**ROA = {roa:.1f}%**")
            st.info("Use ROA to compare asset efficiency across firms or over time.")
        else:
            st.info("Enter positive beginning and ending asset values to compute ROA.")

    elif "debttoequity" in name:
        debt = st.number_input("Total Debt (₦)", min_value=0.0, step=1000.0, key="debt")
        eq = st.number_input("Total Equity (₦)", min_value=0.0, step=1000.0, key="eq")
        if eq > 0:
            de = debt / eq
            st.write(f"**Debt-to-Equity = {de:.2f}x**")
            st.info("Higher leverage can amplify returns but also raises financial risk.")
        else:
            st.info("Enter a positive equity value to compute the ratio.")

    else:
        st.write("No dedicated calculator for this concept yet. Apply formulas from the theory section manually.")


# -------------------------------------------------
# Guard: Ontology must load
# -------------------------------------------------
if not onto:
    st.error("Ontology failed to load. Ensure 'financial_analysis_enhanced.owl' is in the same folder as this app.")
    st.stop()

all_concepts = list_concepts()
if not all_concepts:
    st.error("No Concept individuals found in the ontology.")
    st.stop()

groups = group_concepts(all_concepts)

# -------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "📚 Learn", "🧠 Quiz Hub", "📈 Progress & Recommendations"],
)

# Global progress bar at top
overall_progress = compute_progress(all_concepts)
st.progress(overall_progress / 100.0)
st.caption(f"Overall learning progress: **{overall_progress:.1f}%** of quiz-enabled topics mastered.")


# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
if page == "🏠 Home":
    st.markdown("## 🏠 Welcome to the Financial Analysis Intelligent Tutoring System")
    st.write(
        """
This platform is built around an **ontology of financial analysis concepts**.
You will:
- Start from the **foundations of financial statements**
- Move into **profitability, return, liquidity, leverage, and DuPont analysis**
- Practise with **exercises, case studies, and quizzes**
- Track your **learning progress** and get **personalised recommendations** for what to study next.
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Concepts", len(all_concepts))
    with col2:
        quiz_concepts = [c for c in all_concepts if get_quizzes(c)]
        st.metric("Concepts with Quizzes", len(quiz_concepts))
    with col3:
        st.metric("Mastered Topics", f"{sum(1 for c in quiz_concepts if concept_mastered(c))} / {len(quiz_concepts)}")

    st.markdown("---")
    st.markdown("### 📌 Your Learning Status")

    visited = list(st.session_state["visited_concepts"])  # type: ignore
    if visited:
        st.write(f"You have visited **{len(visited)}** topics so far.")
        last_name = st.session_state.get("last_concept")
        if last_name:
            last_obj = next((c for c in all_concepts if c.name == last_name), None)
            if last_obj:
                st.info(f"Last topic you studied: **{concept_display_name(last_obj)}**")
    else:
        st.write("You haven't opened any topics yet. Start with the **Learn** page.")

    st.markdown("---")
    st.markdown("### 🎯 Recommended Next Topics")

    recs = recommend_next(all_concepts, groups, k=5)
    if recs:
        for c in recs:
            lvl = get_level(c)
            mod = next((m for m, cs in groups.items() if c in cs), "Curriculum")
            status = "Mastered ✅" if concept_mastered(c) else "Not Mastered"
            st.markdown(f"- **{concept_display_name(c)}**  \n  _Module_: {mod} | _Level_: {lvl} | _Status_: {status}")
    else:
        st.write("No recommendations available yet. Try answering some quizzes first.")

    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    st.write(
        """
1. Go to **📚 Learn** and choose the module **“Foundations: Financial Statements”**.  
2. Start with **Financial Statements**, **Balance Sheet**, **Income Statement**, and **Cash Flow Statement**.  
3. Then move into **Ratio Analysis**, **Liquidity**, and **Profitability** modules.
        """
    )


# -------------------------------------------------
# LEARN PAGE
# -------------------------------------------------
elif page == "📚 Learn":
    st.markdown("## 📚 Learn Concepts")

    st.sidebar.subheader("Learn: Select Module & Concept")
    module = st.sidebar.selectbox("Choose a module:", list(groups.keys()))
    module_concepts = groups.get(module, [])

    search = st.sidebar.text_input("Search concept")
    if search:
        s = search.lower()
        module_concepts = [
            c for c in module_concepts
            if s in c.name.lower() or s in concept_display_name(c).lower()
        ]

    if not module_concepts:
        st.warning("No concepts available for this module or search filter.")
        st.stop()

    selected_name = st.sidebar.selectbox(
        "Choose a topic:",
        [concept_display_name(c) for c in module_concepts],
    )

    selected_concept = next(c for c in module_concepts if concept_display_name(c) == selected_name)

    # Track last concept & visited set
    st.session_state["last_concept"] = selected_concept.name
    st.session_state["visited_concepts"].add(selected_concept.name)  # type: ignore

    left_col, right_col = st.columns([2.6, 1.4])

    with left_col:
        st.markdown(f"### 📖 {selected_name}")
        st.caption(f"Module: {module} • Level: {get_level(selected_concept)}")

        tabs = st.tabs(["Definition", "Theory / Explanation", "Examples & Practice", "Quiz"])

        definition = get_literal(selected_concept, "hasDefinition")
        theory = get_literal(selected_concept, "hasTheory")
        example = get_literal(selected_concept, "hasExample")
        practices = get_practices(selected_concept)
        cases = get_cases(selected_concept)
        quizzes = get_quizzes(selected_concept)

        with tabs[0]:
            st.subheader("Definition")
            st.write(definition if definition else "No definition available yet for this concept.")

        with tabs[1]:
            st.subheader("Theory / Explanation")
            st.write(theory if theory else "No detailed theory has been added yet.")

        with tabs[2]:
            st.subheader("Examples")
            if example:
                st.write(example)
            else:
                st.write("No worked example is stored for this concept yet.")

            st.markdown("---")
            st.subheader("Practice Exercises")
            if practices:
                for p in practices:
                    desc = get_literal(p, "description")
                    st.markdown(f"**📝 {p.name}**")
                    st.write(desc if desc else "No description for this exercise yet.")
            else:
                st.write("No practice exercises are linked to this concept.")

            st.markdown("---")
            st.subheader("Case Studies")
            if cases:
                for c in cases:
                    title = get_literal(c, "title") or c.name
                    desc = get_literal(c, "description")
                    st.markdown(f"**📊 {title}**")
                    st.write(desc if desc else "No description available.")
            else:
                st.write("No case studies linked to this concept yet.")

        with tabs[3]:
            st.subheader("Quiz Yourself")
            if quizzes:
                for q in quizzes:
                    st.markdown(f"#### 🧠 {q.name}")
                    q_text = get_literal(q, "questionText")
                    options = get_literal(q, "options")
                    correct = get_literal(q, "correctAnswer")

                    if not q_text or not options or not correct:
                        st.write("This quiz question is not fully defined in the ontology.")
                        continue

                    st.write(q_text)
                    choices = [o.strip() for o in options.split("|")]

                    user_answer = st.radio(
                        "Choose your answer:",
                        choices,
                        key=f"quiz_{q.name}",
                    )

                    if st.button("Check answer", key=f"check_{q.name}"):
                        if user_answer == correct.strip():
                            st.success("✅ Correct! Well done.")
                            mark_quiz_result(q.name, True)
                        else:
                            st.error(f"❌ Incorrect. Correct answer: **{correct}**")
                            mark_quiz_result(q.name, False)
            else:
                st.info("No quizzes attached to this concept yet. Extend the ontology with QuizQuestion individuals to add more questions.")

    with right_col:
        st.markdown("#### 🔗 Related Concepts")
        related = get_related(selected_concept, "relatedTo")
        if related:
            for r in related:
                st.markdown(f"- {concept_display_name(r)}")
        else:
            st.write("No explicit related concepts recorded.")

        st.markdown("---")
        show_ratio_calculator(selected_concept)

        st.markdown("---")
        st.markdown("#### 🎯 Module Progress")
        mp = module_progress(module_concepts)
        st.write(f"Module completion: **{mp:.1f}%** (based on quiz performance).")


# -------------------------------------------------
# QUIZ HUB PAGE
# -------------------------------------------------
elif page == "🧠 Quiz Hub":
    st.markdown("## 🧠 Quiz Hub")
    st.write("Review and test your knowledge across all concepts that have quizzes.")

    quiz_concepts = [c for c in all_concepts if get_quizzes(c)]
    if not quiz_concepts:
        st.info("No concepts with quizzes are defined yet in the ontology.")
        st.stop()

    mode = st.radio("Quiz mode:", ["By Topic", "Random Question"])

    if mode == "By Topic":
        topic = st.selectbox(
            "Choose a topic:",
            [concept_display_name(c) for c in quiz_concepts],
        )
        concept = next(c for c in quiz_concepts if concept_display_name(c) == topic)
        st.markdown(f"### Topic: {concept_display_name(concept)}")

        quizzes = get_quizzes(concept)
        for q in quizzes:
            st.markdown(f"#### 🧠 {q.name}")
            q_text = get_literal(q, "questionText")
            options = get_literal(q, "options")
            correct = get_literal(q, "correctAnswer")

            if not q_text or not options or not correct:
                st.write("This quiz question is not fully defined.")
                continue

            st.write(q_text)
            choices = [o.strip() for o in options.split("|")]
            user_answer = st.radio(
                "Choose your answer:",
                choices,
                key=f"qh_{q.name}",
            )
            if st.button("Check", key=f"qh_check_{q.name}"):
                if user_answer == correct.strip():
                    st.success("✅ Correct!")
                    mark_quiz_result(q.name, True)
                else:
                    st.error(f"❌ Incorrect. Correct answer: **{correct}**")
                    mark_quiz_result(q.name, False)

    else:  # Random Question
        import random

        questions = []
        for c in quiz_concepts:
            for q in get_quizzes(c):
                questions.append((c, q))

        if not questions:
            st.info("No quiz questions found.")
            st.stop()

        if st.button("🎲 Draw Random Question"):
            st.session_state["random_q"] = random.choice(questions)  # type: ignore

        if "random_q" in st.session_state:
            concept, q = st.session_state["random_q"]
            st.markdown(f"### Topic: {concept_display_name(concept)}")
            st.markdown(f"#### 🧠 {q.name}")
            q_text = get_literal(q, "questionText")
            options = get_literal(q, "options")
            correct = get_literal(q, "correctAnswer")

            if q_text and options and correct:
                st.write(q_text)
                choices = [o.strip() for o in options.split("|")]
                user_answer = st.radio(
                    "Choose your answer:",
                    choices,
                    key=f"rand_{q.name}",
                )
                if st.button("Check Answer", key=f"rand_check_{q.name}"):
                    if user_answer == correct.strip():
                        st.success("✅ Correct!")
                        mark_quiz_result(q.name, True)
                    else:
                        st.error(f"❌ Incorrect. Correct answer: **{correct}**")
                        mark_quiz_result(q.name, False)
            else:
                st.write("This random question is not fully defined in the ontology.")


# -------------------------------------------------
# PROGRESS & RECOMMENDATIONS PAGE
# -------------------------------------------------
elif page == "📈 Progress & Recommendations":
    st.markdown("## 📈 Progress & Recommendations")

    quiz_concepts = [c for c in all_concepts if get_quizzes(c)]
    mastered = [c for c in quiz_concepts if concept_mastered(c)]
    visited = list(st.session_state["visited_concepts"])  # type: ignore

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Topics Visited", len(visited))
    with c2:
        st.metric("Quiz Topics Mastered", f"{len(mastered)} / {len(quiz_concepts)}")
    with c3:
        st.metric("Overall Progress", f"{overall_progress:.1f}%")

    st.markdown("---")
    st.markdown("### 📚 Topic Status Overview")

    rows = []
    for m_name, m_concepts in groups.items():
        for c in m_concepts:
            status = "Not started"
            if c.name in visited:
                status = "In progress"
            if concept_mastered(c):
                status = "Mastered ✅"
            rows.append({
                "Module": m_name,
                "Topic": concept_display_name(c),
                "Level": get_level(c),
                "Status": status,
            })

    st.write("Below is a summary of your status by topic:")
    st.markdown("| Module | Topic | Level | Status |")
    st.markdown("|---|---|---|---|")
    for row in rows:
        st.markdown(f"| {row['Module']} | {row['Topic']} | {row['Level']} | {row['Status']} |")

    st.markdown("---")
    st.markdown("### 🎯 Recommended Next Topics")

    recs = recommend_next(all_concepts, groups, k=7)
    if recs:
        for c in recs:
            mod = next((m for m, cs in groups.items() if c in cs), "Curriculum")
            lvl = get_level(c)
            status = "Mastered ✅" if concept_mastered(c) else "Not Mastered"
            st.markdown(f"- **{concept_display_name(c)}**  \n  _Module_: {mod} | _Level_: {lvl} | _Status_: {status}")
    else:
        st.write("No recommendations yet. Try completing some quizzes first.")

    st.markdown("---")
    st.markdown("### ✅ How to Improve Your Score")
    st.write(
        """
- Make sure each topic you visit also has its **quiz attempted**.  
- Aim to move from “In progress” to **“Mastered ✅”** on the key foundation topics:  
  Financial Statements, Ratio Analysis, Liquidity Ratios, Profitability Ratios, Return on Equity, and DuPont Analysis.  
- Use the **Quiz Hub** for focused revision and the **Learn** page for deeper theory and practice.
        """
    )
