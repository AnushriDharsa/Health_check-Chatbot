import streamlit as st
import joblib
import numpy as np

model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

# Session state initialize
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = -1
if "data" not in st.session_state:
    st.session_state.data = {}
if "lang" not in st.session_state:
    st.session_state.lang = None
if "result" not in st.session_state:
    st.session_state.result = None
if "done" not in st.session_state:
    st.session_state.done = False

questions_en = [
    ("pregnancies", "1️⃣ How many times have you been pregnant? (Write 0 if male or never)"),
    ("glucose", "2️⃣ What is your Glucose level? (Normal: 70-100)"),
    ("blood_pressure", "3️⃣ What is your Blood Pressure? (Normal: 60-80)"),
    ("skin_thickness", "4️⃣ What is your Skin Thickness? (Write 20 if not known)"),
    ("insulin", "5️⃣ What is your Insulin level? (Write 80 if not known)"),
    ("bmi", "6️⃣ What is your BMI? (Normal: 18.5-24.9)"),
    ("dpf", "7️⃣ Diabetes family history score? (Write 0.5 if not known)"),
    ("age", "8️⃣ What is your Age?"),
]

questions_hi = [
    ("pregnancies", "1️⃣ Kitni baar pregnancy hui? (0 likho agar male ho ya kabhi nahi)"),
    ("glucose", "2️⃣ Glucose level kya hai? (Normal: 70-100)"),
    ("blood_pressure", "3️⃣ Blood Pressure kya hai? (Normal: 60-80)"),
    ("skin_thickness", "4️⃣ Skin Thickness kya hai? (Pata nahi toh 20 likho)"),
    ("insulin", "5️⃣ Insulin level kya hai? (Pata nahi toh 80 likho)"),
    ("bmi", "6️⃣ BMI kya hai? (Normal: 18.5-24.9)"),
    ("dpf", "7️⃣ Family mein diabetes hai? (Pata nahi toh 0.5 likho)"),
    ("age", "8️⃣ Tumhari age kya hai?"),
]

def get_questions():
    return questions_en if st.session_state.lang == "English" else questions_hi

