import streamlit as st
import requests
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Playwright Test Script Refiner",
    page_icon="🎭",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎭 Playwright Test Script Refiner</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for configuration
# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("🔑 API Settings (Loaded from Streamlit Secrets)")

    # Load from Streamlit secrets
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
        MODEL_NAME = st.secrets["GROQ_MODEL"]

        st.success("✅ API Key & Model loaded from Streamlit Secrets!")
    
    except Exception as e:
        st.error("❌ Missing secrets! Please add them in Streamlit → Settings → Secrets")
        st.info("""
        Add the following in your Streamlit secrets:
        
        GROQ_API_KEY = "your_key_here"
        GROQ_MODEL = "llama-3.3-70b-versatile"
        """)
        GROQ_API_KEY = ""
        MODEL_NAME = "llama-3.3-70b-versatile"

    st.markdown("---")
    st.markdown("### 📝 Output Settings")
    output_filename = st.text_input(
        "Output Filename",
        value="refined_file.py",
        help="Name for the refined script file"
    )


# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Auto-Generated Test Script")
    generated_script = st.text_area(
        "Paste your auto-generated Playwright Python test script here:",
        height=400,
        placeholder="Your auto-generated Playwright Python test script goes here...",
        key="generated_script"
    )

with col2:
    st.subheader("🎬 Playwright Codegen Interactions")
    playwright_codegen_interactions = st.text_area(
        "Paste your Playwright Codegen interactions here:",
        height=400,
        placeholder="Your Playwright Codegen interactions go here...",
        key="codegen_interactions"
    )

# Refine button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    refine_button = st.button("🚀 Refine Test Script", type="primary", use_container_width=True)

# Process refinement
if refine_button:
    # Validation
    if not GROQ_API_KEY:
        st.error("❌ Please provide a API Key in the sidebar.")
    elif not generated_script.strip():
        st.error("❌ Please provide the auto-generated test script.")
    elif not playwright_codegen_interactions.strip():
        st.error("❌ Please provide the Playwright Codegen interactions.")
    else:
        with st.spinner("🔄 Refining your test script with Grok AI..."):
            # Create the refine prompt
            refine_prompt = f"""
You are an expert QA automation assistant specializing in Playwright.

Your task is to take the **auto-generated test script** below and refine it 
according to the **Playwright Codegen interactions** that follow.

Requirements:

1. Carefully compare the auto-generated test script with the recorded Playwright Codegen steps. Update the script to match every step, including navigation, clicks, typing, and element interactions.
2. Fix all selectors in the auto-generated script to exactly match those recorded by Playwright Codegen.
3. Ensure proper waiting:
   - Always use `expect(locator).to_be_visible()` before interacting with an element.
   - Use `wait_for_load_state("domcontentloaded")` for page navigations if necessary.
   - Use `wait_for_function` to wait for dynamic content when verifying chatbot responses.
   - Use expect().to_contain_text() for verifying chatbot responses that expect some text to appear/visible.
4. You must adhere to five golden rules to fix the race conditions between terminal execution and the visual browser rendering:
    - Every single test function must start by reloading the page (page.goto(BASE_URL)). Do not rely on the state from a previous test.
    - Wait for the load state immediately after: page.wait_for_load_state("domcontentloaded").
    - Never sleep/wait before verifying the text. Always use expect(locator).to_contain_text(...) first. This ensures the code waits for the response to actually arrive in the DOM.
    - Immediately after the expect assertion passes, but before the print and screenshot commands, insert a hard pause: page.wait_for_timeout(5000).
    - All screenshots must use the argument: full_page=True.
    - Wrap every test in a try/except block.
5. Assertions:
   - Use `expect()` for assertions such as `to_have_text()`, `to_be_visible()`, or equivalent.
   - Use `print()` only for logging success/failure messages.
6. Input fields:
   - Include `.click()` before filling if required.
   - Include `.press("Enter")` if part of the recorded interaction.
7. Timeouts:
   - Add reasonable wait times or checks between steps where required for the page to load or update.
8. Script structure:
   - Each test case should run inside a `try/except` block.
   - If a test passes, mark `"Pass"`; if it fails, mark `"Fail"`.
   - Generate an Excel sheet at the end containing test case names and their status.
9. Comments:
   - Include concise, relevant code comments for clarity.
   - Do not add unrelated explanations.
10. Final script:
   - Must be syntactically correct and ready to run.
   - Remove any ```python``` code fences or tags.
11. Output:
   - Return a complete Playwright Python test script with dynamic Pass/Fail logging and Excel export.
   - Generate screenshots for each test case and save them in a `screenshots` folder.
   - Moreover, for the generated excel sheet that includes test case names and their status, can you also give me over all count of total test cases, passed test cases, and failed test cases. Show them through a interactive grid format using pandas library.
   - For generating the summary:
        - Create a new sheet named "Overview" in the same Excel file.
        - Write the overall statistics to this sheet.
        - The summary should include:
            - Total Test Cases
            - Passed Test Cases
            - Failed Test Cases
        - Generate a Bar Chart visualizing the Total vs. Passed vs. Failed counts.
        - Place the chart below the overall statistics in the "Overview" sheet.
    - After doing all of the above, create another sheet named "Details" in the same Excel file.
    - IMPORTANT: In the "Details" sheet, generate a summary table where each row represents a Feature Name and columns represent the 
    following status counts: Pass, Fail, and Total. The table should resemble a structured grid where 
    the first column lists feature names and the rest of the columns show numerical counts of test cases in each category. 
    The Total column must show the sum of Pass + Fail for each feature. This grid should visually resemble a clean tabular report summarizing test case execution by feature.
    - The requirements for creating this grid are:
        - Each row represents a Feature Name.
        - Columns must include
           Feature Name
           Pass Count (colored green)
           Fail Count (colored red)
           Total Test Cases (colored blue/gray)
           Total Test Cases = Pass + Fail for every feature.
        - Apply the following formatting:
        Header row must be bold with a light gray background.
        Pass cells must have a green background with white or dark text.
        Fail cells must have a red background with white text.
        Total cells must have a blue/gray background.
        Feature names remain uncolored (white background).
    - The grid must visually look like a clean dashboard-style report (similar to a KPI table).
---
Auto-generated test script:
{generated_script}

---
Playwright Codegen interactions:
{playwright_codegen_interactions}

---
Now produce the corrected and refined **Playwright Python test script** ready to run.
"""

