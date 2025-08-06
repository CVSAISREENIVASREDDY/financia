import streamlit as st
import os
import requests
from bs4 import BeautifulSoup 

from utils.auth import logout_button, check_login
from utils.database import Database
from utils.parser import parse_pdf
from utils.llm import GeminiModel

st.set_page_config(page_title="Upload Balance Sheet", page_icon="📤", layout="wide") 

if not "group_name" in st.session_state:
    group = st.selectbox("enter the group",["reliance","tata"])
    st.error("select group") 
else:
    group = st.session_state["group_name"]

group_db = Database(group) 
model = GeminiModel()

check_login()
logout_button()

st.write("login successful")

user_role = st.session_state.get('role')

if user_role != "analyst":
    st.error("Access Denied, you must login as analyst to upload files")
    st.stop()

st.title("📤 Upload Financial Report")

companies = group_db.get_all_companies()

st.write(f"As an analyst for the **{group}** group, you can upload annual financial reports for the following companies.")

source_format = st.selectbox("select your source format", ["pdf","web link"]) 


with st.form("upload_form", clear_on_submit=True):
    company_list = {c['name']: c['id'] for c in companies}

    selected_company_name = st.selectbox("Select Company", options=company_list.keys())
    year = st.number_input("Enter the Financial Year (e.g., 2023)", min_value=1950, max_value=2050, step=1, value=2023) 

    if source_format == "pdf":
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    else:
        url = st.text_input("enter the url")

    submitted = st.form_submit_button("Process and Save Data")

if source_format == "pdf" and submitted and uploaded_file is not None and year and selected_company_name:
    company_id = company_list[selected_company_name] 

    with st.spinner(f"Processing '{uploaded_file.name}' for {year}... This may take several minutes."):
        save_path = os.path.join("files", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.info("Step 1: Extracting text from PDF...")
        pages = parse_pdf(save_path)

        if not pages:
            st.error("Failed to extract any text from the PDF. The document might be scanned, encrypted or corrupted.")
            os.remove(save_path)
            st.stop()

        st.success(f"Text extraction complete. Found {len(pages)} pages with text.")

        st.info("Step 2: Analyzing pages with AI to extract financial data...") 

        financial_data = model.process_pdf_pages(pages, year)
        st.write(financial_data)

        os.remove(save_path)

        if "error" in financial_data:
            st.error(f"AI Analysis Failed: {financial_data['error']}")
        else:
            st.info("Step 3: Saving extracted data to the database...")
            group_db.save_financial_data(company_id, year, metrics= financial_data, source_document=uploaded_file.name)
            st.success(f"Successfully processed and saved") 

elif source_format == "web link" and submitted and year and selected_company_name:
    company_id = company_list[selected_company_name] 
    with st.spinner("Extracting and Processing the data in the given web page, this may take several minutes"):
        try:
            st.info("Extracting the data from the web page")
            response = requests.get(url)
            response.raise_for_status()  

            soup = BeautifulSoup(response.text, 'html.parser')

            text = soup.get_text(separator='\n')  

            cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip()) 
            st.success("Extraction Completed") 

            financial_data = model.structure_data_with_gemini(cleaned_text,year)
            st.write(financial_data) 
            
            if "error" in financial_data:
                st.error(f"AI Analysis Failed: {financial_data['error']}")
            else:
                st.info("Step 3: Saving extracted data to the database...")
                group_db.save_financial_data(company_id, year, metrics= financial_data, source_document= f'web source of {selected_company_name}' )
                st.success(f"Successfully processed and saved")

        except requests.exceptions.RequestException as e:
            st.error("fetch error") 