# AI-Powered-Learning-Diagnostic-Agent
An interactive AI agent designed to assess a learner’s weaknesses in any chosen topic and skill level by generating targeted diagnostic questions, analyzing responses, and providing personalized learning resources.

---

# 🧠 AI-Powered-Learning-Diagnostic-Agent

> *An AI agent to diagnose learning weaknesses and suggest resources, supporting SDG 4: Quality Education*

---
## 💡How it Works

* Identifies key subtopics under any subject
* Asks diagnostic questions to test understanding
* Analyzes user responses to detect learning gaps
* Recommends personalized learning resources

🧭 The tool is designed to empower personalized learning and **fulfill SDG Goal 4: Quality Education for All**.

---

## 💡 Features

* ✅ Auto-generated topic-wise subtopics
* ✅ Diagnostic questions for deep analysis
* ✅ Real-time interactive answering interface
* ✅ Feedback with weakness analysis
* ✅ Learning resource recommendations (videos, sites)
* ✅ Designed for **students**, **teachers**, and **coaching centers**

---

## 🔧 Tech Stack

* Python 3.8+
* OpenRouter AI API (LLaMA 3.3 70B Instruct)
* Google Colab / Jupyter Notebook
* `ipywidgets`, `requests`, `openai`

---

## 🚀 How to Use

### 1. 📦 Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Powered-Learning-Diagnostic-Agent.git
cd AI-Powered-Learning-Diagnostic-Agent
```

---

### 2. 🧩 Install Dependencies

Ensure you have Python installed (recommended: v3.8+), then install required packages:

```bash
pip install ipywidgets requests openai
```

---

### 3. 🔑 API Key Setup

> ✅ **Note**: A demo OpenRouter API key is already included in the code.
> ⚠️ **However, this key may be removed or limited in the future.**
> For reliable access, we recommend getting your own key:

#### ✅ Steps to get your OpenRouter API Key:

1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Create a free account or log in
3. Click on your profile (top right corner)
4. Go to the **"API Keys"** section
5. Click **"Create API Key"**
6. Copy the key and paste it into the `OPENROUTER_API_KEY` variable inside the code

---

### 4. 💻 Run the Notebook

#### Option 1: Local Jupyter Notebook

```bash
jupyter notebook ai_agent.ipynb
```

#### Option 2: Google Colab

> ⚠️ **Important Note:**
> Google Colab **free version may crash or cut off** responses due to **CPU limitations**.
> To run this project smoothly on Colab:

* Upgrade to **Google Colab Pro**
* OR run locally via Jupyter

---

## 🧪 How It Works

1. **Input:** User enters a topic (e.g., "Photosynthesis") and selects level (Foundation/Intermediate/Advanced)
2. **AI Tasks:**

   * Breaks the topic into subtopics
   * Generates multiple questions for each subtopic
3. **User:** Answers all questions interactively
4. **AI Analysis:** Evaluates answers, identifies weaknesses, and suggests videos/resources for improvement

---

## 🛠️ Known Issues & Recommendations

| Issue                                  | Recommendation                                                |
| -------------------------------------- | ------------------------------------------------------------- |
| ❌ Long responses cut off in Colab free | Use **Colab Pro** or **Jupyter locally**                      |
| ❌ Provided API key may expire          | Get your own free key via [OpenRouter](https://openrouter.ai) |
| ➕ Basic UI with `ipywidgets` only      | Future update: Use Streamlit or Flask for web app             |
| ➕ No scoring/leaderboard               | Add scoring to improve gamification                           |

---

## 🧭 Future Enhancements

* [ ] Add performance score & difficulty adaptation
* [ ] Export feedback to PDF
* [ ] Save session history
* [ ] Admin dashboard for teachers
* [ ] Multi-language support

---

## 💬 Target Audience

* 🎓 Students preparing for exams
* 🧑‍🏫 Teachers who want to run diagnostics
* 🏫 Coaching centers / Institutions for batch assessments

---

## 📘 License

This project is licensed under the **MIT License**.
You are free to use, distribute, and modify it.

---

## 🤝 Contributing

Pull requests and suggestions are welcome.
Feel free to fork the repository and propose changes!
