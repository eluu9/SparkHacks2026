"""
Full workflow test for LLM clarification gate + kit generation.
Tests the complete loop: user prompt → clarification (if needed) → kit generation.
"""

import sys
from pathlib import Path

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import json
from unittest.mock import Mock, patch
from app.services.planner_service import gate_clarification
from app.services.kit_service import generate_kit
from app.services.llm_service import convert_schema_to_dict, validate_response


class MockLLMProvider:
    """Mock LLM provider for testing different scenarios."""
    
    def __init__(self, response_data):
        self.response_data = response_data
    
    def generate_response(self, system_prompt, user_prompt, schema):
        """Return pre-configured mock response."""
        return self.response_data


@pytest.fixture
def clarify_gate_no_clarification_needed():
    """Mock response when user prompt is clear."""
    return {
        "need_clarification": False,
        "task_interpretation": {
            "domain": "camping",
            "goals": [
                "Assemble a complete camping kit for a 3-day backpacking trip",
                "Focus on lightweight, multi-use items"
            ],
            "assumptions": [
                "Warm weather camping (spring/summer)",
                "Temperate climate",
                "No extreme altitude"
            ],
            "constraints": [
                "Budget: under $500",
                "Must be backpacker-friendly (lightweight)",
                "Solo trip"
            ],
            "safety_considerations": [
                "Bear-proof storage considerations",
                "First aid essentials",
                "Weather protection"
            ],
            "regulatory_or_best_practice_notes": [
                "Leave No Trace principles",
                "Basic wilderness safety"
            ]
        }
    }


@pytest.fixture
def clarify_gate_needs_clarification():
    """Mock response when clarification is needed."""
    return {
        "need_clarification": True,
        "questions": [
            "What is your target budget for this camping kit?",
            "How many people will be camping?",
            "What season and climate conditions do you expect?"
        ]
    }


@pytest.fixture
def kit_generation_response():
    """Mock response for full kit generation."""
    return {
        "kit_title": "3-Day Backpacking Camping Kit",
        "summary": "A comprehensive lightweight camping kit designed for warm-weather backpacking trips with budget considerations.",
        "sections": [
            {
                "name": "Essential Items",
                "items": [
                    {
                        "item_key": "tent-3season",
                        "name": "3-Season Backpacking Tent",
                        "description": "Lightweight dome tent with integrated rainfly suitable for spring/summer camping",
                        "sku_type": "Camping Tent",
                        "specs_to_search": ["3-season", "backpacking", "2-person", "lightweight"],
                        "quantity_suggestion": "1",
                        "priority": "essential",
                        "safety_notes": ["Must have rainfly and good ventilation to prevent condensation"],
                        "compatibility_notes": ["Compatible with standard tent stakes", "Groundsheet recommended"],
                        "query_terms": ["dome tent", "backpacking shelter", "3-season tent"],
                        "identifier_hints": {
                            "mpn": None,
                            "model": None,
                            "upc": None
                        }
                    },
                    {
                        "item_key": "sleeping-bag-summer",
                        "name": "Summer Sleeping Bag",
                        "description": "Temperature-rated 40-50°F sleeping bag with synthetic or down insulation",
                        "sku_type": "Sleeping Bag",
                        "specs_to_search": ["40-50°F", "summer", "lightweight", "packable"],
                        "quantity_suggestion": "1",
                        "priority": "essential",
                        "safety_notes": ["Check temperature rating matches expected climate"],
                        "compatibility_notes": ["Compatible with standard sleeping pads"],
                        "query_terms": ["summer sleeping bag", "lightweight bag"],
                        "identifier_hints": {
                            "mpn": None,
                            "model": None,
                            "upc": None
                        }
                    }
                ]
            },
            {
                "name": "Safety / PPE",
                "items": [
                    {
                        "item_key": "first-aid-kit",
                        "name": "Compact First Aid Kit",
                        "description": "Backpacking-sized first aid kit with blister treatment, pain relief, and wound care",
                        "sku_type": "First Aid Kit",
                        "specs_to_search": ["compact", "backpacking", "waterproof"],
                        "quantity_suggestion": "1",
                        "priority": "essential",
                        "safety_notes": ["Essential for wilderness safety"],
                        "compatibility_notes": ["Fits in backpack side pocket"],
                        "query_terms": ["hiking first aid", "compact medical kit"],
                        "identifier_hints": {
                            "mpn": None,
                            "model": None,
                            "upc": None
                        }
                    }
                ]
            },
            {
                "name": "Frequently Forgotten Items",
                "items": [
                    {
                        "item_key": "toilet-paper-pack",
                        "name": "Biodegradable Toilet Paper Pack",
                        "description": "Portable toilet paper with pack-out system for Leave No Trace compliance",
                        "sku_type": "Hygiene Product",
                        "specs_to_search": ["biodegradable", "lightweight", "portable"],
                        "quantity_suggestion": "2",
                        "priority": "recommended",
                        "safety_notes": ["Must be packed out", "Never leave behind"],
                        "compatibility_notes": ["Works with portable trowel"],
                        "query_terms": ["camping toilet paper", "waste pack-out"],
                        "identifier_hints": {
                            "mpn": None,
                            "model": None,
                            "upc": None
                        }
                    }
                ]
            }
        ]
    }


