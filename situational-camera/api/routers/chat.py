from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from api.routers.events import load_all_events

load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None

router = APIRouter(prefix="/api/chat", tags=["chat"])

from typing import Optional

class ChatRequest(BaseModel):
    question: str
    date_from: Optional[str] = None  # YYYY-MM-DD
    date_to: Optional[str] = None    # YYYY-MM-DD
    camera_id: Optional[str] = None

@router.post("")
def ask_footage(req: ChatRequest):
    """
    Asks Gemini a question regarding the security log footage history.
    """
    # 1. Load and filter events
    events = load_all_events()
    filtered = events

    if req.date_from:
        try:
            from_dt = datetime.datetime.strptime(req.date_from, "%Y-%m-%d")
            filtered = [
                e for e in filtered
                if datetime.datetime.strptime(e["timestamp"][:10], "%Y-%m-%d") >= from_dt
            ]
        except ValueError:
            pass

    if req.date_to:
        try:
            to_dt = datetime.datetime.strptime(req.date_to, "%Y-%m-%d")
            filtered = [
                e for e in filtered
                if datetime.datetime.strptime(e["timestamp"][:10], "%Y-%m-%d") <= to_dt
            ]
        except ValueError:
            pass

    # 2. Extract relevant events for reference
    # Find events that match terms from the question
    q_words = [w.lower() for w in req.question.split() if len(w) > 3]
    relevant_events = []
    
    for event in filtered:
        # Check keyword matches
        is_relevant = False
        for word in q_words:
            if word in event["situation"].lower() or word in event["explanation"].lower():
                is_relevant = True
                break
                
        # Fallback: if the event is High risk, it's generally relevant
        if not is_relevant and event["risk"] == "High":
            is_relevant = True

        if is_relevant:
            relevant_events.append(event)

    # Limit to top 5 relevant events
    relevant_events = relevant_events[:5]
    
    # If no specific relevance was found, just return the 3 most recent events in date range
    if not relevant_events and filtered:
        relevant_events = filtered[:3]

    # 3. Format context for Gemini
    # Limit number of logs in prompt to avoid token bloat (max 50)
    context_events = filtered[:50]
    formatted_logs = ""
    for idx, e in enumerate(context_events):
        formatted_logs += (
            f"[{idx+1}] Time: {e['timestamp']} | Situation: {e['situation']} | "
            f"Risk: {e['risk']} | Safety Score: {e['safety_score']}/10 | "
            f"Focus Score: {e['focus_score']}/100 | Explanation: {e['explanation']}\n"
        )

    if not formatted_logs:
        formatted_logs = "No security incidents logged during this period."

    # 4. Invoke Gemini Model
    if not gemini_model:
        # Mock/Fallback answer if Gemini API key is missing
        answer = (
            f"Gemini API key is not configured. Here is an automated search response:\n\n"
            f"I found {len(filtered)} total events logged in the selected period. "
            f"There are {len([e for e in filtered if e['risk'] == 'High'])} High risk events. "
            f"The most common situation was '{filtered[0]['situation'] if filtered else 'None'}'. "
            f"Please configure your GOOGLE_API_KEY in the backend .env file to enable full cognitive Q&A."
        )
        return {
            "answer": answer,
            "relevant_events": relevant_events
        }

    prompt = f"""
You are SituVision AI, a professional SOC (Security Operations Center) intelligence assistant.
You are tasked with answering a security operator's question based on the surveillance logs provided below.

Operator's Question:
"{req.question}"

Surveillance Event Logs (ordered newest to oldest):
{formatted_logs}

Instructions:
- Provide a clear, cohesive, and professional response analyzing the logs.
- Address the user's question directly.
- Summarize critical risks, patterns, or timing of events.
- Be concise (2-3 paragraphs max).
- If the logs do not contain the answer, say so, but summarize what is present in the period.
- Do not mention "[1]", "[2]" indices in your output, talk naturally.
"""

    try:
        response = gemini_model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer from Gemini: {e}"
        )

    return {
        "answer": answer,
        "relevant_events": relevant_events
    }
