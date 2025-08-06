# System Architecture

This document outlines the architecture of the Financia application, a web-based tool for financial analysis.

## Components

### 1. `login.py`

* **Purpose:** Handles user authentication.
* **Components:**
    * **`st.set_page_config`:** Configures the Streamlit page with a title and layout.
    * **`st.selectbox`:** Allows the user to select the parent group ("reliance" or "tata").
    * **`Database` class:** Initializes a connection to the database for the selected group.
    * **`st.form`:** Creates a login form with fields for username and password.
    * **`group_db.get_user`:** Validates user credentials against the database.
    * **`st.session_state`:** Stores user session information, such as login status, username, and role.
    * **`logout_button`:** A button to log the user out.

### 2. `pages/upload.py`

* **Purpose:** Allows analysts to upload financial reports in PDF or web link format.
* **Components:**
    * **`st.set_page_config`:** Configures the Streamlit page.
    * **`Database` class:** Connects to the database.
    * **`GeminiModel` class:** Initializes the Gemini model for AI-powered data extraction.
    * **`check_login` and `logout_button`:** Enforces authentication and provides a logout option.
    * **`st.form`:** A form for uploading files, including company selection, financial year, and file/URL input.
    * **`parse_pdf`:** Extracts text from uploaded PDF files.
    * **`model.process_pdf_pages`:** Processes the extracted text to extract financial data.
    * **`requests` and `BeautifulSoup`:** Fetches and parses content from web links.
    * **`model.structure_data_with_gemini`:** Extracts financial data from the cleaned text of a web page.
    * **`group_db.save_financial_data`:** Saves the extracted financial data to the database.

### 3. `pages/analysis.py`

* **Purpose:** Provides an interface for financial analysis and chat with an AI assistant.
* **Components:**
    * **`st.set_page_config`:** Sets up the Streamlit page.
    * **`Database` class:** Connects to the database.
    * **`GeminiModel` class:** Initializes the Gemini model for analysis and chat.
    * **`check_login` and `logout_button`:** Manages user authentication.
    * **`st.selectbox`:** Allows users to select a company to analyze.
    * **`pd.DataFrame`:** Displays financial data in a structured table.
    * **`st.chat_input` and `st.chat_message`:** Creates a chat interface for interacting with the AI assistant.
    * **`model.chat_with_gemini`:** Sends user prompts and financial data to the Gemini model for analysis.
    * **Plotting functions (`create_line_chart`, `create_bar_chart`, etc.):** Generates visualizations of the financial data.

### 4. `utils/`

* **`auth.py`:**
    * **`check_login`:** Checks if a user is logged in.
    * **`check_role_access`:** Verifies if the user has the appropriate role for a given page.
    * **`login_user`:** Validates user credentials.
    * **`logout_button`:** Creates a logout button.

* **`database.py`:**
    * **`Database` class:** Manages the SQLite database connection and operations.
    * **`setup_database`:** Initializes the database schema and populates initial data.
    * **`get_user`:** Retrieves user information from the database.
    * **`get_user_accessible_companies`:** Fetches the list of companies a user can access.
    * **`save_financial_data`:** Saves extracted financial data.

* **`llm.py`:**
    * **`GeminiModel` class:** A wrapper for the Google Generative AI API.
    * **`start_chat_session`:** Initializes a chat session with the AI model.
    * **`chat_with_gemini`:** Sends messages to the AI model and receives responses.
    * **`structure_data_with_gemini`:** Extracts and structures financial data from text using the AI model.
    * **`process_pdf_pages`:** Processes text from a PDF to extract financial data.

* **`parser.py`:**
    * **`parse_pdf`:** Extracts text from PDF files using the `pdfplumber` library.

* **`plot.py`:**
    * Contains functions to create various charts (`line`, `bar`, `asset_liability_comparison`, `growth`) using the `plotly` library.