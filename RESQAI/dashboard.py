import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
import streamlit as st
import folium
from streamlit_folium import st_folium
st.set_page_config(
    page_title="RESQ AI Command Center",
    layout="wide"
)
from ai_engine.classifier import classify_disaster
from ai_engine.severity import assess_severity
from ai_engine.priority import calculate_priority

from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def signup_user(email, password, full_name):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"full_name": full_name}
            }
        })
        return response
    except Exception as e:
        st.error(f"Signup failed: {e}")


def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        st.error(f"Login failed: {e}")

# SESSION STATE
defaults = {
    "nav": "🏠 Dashboard",
    "report": "",
    "people": 0,
    "trapped": "No",
    "location": "Chennai",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "analysis": None,
    "chat_messages": [],
    "chat_step": 0,
    "chat_data": {}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

 # USER LOGIN STATE
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:

    st.title("🚨 RESQ AI - Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login"):
            response = login_user(email, password)

            if response and response.user:
               st.session_state.user = response.user
               st.session_state.access_token = response.session.access_token
               st.session_state.refresh_token = response.session.refresh_token

               st.success("Login successful!")
               st.rerun()


    with tab2:
        name = st.text_input("Full Name", key="signup_name")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account"):
            response = signup_user(
                new_email,
                new_password,
                name
            )

            if response and response.user:
                st.success(
                    "Account created! Check your email if confirmation is required."
                )

    st.stop()

# DASHBOARD FUNCTIONS
# GET SAVED INCIDENTS
# GET SAVED INCIDENTS
def get_incidents():
    try:
        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        response = (
            supabase.table("incidents")
            .select("*")
            .eq("user_id", st.session_state.user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        st.error(f"Unable to load incidents: {e}")
        return []
def demo():
    st.session_state.report = "Flood water rising near houses and people trapped"
    st.session_state.people = 25
    st.session_state.trapped = "Yes"
    st.session_state.location = "Chennai"
    st.session_state.nav = "🧠 AI Analysis"
    st.session_state.analysis = None


def reset():
    for key in ["report", "people", "trapped", "location",
                "latitude", "longitude", "analysis"]:
        st.session_state[key] = defaults[key]
    st.session_state.nav = "🏠 Dashboard"


def new_incident():
    st.session_state.report = ""
    st.session_state.people = 0
    st.session_state.trapped = "No"
    st.session_state.location = ""
    st.session_state.analysis = None
    st.session_state.nav = "🧠 AI Analysis"


# CHATBOT FUNCTIONS
def start_chat():
    st.session_state.chat_step = 0
    st.session_state.chat_data = {}
    st.session_state.chat_messages = [{
        "role": "assistant",
        "content": "Hi! 👋 Welcome to RESQ AI. Which disaster are you facing? Type Flood, Fire, Cyclone, Earthquake, Landslide or Tsunami."
    }]


def open_chatbot():
    start_chat()
    st.session_state.nav = "🤖 AI Chatbot"


def open_dashboard():
    st.session_state.nav = "🏠 Dashboard"


def chatbot_response(answer):
    step = st.session_state.chat_step

    if step == 0:
        choices = ["Flood", "Fire", "Cyclone", "Earthquake", "Landslide", "Tsunami"]
        disaster = answer.strip().title()

        if disaster not in choices:
            return "Please type Flood, Fire, Cyclone, Earthquake, Landslide or Tsunami."

        st.session_state.chat_data["disaster"] = disaster
        st.session_state.chat_step = 1
        return "How many people are affected? Enter a number."

    elif step == 1:
        try:
            people = int(answer)
            if people < 0:
                return "Please enter a valid number."
        except ValueError:
            return "Please enter numbers only."

        st.session_state.chat_data["people"] = people
        st.session_state.chat_step = 2
        return "Are any people trapped? Type Yes or No."

    elif step == 2:
        trapped = answer.strip().lower()

        if trapped not in ["yes", "no"]:
            return "Please type Yes or No."

        st.session_state.chat_data["trapped"] = trapped.title()
        st.session_state.chat_step = 3
        return "Enter your location (area, town or district)."

    elif step == 3:
        if not answer.strip():
            return "Please enter your location."

        data = st.session_state.chat_data
        data["location"] = answer.strip()

        disaster = data["disaster"]

        advice = {
            "Flood": "Move to higher ground. Never walk or drive through floodwater. Stay away from fallen electric wires.",
            "Fire": "Evacuate immediately. Use stairs, not lifts. Stay low in smoke. Do not re-enter the building.",
            "Cyclone": "Stay inside a strong building, away from windows. Follow official evacuation instructions.",
            "Earthquake": "Drop, Cover and Hold On. Protect your head and neck. Avoid windows.",
            "Landslide": "Move away from slopes and debris. Do not cross the landslide area.",
            "Tsunami": "Move immediately to higher ground or inland. Stay away from the shore."
        }

        contacts = {
            "Flood": "112 (Emergency), 1070 (State Control), 1077 (District Control)",
            "Fire": "101 (Fire & Rescue), 112 (Emergency)",
            "Cyclone": "112, 1070, 1077",
            "Earthquake": "112, 1077",
            "Landslide": "112, 1070, 1077",
            "Tsunami": "112, 1070, 1077"
        }

        st.session_state.chat_step = 4

        return (
            "✅ **Incident details collected!**\n\n"
            f"**Disaster:** {disaster}\n\n"
            f"**People affected:** {data['people']}\n\n"
            f"**People trapped:** {data['trapped']}\n\n"
            f"**Location:** {data['location']}\n\n"
            f"### 🛡️ Safety Advice\n{advice[disaster]}\n\n"
            f"### 📞 Emergency Contacts\n{contacts[disaster]}\n\n"
            "This chatbot cannot call emergency services or dispatch rescue teams. "
            "Contact authorities directly and follow official instructions."
        )

    return "Chat completed. Click Restart Chat to start again."


# DESIGN
st.markdown("""
<style>
header[data-testid="stHeader"]{background:transparent!important}
[data-testid="stDecoration"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
background:linear-gradient(130deg,#020817,#082f49,#06172c,#020817)!important;color:white!important}
.stApp{
background-image:
radial-gradient(ellipse at 15% 18%,rgba(14,165,233,.28),transparent 38%),
radial-gradient(ellipse at 85% 72%,rgba(37,99,235,.24),transparent 40%),
linear-gradient(125deg,#020817,#082f49,#06172c,#020817)!important;
background-size:220% 220%;
animation:skyShift 18s ease-in-out infinite}
@keyframes skyShift{
0%{background-position:0 50%}
50%{background-position:100% 50%}
100%{background-position:0 50%}}
.stApp:before{
content:"";position:fixed;inset:-20%;pointer-events:none;z-index:0;opacity:.30;
background:radial-gradient(ellipse 260px 90px at 18% 24%,#38bdf8 0,transparent 72%),
radial-gradient(ellipse 320px 110px at 78% 35%,#0ea5e9 0,transparent 72%),
radial-gradient(ellipse 240px 90px at 55% 82%,#2563eb 0,transparent 72%);
filter:blur(32px);
animation:cloudDrift 28s ease-in-out infinite alternate}
@keyframes cloudDrift{
from{transform:translate(-3%,-1%) scale(1)}
to{transform:translate(4%,3%) scale(1.12)}}
.block-container{padding-top:1.8rem!important}
.stApp p,.stApp label,.stApp li{color:#f0f8ff!important}
h1{color:#67d5ff!important;font-size:44px!important;font-weight:900!important;text-shadow:0 0 18px #0284c7}
h2{color:#9bdfff!important}
h3,h4{color:#c6edff!important}
[data-testid="stMetric"]{
background:linear-gradient(135deg,rgba(13,48,76,.98),rgba(15,69,91,.96))!important;
border:1px solid #38bdf8!important;border-radius:18px!important;
padding:20px!important;box-shadow:0 8px 26px #0006}
[data-testid="stMetricLabel"]{color:#d6f2ff!important}
[data-testid="stMetricValue"]{color:white!important;font-size:30px!important;font-weight:800!important}
section[data-testid="stSidebar"]{
background:linear-gradient(180deg,#020817,#0b2945,#082f49)!important;
border-right:1px solid #1677a6}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label{color:white!important}
.stButton>button,.stFormSubmitButton>button{
background:linear-gradient(90deg,#0369a1,#0284c7,#06b6d4)!important;
color:white!important;border:1px solid #38bdf8!important;
border-radius:12px!important;min-height:46px;font-weight:800!important}
.stButton>button:hover{
box-shadow:0 0 18px #0ea5e9;transform:translateY(-2px)}
.stTextInput input,.stTextArea textarea,.stNumberInput input{
background:#10243d!important;color:white!important;border:1px solid #38bdf8!important}
.stSelectbox div[data-baseweb="select"]{background:#10243d!important}
[data-testid="stForm"]{
background:rgba(8,34,58,.92);border:1px solid #1e6b91;
padding:22px;border-radius:18px}
hr{border-color:#25638a!important}
footer{visibility:hidden}
/* Chat input text - BLACK */
[data-testid="stChatInput"] textarea {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #f1f3f6 !important;
}

/* Placeholder text */
[data-testid="stChatInput"] textarea::placeholder {
    color: #666666 !important;
    -webkit-text-fill-color: #666666 !important;
}

/* Remove extra white background at bottom */
[data-testid="stBottom"] {
    background: transparent !important;
}

[data-testid="stBottom"] > div {
    background: transparent !important;
}

/* Chat input box */
[data-testid="stChatInput"] {
    background: #f1f3f6 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)


# SIDEBAR
with st.sidebar:
    st.markdown("# 🚨 RESQ AI")
    st.caption("DISASTER RESPONSE COMMAND CENTER")
    st.markdown("---")

    st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "🧠 AI Analysis",
            "📋 Incident History",
            "🗺️ Live Map",
            "🤖 AI Chatbot",
            "⚙️ About"
        ],
        key="nav"
    )

    st.markdown("---")
    st.success("🟢 SYSTEM ONLINE")
    st.caption("HACKATHON PROTOTYPE • v1.0")


# HEADER
st.title("🚨 RESQ AI")
st.subheader("DISASTER RESPONSE COMMAND CENTER")
st.caption("WEATHER-INSPIRED INTERFACE • AI INCIDENT ANALYSIS • RESCUE COORDINATION")
st.markdown("---")


# DASHBOARD
if st.session_state.nav == "🏠 Dashboard":

    st.header("🌦️ COMMAND CENTER OVERVIEW")

    a, b, c = st.columns(3)
    a.metric("SYSTEM STATUS", "ONLINE", "Operational")
    b.metric("AI ENGINE", "READY", "Available")
    c.metric("MAP MODULE", "READY", "Available")

    st.markdown("---")
    st.subheader("⚡ QUICK ACTIONS")

    x, y, z = st.columns(3)

    with x:
        st.button("🚨 NEW INCIDENT", use_container_width=True, on_click=new_incident)

    with y:
        st.button("🤖 AI CHATBOT", use_container_width=True, on_click=open_chatbot)

    with z:
        st.button("🔄 RESET", use_container_width=True, on_click=reset)

    st.markdown("---")
    st.subheader("🌧️ WEATHER-INSPIRED CONTROL ROOM")
    st.info("Animated blue cloud-glow is a visual effect, not a live weather forecast.")

    left, right = st.columns(2)

    with left:
        st.markdown("### 🧠 AI INCIDENT INTELLIGENCE")
        st.write("• Disaster type classification\n\n• Severity estimation\n\n• Rule-based response priority")

    with right:
        st.markdown("### 🗺️ RESCUE LOCATION MODULE")
        st.write("• Interactive map\n\n• Reported emergency marker\n\n• Manually entered coordinates")

    if st.session_state.analysis:
        q = st.session_state.analysis
        p1, p2, p3 = st.columns(3)
        p1.metric("DISASTER", q["disaster"])
        p2.metric("SEVERITY", q["severity"])
        p3.metric("PRIORITY", q["priority"])


# AI ANALYSIS
elif st.session_state.nav == "🧠 AI Analysis":

    st.header("🧠 AI EMERGENCY ANALYSIS")

    st.markdown("""
    <style>
    textarea::placeholder {
        color: white !important;
        opacity: 1 !important;
    }
     </style>
""", unsafe_allow_html=True)

    with st.form("incident_form"):

        report = st.text_area(
            "DISASTER DESCRIPTION",
            key="report",
            placeholder="Example: Flood water rising and people trapped..."
        )

        c1, c2 = st.columns(2)

        with c1:
            people = st.number_input(
                "PEOPLE AFFECTED", min_value=0, step=1, key="people"
            )

        with c2:
            trapped = st.selectbox(
                "ARE PEOPLE TRAPPED?", ["No", "Yes"], key="trapped"
            )

        location = st.text_input(
            "REPORTED LOCATION", key="location", placeholder="Example: Chennai"
        )

        submitted = st.form_submit_button(
            "🚨 ANALYZE EMERGENCY", use_container_width=True
        )

    if submitted:
        if not report.strip():
            st.error("Please enter the disaster description.")
        else:
            disaster = classify_disaster(report)
            severity_score, severity = assess_severity(
                people, trapped == "Yes", report
            )
            priority_score, priority = calculate_priority(
                people, trapped == "Yes", severity
            )

            st.session_state.analysis = {
                "disaster": disaster,
                "severity_score": severity_score,
                "severity": severity,
                "priority_score": priority_score,
                "priority": priority,
                "people": people,
                "trapped": trapped,
                "location": location,
                "report": report
            }



                      # SAVE INCIDENT IN SUPABASE
            try:
                supabase.auth.set_session(
                    st.session_state.access_token,
                    st.session_state.refresh_token
                )

                supabase.table("incidents").insert({
                    "user_id": st.session_state.user.id,
                    "disaster_type": disaster,
                    "location": location,
                    "affected_people": people,
                    "trapped_people": 1 if trapped == "Yes" else 0,
                    "severity": severity,
                    "description": report
                }).execute()

                st.success("Incident saved successfully!")

            except Exception as e:
                st.error(f"Incident save failed: {e}")

    if st.session_state.analysis:
        q = st.session_state.analysis

        st.markdown("---")
        st.success("ANALYSIS COMPLETED")
        st.subheader("📊 ANALYSIS RESULTS")

        a, b, c = st.columns(3)
        a.metric("DISASTER TYPE", q["disaster"])
        b.metric("SEVERITY SCORE", f'{q["severity_score"]}/100')
        c.metric("PRIORITY SCORE", q["priority_score"])

        st.write("**Severity level:**", q["severity"])
        st.write("**Priority level:**", q["priority"])

        st.markdown("---")
        st.subheader("📋 INCIDENT DETAILS")
        st.write("**Location:**", q["location"] or "Not provided")
        st.write("**People affected:**", q["people"])
        st.write("**People trapped:**", q["trapped"])
        st.write("**Description:**", q["report"])

        st.warning("Prototype estimate only. Authorized responders must verify reports and decide actual response priority.")


# LIVE MAP
elif st.session_state.nav == "🗺️ Live Map":

    st.header("🗺️ EMERGENCY LOCATION MAP")
    st.info("Enter the reported location coordinates. This is not live GPS tracking.")

    a, b = st.columns(2)

    with a:
        location = st.text_input("LOCATION NAME", key="location")
        latitude = st.number_input(
            "LATITUDE", min_value=-90.0, max_value=90.0,
            format="%.6f", key="latitude"
        )

    with b:
        longitude = st.number_input(
            "LONGITUDE", min_value=-180.0, max_value=180.0,
            format="%.6f", key="longitude"
        )

    map_view = folium.Map(
        location=[latitude, longitude],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    folium.Marker(
        [latitude, longitude],
        popup=location or "Reported Emergency Location",
        tooltip="Reported Emergency Location",
        icon=folium.Icon(color="red", icon="warning-sign")
    ).add_to(map_view)

    st_folium(map_view, width=None, height=520, key="resq_map")
    st.caption("Map tiles need internet access. Marker uses the coordinates entered above.")


# INCIDENT HISTORY
elif st.session_state.nav == "📋 Incident History":

    st.header("📋 INCIDENT HISTORY")
    st.caption("Your previously reported incidents")

    incidents = get_incidents()
                                                   
    if incidents:
        st.dataframe(
            incidents,
            use_container_width=True,
            hide_index=True
        )

        st.success(f"Total incidents: {len(incidents)}")

        st.markdown("---")
        st.subheader("🗑️ MANAGE INCIDENT HISTORY")

        selected_ids = st.multiselect(
            "Select incidents to delete",
            options=[item["id"] for item in incidents],
            format_func=lambda x: next(
                f'ID: {item["id"]} | {item["disaster_type"]} | {item["location"]}'
                for item in incidents if item["id"] == x
            )
        )

        if st.button("🗑️ DELETE SELECTED"):
            if selected_ids:
                st.session_state.delete_ids = selected_ids
                st.session_state.delete_mode = "selected"
                st.rerun()
            else:
                st.warning("Please select incidents first.")

        if st.button("🔥 DELETE ALL HISTORY"):
            st.session_state.delete_ids = [item["id"] for item in incidents]
            st.session_state.delete_mode = "all"
            st.rerun()

        if st.session_state.get("delete_mode"):

            st.warning("Are you sure? This action cannot be undone.")
            if st.button("YES, CONFIRM DELETE"):
                try:
                    supabase.auth.set_session(
                        st.session_state.access_token,
                        st.session_state.refresh_token
                    )

                    response = supabase.table("incidents").delete().in_(
                        "id", st.session_state.delete_ids
                    ).eq(
                        "user_id", st.session_state.user.id
                    ).execute()

                    if response.data:
                        st.success(
                            f"{len(response.data)} incident(s) deleted!"
                        )
                    else:
                        st.warning("No matching incidents deleted.")

                    st.session_state.delete_ids = []
                    st.session_state.delete_mode = None
                    st.rerun()

                except Exception as e:
                    st.error(f"Delete failed: {e}")

            if st.button("CANCEL"):
                st.session_state.delete_ids = []
                st.session_state.delete_mode = None
                st.rerun()

            else:
                st.info("No incidents found. Submit a new incident to get started.")

        
# REPORTS
elif st.session_state.nav == "📊 Reports":


    st.header("📊 INCIDENT REPORTS")

    if st.session_state.analysis:
        q = st.session_state.analysis

        a, b, c = st.columns(3)
        a.metric("DISASTER", q["disaster"])
        b.metric("SEVERITY", q["severity"])
        c.metric("PRIORITY", q["priority"])

        st.write("**Location:**", q["location"] or "Not provided")
        st.write("**People affected:**", q["people"])
        st.write("**People trapped:**", q["trapped"])
        st.write("**Description:**", q["report"])

    else:
        st.info("No report yet. Submit an incident in AI Analysis.")


# CHATBOT
elif st.session_state.nav == "🤖 AI Chatbot":

    st.header("🤖 RESQ AI CHATBOT")
    st.info("Guided disaster assistant – collects details and provides basic safety advice.")

    if not st.session_state.chat_messages:
        start_chat()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input("Type your answer...")

    if user_text:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_text
        })

        response = chatbot_response(user_text)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()

    a, b = st.columns(2)

    with a:
        st.button(
            "🔄 RESTART CHAT",
            on_click=start_chat,
            use_container_width=True
        )

    with b:
        st.button(
            "🏠 BACK TO DASHBOARD",
            on_click=open_dashboard,
            use_container_width=True
        )

    st.caption(
        "This chatbot cannot call emergency services or dispatch rescue teams. "
        "For immediate danger in India, call 112."
    )


# ABOUT
elif st.session_state.nav == "⚙️ About":

    st.header("⚙️ ABOUT RESQ AI")
    st.write(
        "A hackathon prototype for disaster classification, severity estimation, "
        "priority calculation, map visualization and guided safety assistance."
    )
    st.write("**Technology:** Python, Streamlit, Folium")
    st.warning("Not a validated emergency dispatch or rescue system.")


st.markdown("---")
st.caption("🚨 RESQ AI • DISASTER RESPONSE COMMAND CENTER • HACKATHON PROTOTYPE")