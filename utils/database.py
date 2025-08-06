import sqlite3

class Database:
    def __init__(self,group_name):
        self.group_name = group_name 
        self.DB_PATH = f"data/{group_name}.db"

    def get_db_connection(self):
        """Establishes a connection to the SQLite database."""
        conn = sqlite3.connect(self.DB_PATH, check_same_thread=False) 
        conn.row_factory = sqlite3.Row
        return conn

    def setup_database(self): 
        """Creates the necessary tables if they don't exist and populates initial data."""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT UNIQUE, group_name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS user_company_access (user_id INTEGER, company_id INTEGER, PRIMARY KEY (user_id, company_id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS financial_data (id INTEGER PRIMARY KEY, company_id INTEGER, year INTEGER, metric TEXT, value REAL, source_document TEXT, UNIQUE(company_id, year, metric))")

        if self.group_name == 'reliance' and cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('reliance_analyst', 'reliance123', 'analyst'))
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('jio_ceo', 'jio12345', 'ceo'))
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('reliance_owner', 'reliance123', 'top_management'))

        if self.group_name == 'tata' and cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('tata_analyst', 'tata1234', 'analyst'))
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('tata_steel_ceo', 'steel1234', 'ceo'))
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('tata_owner', 'tata1234', 'top_management'))

        if self.group_name == 'reliance' and cursor.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
            cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Reliance Jio', 'Reliance'))
            cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Reliance Trends', 'Reliance'))
            cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Reliance Industries', 'Reliance')) 

        if self.group_name == 'tata' and cursor.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
            cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Tata Steel', 'TATA'))
            cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Tata Motors', 'TATA'))
            cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Tata Salt', 'TATA')) 

        if self.group_name == "reliance" and cursor.execute("SELECT COUNT(*) FROM user_company_access").fetchone()[0] == 0:
            cursor.execute("INSERT INTO user_company_access (user_id, company_id) VALUES ((SELECT id FROM users WHERE username='jio_ceo'), (SELECT id FROM companies WHERE name='Reliance Jio'))")
        
        if self.group_name == "tata" and cursor.execute("SELECT COUNT(*) FROM user_company_access").fetchone()[0] == 0:
            cursor.execute("INSERT INTO user_company_access (user_id, company_id) VALUES ((SELECT id FROM users WHERE username='tata_steel_ceo'), (SELECT id FROM companies WHERE name='Tata Steel'))")

        conn.commit()
        conn.close()

    def get_user(self,username):
        conn = self.get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        return user

    def get_user_accessible_companies(self,user_id, role):
        conn = self.get_db_connection()
        if role == 'top_management' or role == 'analyst':
            companies = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
        elif role == 'ceo':
            companies = conn.execute('SELECT c.* FROM companies c JOIN user_company_access uca ON c.id = uca.company_id WHERE uca.user_id = ?', (user_id,)).fetchall()
        else:
            companies = []
        conn.close()
        return companies

    def get_all_companies(self):
        conn = self.get_db_connection()
        companies = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
        conn.close()
        return companies

    def save_financial_data(self, company_id, year, metrics, source_document):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        print(f"[DEBUG] Connected to DB: {self.DB_PATH}")
        print(f"[DEBUG] Saving data for company_id={company_id}, year={year}, source={source_document}")
    
        inserted_count = 0
        for metric, value in metrics.items():
            try:
                cleaned_value = float(str(value).replace(',', '').replace('(', '-').replace(')', ''))
            except (ValueError, TypeError):
                print(f"[SKIP] Metric: {metric} has invalid value: {value}")
                continue
            
            try:
                cursor.execute(
                    '''INSERT OR REPLACE INTO financial_data 
                       (company_id, year, metric, value, source_document) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (company_id, year, metric, cleaned_value, source_document)
                )
                inserted_count += 1
                print(f"[OK] Inserted: {metric} = {cleaned_value}")
            except Exception as e:
                print(f"[ERROR] Failed to insert {metric}: {e}")
    
        conn.commit()
    
        try:
            cursor.execute('SELECT * FROM financial_data WHERE company_id = ? AND year = ?', (company_id, year))
            rows = cursor.fetchall()
            print(f"[DEBUG] {len(rows)} rows now exist for company_id={company_id}, year={year}")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"[ERROR] Failed to fetch saved data: {e}")
    
        conn.close()
        print(f"[DONE] Saved {inserted_count} metrics.\n")
    

    def get_company_financials(self,company_id):
        conn = self.get_db_connection()
        data = conn.execute('SELECT year, metric, value FROM financial_data WHERE company_id = ? ORDER BY year, metric', (company_id,)).fetchall()
        conn.close()
        return data 