def get_response(user_input):
    step = st.session_state.step
    data = st.session_state.data
    questions = get_questions()
    lang = st.session_state.lang

    # Done state — general chat
    if st.session_state.done:
        u = user_input.lower()
        if any(x in u for x in ["start", "shuru", "check", "again", "dobara"]):
            st.session_state.step = 0
            st.session_state.data = {}
            st.session_state.done = False
            st.session_state.result = None
            return questions[0][1]
        elif any(x in u for x in ["thank", "shukriya", "thanks"]):
            return "You're welcome! Take care! 😊" if lang == "English" else "Bahut shukriya! Apna khayal rakhna! 😊"
        elif any(x in u for x in ["doctor", "hospital", "help"]):
            return "Please consult a doctor nearby. Regular checkups are important! 🏥" if lang == "English" else "Najdeeki doctor se milna. Regular checkup bahut zaroori hai! 🏥"
        elif any(x in u for x in ["diet", "food", "khana", "exercise"]):
            return "Eat healthy — less sugar, more vegetables. Exercise 30 mins daily! 🥗" if lang == "English" else "Healthy khana khao — kam cheeni, zyada sabzi. Roz 30 min exercise karo! 🥗"
        else:
            return "Type 'start' to check again, or ask about diet/doctor/exercise! 😊" if lang == "English" else "'start' likho dobara check karne ke liye, ya diet/doctor ke baare mein pucho! 😊"

    # Step -1 — waiting for start
    if step == -1:
        u = user_input.lower()
        if any(x in u for x in ["start", "shuru", "haan", "yes", "check"]):
            st.session_state.step = 0
            return questions[0][1]
        else:
            return "Type 'start' to begin! 🩺" if lang == "English" else "'start' likho shuru karne ke liye! 🩺"

    # Questions flow
    elif step < len(questions):
        key = questions[step][0]
        try:
            data[key] = float(user_input)
            st.session_state.data = data
        except:
            return "Please enter numbers only! 😊" if lang == "English" else "Sirf number likho! 😊"

        st.session_state.step += 1

        if st.session_state.step < len(questions):
            return questions[st.session_state.step][1]
        else:
            # Predict
            input_data = np.array([[
                data["pregnancies"], data["glucose"], data["blood_pressure"],
                data["skin_thickness"], data["insulin"], data["bmi"],
                data["dpf"], data["age"]
            ]])
            input_scaled = scaler.transform(input_data)
            result = model.predict(input_scaled)
            st.session_state.result = int(result[0])
            st.session_state.done = True

            if result[0] == 1:
                return ("⚠️ Results show possibility of Diabetes.\n\n"
                        "👨‍⚕️ Please consult a doctor immediately.\n"
                        "🥗 Reduce sugar intake.\n"
                        "🏃 Exercise daily.\n"
                        "💊 Get HbA1c test done.\n\n"
                        "Type 'start' to check again!") if lang == "English" else \
                       ("⚠️ Results ke anusar diabetes ki sambhavna hai.\n\n"
                        "👨‍⚕️ Doctor se turant milein.\n"
                        "🥗 Cheeni kam karein.\n"
                        "🏃 Roz exercise karein.\n"
                        "💊 HbA1c test karwayein.\n\n"
                        "'start' likho dobara check karne ke liye!")
            else:
                return ("✅ No Diabetes detected! Great news!\n\n"
                        "💪 Keep maintaining healthy lifestyle:\n"
                        "🥗 Eat balanced diet.\n"
                        "🏃 Exercise regularly.\n"
                        "💧 Drink plenty of water.\n\n"
                        "Type 'start' to check again!") if lang == "English" else \
                       ("✅ Diabetes nahi hai! Bahut achhi baat!\n\n"
                        "💪 Healthy lifestyle banaye rakhein:\n"
                        "🥗 Balanced diet khayein.\n"
                        "🏃 Roz exercise karein.\n"
                        "💧 Paani zyada piyein.\n\n"
                        "'start' likho dobara check karne ke liye!")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🩺 Diabetes Assistant")
    st.markdown("---")
    
    if st.session_state.lang:
        st.markdown("### 📊 Progress")
        if not st.session_state.done:
            total = len(get_questions())
            current = max(st.session_state.step, 0)
            st.progress(current / total)
            st.write(f"Question {current} of {total}")
        else:
            st.progress(1.0)
            st.write("✅ Check Complete!")
            
            if st.session_state.result == 1:
                st.error("⚠️ Diabetes Risk Detected")
            else:
                st.success("✅ No Diabetes Detected")

        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.info("🥗 Eat healthy food")
        st.info("🏃 Exercise 30 min daily")
        st.info("💧 Drink 8 glasses water")
        st.info("😴 Sleep 7-8 hours")
        
        st.markdown("---")
        st.markdown("### 🏥 Need Help?")
        st.warning("If you feel unwell, please consult a doctor immediately!")
        
        if st.button("🔄 Start New Check"):
            st.session_state.step = -1
            st.session_state.data = {}
            st.session_state.done = False
            st.session_state.result = None
            st.session_state.messages = []
            st.rerun()

# --- MAIN CHAT ---
st.title("🤖 Diabetes Chatbot")

# Language selection
if st.session_state.lang is None:
    st.markdown("## 👋 Welcome! / Swagat hai!")
    st.write("Please choose your language:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.lang = "English"
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hello! 👋 I am your Diabetes Assistant!\n\nType 'start' to begin your diabetes check! 🩺"
            })
            st.rerun()
    with col2:
        if st.button("🇮🇳 Hindi", use_container_width=True):
            st.session_state.lang = "Hindi"
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Namaskar! 👋 Main aapka Diabetes Assistant hoon!\n\n'start' likho diabetes check shuru karne ke liye! 🩺"
            })
            st.rerun()
else:
    # Show messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # User input
    placeholder = "Type here..." if st.session_state.lang == "English" else "Yahan likho..."
    user_input = st.chat_input(placeholder)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        reply = get_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)