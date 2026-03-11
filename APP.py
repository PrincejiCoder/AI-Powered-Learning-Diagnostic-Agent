import streamlit as st
import requests
import re
import json
import os

# ===================== CONFIG =====================
OPENROUTER_API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3-70b-instruct"
USER_DB_FILE = "users.json"

# ===================== AUTHENTICATION & STORAGE =====================
def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password, profile):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": password,
        "profile": profile
    }
    save_users(users)
    return True

def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        profile = users[username]["profile"]
        profile["username"] = username
        return profile
    return None

# ===================== LLM ENGINE =====================
SYSTEM_TEMPLATE = """
You are an Adaptive Curriculum-Aware Tutor.

You MUST strictly respect the learner profile provided.
Do NOT assume knowledge beyond the learner’s level.
Do NOT introduce advanced terminology unless it is explicitly expected.

--------------------------------
LEARNER PROFILE (AUTHORITATIVE)
--------------------------------
Education Level: {education_level}
Stream / Discipline: {stream}
Curriculum / Board: {curriculum}
Learning Goal: {goal}
Prior Knowledge Level: {prior_level}
Language Level: {language_level}
Preferred Learning Style: {learning_style}
Exam Target (if any): {exam_target}
Topics to Avoid (if any): {avoid_topics}

--------------------------------
GLOBAL RULES (NON-NEGOTIABLE)
--------------------------------
1. Only include concepts that are:
   - Explicitly taught at this education level
   - Relevant to the given stream and curriculum
2. If a concept is:
   - Too advanced -> EXCLUDE it
   - Borderline -> SIMPLIFY it
   - Not in syllabus -> OMIT it completely
3. Vocabulary rules:
   - Use SIMPLE words if language_level = simple
   - Avoid technical jargon unless required by syllabus
   - Never use unexplained terminology
4. Depth rules:
   - Beginner -> intuition, examples, no equations
   - Intermediate -> definitions + basic reasoning
   - Advanced -> formal explanations allowed
5. NEVER:
   - Introduce university-level or research terms for school learners
   - Add "extra knowledge" just to sound smart
   - Mention concepts not typically examined at this level

--------------------------------
TASK TYPE: {task_type}
--------------------------------
TASK INSTRUCTIONS
Topic: "{topic}"

{specific_instructions}

--------------------------------
OUTPUT FORMAT (STRICT)
--------------------------------
{output_format}

If you are unsure whether a concept belongs to this level,
ERR ON THE SIDE OF EXCLUSION.
"""

