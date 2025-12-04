# 📊 Advanced Financial Analysis Intelligent Tutoring System (ITS)

An AI-assisted **Intelligent Tutoring System** built with **Streamlit** and **Owlready2**, designed to help learners master **Advanced Financial Analysis** through:

- Structured concepts (from an OWL **ontology**)
- Rich definitions, theory, and worked examples
- Concept-level quizzes and feedback
- Progress tracking across modules
- A simple recommendation engine for “what to learn next”

The system loads a **financial analysis ontology** (`financial_analysis_enhanced.owl`) for dynamic, ontology-driven learning — with **automatic fallback to built-in dummy data** if no ontology is found.

---

## 🚀 Features Overview

### ✅ 1. Dynamic Home Dashboard

The landing page acts as a **learning overview** and hub:

- High-level **course introduction**  
- Summary tiles (varies slightly by app version), such as:
  - Concepts available
  - Concepts completed / in progress
  - Overall quiz performance
- Quick navigation buttons to:
  - **Start Learning**
  - **Quiz Hub**
  - **Progress & Recommendations**

This gives the learner a sense of where they are in the course before diving into details.

---

### 📘 2. Learning Module (Concept-Based Learning)

The **Learn** section is the main ITS learning environment.

When an ontology is loaded, the app pulls real content from `financial_analysis_enhanced.owl`. If not, it falls back to **dummy concepts** so the app still works.

You can:

- Select a **module** (e.g.:
  - Foundations: *Financial Statements*
  - *Profitability & Return Ratios*
  - *Asset Utilisation*
  - *Leverage*
  - *Trend & Growth Analysis*
  - *Benchmarking*
  - *DuPont / Pyramid Analysis*)
- Then select a **concept** inside the module, mapped to an OWL `Concept` individual.

For each concept, the app uses ontology properties:

- `hasDefinition` → **Definition tab**  
- `hasTheory` → **Theory / Explanation tab**  
- `hasExample` → **Examples & Practice tab**  
- `hasLevel` → Difficulty (Beginner / Intermediate / Advanced)  
- `hasPractice` → Linked **PracticeExercise** descriptions  
- `hasCaseStudy` → Linked **CaseStudy** descriptions  
- `relatedTo` → “Related concepts” panel for deeper exploration  

Each concept can be **marked as learned**, contributing to the learner’s overall progress.

If the ontology is missing or does not contain a given concept, the app can use **fallback dummy content** so the UI is never empty.

---

### 📝 3. Quiz Module (Quiz Hub)

An interactive **quiz system** mapped to OWL `QuizQuestion` individuals.

Features:

- **Concept-linked quiz items** from the ontology via `hasQuiz`
- Fallback **static quiz bank** if the ontology has no quiz questions
- Choose:
  - Concept / topic (e.g. `CurrentRatio`, `TrendAnalysis`, `LeverageRatios`)
  - Number of questions (where supported)
- For each question, the app uses:
  - `questionText`
  - `options` (parsed from a `|`-separated string)
  - `correctAnswer`
  - `difficulty` (optional but supported)

After submission, learners see:

- Immediate **score feedback**
- Which options were correct/incorrect
- A history update for **progress tracking**

---

### 📈 4. Learning Progress

The **Progress / Analytics** area visualises how the learner is doing over time.

Typical elements include:

- A table of concepts:
  - Not started / in progress / completed
- Overall quiz success rate
- Module-level summaries (e.g. stronger vs weaker areas)
- (Optional in your `app.py`) simple charts like:
  - Completed vs remaining concepts
  - Average quiz score per module

Progress is maintained in **Streamlit session state** (or similar in the final `app.py`), keyed by concepts and quiz attempts.

---

### 🎯 5. Recommendation Engine

A lightweight **recommendation engine** suggests “what next?” based on:

- **Ontology-based relationships:**
  - Uses `relatedTo` for the last studied concept
  - Can prefer concepts in the same module that are still unlearned
- **Performance-based signals:**
  - Concepts with low quiz scores → flagged for revision
  - Concepts with no quiz attempts → suggested as “next up”

If the ontology has insufficient links or is missing, the app falls back to **static “good next steps”**, such as:

- Study **FinancialStatements** before **RatioAnalysis**
- Study **ProfitabilityRatios** before **DuPontAnalysis**
- Study **LeverageRatios** before **Growth & Trend Analysis**

---

## 🧠 Ontology: `financial_analysis_enhanced.owl`

The ITS is driven by the OWL ontology `financial_analysis_enhanced.owl`, which encodes:

- Concepts (topics)
- Relationships between concepts
- Definitions, theory, examples
- Practice exercises & case studies
- Quiz questions and difficulty