# Grok API URL
# Groq LLaMA API URL
            url = "https://api.groq.com/openai/v1/chat/completions"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            }

            # Payload for Groq LLaMA
            data = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "You are an expert QA automation assistant specializing in Playwright."},
                    {"role": "user", "content": refine_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 8192,
                "top_p": 0.95
            }

            # Send request to Groq LLaMA
            try:
                response = requests.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    try:
                        reply_json = response.json()
                        reply = reply_json["choices"][0]["message"]["content"]

                        # Save to file
                        with open(output_filename, "w", encoding="utf-8") as f:
                            f.write(reply.strip())

                        st.success(f"✅ Refined script saved successfully to: **{output_filename}**")

                        st.markdown("---")
                        st.subheader("🎉 Refined Test Script")

                        tab1, tab2 = st.tabs(["📖 View Script", "📥 Download"])

                        with tab1:
                            st.code(reply.strip(), language="python", line_numbers=True)

                        with tab2:
                            st.download_button(
                                label="⬇️ Download Refined Script",
                                data=reply.strip(),
                                file_name=output_filename,
                                mime="text/x-python",
                                use_container_width=True
                            )

                    except Exception as e:
                        st.error(f"❌ Error parsing Groq response: {str(e)}")
                        with st.expander("🔍 View Raw Response"):
                            st.text(response.text)

                else:
                    st.error(f"❌ API Error {response.status_code}")
                    with st.expander("🔍 View Error Details"):
                        st.text(response.text)

            except Exception as e:
                st.error(f"❌ Request failed: {str(e)}")


            # Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🎭 Playwright Test Script Refiner | Powered by Grok API AI</p>
        <p style='font-size: 0.8rem;'>Automatically refines auto-generated test scripts using Playwright Codegen interactions</p>
    </div>
""", unsafe_allow_html=True)