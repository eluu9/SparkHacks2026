import time
import datetime
from app.services.planner_service import gate_clarification
from app.services.kit_service import generate_kit
from app.services.query_service import build_query_for_item
from app.services.search_service import SearchService
from app.services.match_service import rankCandidates
from app.extensions import mongo

def run_lab_pipeline(user_input, history_list=None):
    # 1. Format History for the AI
    # This answers your question: "Where do I put the conversation history thing?"
    history_str = ""
    if history_list:
        for msg in history_list:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_str += f"{role.upper()}: {content}\n"

    # 2. Check for explicit constraints in the current prompt
    has_budget = "$" in user_input or any(char.isdigit() for char in user_input)
    
    # 3. Call the Gate
    # We pass the history string so the Gate can summarize previous context
    gate = gate_clarification(user_input, conversation_history=history_str)

    # 4. THE HARD FIX: LOOP BREAKER
    # If we have history OR budget is present, IGNORE the 'questions' field.
    # We force the system to proceed to building.
    if history_list or has_budget:
        print("DEBUG: Context detected. Overriding Gate to FORCE BUILD.")
        gate["need_clarification"] = False

    # 5. Return questions ONLY if truly necessary (First turn, vague prompt)
    if gate.get("need_clarification"):
        return {"type": "questions", "data": gate["questions"]}

    # 6. Force Build & Search
    # We pass history_str as 'clarifications' so the Kit Builder sees the full context
    task = gate.get("task_interpretation", user_input)
    
    # Ensure task is a string or dict as expected by your service
    kit_json = generate_kit(task, clarifications=history_str)
    
    searcher = SearchService(mongo_db=mongo.db)
    
    for section in kit_json.get("sections", []):
        for item in section.get("items", []):
            queries = build_query_for_item(item)
            raw_results = searcher.search(queries["clean_query"])
            matches = rankCandidates(item, raw_results)

            if matches:
                best = matches[0]["Search Item"]
                item["buy_url"] = best.get("url")
                item["price"] = best.get("price", "View")
                item["img_url"] = best.get("img_url")
            elif raw_results:
                best = raw_results[0]
                item["buy_url"] = best.get("url")
                item["price"] = best.get("price", "View")
                item["img_url"] = best.get("img_url")

    kit_json["type"] = "final_kit"
    return kit_json