import os
from openai import OpenAI

# ============================================================
# 1. CONNECT TO GROQ
# ============================================================

client = OpenAI(
    base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# 2. GET INTERVIEW SETTINGS
# ============================================================

subject = input("Enter interview subject: ")

topics_input = input("Enter specific topics separated by commas: ")

topics = [topic.strip() for topic in topics_input.split(",") if topic.strip()]

difficulty = input("Enter difficulty (Easy/Medium/Hard): ")

number_of_questions = int(input("How many interview questions do you want? "))


# ============================================================
# 3. STORE INTERVIEW DATA
# ============================================================

previous_questions = []

answers = []

evaluations = []


# ============================================================
# 4. START INTERVIEW
# ============================================================

for question_number in range(1, number_of_questions + 1):

    print("\n" + "=" * 60)

    print(f"QUESTION {question_number} " f"OF {number_of_questions}")

    print("=" * 60)

    # ========================================================
    # 5. GENERATE QUESTION DYNAMICALLY
    # ========================================================

    question_prompt = f"""
You are a technical interviewer conducting a real interview.

Subject:
{subject}

Specific Topics:
{topics}

Difficulty:
{difficulty}

Generate ONE interview question.

Previously asked questions:
{previous_questions}

Rules:

- The question MUST be related to the given subject.
- The question MUST come from one of the specified topics.
- Clearly focus on one topic at a time.
- Match the requested difficulty.
- Generate a new question different from previous questions.
- Do not repeat the same question.
- Do not unnecessarily repeat the same concept.
- Questions should test technical understanding.
- Questions can include conceptual, practical, scenario-based,
  or coding/query questions when appropriate.
- Do not provide the answer.
- Return ONLY the interview question.
"""

    response = client.responses.create(
        model="openai/gpt-oss-20b", input=question_prompt
    )

    question = response.output_text.strip()

    # ========================================================
    # 6. DISPLAY QUESTION
    # ========================================================

    print("\nAI Interviewer:")

    print(question)

    # ========================================================
    # 7. SAVE QUESTION
    # ========================================================

    previous_questions.append(question)

    # ========================================================
    # 8. GET CANDIDATE ANSWER
    # ========================================================

    answer = input("\nYour answer: ")

    answers.append({"question": question, "answer": answer})

    # ========================================================
    # 9. EVALUATE ANSWER
    # ========================================================

    evaluation_prompt = f"""
You are a concise technical interview coach.

Subject:
{subject}

Topics:
{topics}

Difficulty:
{difficulty}

Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate's answer based on:

1. Technical correctness
2. Completeness
3. Relevance to the question
4. Requested difficulty

Return ONLY this format:

Score: X/10

Correct:
- [maximum 2 short points]

Missing / Incorrect:
- [maximum 2 short points]
- If nothing important is missing, write:
  Nothing major.

Technical words to use:
- [3 to 5 important technical terms]

Answer depth:
- Tell the candidate exactly how deeply they should
  explain this particular question.
- Mention 2 to 4 important points they should cover.
- Do not demand advanced/internal details unless
  the question requires them.

Improve:
- Give only 1 or 2 short sentences explaining how
  to improve the answer.

Rules:

- Be concise and interview-focused.
- Do not give a long explanation.
- Do not give a long sample answer.
- Do not provide code unless the question specifically
  requires code.
- Do not invent mistakes when the answer is technically correct.
- Do not penalize the candidate for unnecessary details.
- Match the feedback to the question difficulty.
"""

    evaluation = client.responses.create(
        model="openai/gpt-oss-20b", input=evaluation_prompt
    )

    evaluation_text = evaluation.output_text.strip()

    # ========================================================
    # 10. SAVE EVALUATION
    # ========================================================

    evaluations.append(
        {"question": question, "answer": answer, "evaluation": evaluation_text}
    )

    # ========================================================
    # 11. DISPLAY EVALUATION
    # ========================================================

    print("\nAI Evaluation:")

    print(evaluation_text)


# ============================================================
# 12. PREPARE COMPLETE INTERVIEW DATA
# ============================================================

interview_history = ""

for index, item in enumerate(evaluations, start=1):

    interview_history += f"""
Question {index}:
{item["question"]}

Candidate Answer:
{item["answer"]}

Evaluation:
{item["evaluation"]}

----------------------------------------
"""


# ============================================================
# 13. GENERATE FINAL INTERVIEW REVIEW
# ============================================================

print("\n" + "=" * 60)

print("GENERATING FINAL INTERVIEW REVIEW...")

print("=" * 60)


final_review_prompt = f"""
You are a concise technical interview coach.

Subject:
{subject}

Selected Topics:
{topics}

Difficulty:
{difficulty}

Number of Questions:
{number_of_questions}

Complete Interview:
{interview_history}

Analyze ALL answers together.

Pay special attention to performance across
the selected topics.

Return ONLY this format:

FINAL REVIEW

Overall Score: X/10

Strong:
- [maximum 2 short points]

Improve:
- [maximum 2 short points]

Topics to Revise:
- [maximum 4 topics]

Technical Terms to Revise:
- [maximum 5 terms]

Next Focus:
- [maximum 2 specific topics or skills]

Rules:

- Keep the entire review under 10 lines.
- Base the review on ALL answers.
- Identify repeated strengths or weaknesses.
- Connect weaknesses to the selected topics.
- Do not repeat individual question evaluations.
- Do not explain answers again.
- Do not give sample answers.
- Do not give lengthy advice.
- Do not invent weaknesses.
- If a topic was not sufficiently tested,
  do not claim the candidate is weak in it.
"""

final_review = client.responses.create(
    model="openai/gpt-oss-20b", input=final_review_prompt
)


# ============================================================
# 14. DISPLAY FINAL REVIEW
# ============================================================

print("\n" + "=" * 60)

print("FINAL INTERVIEW REVIEW")

print("=" * 60)

print(final_review.output_text.strip())


# ============================================================
# 15. INTERVIEW COMPLETE
# ============================================================

print("\n" + "=" * 60)

print("INTERVIEW COMPLETED")

print("=" * 60)

print("\nThank you for completing the interview!")
