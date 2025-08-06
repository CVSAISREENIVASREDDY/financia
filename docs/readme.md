# Financia - AI-Powered Financial Analysis Tool

## Introduction

Financia is a web application that allows users to analyze the financial performance of companies. The application provides features for uploading financial reports, extracting key financial metrics using AI, and visualizing data through various charts. It also includes an AI-powered chat assistant to help users with their analysis.

## Features

- Secure Login with Role-Based Access 
    - Analyst: Upload PDFs and view all companies of the selected Group of Industries. 
    - CEO: View their company's financials.
    - Top Management: View all companies under their group. 

- upload sources 
    - PDF Parsing using `pdfplumber`, page-by-page
    - Web Page Content Extraction using `requests` and `BeautifulSoup` 
    - Structured Storage of extracted metrics in SQLite

- Analysis 
    - AI-Powered Financial Analysis using Google Gemini
    - Interactive Visualizations with Plotly (Line, Bar, Growth, Asset-Liability charts)
    - Natural Language Chat Interface for AI-based Q&A

---

## Tech Stack

| Component | Tool / Library |
|---|---|
| Frontend | Streamlit |
| AI / LLM | Gemini 1.5 flash |
| PDF Parsing | pdfplumber |
| Web Scraping | requests, beautifulsoup4 |
| Database | SQLite |
| Charts | Plotly |

---

## Sample Login Credentials 
Tata
| username | password |
|---|---|
| tata_analyst | tata1234 | 
| tata_steel_ceo | steel1234 | 
| tata_owner | tata1234 | 

Reliance
|---|---|
| reliance_analyst | reliance123 | 
| jio_ceo | jio12345 | 
| reliance_owner | reliance123 |


## Setup & Installation
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