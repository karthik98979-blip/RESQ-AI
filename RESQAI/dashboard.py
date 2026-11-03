import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
import streamlit as st
import folium
from streamlit_folium import st_folium
from ai_engine.classifier import classify_disaster
from ai_engine.severity import assess_severity
from ai_engine.priority import calculate_priority
from database import fetch_recent_reports, init_db, save_emergency_report

st.set_page_config(page_title="RESQ AI Command Center", page_icon="🚨", layout="wide")
init_db()

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


# DASHBOARD FUNCTIONS
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
            "🗺️ Live Map",
            "📊 Reports",
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

            try:
                report_id = save_emergency_report(
                    disaster_type=disaster,
                    location_text=location,
                    description=report,
                    affected_people=people,
                    people_trapped=trapped == "Yes",
                    severity_score=severity_score,
                    severity=severity,
                    priority_score=priority_score,
                    priority_level=priority,
                )
                st.session_state.analysis["report_id"] = report_id
                st.success(f"Report saved to the local database (ID {report_id}).")
            except Exception as error:
                st.error(f"Analysis completed, but the report could not be saved: {error}")

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


# REPORTS
elif st.session_state.nav == "📊 Reports":

    st.header("📊 INCIDENT REPORTS")
    try:
        reports = fetch_recent_reports()
    except Exception as error:
        reports = []
        st.error(f"Could not load reports from the local database: {error}")

    if reports:
        urgent_count = sum(row["priority_level"] == "Urgent" for row in reports)
        high_count = sum(row["severity"] in ("High", "Critical") for row in reports)
        a, b, c = st.columns(3)
        a.metric("SAVED REPORTS", len(reports))
        b.metric("URGENT PRIORITY", urgent_count)
        c.metric("HIGH / CRITICAL", high_count)

        st.dataframe(
            [
                {
                    "ID": row["report_id"],
                    "Disaster": row["disaster_type"],
                    "Location": row["location_text"],
                    "People Affected": row["affected_people"],
                    "Severity": row["severity"],
                    "Priority": row["priority_level"],
                    "Priority Score": row["priority_score"],
                    "Status": row["status"],
                    "Reported At (UTC)": row["created_at"],
                }
                for row in reports
            ],
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("View report descriptions"):
            for row in reports:
                st.markdown(
                    f"**#{row['report_id']} · {row['disaster_type']} · "
                    f"{row['location_text']}**"
                )
                st.write(row["description"])
                st.caption(
                    f"Affected: {row['affected_people']} · "
                    f"Trapped: {'Yes' if row['people_trapped'] else 'No'} · "
                    f"Severity score: {row['severity_score']} · "
                    f"Reported at: {row['created_at']}"
                )
                st.markdown("---")
    else:
        st.info("No saved reports yet. Submit an incident in AI Analysis.")


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
