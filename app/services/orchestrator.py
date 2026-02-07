from app.services.planner_service import gate_clarification
from app.services.kit_service import generate_kit
from app.services.query_service import build_query_for_item
from app.services.search_service import SearchService
from app.services.match_service import rankCandidates
from app.extensions import mongo

def run_lab_pipeline(user_input, history_list=None):
    history_str = ""
    if history_list:
        for msg in history_list:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_str += f"{role.upper()}: {content}\n"

    has_budget = "$" in user_input or any(char.isdigit() for char in user_input)
    gate = gate_clarification(user_input, conversation_history=history_str)

    if history_list or has_budget:
        gate["need_clarification"] = False

    if gate.get("need_clarification"):
        return {"type": "questions", "data": gate["questions"]}

    task = gate.get("task_interpretation", user_input)
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