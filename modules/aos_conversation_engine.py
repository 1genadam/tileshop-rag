#!/usr/bin/env python3
"""
AOS Conversation Engine - Dynamic, Learning-Based Sales Conversation System
Provides context-aware questions and learns from successful conversions
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Track conversation state and customer context"""
    project_type: str = ""
    customer_phase: str = "discovery"  # discovery, qualification, recommendation, closing
    gathered_info: Dict[str, Any] = None
    phone_number: str = ""
    conversation_quality_score: float = 0.0
    
    def __post_init__(self):
        if self.gathered_info is None:
            self.gathered_info = {}

class AOSConversationEngine:
    """Dynamic conversation engine that learns and adapts AOS questions"""
    
    def __init__(self):
        self.question_library = self._initialize_question_library()
        self.conversation_patterns = self._load_successful_patterns()
        self.learning_metrics = {
            "successful_conversions": [],
            "question_effectiveness": {},
            "customer_response_patterns": {}
        }
    
    def _initialize_question_library(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize dynamic question library organized by phase and project type"""
        return {
            "discovery": {
                "kitchen": [
                    "What's your color scheme? Are your cabinets and countertops already selected?",
                    "Do you prefer matte or polished finishes for your kitchen?",
                    "Are you thinking warm tones like wood-look or cool tones like stone?",
                    "What size kitchen are we working with? This helps with tile size recommendations.",
                    "Are you renovating the whole kitchen or just the floor?",
                    "Do you have kids or pets? This affects durability needs.",
                    "What's your cooking style - lots of prep work or more casual?",
                    "Are you considering a matching backsplash to tie everything together?"
                ],
                "bathroom": [
                    "Is this for a master bathroom or guest bath?",
                    "Are you looking for floor tile, shower tile, or both?",
                    "What's your style preference - modern, traditional, or transitional?",
                    "Do you prefer large format tiles or smaller mosaic styles?",
                    "What's your color palette for the space?",
                    "Are you doing a full renovation or just updating the tile?",
                    "Do you want slip-resistant options for safety?"
                ],
                "general": [
                    "What room are we tiling?",
                    "What's driving this project - renovation, new construction, or repair?",
                    "What's your timeline for starting the project?",
                    "What's your style preference?",
                    "Do you have any specific requirements or concerns?"
                ]
            },
            "qualification": {
                "timeline": [
                    "When are you planning to start the project?",
                    "Is this project scheduled with a contractor or DIY?",
                    "Do you need the tile delivered by a specific date?",
                    "Are you working around any other renovations?"
                ],
                "budget": [
                    "What's your budget range for this project?",
                    "Are you looking for premium options or value-focused choices?",
                    "Does your budget include installation materials?",
                    "Are you interested in seeing options at different price points?"
                ],
                "decision_making": [
                    "Who else is involved in this decision?",
                    "What's most important to you - style, durability, or price?",
                    "Have you looked at tiles elsewhere?",
                    "What would make this the perfect solution for you?"
                ]
            },
            "recommendation": {
                "product_focused": [
                    "Based on what you've told me, I have some perfect options. Want to see them?",
                    "I'm thinking {product_type} would be ideal for your {project_type}. Here's why...",
                    "Let me show you three options that fit your {criteria}.",
                    "This tile checks all your boxes: {benefits}. What do you think?"
                ],
                "solution_focused": [
                    "I can put together a complete package for your {project_type}.",
                    "Would you like me to calculate everything you'll need for installation?",
                    "I can show you how this will look in your {room_type}.",
                    "Let me create a complete project plan for you."
                ]
            },
            "closing": {
                "urgency": [
                    "I can reserve these tiles for you while you finalize your decision.",
                    "These are popular - I'd recommend securing your quantity soon.",
                    "Would you like me to save this quote with your phone number?",
                    "When would you like to move forward with this?"
                ],
                "next_steps": [
                    "What questions can I answer to help you move forward?",
                    "Would you like me to connect you with our installation team?",
                    "I can have these ready for pickup or delivery. What works better?",
                    "Shall we finalize the quantities and get this ordered?"
                ]
            }
        }
    
    def _load_successful_patterns(self) -> Dict[str, Any]:
        """Load conversation patterns that led to successful conversions"""
        # In production, this would load from a database of successful conversations
        return {
            "high_conversion_sequences": [
                ["project_type", "color_scheme", "timeline", "phone_number", "recommendation"],
                ["project_type", "phone_number", "style_preference", "size", "budget_range"],
                ["project_type", "phone_number", "timeline", "decision_makers", "solution"]
            ],
            "effective_question_combinations": {
                "kitchen": ["color_scheme", "finish_preference", "size", "timeline"],
                "bathroom": ["room_type", "style", "safety_needs", "timeline"]
            }
        }
    
    def get_next_questions(self, context: ConversationContext, num_questions: int = 2) -> List[str]:
        """Get the next best questions based on conversation context and learning"""
        
        # Determine project type if not set
        if not context.project_type:
            return ["What room are we tiling?", "What's driving this project - renovation, new construction, or repair?"]
        
        # Get questions for current phase
        phase_questions = self.question_library.get(context.customer_phase, {})
        project_questions = phase_questions.get(context.project_type, phase_questions.get("general", []))
        
        # Filter out questions we already have answers for
        available_questions = []
        for question in project_questions:
            if not self._already_answered(question, context.gathered_info):
                available_questions.append(question)
        
        # Apply learning-based prioritization
        prioritized_questions = self._prioritize_questions(available_questions, context)
        
        return prioritized_questions[:num_questions]
    
    def _already_answered(self, question: str, gathered_info: Dict[str, Any]) -> bool:
        """Check if we already have information that this question would gather"""
        question_keywords = {
            "color": ["color_scheme", "colors", "color_preferences", "cabinet_info", "countertop_info", "color_scheme_provided"],
            "cabinet": ["cabinet_info", "color_scheme_provided", "has_detailed_design_info"],
            "countertop": ["countertop_info", "color_scheme_provided", "has_detailed_design_info"],
            "size": ["room_size", "square_feet", "dimensions"],
            "style": ["style", "design_preference", "style_preferences"],
            "timeline": ["timeline", "start_date"],
            "budget": ["budget", "price_range"],
            "finish": ["finish", "matte", "polished", "finish_preferences"]
        }
        
        for keyword, info_keys in question_keywords.items():
            if keyword in question.lower():
                if any(key in gathered_info for key in info_keys):
                    return True
        return False
    
    def _prioritize_questions(self, questions: List[str], context: ConversationContext) -> List[str]:
        """Prioritize questions based on learning and context"""
        
        # In a real implementation, this would use ML to rank questions
        # For now, we'll use heuristic-based prioritization
        
        priority_scores = {}
        for question in questions:
            score = 1.0
            
            # Boost score for high-converting question types
            if "phone number" in question.lower():
                score += 2.0  # Always prioritize getting contact info
            elif "color" in question.lower() or "style" in question.lower():
                score += 1.5  # Visual preferences are highly converting
            elif "timeline" in question.lower() or "start" in question.lower():
                score += 1.3  # Timeline indicates buying intent
            elif "budget" in question.lower():
                score += 1.2  # Budget questions help qualification
            
            # Boost based on conversation flow effectiveness
            effective_combos = self.conversation_patterns.get("effective_question_combinations", {})
            if context.project_type in effective_combos:
                for effective_keyword in effective_combos[context.project_type]:
                    if effective_keyword in question.lower():
                        score += 0.5
            
            priority_scores[question] = score
        
        # Sort by priority score
        return sorted(questions, key=lambda q: priority_scores.get(q, 0), reverse=True)
    
    def extract_info_from_response(self, customer_response: str, context: ConversationContext) -> Dict[str, Any]:
        """Extract structured information from customer response"""
        
        extracted = {}
        response_lower = customer_response.lower()
        
        # Extract common information patterns
        info_patterns = {
            "phone_number": [r"(\d{3}[-.]?\d{3}[-.]?\d{4})", r"(\d{10})"],
            "room_size": [r"(\d+)\s*x\s*(\d+)", r"(\d+)\s*sq\s*ft", r"(\d+)\s*square"],
            "color_preferences": ["white", "gray", "grey", "black", "beige", "brown", "blue", "green", "charcoal", "neutral"],
            "style_preferences": ["modern", "traditional", "rustic", "farmhouse", "contemporary", "transitional"],
            "finish_preferences": ["matte", "polished", "satin", "glossy", "textured"],
            "timeline": ["asap", "this week", "next month", "spring", "summer", "fall", "winter"],
            "cabinet_info": ["cabinet", "cabinets", "upper", "lower", "charcoal", "white"],
            "countertop_info": ["countertop", "countertops", "blue", "white specs", "granite", "quartz"]
        }
        
        # Extract phone number
        import re
        for pattern in info_patterns["phone_number"]:
            match = re.search(pattern, customer_response)
            if match:
                extracted["phone_number"] = match.group(1)
                break
        
        # Extract room size
        for pattern in info_patterns["room_size"]:
            match = re.search(pattern, response_lower)
            if match:
                if "x" in match.group(0):
                    extracted["room_dimensions"] = match.group(0)
                else:
                    extracted["room_size"] = match.group(1)
                break
        
        # Extract preferences and design info
        for pref_type, options in info_patterns.items():
            if pref_type.endswith("_preferences") or pref_type.endswith("_info"):
                found_prefs = [opt for opt in options if opt in response_lower]
                if found_prefs:
                    extracted[pref_type] = found_prefs
        
        # Special handling for comprehensive color scheme descriptions
        if any(word in response_lower for word in ["cabinet", "countertop", "blue", "charcoal", "white"]):
            extracted["color_scheme_provided"] = True
            extracted["has_detailed_design_info"] = True
        
        # Extract timeline information
        timeline_keywords = info_patterns["timeline"]
        for keyword in timeline_keywords:
            if keyword in response_lower:
                extracted["timeline"] = keyword
                break
        
        return extracted
    
    def advance_conversation_phase(self, context: ConversationContext) -> str:
        """Determine if conversation should advance to next phase"""
        
        current_phase = context.customer_phase
        gathered = context.gathered_info
        
        # Phase advancement logic
        if current_phase == "discovery":
            # Move to qualification if we have basic project info
            required_discovery = ["project_type"]
            if all(key in gathered or any(k in gathered for k in [key]) for key in required_discovery):
                if "phone_number" in gathered:
                    return "qualification"
        
        elif current_phase == "qualification":
            # Move to recommendation if we have enough qualifying info
            qualifying_factors = ["timeline", "style_preferences", "room_size", "budget"]
            if sum(1 for factor in qualifying_factors if factor in gathered) >= 2:
                return "recommendation"
        
        elif current_phase == "recommendation":
            # Move to closing if customer shows interest
            if "product_interest" in gathered or "questions_answered" in gathered:
                return "closing"
        
        return current_phase
    
    def log_conversation_outcome(self, context: ConversationContext, outcome: str, conversion_value: float = 0.0):
        """Log conversation outcome for learning"""
        
        conversation_record = {
            "timestamp": datetime.now().isoformat(),
            "project_type": context.project_type,
            "phases_completed": context.customer_phase,
            "info_gathered": context.gathered_info,
            "outcome": outcome,  # "converted", "qualified", "lost", "follow_up"
            "conversion_value": conversion_value,
            "conversation_quality": context.conversation_quality_score
        }
        
        # In production, save to database for ML training
        self.learning_metrics["successful_conversions"].append(conversation_record)
        
        # Update question effectiveness scores
        self._update_question_effectiveness(conversation_record)
    
    def _update_question_effectiveness(self, conversation_record: Dict[str, Any]):
        """Update question effectiveness based on outcomes"""
        
        # This would be more sophisticated in production with ML
        outcome = conversation_record["outcome"]
        if outcome in ["converted", "qualified"]:
            # Boost effectiveness of questions that led to positive outcomes
            for info_type in conversation_record["info_gathered"]:
                if info_type not in self.learning_metrics["question_effectiveness"]:
                    self.learning_metrics["question_effectiveness"][info_type] = {"score": 1.0, "count": 0}
                
                current = self.learning_metrics["question_effectiveness"][info_type]
                current["score"] = (current["score"] * current["count"] + 2.0) / (current["count"] + 1)
                current["count"] += 1
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        """Get insights for continuous improvement"""
        
        return {
            "total_conversations": len(self.learning_metrics["successful_conversions"]),
            "conversion_rate": self._calculate_conversion_rate(),
            "most_effective_questions": self._get_top_questions(),
            "optimal_conversation_flow": self._analyze_successful_flows(),
            "improvement_recommendations": self._generate_improvements()
        }
    
    def _calculate_conversion_rate(self) -> float:
        """Calculate overall conversion rate"""
        conversations = self.learning_metrics["successful_conversions"]
        if not conversations:
            return 0.0
        
        converted = sum(1 for conv in conversations if conv["outcome"] == "converted")
        return converted / len(conversations)
    
    def _get_top_questions(self) -> List[str]:
        """Get most effective questions based on learning"""
        effectiveness = self.learning_metrics["question_effectiveness"]
        sorted_questions = sorted(effectiveness.items(), key=lambda x: x[1]["score"], reverse=True)
        return [q[0] for q in sorted_questions[:5]]
    
    def _analyze_successful_flows(self) -> List[str]:
        """Analyze most successful conversation flows"""
        # This would use ML in production
        return self.conversation_patterns["high_conversion_sequences"]
    
    def _generate_improvements(self) -> List[str]:
        """Generate improvement recommendations"""
        insights = []
        
        conversion_rate = self._calculate_conversion_rate()
        if conversion_rate < 0.3:
            insights.append("Consider more qualifying questions early in conversation")
        
        if "phone_number" not in self._get_top_questions():
            insights.append("Prioritize getting contact information earlier")
        
        return insights