import streamlit as st
from owlready2 import *
import random
import pandas as pd

# ---------------------------------------
# LOAD ONTOLOGY
# ---------------------------------------
onto_path.append(".")

try:
    onto = get_ontology("financial_analysis_enhanced.owl").load()
except:
    onto = None

# ---------------------------------------------------------
# DUMMY DATA FOR DEMONSTRATION
# ---------------------------------------------------------
DUMMY_CONCEPTS = [
    {"name": "Financial Statements", "description": "Understanding balance sheets, income statements, and cash flow statements."},
    {"name": "Ratio Analysis", "description": "Analyzing financial ratios like liquidity, profitability, and solvency ratios."},
    {"name": "Valuation Methods", "description": "DCF, comparable companies, and precedent transaction analysis."},
    {"name": "Risk Management", "description": "Identifying, measuring, and mitigating financial risks."},
    {"name": "Investment Analysis", "description": "Evaluating investment opportunities and portfolio management."}
]

DUMMY_QUIZ_QUESTIONS = [
    {"question": "What is the primary purpose of a balance sheet?", "answer": "to show the financial position"},
    {"question": "What does ROE stand for?", "answer": "return on equity"},
    {"question": "Which ratio measures liquidity?", "answer": "current ratio"},
    {"question": "What is NPV in investment analysis?", "answer": "net present value"},
    {"question": "Define systematic risk.", "answer": "market risk"}
]

DUMMY_RECOMMENDATIONS = [
    "Master Financial Statement Analysis before moving to Ratio Analysis",
    "Complete Ratio Analysis before attempting Valuation Methods",
    "Study Risk Management alongside Investment Analysis",
    "Review Financial Statements periodically for retention"
]

# ---------------------------------------
# STREAMLIT CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="Advanced Financial Analysis ITS",
    layout="wide"
)

# ---------------------------------------------------------
# HELPER FUNCTIONS FOR ONTOLOGY RELATIONSHIPS
# ---------------------------------------------------------

def get_related_concepts(concept, onto):
    """Extract concepts related to the given concept using relatedTo property"""
    related = []
    if hasattr(concept, 'relatedTo'):
        related = list(concept.relatedTo)
    return related

def get_practice_exercises(concept, onto):
    """Extract practice exercises for a concept using hasPractice property"""
    exercises = []
    if hasattr(concept, 'hasPractice'):
        exercises = list(concept.hasPractice)
    return exercises

def get_case_studies(concept, onto):
    """Extract case studies for a concept using hasCaseStudy property"""
    cases = []
    if hasattr(concept, 'hasCaseStudy'):
        cases = list(concept.hasCaseStudy)
    return cases

def get_quiz_questions(concept, onto):
    """Extract quiz questions for a concept using hasQuiz property"""
    quizzes = []
    if hasattr(concept, 'hasQuiz'):
        quizzes = list(concept.hasQuiz)
    return quizzes

def get_concept_level(concept):
    """Extract the difficulty level of a concept"""
    if hasattr(concept, 'hasLevel') and concept.hasLevel:
        return concept.hasLevel[0]
    return "Beginner"

def get_concept_theory(concept):
    """Extract the theory/explanation for a concept"""
    if hasattr(concept, 'hasTheory') and concept.hasTheory:
        return concept.hasTheory[0]
    return "No theory available."

def get_concept_example(concept):
    """Extract an example for a concept"""
    if hasattr(concept, 'hasExample') and concept.hasExample:
        return concept.hasExample[0]
    return "No example available."

# ---------------------------------------------------------
st.title("📊 Advanced Financial Analysis Intelligent Tutoring System")

# ---------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------
if "concepts_learned" not in st.session_state:
    st.session_state.concepts_learned = 0

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "level" not in st.session_state:
    st.session_state.level = "Beginner"

if "time_spent" not in st.session_state:
    st.session_state.time_spent = 0.0

if "learning_history" not in st.session_state:
    st.session_state.learning_history = []

if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

# ---------------------------------------
# TABS
# ---------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📌 Dashboard", "📘 Learning", "📝 Quiz", "📈 Progress", "🎯 Recommendations"]
)

