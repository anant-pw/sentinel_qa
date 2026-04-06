### [PROJECT ASSET: README.MD]

# 🛡️ Sentinel-QA (Pilot)
**Cognitive QA Engine: AI-Generated, Human-Approved, Autonomous Testing.**

Sentinel-QA transforms the testing lifecycle from manual scripting to AI orchestration. It uses **SambaNova LPU** (Llama-3.3-70B) and **LangChain** to generate, execute, and triage tests with human oversight.

---

### 🔬 Core Architecture
1.  **Requirement Analyst:** AI converts messy Jira/unstructured text into structured **YAML Test Plans**.
2.  **HITL Approval Portal:** A **Streamlit** dashboard where humans review/edit AI-generated plans before execution.
3.  **Hybrid Engine:** Performs **API Tier-1/2 validation** before triggering **Playwright UI** automation.
4.  **Sentinel Triage:** **LangChain-powered** agent identifies recurring failure patterns across the test session and drafts Jira-ready reports.

---

### 🛠️ The Tech Stack
*   **Engine:** Python 3.11, Playwright (Sync), Pytest.
*   **Brain:** SambaNova Cloud (Primary) | Groq (Fallback) | Ollama (Local).
*   **Orchestration:** LangChain (LCEL + ConversationBufferMemory).
*   **Reporting:** Allure + AI-Generated Failure Analysis.

---

### 🚀 Quick Start

**1. Setup Environment**
```bash
pip install -r requirements.txt
playwright install chromium
```

**2. Configure `.env`**
```env
SAMBANOVA_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

**3. The Workflow**
*   **Step 1 (Generate):** Run `requirement_analyst.py` to create a `pending/` YAML.
*   **Step 2 (Approve):** Launch Streamlit: `streamlit run ui/approval_app.py`. Move test to `approved/`.
*   **Step 3 (Execute):** `pytest tests/test_engine.py --alluredir=allure-results`.
*   **Step 4 (Triage):** Review AI bug analysis in the generated Allure report.

---

### 🔮 Phase 2 Roadmap (Suggested)
- [ ] **PostgreSQL Migration:** Move from YAML files to a stateful DB.
- [ ] **Real Jira API:** Direct push of AI-drafted bugs to Jira.
- [ ] **Horizontal Scaling:** `pytest-xdist` integration for parallel execution.

---

Built by [Anant Jain](https://www.linkedin.com/in/anant-jain-40760719/)) as part of the **Sentinel Series** — documenting the evolution from manual QA scripting to fully autonomous AI-driven testing pipelines.
