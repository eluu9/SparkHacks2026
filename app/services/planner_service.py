import json
from app.services.llm_service import LocalLLMProvider, validate_response, convert_schema_to_dict
from pathlib import Path

MAX_CLARIFICATION_ROUNDS = 3


def gate_clarification(user_prompt, conversation_history=None, user_preferences=None):
    clarify_gate_str = Path("app/services/prompts/clarify_gate.md").read_text(encoding="utf-8")
    llm = LocalLLMProvider()
    
    if conversation_history and isinstance(conversation_history, list):
        history_str = "\n".join([
            f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}" 
            for item in conversation_history
        ])
    else:
        history_str = str(conversation_history or "")
    
    formatted_prompt = clarify_gate_str.format(
        user_prompt=user_prompt,
        conversation_history=history_str,
        user_preferences=user_preferences or ""
    )

    response = llm.generate_response(
        system_prompt=formatted_prompt,
        user_prompt=user_prompt,
        schema=convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")
    )

    validated_response = validate_response(response, convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json"))
    return validated_response


def run_clarification_loop(user_prompt, user_preferences=None, max_rounds=MAX_CLARIFICATION_ROUNDS):
    conversation_history = []
    asked_questions = set()
    
    for round_num in range(max_rounds):
        response = gate_clarification(user_prompt, conversation_history, user_preferences)
        
        if not response.get("need_clarification"):
            return response.get("task_interpretation"), conversation_history
        
        questions = response.get("questions", [])
        new_questions = [q for q in questions if q.lower().strip() not in asked_questions]
        
        if not new_questions:
            conversation_history.append({
                "question": "All questions have been answered",
                "answer": "User has provided all available information"
            })
            response = gate_clarification(user_prompt, conversation_history, user_preferences)
            if response.get("task_interpretation"):
                return response.get("task_interpretation"), conversation_history
            else:
                return None, conversation_history
        
        for q in new_questions:
            asked_questions.add(q.lower().strip())
            
        return {
            "incomplete": True,
            "questions": new_questions,
            "round": round_num + 1
        }, conversation_history
    
    conversation_history.append({
        "question": "Maximum clarification rounds reached",
        "answer": "Please proceed with available information"
    })
    final_response = gate_clarification(user_prompt, conversation_history, user_preferences)
    return final_response.get("task_interpretation"), conversation_history