# ---------------------------------------------------------
# TAB 1: DASHBOARD
# ---------------------------------------------------------
with tab1:
    st.subheader("Financial Analysis Learning Center")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Concepts Learned", st.session_state.concepts_learned)
    col2.metric("Quiz Score", f"{st.session_state.quiz_score}%")
    col3.metric("Current Level", st.session_state.level)
    col4.metric("Time Spent", f"{st.session_state.time_spent}h")

    st.write("---")
    st.subheader("Quick Actions")

    c1, c2, c3, c4 = st.columns(4)
    c1.button("Continue Learning")
    c2.button("Take Quick Quiz")
    c3.button("View Progress")
    c4.button("Get Recommendations")

# ---------------------------------------------------------
# TAB 2: LEARNING
# ---------------------------------------------------------
with tab2:
    st.subheader("📘 Learning Center")

    if onto:
        Concept = onto.search_one(iri="*Concept")
        concepts = list(Concept.instances())
    else:
        concepts = DUMMY_CONCEPTS

    if concepts:
        # Convert concepts to names for selectbox (avoid deepcopy recursion issue with owlready2)
        if onto:
            concept_names = [c.name for c in concepts]
            concept_map = {c.name: c for c in concepts}
        else:
            concept_names = [c["name"] for c in DUMMY_CONCEPTS]
            concept_map = {c["name"]: c for c in DUMMY_CONCEPTS}
        
        selected_name = st.selectbox(
            "Choose a concept to study:",
            concept_names
        )
        
        # Get the actual concept object from the map
        selected_concept = concept_map[selected_name]

        # Display concept name and description
        st.write(f"### 📖 {selected_concept.get('name') if isinstance(selected_concept, dict) else selected_concept.name}")
        
        if isinstance(selected_concept, dict):
            description = selected_concept.get("description", "No description available.")
        else:
            description = selected_concept.description[0] if (hasattr(selected_concept, "description") and selected_concept.description) else "No description available."
        
        st.write(description)

        # Display ontology relationships if available
        if onto and not isinstance(selected_concept, dict):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### 📚 Theory & Level")
                theory = get_concept_theory(selected_concept)
                st.info(f"**Level:** {get_concept_level(selected_concept)}\n\n{theory}")
                
                example = get_concept_example(selected_concept)
                st.write(f"**Example:** {example}")
            
            with col2:
                st.write("#### 🔗 Related Concepts")
                related = get_related_concepts(selected_concept, onto)
                if related:
                    for rel in related:
                        st.write(f"→ {rel.name if hasattr(rel, 'name') else str(rel)}")
                else:
                    st.write("No related concepts")
            
            # Practice Exercises
            st.write("#### 💪 Practice Exercises")
            exercises = get_practice_exercises(selected_concept, onto)
            if exercises:
                for idx, exercise in enumerate(exercises, 1):
                    desc = exercise.description[0] if (hasattr(exercise, 'description') and exercise.description) else "No description"
                    st.write(f"{idx}. {desc}")
            else:
                st.write("No practice exercises available")
            
            # Case Studies
            st.write("#### 📋 Case Studies")
            cases = get_case_studies(selected_concept, onto)
            if cases:
                for case in cases:
                    title = case.title[0] if (hasattr(case, 'title') and case.title) else case.name
                    desc = case.description[0] if (hasattr(case, 'description') and case.description) else "No description"
                    st.write(f"**{title}:** {desc}")
            else:
                st.write("No case studies available")

        if st.button("Mark as Learned"):
            concept_name = selected_concept.get("name") if isinstance(selected_concept, dict) else selected_concept.name
            st.session_state.concepts_learned += 1
            st.session_state.learning_history.append(concept_name)
            st.success(f"Marked {concept_name} as learned!")

    else:
        st.error("❌ OWL Ontology not found and no dummy data available.")