def test_workflow_no_clarification_needed(clarify_gate_no_clarification_needed, kit_generation_response):
    """
    Test complete workflow when user prompt is clear:
    1. Call gate_clarification
    2. Check that no clarification is needed
    3. Extract task_interpretation
    4. Call generate_kit with task_interpretation
    5. Validate kit structure
    """
    user_prompt = "I want a camping kit for a 3-day backpacking trip under $500"
    
    # Mock planner_service.gate_clarification
    with patch('app.services.planner_service.LocalLLMProvider') as mock_llm:
        mock_instance = mock_llm.return_value
        mock_instance.generate_response.return_value = clarify_gate_no_clarification_needed
        
        # Step 1: Call gate_clarification
        gate_response = gate_clarification(user_prompt)
        
        # Step 2: Verify no clarification needed
        assert gate_response["need_clarification"] is False
        assert "task_interpretation" in gate_response
        
        # Step 3: Extract task_interpretation
        task_interpretation = gate_response["task_interpretation"]
        assert task_interpretation["domain"] == "camping"
        assert len(task_interpretation["goals"]) > 0
    
    # Mock kit_service.generate_kit
    with patch('app.services.kit_service.LocalLLMProvider') as mock_llm:
        mock_instance = mock_llm.return_value
        mock_instance.generate_response.return_value = kit_generation_response
        
        # Step 4: Call generate_kit
        kit = generate_kit(
            task_interpretation=task_interpretation,
            clarifications=""
        )
        
        # Step 5: Validate kit structure
        assert "kit_title" in kit
        assert "summary" in kit
        assert "sections" in kit
        assert len(kit["sections"]) > 0
        
        # Validate section structure
        for section in kit["sections"]:
            assert "name" in section
            assert "items" in section
            assert len(section["items"]) > 0
            
            for item in section["items"]:
                assert "item_key" in item
                assert "name" in item
                assert "description" in item
                assert "sku_type" in item
                assert "specs_to_search" in item
                assert "quantity_suggestion" in item


def test_workflow_with_clarification_loop(
    clarify_gate_needs_clarification,
    clarify_gate_no_clarification_needed,
    kit_generation_response
):
    """
    Test complete workflow with clarification loop:
    1. Call gate_clarification - gets questions
    2. Simulate user providing clarification answers
    3. Call gate_clarification again with conversation history - gets task_interpretation
    4. Call generate_kit with task_interpretation + clarifications
    5. Validate final kit
    """
    user_prompt = "I need a camping kit"
    
    # Step 1: First call to gate_clarification - needs clarification
    with patch('app.services.planner_service.LocalLLMProvider') as mock_llm:
        mock_instance = mock_llm.return_value
        mock_instance.generate_response.return_value = clarify_gate_needs_clarification
        
        gate_response_1 = gate_clarification(user_prompt)
        
        assert gate_response_1["need_clarification"] is True
        assert "questions" in gate_response_1
        questions = gate_response_1["questions"]
        assert len(questions) == 3
    
    # Step 2: Simulate user providing clarification answers
    user_answers = [
        "$300-400",
        "2 people",
        "Summer in temperate climate"
    ]
    
    # Build clarification context for next call
    clarifications_str = "\n".join(
        f"Q: {q}\nA: {a}" for q, a in zip(questions, user_answers)
    )
    
    conversation_history = f"{user_prompt}\n\nClarification Q&A:\n{clarifications_str}"
    
    # Step 3: Call gate_clarification again with conversation history
    with patch('app.services.planner_service.LocalLLMProvider') as mock_llm:
        mock_instance = mock_llm.return_value
        mock_instance.generate_response.return_value = clarify_gate_no_clarification_needed
        
        gate_response_2 = gate_clarification(
            user_prompt,
            conversation_history=conversation_history
        )
        
        assert gate_response_2["need_clarification"] is False
        task_interpretation = gate_response_2["task_interpretation"]
    
    # Step 4: Call generate_kit with task_interpretation + clarifications
    with patch('app.services.kit_service.LocalLLMProvider') as mock_llm:
        mock_instance = mock_llm.return_value
        mock_instance.generate_response.return_value = kit_generation_response
        
        kit = generate_kit(
            task_interpretation=task_interpretation,
            clarifications=clarifications_str
        )
        
        # Step 5: Validate final kit
        assert "kit_title" in kit
        assert "sections" in kit
        assert len(kit["sections"]) > 0


def test_schema_validation():
    """Test that schemas are valid and can be loaded."""
    clarify_gate_schema = convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")
    kit_schema = convert_schema_to_dict("app/schemas/kit.schema.json")
    
    assert clarify_gate_schema is not None
    assert clarify_gate_schema.get("type") == "object"
    
    assert kit_schema is not None
    assert kit_schema.get("type") == "object"


def test_clarification_response_validation(clarify_gate_needs_clarification):
    """Test that clarification response validates against schema."""
    schema = convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")
    
    # Should not raise
    validated = validate_response(clarify_gate_needs_clarification, schema)
    assert validated == clarify_gate_needs_clarification


def test_kit_response_validation(kit_generation_response):
    """Test that kit response validates against schema."""
    schema = convert_schema_to_dict("app/schemas/kit.schema.json")
    
    # Should not raise
    validated = validate_response(kit_generation_response, schema)
    assert validated == kit_generation_response


def test_malformed_clarification_response_fails():
    """Test that malformed clarification response fails validation."""
    schema = convert_schema_to_dict("app/schemas/llm_clarify_gate.schema.json")
    
    # Missing required field: need_clarification
    malformed = {
        "questions": ["What is your budget?"]
    }
    
    with pytest.raises(Exception):  # jsonschema.ValidationError
        validate_response(malformed, schema)


def test_malformed_kit_response_fails():
    """Test that malformed kit response fails validation."""
    schema = convert_schema_to_dict("app/schemas/kit.schema.json")
    
    # Missing required fields: kit_title, summary, sections
    malformed = {
        "kit_title": "Test Kit"
    }
    
    with pytest.raises(Exception):  # jsonschema.ValidationError
        validate_response(malformed, schema)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
