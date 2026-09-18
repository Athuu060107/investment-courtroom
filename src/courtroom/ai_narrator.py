import os
import google.generativeai as genai
from dotenv import load_dotenv

from src.courtroom.bull_engine import build_bull_case
from src.courtroom.bear_engine import build_bear_case
from src.courtroom.cross_exam import cross_examine
from src.scoring.judge import judge_company

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def build_prompt(company_name, bull_points, bear_points, challenges, verdict_result):
    prompt = f"""You are narrating a courtroom scene for an investment analysis tool called Investment Courtroom.
The company on trial is {company_name}.

You must turn the evidence below into natural, engaging courtroom dialogue between a Bull lawyer,
a Bear lawyer, and a Judge. This is a strict rule: you must NOT invent any number, fact, or claim
that is not already given below. Only rephrase and dramatize the existing evidence into dialogue.
Do not add new financial figures of your own.

BULL'S EVIDENCE:
{chr(10).join(f"- {p}" for p in bull_points) if bull_points else "- No strong bullish evidence found."}

BEAR'S EVIDENCE:
{chr(10).join(f"- {p}" for p in bear_points) if bear_points else "- No strong bearish evidence found."}

CROSS-EXAMINATION CHALLENGES:
{chr(10).join(f"- {c}" for c in challenges) if challenges else "- No direct contradictions found."}

JUDGE'S FINAL VERDICT: {verdict_result['verdict']} (Overall Score: {verdict_result['overall_score']}/100)

Write this as a short courtroom scene with these exact speaker labels: "BULL:", "BEAR:", "JUDGE:".
Keep it to about 6-8 short lines total. Keep the tone lively but professional, like a courtroom drama.
End with the Judge announcing the verdict clearly.
"""
    return prompt


def generate_courtroom_dialogue(company_name):
    bull_points = build_bull_case(company_name)
    bear_points = build_bear_case(company_name)
    challenges = cross_examine(company_name)
    verdict_result = judge_company(company_name)

    if verdict_result is None:
        return "Could not generate a courtroom scene - no data found for this company."

    prompt = build_prompt(company_name, bull_points, bear_points, challenges, verdict_result)

    model = genai.GenerativeModel("gemini-3.1-flash-lite")
    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":
    dialogue = generate_courtroom_dialogue("TCS")
    print(dialogue)
