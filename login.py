import streamlit as st
from utils.database import Database
from utils.auth import logout_button

st.set_page_config(
    page_title="Balance Sheet Analyzer",
    layout="centered"
)

group = st.selectbox("select the parent group",["reliance","tata"]) 
st.session_state["group_name"] = group

if not ("group_name" in st.session_state or st.session_state['group_name'] == group):
    st.error("select group") 

group_db = Database(group)  

group_db.setup_database()

st.write("Please log in to continue.")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        user = group_db.get_user(username) 
        if user and user['password'] == password:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["username"] = user[1]
            st.session_state["role"] = user[3]
            st.success(f"Welcome, {st.session_state['username']}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.sidebar.success(f"Logged in as {st.session_state['username']} ({st.session_state['role']})")

    st.write("Login successful")
    st.write('You can now access the other pages')

    logout_button()
else:
    st.info("Please enter your credentials to access the application.")   