def call_llm(user_profile, task_type, topic, specific_instructions, output_format, temperature=0.4):
    # Construct the full prompt using the profile and task
    prompt = SYSTEM_TEMPLATE.format(
        education_level=user_profile.get("education_level", "General"),
        stream=user_profile.get("stream", "General"),
        curriculum=user_profile.get("curriculum", "General"),
        goal=user_profile.get("goal", "Learn"),
        prior_level=user_profile.get("prior_level", "Beginner"),
        language_level=user_profile.get("language_level", "Simple"),
        learning_style=user_profile.get("learning_style", "Text"),
        exam_target=user_profile.get("exam_target", "None"),
        avoid_topics=user_profile.get("avoid_topics", "None"),
        task_type=task_type,
        topic=topic,
        specific_instructions=specific_instructions,
        output_format=output_format
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Adaptive Tutor"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 1500
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# ===================== APP LOGIC =====================
def generate_subtopics(topic, profile):
    instructions = f"""You are Antigravity — an adaptive learning engine.

A learner profile is already known and must be strictly respected.
Do NOT restate or reference the profile.
Do NOT introduce concepts beyond the learner’s expected scope.

--------------------------------
TASK: ESSENTIAL SUBTOPIC SELECTION
--------------------------------

Topic: "{topic}"

Your goal is to SELECT (not list) the smallest possible set of
ESSENTIAL subtopics required for the learner to understand this topic.

PROCESS (INTERNAL, DO NOT OUTPUT):
1. Consider all possible concepts related to the topic.
2. Score each concept based on:
   - Relevance to learner
   - Syllabus appropriateness
   - Conceptual importance
   - Dependency value
3. Remove:
   - Redundant concepts
   - Advanced or unnecessary concepts
4. Select ONLY the top-performing concepts.

HARD CONSTRAINTS:
- Maximum 5 subtopics.
- Fewer is better if sufficient.
- No overlapping or repeated ideas.
- Each subtopic must represent a distinct core concept.
- Subtopics must collectively be sufficient for topic mastery.

ORDERING:
- Arrange subtopics from foundational to advanced understanding.

OUTPUT FORMAT (STRICT):
Numbered list of subtopic titles only.
No explanations.
No metadata.
No commentary.

If a concept is optional or borderline, EXCLUDE it.
"""
    # Prompt asks for Numbered list only.
    raw = call_llm(profile, "Generate subtopics", topic, instructions, "Numbered list of subtopic titles.")
    
    subtopics = []
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    
    for i, line in enumerate(lines):
        # Clean numbering like "1. ", "1) ", "- "
        clean_name = re.sub(r'^[\d\-\.\)]+\s*', '', line)
        if not clean_name: continue
        
        # We infer metadata since the strict prompt doesn't provide it
        # Order implies dependency (Foundational -> Advanced)
        subtopics.append({
            "name": clean_name,
            "dependency": i, 
            "importance": 1.0, # All selected are essential
            "difficulty": "Core",
            "score": {},
            "status": "pending"
        })
            
    return subtopics

def generate_questions(subtopic, profile):
    instructions = """Generate exactly 3 diagnostic questions to test the learner's understanding of this subtopic.
    
    REQUIREMENTS:
    1. Question 1: Concept check (Fundamentals)
    2. Question 2: Misconception trap (Tricky)
    3. Question 3: Application (Scenario-based)
    
    STRICT FORMAT:
    - Output ONLY the questions.
    - Number them 1., 2., 3.
    - Do NOT include answers.
    - Do NOT include blank numbered lines.
    - Do NOT output more than 3 questions.
    """
    fmt = "Numbered list of 3 questions."
    
    raw = call_llm(profile, "Generate diagnostic questions", subtopic, instructions, fmt)
    
    questions = []
    # robust regex parsing
    for line in raw.splitlines():
        line = line.strip()
        if not line: continue
        
        # Match "1. Text" or "1) Text"
        match = re.match(r'^\d+[\.\)]\s*(.+)', line)
        if match:
            q_text = match.group(1).strip()
            # Filter out empty questions or placeholders
            if len(q_text) > 5 and "question" not in q_text.lower(): 
                questions.append(q_text)
            elif len(q_text) > 5: # Allow text with "question" if it looks like real content
                 questions.append(q_text)
                 
    return questions[:3] # Ensure we never return more than 3

def analyze_answer(question, answer, profile):
    instructions = f"""Evaluate the user's answer.
Question: {question}
User Answer: "{answer}"

SCORING RULES (STRICT):
1. Zero Tolerance for Nonsense: Random letters, nonsense, or "I don't know" answers must receive a 0/5.
2. Vague Answers Penalized: Extremely short or vague answers (like "it works") will get very low scores (0 or 1).
3. High Standards: Scores of 4 or 5 are reserved only for clear, reasoned demonstrations of knowledge.

Output exactly:
Concept: <0-5>
Recall: <0-5>
Application: <0-5>
"""
    
    fmt = "Concept: <0-5>\nRecall: <0-5>\nApplication: <0-5>"
    
    raw = call_llm(profile, "Evaluate an answer", "N/A", instructions, fmt)
    
    scores = {"concept": 0, "recall": 0, "application": 0}
    for line in raw.splitlines():
        match = re.search(r"(concept|recall|application)\s*:\s*(\d)", line.lower())
        if match:
            scores[match.group(1)] = int(match.group(2))
            
    return scores

# ===================== UI =====================
st.set_page_config(page_title="Adaptive Context Tutor", page_icon="🎓")

if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

# --- LOGIN / SIGNUP VIEW ---
if not st.session_state.user_profile:
    st.title("🎓 Adaptive Tutor")

    # Initialize auth state
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "login_msg" not in st.session_state:
        st.session_state.login_msg = None

    # --- LOGIN MODE ---
    if st.session_state.auth_mode == "login":
        st.subheader("Login")
        
        # Display success message from signup if any
        if st.session_state.login_msg:
            st.success(st.session_state.login_msg)
            st.session_state.login_msg = None
            
        l_user = st.text_input("Username", key="l_user")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        
        col_login, col_switch = st.columns([1, 2])
        with col_login:
            if st.button("Login", type="primary"):
                profile = authenticate_user(l_user, l_pass)
                if profile:
                    st.session_state.user_profile = profile
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Create New Account"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    # --- SIGNUP MODE ---
    elif st.session_state.auth_mode == "signup":
        st.subheader("Create your Learner Profile")
        
        if st.button("← Back to Login"):
            st.session_state.auth_mode = "login"
            st.rerun()
            
        s_user = st.text_input("Choose Username", key="s_user")
        s_pass = st.text_input("Choose Password", type="password", help="Min 8 chars, 1 uppercase, 1 special char, 1 number", key="s_pass")
        
        col1, col2 = st.columns(2)
        with col1:
            ed_level = st.selectbox("Education Level", ["School (K-12)", "Undergraduate", "Professional"])
            
            # Dynamic fields based on Education Level
            if ed_level == "School (K-12)":
                grade = st.selectbox("Grade", ["7th Grade", "8th Grade", "9th Grade", "10th Grade", "11th Grade", "12th Grade"])
                real_ed_level = grade
                curriculum = st.selectbox("Board", ["CBSE", "ICSE", "State Board", "IB"])
                stream = st.selectbox("Stream", ["Science", "Commerce", "Arts", "General"])
            
            elif ed_level == "Undergraduate":
                real_ed_level = "Undergraduate"
                curriculum = "University Standard" # Default for undergrads
                stream = st.text_input("Major / Degree", placeholder="e.g. Computer Science")
                
            else: # Professional
                real_ed_level = "Professional"
                curriculum = "Industry Standards"
                stream = st.text_input("Field of Work", placeholder="e.g. Data Science")

            prior = st.selectbox("Prior Knowledge", ["Beginner", "Intermediate", "Advanced"])

        with col2:
            lang = st.selectbox("Language Level", ["Simple", "Academic"])
            goal = st.text_input("Learning Goal", value="Concept Clarity")
            style = st.text_input("Learning Style", value="Examples, Diagrams")
            exam = st.text_input("Exam Target (Optional)")
            
        def validate_password(p):
            if len(p) < 8: return False
            if not re.search(r"[A-Z]", p): return False
            if not re.search(r"[a-z]", p): return False
            if not re.search(r"\d", p): return False
            if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", p): return False
            return True
        
        if st.button("Create Account", type="primary"):
            if not s_user or not s_pass:
                st.error("Please fill in username and password.")
            elif not validate_password(s_pass):
                st.error("Password must be at least 8 chars, have 1 uppercase, 1 lowercase, 1 number, and 1 special char.")
            else:
                profile = {
                    "education_level": real_ed_level,
                    "stream": stream,
                    "curriculum": curriculum,
                    "prior_level": prior,
                    "language_level": lang,
                    "goal": goal,
                    "learning_style": style,
                    "exam_target": exam,
                    "avoid_topics": ""
                }
                if register_user(s_user, s_pass, profile):
                    st.session_state.login_msg = "Account created successfully! Please log in."
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("Username already exists.")

# --- MAIN APP VIEW ---
else:
    # Cleaner Top Navbar
    with st.container():
        col_header, col_actions = st.columns([5, 2])
        
        user_name = st.session_state.user_profile.get("username", "Learner")
        
        with col_header:
            st.subheader(f"👋 Hi, {user_name}")
            
        with col_actions:
            # Nested columns to keep buttons tightly aligned
            b1, b2 = st.columns(2)
            with b1:
                st.button("Contact", key="contact_btn", use_container_width=True)
            with b2:
                if st.button("Logout", key="logout_btn", use_container_width=True):
                    st.session_state.user_profile = None
                    st.rerun()
            
    st.divider()

    # Main Learning Logic
    if "state" not in st.session_state:
        st.session_state.state = "INIT"
    if "data" not in st.session_state:
        st.session_state.data = {} # Stores topic, subtopics, etc.

    st.title("🎓 Adaptive Learning Session")

    if st.session_state.state == "INIT":
        # Removed the "Targeting: ..." info text as requested
        topic = st.text_input("What do you want to learn today?", key="topic_input_main")
        if st.button("Start Learning", type="primary"):
            with st.spinner("Generating curriculum-aligned path..."):
                subs = generate_subtopics(topic, st.session_state.user_profile)
                if subs:
                    st.session_state.data["topic"] = topic
                    st.session_state.data["subtopics"] = subs
                    st.session_state.data["current_idx"] = 0
                    st.session_state.state = "LEARNING"
                    st.rerun()
                else:
                    st.error("Could not generate plan. Try again.")

    elif st.session_state.state == "LEARNING":
        idx = st.session_state.data["current_idx"]
        subs = st.session_state.data["subtopics"]
        
        if idx >= len(subs):
            st.session_state.state = "COMPLETE"
            st.rerun()
            
        current = subs[idx]
        st.header(f"Topic: {current['name']}")
        st.caption(f"Difficulty: {current['difficulty']}")
        
        if "questions" not in st.session_state.data or st.session_state.data.get("q_subtopic") != current["name"]:
             with st.spinner("Creating level-appropriate questions..."):
                qs = generate_questions(current["name"], st.session_state.user_profile)
                st.session_state.data["questions"] = qs
                st.session_state.data["q_subtopic"] = current["name"]
                st.rerun()
        
        with st.form("answers"):
            answers = {}
            for i, q in enumerate(st.session_state.data["questions"]):
                st.write(f"**Q{i+1}: {q}**")
                answers[q] = st.text_area(f"Answer {i+1}", key=f"a_{i}")
            
            if st.form_submit_button("Submit"):
                with st.spinner("Grading against curriculum standards..."):
                    results = []
                    for q, a in answers.items():
                        results.append(analyze_answer(q, a, st.session_state.user_profile))
                    
                    # Store results and move on for now (simple flow)
                    current["score"] = results[0] # Just taking first for demo simplicity or avg
                    
                    st.session_state.data["current_idx"] += 1
                    st.success("Answers recorded!")
                    st.rerun()

    elif st.session_state.state == "COMPLETE":
        st.balloons()
        st.title("🎯 Diagnostic Complete!")
        
        # --- CALCULATE METRICS ---
        subs = st.session_state.data["subtopics"]
        
        total_subtopic_scores = 0
        count = 0
        
        weakest_sub = None
        min_score = 100
        
        # Accumulators for details
        total_concept = 0
        total_recall = 0
        total_app = 0

        for sub in subs:
            if "score" in sub and sub["score"]:
                s = sub["score"]
                c, r, a = s.get("concept", 0), s.get("recall", 0), s.get("application", 0)
                
                sub_avg = (c + r + a) / 3.0
                total_subtopic_scores += sub_avg
                
                total_concept += c
                total_recall += r
                total_app += a
                count += 1
                
                if sub_avg < min_score:
                    min_score = sub_avg
                    weakest_sub = sub["name"]

        # Final Mastery Score
        final_score = total_subtopic_scores / count if count > 0 else 0
        
        # Classification Logic
        if final_score < 2.0:
            mastery_level = "Not Understood 🔴"
            mastery_msg = "You need to restart this topic from scratch."
        elif final_score < 3.0:
            mastery_level = "Weak Understanding 🟠"
            mastery_msg = "You have some gaps. Review the weak areas."
        elif final_score < 4.0:
            mastery_level = "Satisfactory 🟡"
            mastery_msg = "Good job! You grasp the basics."
        else:
            mastery_level = "Strong Mastery 🟢"
            mastery_msg = "Excellent! You have mastered this topic."

        # Average breakdowns
        avg_c = total_concept / count if count > 0 else 0
        avg_r = total_recall / count if count > 0 else 0
        avg_a = total_app / count if count > 0 else 0

        # --- DISPLAY REPORT ---
        st.subheader(f"📊 Overall Mastery: {mastery_level}")
        st.write(f"**Score: {final_score:.1f} / 5.0**")
        st.info(mastery_msg)
        
        st.markdown("---")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🧠 Concept", f"{avg_c:.1f}/5")
        c2.metric("📖 Recall", f"{avg_r:.1f}/5")
        c3.metric("🛠️ Application", f"{avg_a:.1f}/5")

        st.markdown("---")
        
        # Definitions
        with st.expander("ℹ️ Understanding Your Scores", expanded=True):
            st.markdown("""
            **🧠 Concept (Understanding):** Do you "get" the main idea? This checks if you grasp the underlying principles and "why" things work, rather than just memorizing facts.
            
            **📖 Recall (Memory):** Can you remember the facts? This checks your ability to retrieve specific terms, definitions, formulas, or names from memory.
            
            **🛠️ Application (Problem Solving):** Can you use what you know? This checks if you can take your knowledge and apply it to solve a new problem or a scenario you haven't seen before.
            """)

        st.markdown("---")

        if weakest_sub:
            st.error(f"⚠️ **Weakest Area:** {weakest_sub}")
            st.markdown(f"We recommend revising **{weakest_sub}** before moving to the next level.")

        st.markdown("### Topic Breakdown")
        for sub in subs:
            status = "✅ Mastered" if sub.get("status") == "mastered" else "⚠️ Needs Review"
            with st.expander(f"{sub['name']} - {status}"):
                st.write(sub.get("score", "No score"))

        if st.button("Start New Topic"):
            st.session_state.state = "INIT"
            st.rerun()
