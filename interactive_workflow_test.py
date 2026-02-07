"""
Interactive workflow test for LLM clarification gate + kit generation.
Allows manual testing by chatting in the terminal through the full clarification loop.
"""

import sys
from pathlib import Path

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent))

import json
from app.services.planner_service import gate_clarification
from app.services.kit_service import generate_kit
from app.services.query_service import generate_item_queries


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


def get_user_input(prompt, allow_empty=False):
    """Get non-empty user input."""
    while True:
        user_input = input(prompt).strip()
        if user_input or allow_empty:
            return user_input
        print("Input cannot be empty. Please try again.")


def interactive_workflow():
    """Run interactive clarification gate + kit generation workflow."""
    
    print_section("🏕️ INTERACTIVE KIT GENERATION WORKFLOW")
    print("This tool will help you generate a comprehensive kit using AI.")
    print("Follow the steps to describe what you need, answer clarification questions,")
    print("and get a structured kit with items organized by category.\n")
    
    # Step 1: Get initial user prompt
    print_section("STEP 1: DESCRIBE YOUR NEEDS")
    print("Tell me what kind of kit you need. Be as specific or general as you like.")
    print("Example: 'I need a camping kit for a 3-day backpacking trip'")
    user_prompt = get_user_input("\nYour request: ")
    
    conversation_history = user_prompt
    previous_questions = None  # Track questions to detect if they repeat
    
    # Loop until user approves task interpretation
    while True:
        # Step 2: Call gate_clarification
        print_section("ANALYZING YOUR REQUEST")
        print("Let me analyze your request and see if I need clarification...")
        
        try:
            gate_response = gate_clarification(user_prompt, conversation_history=conversation_history)
        except Exception as e:
            print(f"Error during clarification gate: {e}")
            return
        
        # Step 3: Check if clarification is needed
        need_clarification = gate_response.get("need_clarification", False)
        
        if need_clarification:
            questions = gate_response.get("questions", [])
            
            # Check if we're asking the same questions again
            if previous_questions and previous_questions == questions:
                print_section("⚠️  DUPLICATE QUESTIONS DETECTED")
                print("I'm asking the same questions again. This might mean:")
                print("  • Your answers need more detail")
                print("  • You should provide a more specific/different request\n")
                choose = get_user_input("What would you like to do? (retry/new_request): ").lower().strip()
                
                if choose in ['new_request', 'new']:
                    print_section("STEP 1: DESCRIBE YOUR NEEDS")
                    user_prompt = get_user_input("Your request: ")
                    conversation_history = user_prompt
                    previous_questions = None
                    continue
            
            previous_questions = questions
            
            print_section("CLARIFICATION NEEDED")
            print(f"I have {len(questions)} question(s) to better understand your needs:\n")
            
            clarifications = []
            for i, question in enumerate(questions, 1):
                print(f"Q{i}: {question}")
                answer = get_user_input(f"Your answer: ")
                clarifications.append({
                    "question": question,
                    "answer": answer
                })
            
            # Build clarification string for next call
            clarifications_str = "\n".join(
                f"Q: {c['question']}\nA: {c['answer']}" for c in clarifications
            )
            
            # Update conversation history
            conversation_history = f"{user_prompt}\n\nClarification Q&A:\n{clarifications_str}"
            
            print("\n🔄 Continuing analysis with your answers...\n")
            continue  # Loop back to gate_clarification with updated history
        
        # Extract task interpretation
        task_interpretation = gate_response.get("task_interpretation")
        
        if not task_interpretation:
            print("❌ Failed to extract task interpretation. Exiting.")
            return
        
        previous_questions = None  # Reset for next iteration if needed
        
        # Display task interpretation
        print_section("TASK INTERPRETATION")
        print("Based on your input, here's my understanding:\n")
        print(f"📌 Domain: {task_interpretation.get('domain')}\n")
        print(f"🎯 Goals:")
        for goal in task_interpretation.get('goals', []):
            print(f"  • {goal}")
        print(f"\n📋 Assumptions:")
        for assumption in task_interpretation.get('assumptions', []):
            print(f"  • {assumption}")
        print(f"\n🔗 Constraints:")
        for constraint in task_interpretation.get('constraints', []):
            print(f"  • {constraint}")
        print(f"\n⚠️  Safety Considerations:")
        for safety in task_interpretation.get('safety_considerations', []):
            print(f"  • {safety}")
        print(f"\n📚 Best Practices & Regulations:")
        for note in task_interpretation.get('regulatory_or_best_practice_notes', []):
            print(f"  • {note}")
        
        # Step 4: Ask user if they're satisfied with interpretation
        print_section("READY TO GENERATE KIT?")
        proceed = get_user_input(
            "Does this interpretation look correct? (yes/no/clarify): "
        ).lower().strip()
        
        if proceed in ['yes', 'y']:
            # Break out of loop to generate kit
            break
        elif proceed in ['no', 'n']:
            # Get new/refined prompt for next iteration
            print("\n📝 Let's try again with more details or corrections.")
            refined_prompt = get_user_input(
                "Provide a new or refined request (or press Enter to restart): "
            )
            if refined_prompt:
                user_prompt = refined_prompt
                conversation_history = refined_prompt
            else:
                # Restart from scratch
                print_section("STEP 1: DESCRIBE YOUR NEEDS")
                print("Tell me what kind of kit you need.")
                user_prompt = get_user_input("\nYour request: ")
                conversation_history = user_prompt
            # Loop continues with new prompt
            continue
        elif proceed in ['clarify', 'c']:
            # Force another clarification round
            print("\n🔄 Let me ask some more clarifying questions...\n")
            continue
        else:
            print("Please enter 'yes', 'no', or 'clarify'")
            continue
    
    # Step 5: Generate kit (outside the loop now that we have approved interpretation)
    print_section("GENERATING KIT")
    print("Creating your kit with organized items...\n")
    
    try:
        kit = generate_kit(
            task_interpretation=task_interpretation,
            clarifications=conversation_history
        )
    except Exception as e:
        print(f"Error during kit generation: {e}")
        return
    
    # Display kit
    print_section("✅ YOUR GENERATED KIT")
    
    print(f"🎁 Kit Title: {kit.get('kit_title')}\n")
    print(f"📝 Summary: {kit.get('summary')}\n")
    
    sections = kit.get('sections', [])
    total_items = sum(len(section.get('items', [])) for section in sections)
    print(f"📦 Total Items: {total_items} across {len(sections)} sections\n")
    
    for section_idx, section in enumerate(sections, 1):
        section_name = section.get('name', 'Unknown')
        items = section.get('items', [])
        
        print(f"\n{'─'*70}")
        print(f"{section_idx}. {section_name} ({len(items)} items)")
        print(f"{'─'*70}")
        
        for item_idx, item in enumerate(items, 1):
            item_key = item.get('item_key', 'unknown')
            name = item.get('name', 'Unknown')
            description = item.get('description', '')
            sku_type = item.get('sku_type', '')
            priority = item.get('priority', 'unknown')
            quantity = item.get('quantity_suggestion', '1')
            
            print(f"\n  {item_idx}. {name} [{item_key}]")
            print(f"     Type: {sku_type} | Priority: {priority.upper()} | Qty: {quantity}")
            print(f"     Description: {description}")
            
            safety_notes = item.get('safety_notes', [])
            if safety_notes:
                print(f"     ⚠️  Safety: {', '.join(safety_notes)}")
            
            specs = item.get('specs_to_search', [])
            if specs:
                print(f"     🔍 Key Specs: {', '.join(specs[:3])}")
            
            query_terms = item.get('query_terms', [])
            if query_terms:
                print(f"     🏷️  Search Terms: {', '.join(query_terms[:3])}")
    
    # Step 6: Generate queries (optional)
    print_section("GENERATING SEARCH QUERIES")
    print("Creating search queries for each item...\n")
    
    try:
        queries = generate_item_queries(kit)
        
        print(f"📊 Generated {len(queries)} search queries:\n")
        
        for query in queries:
            item_key = query.get('item_key')
            clean_query = query.get('clean_query')
            expanded_query = query.get('expanded_query')
            
            print(f"Item: {item_key}")
            print(f"  Clean: {clean_query}")
            print(f"  Expanded: {expanded_query}")
            print()
    except Exception as e:
        print(f"⚠️  Could not generate queries: {e}")
    
    # Step 7: Final summary
    print_section("WORKFLOW COMPLETE")
    print("✅ Kit generation workflow completed successfully!")
    print(f"✅ Generated kit with {total_items} items across {len(sections)} sections")
    print("✅ Ready for next steps: item search and matching\n")


def main():
    """Main entry point."""
    try:
        interactive_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
