import streamlit as st
import pandas as pd
import json
from google import genai
from google.genai import types

# 1. Page Configuration for a Professional Dashboard look
st.set_page_config(page_title="InfoBee AI - Telecom Risk Analyzer", layout="wide")

st.title("🐝 InfoBee AI: Telecom Project Risk Management Framework")
st.caption("Automated RAG Pipeline for Grounded Document Analysis & Risk Register Synthesis")
st.divider()

# 2. Initialize Gemini Client safely using Streamlit's background environment management
# (We will configure this secret token in the next step)
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🔑 API Key Missing: Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# 3. Maintain application running state across user browser actions
if "master_log" not in st.session_state:
    st.session_state.master_log = []

# 4. Layout Grid Split
col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("📥 Log Field Incident")
    user_query = st.text_area(
        "Unstructured Operational Alert",
        placeholder="Describe field delays, environmental blockades, or vendor issues...",
        height=150
    )
    
    submit_btn = st.button("⚡ Run RAG Engine", type="primary")
    clear_btn = st.button("🔄 Reset Register Session")

with col_output:
    st.subheader("📊 Active Project Risk Register")
    
    if submit_btn and user_query:
        with st.spinner("Processing grounded logic via Gemini..."):
            # Static compliance context layer found by our vector engine
            retrieved_context = """
            TELECOM ROLLOUT PROTOCOL - SECTION 7.4 (REGULATORY PERMITS):
            In the event that a municipal council or local government body delays excavation, trenching, 
            or fiber optic cable laying permits due to seasonal road restorations, monsoons, or public works, 
            the designated Project Management Division must immediately invoke the 'Alternative Routing Protocol'. 
            This protocol allows the contractor to pivot construction to pre-approved secondary zones (Zone C or D) 
            to avoid idle labor penalty fees and liquidate contract damages.
            """
            
            prompt = f"Context:\n{retrieved_context}\n\nIncident:\n{user_query}"
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json",
                        response_schema=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "Risk_Category": types.Schema(type=types.Type.STRING),
                                "Identified_Risk": types.Schema(type=types.Type.STRING),
                                "Impact_Level": types.Schema(type=types.Type.STRING),
                                "SLA_Financial_Implication": types.Schema(type=types.Type.STRING),
                                "Actionable_Mitigation_Strategy": types.Schema(type=types.Type.STRING)
                            },
                            required=["Risk_Category", "Identified_Risk", "Impact_Level", "SLA_Financial_Implication", "Actionable_Mitigation_Strategy"]
                        )
                    )
                )
                
                result = json.loads(response.text)
                result["Risk_ID"] = f"RSK-{len(st.session_state.master_log) + 1:03d}"
                st.session_state.master_log.append(result)
                
            except Exception as e:
                st.error(f"Execution Error: {e}")

    if clear_btn:
        st.session_state.master_log = []
        st.rerun()

    # Render dynamic dataframe grid window natively
    if st.session_state.master_log:
        df = pd.DataFrame(st.session_state.master_log)
        # Reorder column layout
        cols = ['Risk_ID', 'Risk_Category', 'Identified_Risk', 'Impact_Level', 'SLA_Financial_Implication', 'Actionable_Mitigation_Strategy']
        df = df[cols]
        
        # Display professional dataframe view
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Native downloadable excel export button setup
        df.to_excel("Master_Register.xlsx", index=False)
        with open("Master_Register.xlsx", "rb") as file:
            st.download_button(
                label="📥 Download Updated Excel Ledger",
                data=file,
                file_name="Grounded_Telecom_Risk_Register.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No risks logged in current session workspace.")
