# 📊 Advanced Financial Analysis Intelligent Tutoring System (ITS)

An **AI-powered Intelligent Tutoring System** built with **Streamlit** and **Owlready2**, designed to help learners master **Advanced Financial Analysis** through structured concepts, quizzes, progress tracking, and personalized recommendations.  
This system supports loading financial analysis **ontologies (OWL)** for dynamic, ontology-driven learning — with fallback to dummy data when no ontology is available.

---

## 🚀 Features Overview

### ✅ **1. Dynamic Dashboard**
A real-time learning summary showing:
- **Concepts Learned**
- **Quiz Score**
- **Current Level**
- **Time Spent**
- Quick action buttons for navigating the learning flow

---

### 📘 **2. Learning Module**
Learn concepts via:
- Ontology-based concepts (if OWL file is loaded)
- Dummy fallback concepts
- Concept theory & examples
- Practice exercises
- Case studies
- Related concepts via ontology properties

When ontology is available, concepts can contain:
- `hasTheory`
- `hasExample`
- `hasLevel`
- `relatedTo`
- `hasPractice`
- `hasCaseStudy`

Each concept can be **marked as learned**, updating student history.

---

### 📝 **3. Quiz Module**
Interactive quiz system with:
- Customizable number of questions
- Difficulty selection
- Ontology-linked quiz items (via `hasQuiz`)
- Fallback quiz bank if ontology unavailable
- Instant scoring & history tracking

---

### 📈 **4. Learning Progress**
Progress visualization tools include:
- A real-time **progress table** showing all completed concepts
- A **bar chart** comparing completed vs remaining concepts

---

### 🎯 **5. Recommendation Engine**
Smart learning path suggestions:
- Ontology-based recommendations derived from **related concepts** of the last studied topic
- Fallback static recommendations if ontology missing or insufficient

---

## 🗂️ Project Structure


- app.py # Main Streamlit application
- financial_analysis_enhanced.owl # (Expected) Ontology file
- otf ontology .graph # Additional ontology mapping file


## ⚙️ Requirements

### Python Libraries
- `streamlit`
- `owlready2`
- `pandas`

Install dependencies:

```bash
pip install streamlit owlready2 pandas
