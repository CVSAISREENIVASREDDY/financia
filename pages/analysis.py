import streamlit as st
import pandas as pd
import json
from utils.auth import check_login, logout_button
from utils.database import Database
from utils.llm import GeminiModel
from utils.plot import (
    create_line_chart,
    create_bar_chart,
    create_asset_liability_chart,
    create_growth_chart
)

st.set_page_config(page_title="AI Financial Analyst", page_icon="🤖", layout="wide")

# Use a single, persistent model instance
if "model" not in st.session_state:
    st.session_state.model = GeminiModel()
model = st.session_state.model

if "group_name" not in st.session_state or not st.session_state["group_name"]:
    group_name = st.selectbox("select the group", ["reliance", "tata"])
    st.session_state["group_name"] = group_name
else:
    group_name = st.session_state["group_name"]

group_db = Database(group_name)

check_login()
logout_button()

st.title("Financial Analysis with Gemini-1.5-flash")
st.markdown("Select a company to review its financial snapshot and receive expert analysis with your AI partner.")
st.divider()

user_id = st.session_state["user_id"]
role = st.session_state["role"]

accessible_companies = group_db.get_user_accessible_companies(user_id, role)

if not accessible_companies:
    st.warning("You do not have access to any companies. Please contact an administrator.")
    st.stop()
company_options = {c['name']: c['id'] for c in accessible_companies}

selected_company_name = st.selectbox("Select a Company to Analyze", options=company_options.keys(), index=0)

if not selected_company_name:
    st.warning("select a company")
    st.stop()
selected_company_id = company_options[selected_company_name]

financial_records = group_db.get_company_financials(selected_company_id)
if not financial_records:
    st.error(f"No financial data found for {selected_company_name}. Please upload a financial report for this company first.")
    st.stop()

df = pd.DataFrame(financial_records, columns=['year', 'metric', 'value'])
st.header(f"Financial Snapshot: {selected_company_name}")
snapshot_df = df.pivot_table(index='metric', columns='year', values='value').sort_index()
st.dataframe(snapshot_df.style.format("{:,.2f}", na_rep="-"), use_container_width=True)
st.divider()

data_summary = snapshot_df.to_string()

st.title(f"💬 Chat with Expert assistant")

# Reset chat history and start a new session when the company changes
if st.session_state.get("company_id") != selected_company_id:
    st.session_state.messages = [{"role": "assistant", "content": {"message": f"Hi! How can I help you analyze the financial performance of {selected_company_name}?"}}]
    st.session_state.company_id = selected_company_id
    # Pass the initial history to start the new chat session
    model.start_chat_session(st.session_state.messages)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if "message" in content and content["message"]:
            st.markdown(content["message"])

        # Logic for displaying plots from historical messages
        if "plot_request" in content and content.get("plot_request"):
            plot_info = content["plot_request"]
            # ... (plotting logic is the same)
            plot_type = plot_info.get("type")
            metric = plot_info.get("metric")
            title = plot_info.get("title")
            fig = None
            if plot_type == "line":
                fig = create_line_chart(snapshot_df, metric, title)
            elif plot_type == "bar":
                fig = create_bar_chart(snapshot_df, metric, title)
            elif plot_type == "asset_liability_comparison":
                fig = create_asset_liability_chart(snapshot_df, title)
            elif plot_type == "growth":
                fig = create_growth_chart(snapshot_df, metric, title)

            if fig:
                st.plotly_chart(fig, use_container_width=True)


if prompt := st.chat_input(f"Ask about {selected_company_name}'s financial performace"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": {"message": prompt}})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            # The model now handles greetings, analysis, and context internally
            # We check for keywords to decide if the detailed data_summary is needed
            # analysis_keywords = ['analyze', 'revenue', 'profit', 'growth', 'compare', 'show me']
            # should_send_data = any(keyword in prompt.lower() for keyword in analysis_keywords)
            
            summary_to_send = data_summary 
            
            response_dict = model.chat_with_gemini(prompt, summary_to_send)
            response_content = response_dict

            if "message" in response_dict and response_dict["message"]:
                st.markdown(response_dict["message"])

            # Logic for plotting the new response
            if "plot_request" in response_dict and response_dict.get("plot_request"):
                plot_info = response_dict["plot_request"]
                plot_type = plot_info.get("type")
                metric = plot_info.get("metric")
                title = plot_info.get("title")
                fig = None

                if plot_type == "line":
                    fig = create_line_chart(snapshot_df, metric, title)
                elif plot_type == "bar":
                    fig = create_bar_chart(snapshot_df, metric, title)
                elif plot_type == "asset_liability_comparison":
                    fig = create_asset_liability_chart(snapshot_df, title)
                elif plot_type == "growth":
                    fig = create_growth_chart(snapshot_df, metric, title)

                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Could not generate plot for metric: '{metric}'. Please ensure it's in the data table.")

    st.session_state.messages.append({"role": "assistant", "content": response_content})