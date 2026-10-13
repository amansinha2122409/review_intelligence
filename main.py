import os
import csv
import json
import time
from datetime import datetime
from google import genai
from google.genai import types

# ---------------------------------------------------------
# SIMULATED MCP TOOLS (INTERNAL SYSTEMS)
# ---------------------------------------------------------
def append_to_notes(data: dict):
    """Simulates an MCP action appending to a Google Doc/Notion"""
    filename = "product_pulse_log.md"
    
    content = f"""
## Weekly Product Pulse - {data['date']}
**Identified Fee Issue:** {data['identified_fee_issue']}

### The Pulse
{data['weekly_pulse']}

### Fee Explainer (Support Snippet)
{data['explanation_bullets']}

**Sources:** {', '.join(data['source_links'])}
---
"""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(content)
    print(f"\n[SYSTEM] ✅ Successfully appended to internal doc: {filename}")

def create_email_draft(data: dict):
    """Simulates an MCP action drafting an email in Gmail"""
    filename = "email_draft_preview.txt"
    
    draft = f"""SUBJECT: Weekly Product Pulse + Customer Clarification — {data['identified_fee_issue']}

Body:
Team,

Here is this week's product pulse based on recent app reviews:
{data['weekly_pulse']}

---
SUPPORT TEAM ACTION:
Please use the following approved snippet when addressing the {data['identified_fee_issue']} confusion:

{data['explanation_bullets']}
Sources: {', '.join(data['source_links'])}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(draft)
    print(f"[SYSTEM] ✅ Successfully created email draft: {filename}")

# ---------------------------------------------------------
# REVIEW INTELLIGENCE ENGINE
# ---------------------------------------------------------
def analyze_reviews(csv_filepath: str):
    # 1. Load reviews
    try:
        with open(csv_filepath, 'r', encoding='utf-8') as file:
            reviews = file.read()
    except FileNotFoundError:
        print("Error: reviews.csv not found. Please ensure it's in the same directory.")
        return

    # 2. Initialize Gemini Client
    client = genai.Client()
    print("Analyzing recent user reviews... Please wait.\n")

    # 3. System Prompt for structured generation
    prompt = f"""
    You are an expert AI Product Manager. Analyze the following raw customer reviews:
    {reviews}

    Extract and generate the following in strict JSON format:
    1. "top_themes": A list of up to 5 themes, with the top 3 clearly identified.
    2. "quotes": 3 exact quotes from the users backing up the top themes.
    3. "identified_fee_issue": A short string naming the specific fee or charge users are confused about.
    4. "weekly_pulse": A structured weekly note (MAX 250 words) including a summary of top themes, the quotes, a key observation on what is going wrong, and 3 action ideas for the product team.
    5. "explanation_bullets": A structured explanation for the identified fee. STRICTLY <= 6 bullet points, neutral facts-only tone. Include 'Last checked: [Today's Date]'.
    6. "source_links": Provide 2 realistic URL links to official pricing documentation.
    """

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "top_themes": {"type": "ARRAY", "items": {"type": "STRING"}},
            "quotes": {"type": "ARRAY", "items": {"type": "STRING"}},
            "identified_fee_issue": {"type": "STRING"},
            "weekly_pulse": {"type": "STRING"},
            "explanation_bullets": {"type": "STRING"},
            "source_links": {"type": "ARRAY", "items": {"type": "STRING"}}
        },
        "required": ["top_themes", "quotes", "identified_fee_issue", "weekly_pulse", "explanation_bullets", "source_links"]
    }

    # 4. Smart Routing & Model Fallback Mechanism
    models_to_try = ['gemini-3.8-flash', 'gemini-3.8-pro', 'gemini-3.8-flash-8b']
    response = None
    
    for model_name in models_to_try:
        if response: 
            break # Stop if we already got a successful response
            
        print(f"🔄 Attempting request routing via: {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.2
                )
            )
            print(f"✅ Successfully connected to {model_name}\n")
            
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"⚠️ {model_name} is currently overloaded. Rerouting...")
            else:
                raise e # Crash normally if it is a completely different error

    if not response:
        print("❌ All model tiers are completely overloaded right now. Please try running the script again in a few minutes.")
        return

    # 5. Parse the output
    result = json.loads(response.text)
    result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 6. Display to the user (Product Manager review step)
    print("==================================================")
    print(" 📊 REVIEW INTELLIGENCE REPORT READY ")
    print("==================================================")
    print(f"Detected Fee Issue: {result['identified_fee_issue']}\n")
    print("--- DRAFT: Weekly Pulse ---")
    print(result['weekly_pulse'])
    print("\n--- DRAFT: Support Explainer ---")
    print(result['explanation_bullets'])
    print("==================================================")

    # 7. The MCP Approval Gate
    approval = input("\n[APPROVAL REQUIRED] Do you approve logging this pulse and drafting the support email? (Y/N): ")
    
    if approval.lower() == 'y':
        print("\nExecuting approved MCP workflows...")
        append_to_notes(result)
        create_email_draft(result)
        print("\nWorkflow Complete. Have a great day!")
    else:
        print("\nAction cancelled by user. Discarding drafts.")

if __name__ == "__main__":
    analyze_reviews("reviews.csv")