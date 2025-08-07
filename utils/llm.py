import json
import google.generativeai as genai
import os
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not found in environment variables. Please set it before running the app.")
    raise ValueError("GEMINI_API_KEY is required for GeminiModel to function.")
genai.configure(api_key=API_KEY)

REQUIRED_KEYS = [
    "Revenue from Operations", "Other Income", "Total Income", "Profit Before Tax",
    "Net Profit", "Total Equity", "Total Assets", "Total Liabilities",
    "Non-current assets", "Current assets", "Non-current liabilities",
    "Current liabilities", "Cash and cash equivalents", "Earnings Per Share (Basic)"
]

class GeminiModel:
    def __init__(self):
        # Model for data extraction remains stateless
        self.extraction_model = genai.GenerativeModel("gemini-1.5-flash-latest")

        # Instructions for the main analyst model
        analyst_instructions = """
            You are an expert Financial analyst and a helpful conversational assistant. Your goal is to help a top executive understand their company's performance by analyzing data and chatting with them.

            Your Core Directives:
            1.  **Be Conversational**: Remember the user's name and previous parts of the conversation. Respond naturally.
            2.  **Analyze and Interpret**: When asked for analysis, provide concise insights. Identify trends, risks, and opportunities from the provided data.
            3.  **RESPONSE FORMAT**: Your ENTIRE response MUST be a single, valid JSON object.
                - It MUST contain a "message" key with your textual analysis or conversational reply.
                - If and only if the query requires a visualization, include a "plot_request" key.
            4.  **PLOTTING**: The "plot_request" must follow this schema:
                `"plot_request": {"type": "...", "metric": "...", "title": "..."}`.
                - Use types: "line", "bar", "asset_liability_comparison", "growth".
                - Match the "metric" name EXACTLY from the data table.
            5.  **Data Context**: Financial data will be provided with prompts that need analysis. Use it to answer, but don't mention the data prompt itself to the user.
            """
        # We will use this model to create a stateful chat session
        self.analyst_model = genai.GenerativeModel("gemini-1.5-flash-latest", system_instruction=analyst_instructions)
        self.chat_session = None

    def start_chat_session(self, history):
        """Starts a new, stateful chat session, optionally loading previous history."""
        # Convert our Streamlit history to the format google-genai expects
        genai_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            # Ensure content is always a string for the history
            content_text = msg["content"].get("message", "") if isinstance(msg["content"], dict) else str(msg["content"])
            genai_history.append({"role": role, "parts": [content_text]})

        self.chat_session = self.analyst_model.start_chat(history=genai_history)

    def chat_with_gemini(self, user_prompt, data_summary=None):
        """Sends a message to the ongoing chat session, including data context if needed."""
        if not self.chat_session:
            # Failsafe in case chat is not started
            self.start_chat_session([])

        # Prepend data summary to analytical prompts for context
        full_prompt = user_prompt
        if data_summary:
            full_prompt = f"CONTEXTUAL FINANCIAL DATA:\n{data_summary}\n\nUSER PROMPT: {user_prompt}"

        try:
            response = self.chat_session.send_message(
                full_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            return {"message": f"I apologize, but I encountered an issue. (Error: {e})"}

    def structure_data_with_gemini(self, text, year):
        prompt = f"""
        Analyze the following financial report text for the year {year}.
        Your task is to extract the specified financial metrics.

        Follow these rules strictly:
        1.  Return ONLY a single, valid JSON object. Do not include any other text, explanations, or markdown.
        2.  The JSON object must contain these exact keys: {', '.join(REQUIRED_KEYS)}.
        3.  Be flexible with labels: "Revenue from Operations" might appear as "Income from sales" or similar variations. Map them correctly.
        4.  If a value for a specific key cannot be found in the text, the value in the JSON must be `null`. Do not guess or make up values.
        5.  All numerical values must be in a raw number format (e.g., 123456.78). Remove all commas, currency symbols, and text like "Cr.".
        6.  Pay close attention to negative numbers, often in parentheses, e.g., (123.45). Convert them to negative numbers, e.g., -123.45.
        7.  The report might be for a consolidated or standalone entity. Extract the data that is most prominently displayed.
        Full Financial Report Text:
        ---
        {text}
        ---
        """
        try:
            response = self.extraction_model.generate_content(
                prompt,
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )

            json_str = response.text
            data = json.loads(json_str)
            for key in REQUIRED_KEYS:
                if key not in data:
                    data[key] = None
            return data

        except Exception as e:
            print(f"Error during Gemini extraction or JSON parsing: {e}")
            response_text = "No response from API."
            if 'response' in locals() and hasattr(response, 'text'):
                response_text = response.text
            return {"error": f"JSON parsing failed: {str(e)}", "details": response_text}

    def process_pdf_pages(self, pages, year):
        """
        Processes the entire PDF in one go (all pages at once).
        """
        combined_text = "\n\n--- PAGE BREAK ---\n\n".join(pages)

        extracted_data = self.structure_data_with_gemini(combined_text[:900_000], year)

        if "error" in extracted_data:
            return {"error": "Failed to extract data from the report.", "details": extracted_data.get("details")}

        return extracted_data 