# ---------------------------------------------------------
# TAB 3: QUIZ
# ---------------------------------------------------------
with tab3:
    st.subheader("📝 Quiz")

    num_questions = st.number_input("Number of questions:", min_value=1, max_value=20, value=5)
    difficulty = st.selectbox("Difficulty:", ["All Levels", "Beginner", "Intermediate", "Advanced"])

    if st.button("Start Quiz"):
        st.write("### Quiz Started!")

        if onto:
            # Get all concepts and their associated quiz questions
            Concept = onto.search_one(iri="*Concept")
            concepts = list(Concept.instances()) if Concept else []
            
            all_questions = []
            for concept in concepts:
                quiz_q = get_quiz_questions(concept, onto)
                all_questions.extend(quiz_q)
            
            questions = all_questions if all_questions else DUMMY_QUIZ_QUESTIONS
        else:
            questions = DUMMY_QUIZ_QUESTIONS

        random.shuffle(questions)
        selected_questions = questions[:min(num_questions, len(questions))]

        score = 0
        for idx, q in enumerate(selected_questions):
            if isinstance(q, dict):
                st.write(f"**Q{idx+1}: {q['question']}**")
                user_answer = st.text_input(f"Your answer for Q{idx+1}", key=f"q_{idx}")
                correct = q['answer']
            else:
                question_text = q.questionText[0] if (hasattr(q, 'questionText') and q.questionText) else "Question not available"
                difficulty_level = q.difficulty[0] if (hasattr(q, 'difficulty') and q.difficulty) else "Beginner"
                st.write(f"**Q{idx+1} [{difficulty_level}]: {question_text}**")
                user_answer = st.text_input(f"Your answer for Q{idx+1}", key=f"q_{idx}")
                correct = q.correctAnswer[0] if (hasattr(q, "correctAnswer") and q.correctAnswer) else ""

            if user_answer.lower().strip() == correct.lower().strip():
                score += 1

        if st.button("Submit Answers"):
            st.session_state.quiz_score = int((score / len(selected_questions)) * 100) if selected_questions else 0
            st.success(f"Your Score: {st.session_state.quiz_score}%")

# ---------------------------------------------------------
# TAB 4: PROGRESS
# ---------------------------------------------------------
with tab4:
    st.subheader("📈 Learning Progress")

    st.write("### Progress Table")
    df = pd.DataFrame({
        "Concept Learned": st.session_state.learning_history,
    })
    st.dataframe(df)

    st.write("### Learning Progress Chart")

    st.bar_chart({
        "Completed": [st.session_state.concepts_learned],
        "Remaining": [max(0, 10 - st.session_state.concepts_learned)]
    })

# ---------------------------------------------------------
# TAB 5: RECOMMENDATIONS
# ---------------------------------------------------------
with tab5:
    st.subheader("🎯 Personalized Learning Path")

    if onto:
        Concept = onto.search_one(iri="*Concept")
        concepts = list(Concept.instances()) if Concept else []
        
        if concepts and st.session_state.learning_history:
            # Get the last learned concept
            last_concept_name = st.session_state.learning_history[-1]
            
            # Find the corresponding concept object
            last_concept = None
            for c in concepts:
                if c.name == last_concept_name:
                    last_concept = c
                    break
            
            if last_concept:
                related = get_related_concepts(last_concept, onto)
                if related:
                    st.write("#### 📌 Next Recommended Topics (Related to your last concept)")
                    for idx, rel in enumerate(related, 1):
                        rel_name = rel.name if hasattr(rel, 'name') else str(rel)
                        rel_level = get_concept_level(rel) if hasattr(rel, 'hasLevel') else "Beginner"
                        st.write(f"{idx}. **{rel_name}** (Level: {rel_level})")
                        if st.button("Study Now", key=f"rel_{idx}"):
                            st.session_state.concepts_learned += 1
                            st.session_state.learning_history.append(rel_name)
                            st.success(f"Started learning {rel_name}!")
                else:
                    st.info("No related topics found. Explore other concepts!")
            else:
                all_recommendations = DUMMY_RECOMMENDATIONS
                for idx, rec in enumerate(all_recommendations, 1):
                    st.write(f"{idx}. ✓ {rec}")
        else:
            all_recommendations = DUMMY_RECOMMENDATIONS
            st.write("#### 📌 Recommended Learning Path")
            for idx, rec in enumerate(all_recommendations, 1):
                st.write(f"{idx}. ✓ {rec}")
    else:
        all_recommendations = DUMMY_RECOMMENDATIONS
        st.write("#### 📌 Recommended Learning Path")
        for idx, rec in enumerate(all_recommendations, 1):
            st.write(f"{idx}. ✓ {rec}")
