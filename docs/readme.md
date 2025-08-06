# Financia - AI-Powered Financial Analysis Tool

## Introduction

Financia is a web application that allows users to analyze the financial performance of companies. The application provides features for uploading financial reports, extracting key financial metrics using AI, and visualizing data through various charts. It also includes an AI-powered chat assistant to help users with their analysis.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/CVSAISREENIVASREDDY/financia.git](https://github.com/CVSAISREENIVASREDDY/financia.git)
    cd financia
    ```

2.  **Create and activate a virtual environment:**
    * **On Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the environment variables:**
    * Create a `.env` file in the root directory.
    * Add your Gemini API key to the `.env` file:
        ```
        GEMINI_API_KEY="your_api_key"
        ```

5.  **Run the application:**
    ```bash
    streamlit run login.py
    ```

6.  **Access the application:**
    * Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).