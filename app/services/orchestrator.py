import datetime
from app.services.planner_service import gate_clarification
from app.services.kit_service import generate_kit
from app.services.query_service import build_query_for_item
from app.services.search_service import SearchService
from app.services.match_service import rankCandidates
from app.extensions import mongo

def run_lab_pipeline(user_input, history=None):
    gate = gate_clarification(user_input, conversation_history=history)
    
    if gate.get("need_clarification"):
        return {"type": "questions", "data": gate["questions"]}

    task_info = str(gate.get("task_interpretation", "")) 
    kit_json = generate_kit(task_info, clarifications=history)

    searcher = SearchService(mongo_db=mongo.db)
    
    for section in kit_json.get("sections", []):
        for item in section.get("items", []):
            query_data = build_query_for_item(item)
            
            raw_results = searcher.search(query_data["clean_query"])
            matches = rankCandidates(item, raw_results)
            
            if matches:
                item["buy_url"] = matches[0].get("URL")
                item["price"] = matches[0].get("Search Item", {}).get("price", "View Price")
            else:
                item["buy_url"] = f"https://www.google.com/search?q={item['name']}"
                item["price"] = "Check Site"

    kit_json["type"] = "final_kit"
    return kit_json