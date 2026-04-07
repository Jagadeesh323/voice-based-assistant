import streamlit as st
import sqlite3
import bcrypt

hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(page_title="ORA Auth", page_icon="🎙️", layout="centered")

# -----------------------------------
# SQLite Setup
# -----------------------------------
conn = sqlite3.connect("ora_users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

# -----------------------------------
# Helper Functions
# -----------------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def register_user(full_name, email, password):
    try:
        hashed = hash_password(password)
        c.execute(
            "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
            (full_name, email, hashed),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()

    if not user:
        return "email_not_found"

    if verify_password(password, user[3]):
        return user

    return "wrong_password"


# -----------------------------------
# UI Styling
# -----------------------------------
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #334155);
}

.title {
    text-align: center;
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 1.5rem;
}

div[data-testid="stTextInput"] input {
    border-radius: 12px;
}

div[data-testid="stButton"] > button {
    width: 100%;
    border-radius: 12px;
    height: 3rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# Session state
# -----------------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Hyperlink route
if st.query_params.get("auth") == "register":
    st.session_state.page = "register"

# -----------------------------------
# Main UI
# -----------------------------------
st.markdown('<div class="title">ORA</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Voice Email & Messaging Assistant</div>', unsafe_allow_html=True)

# -----------------------------------
# Login Page
# -----------------------------------
if st.session_state.page == "login" and not st.session_state.logged_in:
    st.subheader("Welcome to ORA")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # ✅ Empty field validation
        if not email or not password:
            st.warning("⚠ Please enter email and password")
        else:
            result = login_user(email, password)

            if result == "email_not_found":
                st.error("❌ Email not found")
            elif result == "wrong_password":
                st.error("❌ Incorrect password")
            else:
                st.session_state.logged_in = True
                st.session_state.user = result[1]
                st.session_state.page = "inbox"
                st.rerun()

    st.markdown(
        "New User? <a href='?auth=register' style='color:#60a5fa;text-decoration:underline;font-weight:600;'>Register Here</a>",
        unsafe_allow_html=True
    )

# -----------------------------------
# Register Page
# -----------------------------------
elif st.session_state.page == "register":
    st.subheader("Create Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if not full_name or not email or not password:
            st.warning("Please fill all fields")
        elif password != confirm_password:
            st.error("Passwords do not match")
        else:
            success = register_user(full_name, email, password)

            if success:
                st.success("✅ Registered successfully")
                
                # clear query param
                st.query_params.clear()

                # redirect to login
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Email already exists")

    if st.button("⬅ Back to Login"):
        # clear register route
        st.query_params.clear()

        st.session_state.page = "login"
        st.rerun()

# -----------------------------------
# Unified Inbox
# -----------------------------------
elif st.session_state.page == "inbox":
    st.success(f"✅ Welcome {st.session_state.user}")

    st.title("Unified Inbox")
    st.write("inbox UI comes here...")

    st.markdown("---")  # optional divider

    # ✅ Logout button at bottom
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.session_state.user = None
        st.rerun()

    
    
