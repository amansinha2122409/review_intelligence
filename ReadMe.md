# Milestone 5: AI-Powered Product & Support Workflow

## 🚀 Project Overview
This project is an AI orchestration workflow designed to bridge the gap between Product Management and Customer Support. It digests raw, unstructured customer feedback (CSV), isolates key product friction points, and executes structured communications via an approval-gated simulated Model Context Protocol (MCP) toolset.

To demonstrate both backend engineering and frontend product skills, this project includes **two** functional versions:
1. **CLI Version (`main.py`)**: A robust terminal application.
2. **Web UI Version (`app.py`)**: An interactive, browser-based product built with Streamlit.

---

## 📋 Evaluator Rubric Checklist

### 1. What fee issue was identified from reviews?
From the dataset, the system successfully identified recurring confusion and negative sentiment around a **"Platform Maintenance Fee" (250 Rs)**, which users felt was hidden or poorly explained during onboarding.

### 2. Where does the MCP approval happen?
This project strictly enforces a **Human-in-the-Loop (HITL)** boundary before any internal system (MCP tool) is touched.
* **In the CLI (`main.py`):** The system pauses execution, displays the generated drafts in the terminal, and explicitly waits for a `[APPROVAL REQUIRED] (Y/N)` input from the operator.
* **In the Web UI (`app.py`):** The workflow halts after the intelligence extraction step. The UI renders the drafts and waits for the user to explicitly click the `✅ Approve & Execute Workflows` button. 
* Only *after* approval do the simulated MCP functions trigger to create the local files (`product_pulse_log.md` and `email_draft_preview.txt`).

### 3. Advanced Engineering Implemented
* **Structured Outputs:** Used Gemini's JSON schema enforcement to guarantee exact data extraction and prevent hallucination.
* **Fault Tolerance:** Engineered a "Smart Retry Mechanism" that automatically catches `503 UNAVAILABLE` API traffic errors, pauses for 5 seconds, and retries gracefully without crashing the application.

---

## 🛠️ How to Run

### Prerequisites
Ensure you have the required Python libraries installed:
```bash
python -m pip install google-genai streamlit pandas