### Core OWL Classes

- `Concept`  
  Any financial analysis topic (e.g. `FinancialStatements`, `CurrentRatio`, `ReturnOnEquity`, `TrendAnalysis`).

- `PracticeExercise`  
  Short tasks/exercises such as “compute this ratio and interpret it”.

- `CaseStudy`  
  Richer narrative scenarios (e.g. *RetailChainExpansion*, *ManufacturingTurnaround*).

- `QuizQuestion`  
  Multiple-choice questions linked to a `Concept` through `hasQuiz`.

### Object Properties

- `hasPractice (Concept → PracticeExercise)`
- `hasCaseStudy (Concept → CaseStudy)`
- `hasQuiz (Concept → QuizQuestion)`
- `relatedTo (Concept → Concept)`

### Datatype Properties

- `hasDefinition (Concept → string)`
- `hasTheory (Concept → string)`
- `hasExample (Concept → string)`
- `hasLevel (Concept → string: Beginner / Intermediate / Advanced)`
- `description (PracticeExercise / CaseStudy → string)`
- `title (CaseStudy → string)`
- `questionText (QuizQuestion → string)`
- `options (QuizQuestion → string, options separated by "|")`
- `correctAnswer (QuizQuestion → string)`
- `difficulty (QuizQuestion → string)`

The **final ontology** you’re using includes rich content for, among others:

- Financial statements & components:
  - `FinancialStatements`, `BalanceSheet`, `IncomeStatement`, `CashFlowStatement`
- Ratio analysis:
  - `RatioAnalysis`, `LiquidityRatios`, `CurrentRatio`, `QuickRatio`
  - `Profitability`, `ProfitabilityRatios`, `ReturnRatios`
  - `ReturnOnEquity`, `ReturnOnAssets`, `ExpenseRatios`, `TaxAndInterestRatios`
- Asset utilisation & working capital:
  - `AssetUtilizationRatios`, `WorkingCapital`
- Leverage & debt:
  - `LeverageRatios`, `DebtToEquityRatio`
- Trend & growth:
  - `TrendAnalysis`, `GrowthRatios`
- Benchmarking & DuPont:
  - `Benchmarking`, `DuPontAnalysis`
- Case studies & exercises:
  - `RetailChainExpansion`, `ManufacturingTurnaround`
  - `LiquidityExercise1`, `LiquidityExercise2`, `ProfitabilityExercise1`, `DuPontExercise1`
- Quiz questions:
  - `FinancialStatementsQ1`, `BalanceSheetQ1`, `IncomeStatementQ1`, `CashFlowStatementQ1`
  - `LiquidityQ1`, `LiquidityRatiosQ2`, `CurrentRatioQ1`, `QuickRatioQ1`
  - `ProfitabilityIntroQ1`, `ProfitabilityQ1`, `ProfitabilityRatiosQ2`
  - `RatioAnalysisQ1`, `ReturnRatiosQ1`, `ExpenseRatiosQ1`, `TaxAndInterestRatiosQ1`
  - `ROEQ1`, `ROAQ1`, `AssetUtilizationQ1`, `WorkingCapitalQ1`
  - `LeverageRatiosQ1`, `DebtToEquityQ1`
  - `TrendAnalysisQ1`, `GrowthRatiosQ1`, `BenchmarkingQ1`, `DuPontQ1`

The app reads directly from these individuals and properties to populate the UI.

---

## 🗂️ Project Structure

Typical repository layout:

