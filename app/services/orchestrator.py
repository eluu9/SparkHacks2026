"""Main pipeline that ties clarification, kit generation, and product search."""

from app.extensions import mongo
from app.services.kit_service import generate_kit
from app.services.match_service import rank_candidates
from app.services.planner_service import gate_clarification
from app.services.query_service import build_query_for_item
from app.services.search_service import SearchService


def run_lab_pipeline(user_input, history_list=None):
    """Execute the end-to-end kit building pipeline."""

    # Build a conversation history string for the LLM
    history_str = ""
    if history_list:
        for message in history_list:
            role = message.get("role", "user")
            content = message.get("content", "")
            history_str += f"{role.upper()}: {content}\n"

    has_budget = "$" in user_input or any(ch.isdigit() for ch in user_input)
    gate = gate_clarification(user_input, conversation_history=history_str)

    # Skip clarification if we already have context or a budget
    if history_list or has_budget:
        gate["need_clarification"] = False

    if gate.get("need_clarification"):
        return {"type": "questions", "data": gate["questions"]}

    task = gate.get("task_interpretation", user_input)
    kit_json = generate_kit(task, clarifications=history_str)

    # Search for real products matching each kit item
    searcher = SearchService(mongo_db=mongo.db)

    for section in kit_json.get("sections", []):
        for item in section.get("items", []):
            queries = build_query_for_item(item)
            raw_results = searcher.search(queries["clean_query"])
            matches = rank_candidates(item, raw_results)

            if matches:
                best = matches[0]["search_item"]
            elif raw_results:
                best = raw_results[0]
            else:
                continue

            item["buy_url"] = best.get("url")
            item["price"] = best.get("price", "View")
            item["img_url"] = best.get("img_url")

    kit_json["type"] = "final_kit"
    return kit_json