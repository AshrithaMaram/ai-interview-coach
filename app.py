import os

import streamlit as st
from openai import OpenAI

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="centered")


# ============================================================
# GROQ CLIENT
# ============================================================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# AI HELPER
# ============================================================


def ask_ai(prompt):

    response = client.responses.create(model=MODEL, input=prompt)

    return response.output_text.strip()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "interview_started": False,
    "subject": "",
    "topics": [],
    "difficulty": "",
    "number_of_questions": 0,
    "current_question": 0,
    "questions": [],
    "answers": [],
    "evaluations": [],
    "chat_history": [],
    "interview_completed": False,
    "final_review": "",
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# TITLE
# ============================================================

st.title("🎯 AI Interview Coach")


# ============================================================
# SETUP SCREEN
# ============================================================

if not st.session_state.interview_started:

    st.write(
        "Practice technical interviews with dynamically "
        "generated AI questions and concise technical feedback."
    )

    st.divider()

    st.subheader("Interview Setup")

    # --------------------------------------------------------
    # SUBJECT
    # --------------------------------------------------------

    subject = st.text_input(
        "Interview Subject", placeholder="Example: Java, SQL, Python"
    )

    # --------------------------------------------------------
    # TOPICS
    # --------------------------------------------------------

    topics_input = st.text_input(
        "Specific Topics", placeholder="Example: OOP, Collections, Exception Handling"
    )

    # --------------------------------------------------------
    # DIFFICULTY
    # --------------------------------------------------------

    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    # --------------------------------------------------------
    # NUMBER OF QUESTIONS
    # --------------------------------------------------------

    number_of_questions = st.number_input(
        "Number of Questions", min_value=1, max_value=20, value=5, step=1
    )

    st.divider()

    # --------------------------------------------------------
    # START INTERVIEW
    # --------------------------------------------------------

    start_interview = st.button("🚀 Start Interview", use_container_width=True)

    if start_interview:

        if not subject.strip():

            st.error("Please enter an interview subject.")

        elif not topics_input.strip():

            st.error("Please enter at least one specific topic.")

        else:

            st.session_state.subject = subject.strip()

            st.session_state.topics = [
                topic.strip() for topic in topics_input.split(",") if topic.strip()
            ]

            st.session_state.difficulty = difficulty

            st.session_state.number_of_questions = int(number_of_questions)

            st.session_state.current_question = 0

            st.session_state.questions = []

            st.session_state.answers = []

            st.session_state.evaluations = []

            st.session_state.chat_history = []

            st.session_state.interview_completed = False

            st.session_state.final_review = ""

            st.session_state.interview_started = True

            st.rerun()


# ============================================================
# INTERVIEW SCREEN
# ============================================================

