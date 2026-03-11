# 🎓 Adaptive Context Tutor - Setup Guide

This project is an AI-powered learning diagnostic agent built with **Python**, **Streamlit**, and **OpenRouter AI**.

## 🚀 How to Run the Application

To start the app correctly, follow these steps:

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
Open your terminal and run the following command to install the required libraries:

```bash
pip install streamlit requests
```

### 3. Start the App
Run the application using the Streamlit command (do **not** use `python APP.py` or open the HTML file directly):

```bash
streamlit run APP.py
```

After running this command, the app will automatically open in your default web browser at `http://localhost:8501`.

---

## 🔑 Authentication System

The app includes a built-in user system. Here is what you need to know:

-   **Signup**: You can create a new account by providing a username, password, and your learner profile (Education level, stream, board, etc.).
-   **Login**: Once registered, you can log in with your credentials.
-   **Security**: Passwords must be at least 8 characters long and include an uppercase letter, lowercase letter, number, and special character.
-   **Data Storage**: Your user data and profile are saved locally in `users.json`.

## 🧠 Features
- **Adaptive Learning**: The AI tailors subtopics and questions based on your specific curriculum and knowledge level.
- **Diagnostic Analysis**: After answering questions, the AI analyzes your performance across three metrics: **Concept**, **Recall**, and **Application**.
- **Personalized Feedback**: Identifies your weakest areas and provides clear breakdown of your topic mastery.

---
*Note: Ensure you have an active internet connection as the app communicates with the OpenRouter API for generating educational content.*
