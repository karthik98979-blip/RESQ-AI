import streamlit as st
import folium
from streamlit_folium import st_folium
from ai_engine.classifier import classify_disaster
from ai_engine.severity import assess_severity
from ai_engine.priority import calculate_priority

st.set_page_config(page_title="RESQ AI Command Center", page_icon="🚨", layout="wide")

for k, v in {
    "nav":"🏠 Dashboard", "report":"", "people":0, "trapped":"No",
    "location":"Chennai", "latitude":13.0827, "longitude":80.2707,
    "analysis":None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def demo():
    st.session_state.report = "Flood water rising near houses and people trapped"
    st.session_state.people = 25
    st.session_state.trapped = "Yes"
    st.session_state.location = "Chennai"
    st.session_state.nav = "🧠 AI Analysis"
    st.session_state.analysis = None

def reset():
    for k, v in {"report":"", "people":0, "trapped":"No", "location":"Chennai",
                 "latitude":13.0827, "longitude":80.2707, "analysis":None,
                 "nav":"🏠 Dashboard"}.items():
        st.session_state[k] = v

def new_incident():
    st.session_state.report = ""
    st.session_state.people = 0
    st.session_state.trapped = "No"
    st.session_state.location = ""
    st.session_state.analysis = None
    st.session_state.nav = "🧠 AI Analysis"

st.markdown("""
<style>
header[data-testid="stHeader"]{background:transparent!important}
[data-testid="stDecoration"]{display:none!important}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
 background:linear-gradient(130deg,#020817,#082f49,#06172c,#020817)!important;color:#fff!important}
.stApp{background-image:
 radial-gradient(ellipse at 15% 18%,rgba(14,165,233,.28),transparent 38%),
 radial-gradient(ellipse at 85% 72%,rgba(37,99,235,.24),transparent 40%),
 linear-gradient(125deg,#020817,#082f49,#06172c,#020817)!important;
 background-size:220% 220%;animation:skyShift 18s ease-in-out infinite}
@keyframes skyShift{0%{background-position:0 50%}50%{background-position:100% 50%}100%{background-position:0 50%}}
.stApp:before{content:"";position:fixed;inset:-20%;pointer-events:none;z-index:0;opacity:.30;
 background:radial-gradient(ellipse 260px 90px at 18% 24%,#38bdf8 0,transparent 72%),
 radial-gradient(ellipse 320px 110px at 78% 35%,#0ea5e9 0,transparent 72%),
 radial-gradient(ellipse 240px 90px at 55% 82%,#2563eb 0,transparent 72%);
 filter:blur(32px);animation:cloudDrift 28s ease-in-out infinite alternate}
@keyframes cloudDrift{from{transform:translate(-3%,-1%) scale(1)}to{transform:translate(4%,3%) scale(1.12)}}
.block-container{padding-top:1.8rem!important}
.stApp p,.stApp label,.stApp li,.stApp [data-testid="stMarkdownContainer"]{color:#f0f8ff!important}
h1{color:#67d5ff!important;font-size:44px!important;font-weight:900!important;text-shadow:0 0 18px #0284c7}
h2{color:#9bdfff!important} h3,h4{color:#c6edff!important}
[data-testid="stMetric"]{background:linear-gradient(135deg,rgba(13,48,76,.98),rgba(15,69,91,.96))!important;
 border:1px solid #38bdf8!important;border-radius:18px!important;padding:20px!important;box-shadow:0 8px 26px #0006}
[data-testid="stMetricLabel"]{color:#d6f2ff!important}
[data-testid="stMetricValue"]{color:#fff!important;font-size:30px!important;font-weight:800!important}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#020817,#0b2945,#082f49)!important;border-right:1px solid #1677a6}
section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] span,section[data-testid="stSidebar"] label{color:#fff!important}
.stButton>button,.stFormSubmitButton>button{background:linear-gradient(90deg,#0369a1,#0284c7,#06b6d4)!important;
 color:white!important;border:1px solid #38bdf8!important;border-radius:12px!important;min-height:46px;font-weight:800!important}
.stButton>button:hover,.stFormSubmitButton>button:hover{box-shadow:0 0 18px #0ea5e9;transform:translateY(-2px)}
.stTextInput input,.stTextArea textarea,.stNumberInput input{background:#10243d!important;color:white!important;border:1px solid #38bdf8!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#c5d9e8!important}
.stSelectbox div[data-baseweb="select"]{background:#10243d!important}
[data-testid="stForm"]{background:rgba(8,34,58,.92);border:1px solid #1e6b91;padding:22px;border-radius:18px}
hr{border-color:#25638a!important} footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 🚨 RESQ AI")
    st.caption("DISASTER RESPONSE COMMAND CENTER")
    st.markdown("---")
    st.radio("MAIN MENU",["🏠 Dashboard","🧠 AI Analysis","🗺️ Live Map","📊 Reports","⚙️ About"],key="nav")
    st.markdown("---")
    st.success("🟢 SYSTEM ONLINE")
    st.caption("HACKATHON PROTOTYPE • v1.0")

st.title("🚨 RESQ AI")
st.subheader("DISASTER RESPONSE COMMAND CENTER")
st.caption("WEATHER-INSPIRED INTERFACE • AI INCIDENT ANALYSIS • RESCUE COORDINATION")
st.markdown("---")

if st.session_state.nav == "🏠 Dashboard":
    st.header("🌦️ COMMAND CENTER OVERVIEW")
    a,b,c=st.columns(3)
    a.metric("SYSTEM STATUS","ONLINE","Operational")
    b.metric("AI ENGINE","READY","Available")
    c.metric("MAP MODULE","READY","Available")
    st.markdown("---")
    st.subheader("⚡ QUICK ACTIONS")
    x,y,z=st.columns(3)
    with x: st.button("🚨 NEW INCIDENT",use_container_width=True,on_click=new_incident)
    with y: st.button("🧪 LOAD DEMO",use_container_width=True,on_click=demo)
    with z: st.button("🔄 RESET",use_container_width=True,on_click=reset)
    st.markdown("---")
    st.subheader("🌧️ WEATHER-INSPIRED CONTROL ROOM")
    st.info("Animated blue cloud-glow is a visual effect, not a live weather forecast.")
    l,r=st.columns(2)
    with l:
        st.markdown("### 🧠 AI INCIDENT INTELLIGENCE")
        st.write("• Disaster type classification\n\n• Severity estimation\n\n• Rule-based response priority")
    with r:
        st.markdown("### 🗺️ RESCUE LOCATION MODULE")
        st.write("• Interactive map\n\n• Reported emergency marker\n\n• Manually entered coordinates")
    if st.session_state.analysis:
        q=st.session_state.analysis
        st.markdown("---")
        p1,p2,p3=st.columns(3)
        p1.metric("DISASTER",q["disaster"]);p2.metric("SEVERITY",q["severity"]);p3.metric("PRIORITY",q["priority"])

elif st.session_state.nav == "🧠 AI Analysis":
    st.header("🧠 AI EMERGENCY ANALYSIS")
    with st.form("incident_form"):
        report=st.text_area("DISASTER DESCRIPTION",key="report",placeholder="Example: Flood water rising and people trapped...")
        c1,c2=st.columns(2)
        with c1: people=st.number_input("PEOPLE AFFECTED",min_value=0,step=1,key="people")
        with c2: trapped=st.selectbox("ARE PEOPLE TRAPPED?",["No","Yes"],key="trapped")
        location=st.text_input("REPORTED LOCATION",key="location",placeholder="Example: Chennai")
        submitted=st.form_submit_button("🚨 ANALYZE EMERGENCY",use_container_width=True)
    if submitted:
        if not report.strip(): st.error("Please enter the disaster description.")
        else:
            disaster=classify_disaster(report)
            ss,sl=assess_severity(people,trapped=="Yes",report)
            ps,pl=calculate_priority(people,trapped=="Yes",sl)
            st.session_state.analysis={"disaster":disaster,"severity_score":ss,"severity":sl,
              "priority_score":ps,"priority":pl,"people":people,"trapped":trapped,
              "location":location,"report":report}
    if st.session_state.analysis:
        q=st.session_state.analysis
        st.markdown("---");st.success("ANALYSIS COMPLETED");st.subheader("📊 ANALYSIS RESULTS")
        a,b,c=st.columns(3)
        a.metric("DISASTER TYPE",q["disaster"]);b.metric("SEVERITY SCORE",f'{q["severity_score"]}/100')
        c.metric("PRIORITY SCORE",q["priority_score"])
        st.write("**Severity level:**",q["severity"])
        st.write("**Priority level:**",q["priority"])
        st.markdown("---");st.subheader("📋 INCIDENT DETAILS")
        st.write("**Location:**",q["location"] or "Not provided")
        st.write("**People affected:**",q["people"])
        st.write("**People trapped:**",q["trapped"])
        st.write("**Description:**",q["report"])
        st.warning("Prototype estimate only. Authorized responders must verify reports and decide actual response priority.")

elif st.session_state.nav == "🗺️ Live Map":
    st.header("🗺️ EMERGENCY LOCATION MAP")
    st.info("Enter the reported location coordinates. This is not live GPS tracking.")
    a,b=st.columns(2)
    with a:
        location=st.text_input("LOCATION NAME",key="location")
        latitude=st.number_input("LATITUDE",min_value=-90.0,max_value=90.0,format="%.6f",key="latitude")
    with b:
        longitude=st.number_input("LONGITUDE",min_value=-180.0,max_value=180.0,format="%.6f",key="longitude")
    m=folium.Map(location=[latitude,longitude],zoom_start=12,tiles="OpenStreetMap")
    folium.Marker([latitude,longitude],popup=location or "Reported Emergency Location",
      tooltip="Reported Emergency Location",icon=folium.Icon(color="red",icon="warning-sign")).add_to(m)
    st_folium(m,width=None,height=520,key="resq_map")
    st.caption("Map tiles need internet access. Marker uses the coordinates entered above.")

elif st.session_state.nav == "📊 Reports":
    st.header("📊 INCIDENT REPORTS")
    if st.session_state.analysis:
        q=st.session_state.analysis
        a,b,c=st.columns(3)
        a.metric("DISASTER",q["disaster"]);b.metric("SEVERITY",q["severity"]);c.metric("PRIORITY",q["priority"])
        st.write("**Location:**",q["location"] or "Not provided")
        st.write("**People affected:**",q["people"])
        st.write("**People trapped:**",q["trapped"])
        st.write("**Description:**",q["report"])
    else: st.info("No report yet. Submit an incident in AI Analysis.")

elif st.session_state.nav == "⚙️ About":
    st.header("⚙️ ABOUT RESQ AI")
    st.write("A hackathon prototype for disaster classification, severity estimation, priority calculation and map visualization.")
    st.write("**Technology:** Python, Streamlit, Folium")
    st.warning("Not a validated emergency dispatch or rescue system.")

st.markdown("---")
st.caption("🚨 RESQ AI • DISASTER RESPONSE COMMAND CENTER • HACKATHON PROTOTYPE")