else:

    st.caption(
        f"{st.session_state.subject} • "
        f"{', '.join(st.session_state.topics)} • "
        f"{st.session_state.difficulty}"
    )

    st.divider()

    # ========================================================
    # GENERATE NEXT QUESTION
    # ========================================================

    if (
        not st.session_state.interview_completed
        and len(st.session_state.questions) == st.session_state.current_question
    ):

        previous_questions = "\n".join(st.session_state.questions)

        question_prompt = f"""
You are a technical interviewer conducting a real interview.

Subject:
{st.session_state.subject}

Specific Topics:
{st.session_state.topics}

Difficulty:
{st.session_state.difficulty}

Generate ONE interview question.

Previously asked questions:
{previous_questions}

Rules:

- The question MUST be related to the given subject.
- The question MUST come from one of the specified topics.
- Focus on one topic at a time.
- Match the requested difficulty.
- Generate a new question different from previous questions.
- Do not repeat the same concept unnecessarily.
- Test technical understanding.
- The question can be conceptual, practical,
  scenario-based, coding, or query-based when appropriate.
- Do not provide the answer.
- Return ONLY the interview question.
"""

        with st.spinner("🤖 AI Interviewer is preparing a question..."):

            question = ask_ai(question_prompt)

        st.session_state.questions.append(question)

        st.session_state.current_question += 1

        st.session_state.chat_history.append({"role": "assistant", "content": question})

        st.rerun()

    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.write(message["content"])

    # ========================================================
    # CANDIDATE ANSWER
    # ========================================================

    if not st.session_state.interview_completed:

        answer = st.chat_input("Type your answer...")

        if answer:

            current_question = st.session_state.questions[-1]

            # ------------------------------------------------
            # SAVE CANDIDATE ANSWER
            # ------------------------------------------------

            st.session_state.chat_history.append({"role": "user", "content": answer})

            # ------------------------------------------------
            # EVALUATION PROMPT
            # ------------------------------------------------

            evaluation_prompt = f"""
You are a concise technical interview coach.

Subject:
{st.session_state.subject}

Topics:
{st.session_state.topics}

Difficulty:
{st.session_state.difficulty}

Question:
{current_question}

Candidate Answer:
{answer}

Evaluate the candidate's answer based on:

1. Technical correctness
2. Completeness
3. Relevance
4. Requested difficulty

Return ONLY this format:

Score: X/10

Correct:
- maximum 2 short points

Missing / Incorrect:
- maximum 2 short points
- If nothing important is missing, write:
  Nothing major.

Technical words to use:
- 3 to 5 important technical terms

Answer depth:
- Explain exactly how deeply this particular question
  should be answered.
- Mention 2 to 4 important points to cover.
- Do not demand advanced/internal details unless
  the question requires them.

Improve:
- 1 or 2 short sentences.

Rules:

- Be concise.
- Be interview-focused.
- Do not give a long sample answer.
- Do not provide code unless the question requires code.
- Do not invent mistakes.
- Do not penalize unnecessary details.
- Match feedback to the question difficulty.
"""

            with st.spinner("🤖 Evaluating your answer..."):

                evaluation = ask_ai(evaluation_prompt)

            # ------------------------------------------------
            # SAVE ANSWER
            # ------------------------------------------------

            st.session_state.answers.append(
                {"question": current_question, "answer": answer}
            )

            # ------------------------------------------------
            # SAVE EVALUATION
            # ------------------------------------------------

            st.session_state.evaluations.append(
                {
                    "question": current_question,
                    "answer": answer,
                    "evaluation": evaluation,
                }
            )

            # ------------------------------------------------
            # DISPLAY EVALUATION
            # ------------------------------------------------

            st.session_state.chat_history.append(
                {"role": "assistant", "content": evaluation}
            )

            # =================================================
            # CHECK WHETHER INTERVIEW IS COMPLETE
            # =================================================

            if len(st.session_state.answers) >= st.session_state.number_of_questions:

                # ------------------------------------------------
                # BUILD INTERVIEW HISTORY
                # ------------------------------------------------

                interview_history = ""

                for index, item in enumerate(st.session_state.evaluations, start=1):

                    interview_history += f"""
Question {index}:
{item["question"]}

Candidate Answer:
{item["answer"]}

Evaluation:
{item["evaluation"]}

----------------------------------------
"""

                # ------------------------------------------------
                # FINAL REVIEW PROMPT
                # ------------------------------------------------

                final_review_prompt = f"""
You are a concise technical interview coach.

Subject:
{st.session_state.subject}

Selected Topics:
{st.session_state.topics}

Difficulty:
{st.session_state.difficulty}

Number of Questions:
{st.session_state.number_of_questions}

Complete Interview:
{interview_history}

Analyze ALL answers together.

Pay special attention to performance across
the selected topics.

Return ONLY:

FINAL REVIEW

Overall Score: X/10

Strong:
- maximum 2 short points

Improve:
- maximum 2 short points

Topics to Revise:
- maximum 4 topics

Technical Terms to Revise:
- maximum 5 terms

Next Focus:
- maximum 2 specific topics or skills

Rules:

- Keep the entire review under 10 lines.
- Base the review on ALL answers.
- Identify repeated strengths or weaknesses.
- Connect weaknesses to the selected topics.
- Do not repeat individual evaluations.
- Do not explain answers again.
- Do not give sample answers.
- Do not give lengthy advice.
- Do not invent weaknesses.
- If a topic was not sufficiently tested,
  do not claim the candidate is weak in it.
"""

                with st.spinner("🏆 Preparing final review..."):

                    final_review = ask_ai(final_review_prompt)

                st.session_state.final_review = final_review

                st.session_state.interview_completed = True

            # ------------------------------------------------
            # REFRESH CHAT
            # ------------------------------------------------

            st.rerun()

    # ========================================================
    # FINAL REVIEW
    # ========================================================

    if st.session_state.interview_completed:

        st.divider()

        st.subheader("🏆 Final Interview Review")

        with st.chat_message("assistant"):

            st.write(st.session_state.final_review)

        st.success("🎉 Interview completed!")
