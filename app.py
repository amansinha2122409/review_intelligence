import os
import time
import json
from datetime import datetime
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# ---------------------------------------------------------
# UI CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Product Pulse Orchestrator", page_icon="📊", layout="wide")

st.title("📊 Product Insight & Support Orchestrator")
st.markdown("Upload raw customer reviews to extract insights, identify friction points, and draft support communications.")

# Ensure API Key is available
if "GEMINI_API_KEY" not in os.environ:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    else:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar to proceed.")
        st.stop()

# ---------------------------------------------------------
# SIMULATED MCP TOOLS (INTERNAL SYSTEMS)
# ---------------------------------------------------------
def execute_mcp_workflows(data: dict):
    """Simulates MCP actions logging to docs and drafting emails"""
    doc_filename = "product_pulse_log.md"
    email_filename = "email_draft_preview.txt"
    
    # 1. Append to Notes
    content = f"\n## Weekly Product Pulse - {data['date']}\n**Identified Fee Issue:** {data['identified_fee_issue']}\n\n### The Pulse\n{data['weekly_pulse']}\n\n### Fee Explainer\n{data['explanation_bullets']}\n\n**Sources:** {', '.join(data['source_links'])}\n---\n"
    with open(doc_filename, "a", encoding="utf-8") as f:
        f.write(content)
        
    # 2. Draft Email
    draft = f"SUBJECT: Weekly Product Pulse + Customer Clarification — {data['identified_fee_issue']}\n\nBody:\nTeam,\n\nHere is this week's product pulse:\n{data['weekly_pulse']}\n\n---\nSUPPORT TEAM ACTION:\nPlease use this approved snippet:\n\n{data['explanation_bullets']}\nSources: {', '.join(data['source_links'])}\n"
    with open(email_filename, "w", encoding="utf-8") as f:
        f.write(draft)
        
    return doc_filename, email_filename

# ---------------------------------------------------------
# MAIN APP FLOW
# ---------------------------------------------------------
# File Uploader
uploaded_file = st.file_uploader("Upload Reviews CSV", type=['csv'])

if uploaded_file is not None:
    # Display the raw data
    df = pd.read_csv(uploaded_file)
    with st.expander("Preview Raw Data"):
        st.dataframe(df)

    # Convert dataframe to string for the prompt
    reviews_text = df.to_csv(index=False)

    if st.button("🧠 Analyze Reviews & Draft Intelligence"):
        with st.spinner("Analyzing themes and detecting issues..."):
            client = genai.Client()
            
            prompt = f"""
            You are an expert AI Product Manager. Analyze the following raw customer reviews:
            {reviews_text}

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

            max_retries = 4
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.8-flash-8b',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=response_schema,
                            temperature=0.2
                        )
                    )
                    break
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        time.sleep(5)
                    else:
                        st.error(f"API Error: {e}")
                        st.stop()
            
            if response:
                result = json.loads(response.text)
                result['date'] = datetime.now().strftime("%Y-%m-%d")
                
                # Save to session state so it persists when we click the approval button
                st.session_state['analysis_result'] = result
                st.success("Analysis Complete!")

# ---------------------------------------------------------
# RESULTS & MCP APPROVAL GATE
# ---------------------------------------------------------
if 'analysis_result' in st.session_state:
    result = st.session_state['analysis_result']
    
    st.header(f"🚨 Detected Friction Point: {result['identified_fee_issue']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Internal Weekly Pulse")
        st.info(result['weekly_pulse'])
        
    with col2:
        st.subheader("Customer-Facing Support Explainer")
        st.warning(result['explanation_bullets'])
        st.write("**References:**")
        for link in result['source_links']:
            st.write(f"- {link}")

    st.divider()
    st.subheader("Human-In-The-Loop Approval")
    
    if st.button("✅ Approve & Execute MCP Actions (Save to Docs & Draft Email)", type="primary"):
        doc_name, email_name = execute_mcp_workflows(result)
        st.success(f"Workflows Executed Successfully! Created `{doc_name}` and `{email_name}` in your local folder.")
        st.balloons()
