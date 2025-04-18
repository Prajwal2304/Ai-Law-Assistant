import streamlit as st
import os
import sqlite3
from hashlib import sha256
import base64
import PyPDF2
import docx
import pdfplumber
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import time

# Page configuration with custom theme
st.set_page_config(
    page_title="LexAssist",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2C3E50;
        --secondary-color: #3498DB;
        --accent-color: #E74C3C;
        --background-color: #ECF0F1;
        --text-color: #2C3E50;
    }
    
    /* Header styling */
    .main-header {
        color: var(--primary-color);
        font-size: 3rem; /* Updated font size */
        font-weight: 700;
        margin-bottom: 0;
        padding-bottom: 0;
        text-align: center;
    }
    
    .sub-header {
        color: var(--secondary-color);
        font-size: 1.5rem; /* Updated font size */
        font-weight: 400;
        margin-top: 0;
        padding-top: 0;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
    }
    
    .card-title {
        color: var(--primary-color);
        font-size: 1.8rem; /* Updated font size */
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .card-icon {
        font-size: 2.5rem;
        color: var(--secondary-color);
        margin-bottom: 10px;
        text-align: center;
    }
    
    .card-text {
        color: var(--text-color);
        font-size: 1.2rem; /* Updated font size */
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--secondary-color);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px; 
        font-weight: 600;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-color);
        transform: translateY(-2px);
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #ddd;
        padding: 10px;
        font-size: 1.2rem; /* Updated font size */
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 5px;
        border: 1px solid #ddd;
        padding: 10px;
        font-size: 1.2rem; /* Updated font size */
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px; /* Updated height */
        white-space: pre-wrap;
        background-color: white;
        border-radius: 5px;
        border: 1px solid #ddd;
        color: var(--text-color);
        font-weight: 500;
        font-size: 1.2rem; /* Updated font size */
        padding: 0 24px; /* Updated padding */
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--secondary-color) !important;
        color: white !important;
    }
    
    /* Main navigation tabs */
    .main-nav {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
        background-color: var(--primary-color);
        padding: 10px;
        border-radius: 10px;
    }
    
    .main-nav-tab {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 12px 24px; /* Updated padding */
        font-weight: 500;
        font-size: 1.2rem; /* Updated font size */
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .main-nav-tab:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    .main-nav-tab.active {
        background-color: var(--secondary-color);
    }
    
    /* User profile section */
    .user-profile {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin-bottom: 10px;
        padding: 5px 10px;
        border-radius: 5px;
    }
    
    .user-avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background-color: var(--secondary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-right: 10px;
        font-size: 1rem;
    }
    
    .user-name {
        color: var(--primary-color);
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed var(--secondary-color);
    }
    
    /* Success/Info/Warning message styling */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
        font-size: 1rem;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
        
        .main-nav {
            flex-wrap: wrap;
        }
        
        .main-nav-tab {
            font-size: 0.9rem;
            padding: 8px 15px;
        }
    }
    
    /* Improved font sizing for better readability */
    p, li, div {
        font-size: 1.2rem; /* Updated font size */
        line-height: 1.6;
    }
    
    h1 {
        font-size: 2.5rem; /* Updated font size */
    }
    
    h2 {
        font-size: 2.2rem; /* Updated font size */
    }
    
    h3 {
        font-size: 1.8rem; /* Updated font size */
    }
    
    h4 {
        font-size: 1.5rem; /* Updated font size */
    }
    
    /* Logout button styling */
    .logout-button {
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        padding: 5px 15px !important;
        font-size: 0.9rem !important;
    }
    
    .logout-button:hover {
        background-color: rgba(44, 62, 80, 0.1) !important;
    }

    /* Login/Signup button positioning */
    .corner-button {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
    }

    .corner-button button {
        min-width: 120px;
        font-size: 1.2rem; /* Updated font size */
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Homepage"

# Database setup
conn = sqlite3.connect('user_profiles.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS user_profiles
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query TEXT,
    response TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id))''')
c.execute('''CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password TEXT)''')

# Groq API setup
groq_api_key = os.getenv('GROQ_API_KEY', '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')
if not groq_api_key:
    st.error("Groq API key not found. Please set the GROQ_API_KEY environment variable.")
else:
    chat = ChatGroq(temperature=0, model="llama-3.3-70b-versatile", api_key=groq_api_key)
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api_key)

# Chat prompts
system_classification = "You are an intelligent assistant that classifies and extracts meaningful data from legal documents. Your task is to understand and categorize the document content and extract crucial details such as the type of document, involved parties, case number, and legal provisions cited."
human_classification = "Classify and extract key details from this legal document: {text}. Determine the document type and identify important information such as involved parties and legal references."
prompt_classification = ChatPromptTemplate.from_messages([("system", system_classification), ("human", human_classification)])

system_legal = "You are an intelligent legal assistant who provides legal advice based on the Indian judiciary, the Indian Penal Code, and the Constitution. For the queries provided, provide detailed explanation along with acts that can be applied and the legal provisions that can be used to support the answer. DO NOT ANSWER OUTSIDE THE LEGAL DOMAIN. IF ASKED, JUST SAY NO RELEVANT INFO."
human_legal = "{text}"
prompt_legal_advice = ChatPromptTemplate.from_messages([("system", system_legal), ("human", human_legal)])

system_doc_gen = "You are an intelligent assistant for document generation. You are supposed to only do the given task for law and legal related documents. You are just for generation of legal documents. If query is from outside this domain, answer that you don't have relevant knowledge."
human_doc_gen = "{text}"
prompt_doc_gen = ChatPromptTemplate.from_messages([("system", system_doc_gen), ("human", human_doc_gen)])

system_metadata = "You are an intelligent assistant for extracting metadata from legal documents. Your task is to understand and categorize the document content and extract crucial details such as the type of document, involved parties, case number, and legal provisions cited."
human_metadata = "Extract the following metadata from this document: {text}"
prompt_metadata = ChatPromptTemplate.from_messages([("system", system_metadata), ("human", human_metadata)])

# Helper functions
def hash_password(password):
    return sha256(password.encode()).hexdigest()

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to split text into chunks of max 2000 tokens
def split_into_chunks(text, chunk_size=2000):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.success("Logged out successfully.")
    time.sleep(1)
    st.rerun()

# Add this function after the other helper functions:
def clear_user_history(user_id):
    c.execute("DELETE FROM user_profiles WHERE user_id=?", (user_id,))
    conn.commit()
    return True

# Main App
if not st.session_state.logged_in:
    # App header for login/signup page
    st.markdown('<h1 class="main-header">LexAssist</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Legal Assistance</p>', unsafe_allow_html=True)
    
    # Login/Signup container with centered content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown('<h3 class="card-title">Welcome Back!</h3>', unsafe_allow_html=True)
            with st.form("login_form"):
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")
                
                # Move login button to corner
                st.markdown('<div class="corner-button">', unsafe_allow_html=True)
                login_button = st.form_submit_button("Login")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if login_button:
                    if login_email and login_password:
                        with st.spinner("Logging in..."):
                            time.sleep(1)  # Simulating login process
                            hashed_password = hash_password(login_password)
                            c.execute("SELECT id, username FROM users WHERE email=? AND password=?", (login_email, hashed_password))
                            user = c.fetchone()
                            if user:
                                user_id, username = user
                                st.session_state.logged_in = True
                                st.session_state.user_id = user_id
                                st.session_state.username = username
                                st.success(f"Welcome, {username}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")
                    else:
                        st.warning("Please fill all the fields.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<h3 class="card-title">Create an Account</h3>', unsafe_allow_html=True)
            with st.form("signup_form"):
                signup_username = st.text_input("Username")
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input("Password", type="password", key="signup_password")
                
                # Move signup button to corner
                st.markdown('<div class="corner-button">', unsafe_allow_html=True)
                signup_button = st.form_submit_button("Sign Up")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if signup_button:
                    if signup_username and signup_email and signup_password:
                        with st.spinner("Creating your account..."):
                            time.sleep(1)  # Simulating account creation process
                            c.execute("SELECT * FROM users WHERE email=?", (signup_email,))
                            if c.fetchone() is not None:
                                st.error("Email already exists. Please use a different email.")
                            else:
                                hashed_password = hash_password(signup_password)
                                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                                        (signup_username, signup_email, hashed_password))
                                conn.commit()
                                st.success("Account created successfully! Please log in.")
                    else:
                        st.warning("Please fill all the fields.")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # App header
    st.markdown('<h1 class="main-header">LexAssist</h1>', unsafe_allow_html=True)
    
    # User profile and logout in header area
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown(
            f"""
            <div class="user-profile">
                <div class="user-avatar">{st.session_state.username[0].upper()}</div>
                <div class="user-name">{st.session_state.username}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Logout", key="logout_button", help="Log out of your account", type="secondary", use_container_width=True):
            logout()
    
    # Horizontal navigation tabs
    st.markdown('<div class="main-nav">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Homepage", key="nav_homepage", 
                    use_container_width=True, 
                    type="secondary" if st.session_state.active_tab != "Homepage" else "primary"):
            st.session_state.active_tab = "Homepage"
            st.rerun()
    
    with col2:
        if st.button("Legal Advice", key="nav_legal", 
                    use_container_width=True,
                    type="secondary" if st.session_state.active_tab != "Legal Advice" else "primary"):
            st.session_state.active_tab = "Legal Advice"
            st.rerun()
    
    with col3:
        if st.button("Document Assistant", key="nav_doc", 
                    use_container_width=True,
                    type="secondary" if st.session_state.active_tab != "Document Assistant" else "primary"):
            st.session_state.active_tab = "Document Assistant"
            st.rerun()
    
    with col4:
        if st.button("Metadata Extraction", key="nav_meta", 
                    use_container_width=True,
                    type="secondary" if st.session_state.active_tab != "Metadata Extraction" else "primary"):
            st.session_state.active_tab = "Metadata Extraction"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display content based on active tab
    if st.session_state.active_tab == "Homepage":
        st.markdown("## Welcome to LexAssist")
        st.markdown("### AI-Driven Legal Assistance and Judicial Support System")
        
        # Feature cards in a grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                """
                <div class="card">
                    <div class="card-icon">💬</div>
                    <h3 class="card-title">Legal Advice</h3>
                    <p class="card-text">Get AI-powered legal Q&A support in multiple languages. Our system is trained on Indian judiciary, the Indian Penal Code, and the Constitution.</p>
                    <br>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                """
                <div class="card">
                    <div class="card-icon">📄</div>
                    <h3 class="card-title">Document Assistant</h3>
                    <p class="card-text">Generate legal documents with ease using AI assistance. Create contracts, affidavits, agreements, and more with just a few clicks.</p>
                    <br>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                """
                <div class="card">
                    <div class="card-icon">📊</div>
                    <h3 class="card-title">Metadata Extraction</h3>
                    <p class="card-text">Extract key information from legal documents automatically. Our AI can identify document type, parties involved, case numbers, and legal provisions.</p>
                    <br>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
       
    elif st.session_state.active_tab == "Legal Advice":
        st.markdown("## Legal Advice Chatbot")
        st.markdown("Get expert legal advice based on Indian law")
        
        
        # Language selection with better UI
        col1, col2 = st.columns([1, 3])
        with col1:
            language = st.selectbox("Language", ["English", "Hindi", "Bengali", "Tamil", "Kannada"])
        
        # Query input with placeholder
        user_input = st.text_area("Enter your legal query:", 
                                height=150, 
                                placeholder="Example: What are my rights if I'm arrested? What is the process for filing a consumer complaint?")
        
        # Submit button with better styling
        if st.button("Get Legal Advice", key="legal_advice_button"):
            if user_input:
                with st.spinner("Analyzing your query..."):
                    # Progress bar for better UX
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    chain = prompt_legal_advice | chat
                    response = chain.invoke({"text": f"Respond in {language}: {user_input}"})
                    
                    # Display response in a nicely formatted box
                    st.markdown("### Legal Opinion")
                    st.info(response.content)
                    
                    # Save to history
                    c.execute("INSERT INTO user_profiles (user_id, query, response) VALUES (?, ?, ?)",
                            (st.session_state.user_id, user_input, response.content))
                    conn.commit()
            else:
                st.warning("Please enter a legal query.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display history of queries
        # Add a clear history button next to the heading
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## Your Previous Queries")
        with col2:
            if st.button("Clear History", key="clear_history_button", type="secondary"):
                if clear_user_history(st.session_state.user_id):
                    st.success("History cleared successfully!")
                    time.sleep(1)
                    st.rerun()
        c.execute("SELECT query, response FROM user_profiles WHERE user_id=? ORDER BY id DESC LIMIT 5", 
                (st.session_state.user_id,))
        history = c.fetchall()
        
        if history:
            for i, (query, response) in enumerate(history):
                with st.expander(f"Query {i+1}: {query[:50]}..."):
                    st.markdown("**Your Query:**")
                    st.write(query)
                    st.markdown("**Response:**")
                    st.write(response)
        else:
            st.info("You haven't made any queries yet.")
    
    elif st.session_state.active_tab == "Document Assistant":
        st.markdown("## Document Generator")
        st.markdown("Create legal documents with AI assistance")
        
        
        # Form for document generation
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="John Doe")
            date = st.date_input("Document Date")
        
        with col2:
            doc_type = st.selectbox("Document Type", [
                "Contract", 
                "Affidavit", 
                "Rental Agreement", 
                "Will", 
                "Power of Attorney",
                "Non-Disclosure Agreement",
                "Employment Contract"
            ])
        
        # Document content with better UI
        st.markdown("### Document Details")
        content = st.text_area(
            "Enter document requirements and details:",
            height=150,
            placeholder="Example: A rental agreement for a 2BHK apartment in Mumbai, monthly rent of ₹25,000, security deposit of ₹50,000, lease term of 11 months..."
        )
        
        # Generate button
        if st.button("Generate Document", key="generate_doc_button"):
            if name and content:
                with st.spinner("Generating your document..."):
                    # Progress bar for better UX
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    prompt = f"Generate a {doc_type} for {name} dated {date} with the following content: {content}"
                    chain = prompt_doc_gen | llm
                    response = chain.invoke({"text": prompt})
                    
                    st.success("Document generated successfully!")
                    
                    # Display document in a formatted box
                    st.markdown("### Generated Document")
                    st.text_area("Preview", response.content, height=300)
                    
                    # Download button
                    b64 = base64.b64encode(response.content.encode()).decode()
                    download_filename = f"{doc_type.lower().replace(' ', '_')}_{name.lower().replace(' ', '_')}.txt"
                    href = f'<a href="data:file/txt;base64,{b64}" download="{download_filename}" class="stButton"><button style="width:100%;">Download {doc_type}</button></a>'
                    st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("Please fill in all required fields.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Document templates section
        st.markdown("## Document Templates")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                """
                <div class="card">
                    <h3 class="card-title">Rental Agreement</h3>
                    <p class="card-text">Standard 11-month rental agreement template with customizable terms for residential properties.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """
                <div class="card">
                    <h3 class="card-title">Employment Contract</h3>
                    <p class="card-text">Comprehensive employment agreement with terms for salary, benefits, and termination clauses.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                """
                <div class="card">
                    <h3 class="card-title">Non-Disclosure Agreement</h3>
                    <p class="card-text">Protect your confidential information with this customizable NDA template.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    elif st.session_state.active_tab == "Metadata Extraction":
        st.markdown("## Document Analysis")
        st.markdown("Extract key information from legal documents")
        
        
        # File uploader with better UI
        uploaded_file = st.file_uploader(
            "Upload a legal document",
            type=["txt", "pdf", "docx"],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file is not None:
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("✅ File successfully uploaded!")
            with col2:
                st.info(f"📄 File name: {uploaded_file.name}")
            with col3:
                st.info(f"📊 File size: {round(uploaded_file.size/1024, 2)} KB")
            
            # Extract text from file
            file_contents = ""
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            with st.spinner("Reading document..."):
                if file_extension == "txt":
                    file_contents = uploaded_file.getvalue().decode("utf-8")
                elif file_extension == "pdf":
                    file_contents = extract_text_from_pdf(uploaded_file)
                elif file_extension == "docx":
                    doc = docx.Document(uploaded_file)
                    for para in doc.paragraphs:
                        file_contents += para.text + "\n"
            
            # Show file contents in expander
            with st.expander("View Document Contents"):
                st.text_area("Content Preview", file_contents[:5000] + ("..." if len(file_contents) > 5000 else ""), height=200)
            
            # Analyze button
            if st.button("Analyze Document", key="analyze_doc_button"):
                with st.spinner("Analyzing document..."):
                    # Progress bar for better UX
                    progress_bar = st.progress(0)
                    
                    # Splitting large documents into chunks
                    chunks = split_into_chunks(file_contents, chunk_size=2000)
                    full_response = ""
                    
                    for i, chunk in enumerate(chunks):
                        progress = int((i + 1) / len(chunks) * 100)
                        progress_bar.progress(progress)
                        
                        chain = prompt_classification | llm
                        response = chain.invoke({"text": chunk})
                        full_response += response.content
                        
                        # Rate limiting
                        if i < len(chunks) - 1:
                            time.sleep(2)
                    
                    # Display results in tabs
                    st.markdown("### Document Analysis Results")
                    result_tab1, result_tab2 = st.tabs(["Extracted Data", "Document Summary"])
                    
                    with result_tab1:
                        st.info(full_response)
                    
                    with result_tab2:
                        # Generate a summary
                        summary_prompt = f"Summarize this legal document in 3-5 bullet points: {file_contents[:4000]}"
                        summary_chain = prompt_metadata | llm
                        summary_response = summary_chain.invoke({"text": summary_prompt})
                        st.write(summary_response.content)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tips section
        st.markdown("## Tips for Document Analysis")
        st.markdown(
            """
            <div class="card">
                <h3 class="card-title">Get Better Results</h3>
                <ul>
                    <li>Upload clear, scanned documents for better text extraction</li>
                    <                    <li>For complex legal documents, consider splitting them into smaller sections</li>
                    <li>The system works best with standard legal formats like contracts, judgments, and petitions</li>
                    <li>Documents in English will yield the most accurate results</li>
                </ul>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Close database connection
conn.close()