```bash
.
├── app.py                          # Main Streamlit application
├── financial_analysis_enhanced.owl # Final financial analysis ontology
├── README.md                       # Documentation (this file)
└── new ontology graph.graph        # (Optional) Graph file / visualisation of ontology links
⚙️ Requirements
Python

Python 3.8+ recommended

Python Libraries

Core:

streamlit
owlready2
pandas
numpy


Install dependencies:

pip install streamlit owlready2 pandas numpy


(Add matplotlib or others if you extend with charts.)

🔧 Installation & Setup

Clone the repository

git clone https://github.com/your-username/financial-analysis-its.git
cd financial-analysis-its


Create & activate a virtual environment (optional but recommended)

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate


Install dependencies

pip install -r requirements.txt


If there’s no requirements.txt, use:

pip install streamlit owlready2 pandas numpy


Place the ontology file

Ensure that:

financial_analysis_enhanced.owl


is in the same directory as app.py.

▶️ Running the App

From the project root:

streamlit run app.py


Streamlit will print a local URL like:

Local URL: http://localhost:8501


Open it in your browser if it doesn’t auto-launch.

If the ontology loads correctly, you’ll see a note in the sidebar or console confirming it. If not, the app will use fallback dummy data, but with reduced richness.

🔌 How app.py Works (High Level)

The exact implementation can vary, but the typical flow with the final version is:

Ontology Loading with Fallback

from owlready2 import get_ontology, default_world
import os

ONTO_FILE = "financial_analysis_enhanced.owl"

if os.path.exists(ONTO_FILE):
    onto = get_ontology(ONTO_FILE).load()
    ONTOLOGY_AVAILABLE = True
else:
    onto = None
    ONTOLOGY_AVAILABLE = False


Mapping OWL Classes & Properties

if ONTOLOGY_AVAILABLE:
    Concept = onto.Concept
    QuizQuestion = onto.QuizQuestion
    # etc...


Reading Concept Data

Convenience helper:

def first_literal(entity, prop):
    vals = list(prop[entity])
    return str(vals[0]) if vals else ""


Usage:

definition = first_literal(concept, onto.hasDefinition)
theory     = first_literal(concept, onto.hasTheory)
example    = first_literal(concept, onto.hasExample)
level      = first_literal(concept, onto.hasLevel)


Following Relations for Practices, Cases, Quizzes

quizzes      = list(onto.hasQuiz[concept])
practices    = list(onto.hasPractice[concept])
case_studies = list(onto.hasCaseStudy[concept])
related      = list(onto.relatedTo[concept])


Streamlit UI

Sidebar: module & concept selectors

Main area: tabs for Definition, Theory, Examples & Practice, Quiz

Progress & recommendations driven by quiz results and ontology links (relatedTo)

➕ Extending the System

You can extend the ITS in two main ways:

1. Extend the Ontology (Content)

Add new Concept, QuizQuestion, PracticeExercise, or CaseStudy individuals to financial_analysis_enhanced.owl following the existing pattern.

Example – new concept:

<ns1:NamedIndividual rdf:about="#EBITDAtoInterestRatio">
  <rdf:type rdf:resource="#Concept" />
  <ns3:hasDefinition rdf:datatype="http://www.w3.org/2001/XMLSchema#string">
    EBITDA to interest ratio measures how many times a company’s EBITDA can cover interest expense.
  </ns3:hasDefinition>
  <ns3:hasTheory rdf:datatype="http://www.w3.org/2001/XMLSchema#string">
    EBITDA / Interest Expense. Values above 3–4x are often considered comfortable, depending on industry.
  </ns3:hasTheory>
  <ns3:hasExample rdf:datatype="http://www.w3.org/2001/XMLSchema#string">
    Example: If EBITDA is ₦5,000,000 and interest expense is ₦1,000,000, the ratio is 5.0x.
  </ns3:hasExample>
  <ns3:hasLevel rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Intermediate</ns3:hasLevel>
  <ns3:relatedTo rdf:resource="#LeverageRatios" />
  <ns3:relatedTo rdf:resource="#TaxAndInterestRatios" />
  <ns3:hasQuiz rdf:resource="#EBITDAtoInterestQ1" />
</ns1:NamedIndividual>

2. Extend the App (Logic / UI)

Add calculators for key ratios (current ratio, quick ratio, ROE, ROA, etc).

Add visualisations (trend charts, scenario comparisons).

Enhance progress analytics (per-module charts, time-based graphs).

Integrate user authentication and persistent storage beyond session state.

🐛 Troubleshooting
ModuleNotFoundError: No module named 'owlready2'

Install:

pip install owlready2


Make sure your virtual environment (if used) is activated.

Failed to load ontology or No such file or directory

Check:

The file is named exactly: financial_analysis_enhanced.owl

It’s in the same directory as app.py

You have read permission on the file

If loading still fails, the app should fall back to dummy data, but you will lose the rich ontology content until this is fixed.

Quiz Tab Says: “No quizzes attached to this concept yet”

This means that concept has no hasQuiz links in the ontology.

To fix it:

Create a QuizQuestion individual with questionText, options, and correctAnswer.

Add a <ns3:hasQuiz rdf:resource="#YourQuizId" /> line inside the concept’s individual.

Reload the app.

🤝 Contributing

Contributions are very welcome:

Adding more concepts (e.g. cash conversion cycle, scenario analysis)

Writing richer examples and case studies

Expanding the question bank (multiple difficulties)

Improving the UI/UX or analytics

Fork the repo

Create a feature branch

Submit a pull request with a clear description

📜 License

You can use any license you prefer. Commonly:

MIT License – very permissive

Apache 2.0 – permissive with explicit patent grant

Example:

MIT License – see LICENSE file for details.
