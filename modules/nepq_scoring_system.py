"""
NEPQ Scoring System for AI Agent Performance Analysis
Provides comprehensive scoring and self-analysis capabilities
"""

import json
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re

@dataclass
class NEPQScore:
    """Individual NEPQ stage score"""
    stage: str
    score: int  # 0-10 scale
    max_score: int = 10
    evidence: List[str] = None
    improvement_notes: str = ""
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []

@dataclass
class ConversationAnalysis:
    """Complete conversation analysis and scoring"""
    conversation_id: str
    timestamp: datetime.datetime
    customer_phone: str
    customer_name: str
    agent_mode: str  # customer, salesperson, contractor
    
    # NEPQ Stage Scores (7 stages)
    connection_score: NEPQScore
    problem_awareness_score: NEPQScore
    consequence_discovery_score: NEPQScore
    solution_awareness_score: NEPQScore
    qualifying_questions_score: NEPQScore
    objection_handling_score: NEPQScore
    commitment_stage_score: NEPQScore
    
    # Overall Metrics
    overall_score: float = 0.0
    conversation_length: int = 0
    questions_asked: int = 0
    objections_encountered: int = 0
    objections_resolved: int = 0
    
    # Analysis Results
    strengths: List[str] = None
    weaknesses: List[str] = None
    improvement_suggestions: List[str] = None
    next_conversation_focus: List[str] = None
    
    def __post_init__(self):
        if self.strengths is None:
            self.strengths = []
        if self.weaknesses is None:
            self.weaknesses = []
        if self.improvement_suggestions is None:
            self.improvement_suggestions = []
        if self.next_conversation_focus is None:
            self.next_conversation_focus = []

class NEPQScoringSystem:
    """NEPQ Performance Scoring and Analysis System"""
    
    def __init__(self):
        self.scoring_criteria = self._initialize_scoring_criteria()
        self.objection_patterns = self._initialize_objection_patterns()
        
    def _initialize_scoring_criteria(self) -> Dict[str, Dict]:
        """Initialize scoring criteria for each NEPQ stage"""
        return {
            "connection": {
                "max_score": 10,
                "criteria": {
                    "disarm_curiosity": {
                        "weight": 0.4,
                        "indicators": [
                            "lowered prospect's guard",
                            "created curiosity/interest",
                            "avoided sales pressure"
                        ]
                    },
                    "focus_shift": {
                        "weight": 0.3,
                        "indicators": [
                            "moved focus to prospect",
                            "asked about their situation",
                            "listened actively"
                        ]
                    },
                    "tone_positioning": {
                        "weight": 0.3,
                        "indicators": [
                            "neutral helpful tone",
                            "expert positioning",
                            "detached from outcome"
                        ]
                    }
                }
            },
            "problem_awareness": {
                "max_score": 10,
                "criteria": {
                    "current_state_challenge": {
                        "weight": 0.4,
                        "indicators": [
                            "uncovered dissatisfaction",
                            "identified current problems",
                            "explored pain points"
                        ]
                    },
                    "emotional_engagement": {
                        "weight": 0.3,
                        "indicators": [
                            "used 'feel' vs 'think'",
                            "engaged emotions",
                            "created internal tension"
                        ]
                    },
                    "gap_creation": {
                        "weight": 0.3,
                        "indicators": [
                            "identified current vs desired",
                            "highlighted shortcomings",
                            "created dissatisfaction"
                        ]
                    }
                }
            },
            "consequence_discovery": {
                "max_score": 10,
                "criteria": {
                    "cost_of_inaction": {
                        "weight": 0.4,
                        "indicators": [
                            "explored consequences",
                            "identified costs of delay",
                            "built urgency"
                        ]
                    },
                    "urgency_building": {
                        "weight": 0.3,
                        "indicators": [
                            "created internal pressure",
                            "highlighted risks",
                            "emphasized timeline"
                        ]
                    },
                    "timeline_pressure": {
                        "weight": 0.3,
                        "indicators": [
                            "established timeframes",
                            "created deadline pressure",
                            "emphasized deterioration"
                        ]
                    }
                }
            },
            "solution_awareness": {
                "max_score": 10,
                "criteria": {
                    "ideal_criteria": {
                        "weight": 0.4,
                        "indicators": [
                            "defined perfect solution",
                            "established criteria",
                            "clarified requirements"
                        ]
                    },
                    "future_state_visualization": {
                        "weight": 0.3,
                        "indicators": [
                            "painted desired outcome",
                            "visualized success",
                            "created aspiration"
                        ]
                    },
                    "buying_criteria": {
                        "weight": 0.3,
                        "indicators": [
                            "identified decision factors",
                            "clarified priorities",
                            "understood preferences"
                        ]
                    }
                }
            },
            "qualifying_questions": {
                "max_score": 10,
                "criteria": {
                    "importance_confirmation": {
                        "weight": 0.4,
                        "indicators": [
                            "validated priority",
                            "confirmed importance",
                            "established significance"
                        ]
                    },
                    "readiness_assessment": {
                        "weight": 0.3,
                        "indicators": [
                            "confirmed willingness",
                            "assessed readiness",
                            "validated commitment"
                        ]
                    },
                    "authority_verification": {
                        "weight": 0.3,
                        "indicators": [
                            "identified decision maker",
                            "understood process",
                            "confirmed authority"
                        ]
                    }
                }
            },
            "objection_handling": {
                "max_score": 10,
                "criteria": {
                    "three_step_formula": {
                        "weight": 0.4,
                        "indicators": [
                            "clarified objection",
                            "discussed concern",
                            "diffused resistance"
                        ]
                    },
                    "emotional_positioning": {
                        "weight": 0.3,
                        "indicators": [
                            "maintained helper stance",
                            "avoided defensiveness",
                            "stayed detached"
                        ]
                    },
                    "self_persuasion": {
                        "weight": 0.3,
                        "indicators": [
                            "got prospect to self-persuade",
                            "used questions not statements",
                            "created internal resolution"
                        ]
                    }
                }
            },
            "commitment_stage": {
                "max_score": 10,
                "criteria": {
                    "next_steps": {
                        "weight": 0.4,
                        "indicators": [
                            "established clear path",
                            "defined next actions",
                            "created momentum"
                        ]
                    },
                    "specific_actions": {
                        "weight": 0.3,
                        "indicators": [
                            "got concrete commitments",
                            "specified deliverables",
                            "defined responsibilities"
                        ]
                    },
                    "follow_up": {
                        "weight": 0.3,
                        "indicators": [
                            "scheduled next interaction",
                            "set specific date/time",
                            "confirmed availability"
                        ]
                    }
                }
            }
        }
    
    def _initialize_objection_patterns(self) -> Dict[str, List[str]]:
        """Initialize common objection patterns for detection"""
        return {
            "price_money": [
                "too expensive", "can't afford", "no budget", "costs too much",
                "price is high", "money is tight", "financial constraints"
            ],
            "timing_delay": [
                "think it over", "need time", "not ready", "too soon",
                "get back to you", "need to wait", "timing isn't right"
            ],
            "authority_approval": [
                "talk to spouse", "check with partner", "need approval",
                "talk to board", "consult with", "need permission"
            ],
            "information_comparison": [
                "send information", "get quotes", "compare prices",
                "need references", "see other options", "research more"
            ],
            "trust_skepticism": [
                "too good to be true", "doesn't work", "tried before",
                "negative reviews", "sounds suspicious", "not sure"
            ],
            "need_interest": [
                "don't need", "not interested", "doing fine",
                "no problems", "satisfied", "not necessary"
            ]
        }
    
    def analyze_conversation(self, conversation_history: List[Dict], 
                           customer_info: Dict) -> ConversationAnalysis:
        """Analyze complete conversation and generate NEPQ scores"""
        
        # Extract conversation metadata
        conversation_id = f"{customer_info.get('phone', 'unknown')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.datetime.now()
        
        # Analyze conversation content
        analysis_data = self._analyze_conversation_content(conversation_history)
        
        # Score each NEPQ stage
        scores = self._score_nepq_stages(conversation_history, analysis_data)
        
        # Generate overall analysis
        overall_analysis = self._generate_overall_analysis(scores, analysis_data)
        
        # Create conversation analysis object
        analysis = ConversationAnalysis(
            conversation_id=conversation_id,
            timestamp=timestamp,
            customer_phone=customer_info.get('phone', 'unknown'),
            customer_name=customer_info.get('name', 'unknown'),
            agent_mode=customer_info.get('mode', 'customer'),
            
            # NEPQ Stage Scores
            connection_score=scores['connection'],
            problem_awareness_score=scores['problem_awareness'],
            consequence_discovery_score=scores['consequence_discovery'],
            solution_awareness_score=scores['solution_awareness'],
            qualifying_questions_score=scores['qualifying_questions'],
            objection_handling_score=scores['objection_handling'],
            commitment_stage_score=scores['commitment_stage'],
            
            # Overall Metrics
            overall_score=overall_analysis['overall_score'],
            conversation_length=len(conversation_history),
            questions_asked=analysis_data['questions_asked'],
            objections_encountered=analysis_data['objections_encountered'],
            objections_resolved=analysis_data['objections_resolved'],
            
            # Analysis Results
            strengths=overall_analysis['strengths'],
            weaknesses=overall_analysis['weaknesses'],
            improvement_suggestions=overall_analysis['improvement_suggestions'],
            next_conversation_focus=overall_analysis['next_conversation_focus']
        )
        
        return analysis
    
    def _analyze_conversation_content(self, conversation_history: List[Dict]) -> Dict:
        """Analyze conversation content for patterns and metrics"""
        analysis = {
            'questions_asked': 0,
            'objections_encountered': 0,
            'objections_resolved': 0,
            'emotional_language_used': 0,
            'consequence_questions': 0,
            'commitment_attempts': 0,
            'objection_types': [],
            'key_phrases': [],
            'stage_progression': []
        }
        
        for message in conversation_history:
            if message.get('role') == 'assistant':
                content = message.get('content', '').lower()
                
                # Count questions
                analysis['questions_asked'] += content.count('?')
                
                # Detect emotional language
                emotional_words = ['feel', 'emotion', 'frustrated', 'concerned', 'worried']
                for word in emotional_words:
                    if word in content:
                        analysis['emotional_language_used'] += 1
                
                # Detect consequence questions
                consequence_patterns = [
                    'what happens if', 'what would happen', 'consequences',
                    'if you don\'t', 'if nothing changes'
                ]
                for pattern in consequence_patterns:
                    if pattern in content:
                        analysis['consequence_questions'] += 1
                
                # Detect commitment attempts
                commitment_patterns = [
                    'next step', 'move forward', 'get started',
                    'schedule', 'when would you', 'ready to'
                ]
                for pattern in commitment_patterns:
                    if pattern in content:
                        analysis['commitment_attempts'] += 1
            
            elif message.get('role') == 'user':
                content = message.get('content', '').lower()
                
                # Detect objections
                objection_found = False
                for objection_type, patterns in self.objection_patterns.items():
                    for pattern in patterns:
                        if pattern in content:
                            analysis['objections_encountered'] += 1
                            analysis['objection_types'].append(objection_type)
                            objection_found = True
                            break
                    if objection_found:
                        break
        
        return analysis
    
    def _score_nepq_stages(self, conversation_history: List[Dict], 
                          analysis_data: Dict) -> Dict[str, NEPQScore]:
        """Score each NEPQ stage based on conversation analysis"""
        scores = {}
        
        for stage_name, criteria in self.scoring_criteria.items():
            evidence = []
            total_score = 0
            
            # Analyze conversation for stage-specific indicators
            for message in conversation_history:
                if message.get('role') == 'assistant':
                    content = message.get('content', '').lower()
                    
                    # Check each criterion for this stage
                    for criterion_name, criterion_data in criteria['criteria'].items():
                        for indicator in criterion_data['indicators']:
                            if any(keyword in content for keyword in indicator.split()):
                                evidence.append(f"Found: {indicator}")
                                total_score += criterion_data['weight'] * criteria['max_score']
            
            # Cap score at max_score
            final_score = min(total_score, criteria['max_score'])
            
            # Create improvement notes
            improvement_notes = self._generate_stage_improvement_notes(
                stage_name, final_score, criteria['max_score'], evidence
            )
            
            scores[stage_name] = NEPQScore(
                stage=stage_name,
                score=int(final_score),
                max_score=criteria['max_score'],
                evidence=evidence,
                improvement_notes=improvement_notes
            )
        
        return scores
    
    def _generate_stage_improvement_notes(self, stage_name: str, score: float, 
                                        max_score: int, evidence: List[str]) -> str:
        """Generate improvement notes for a specific stage"""
        if score >= max_score * 0.8:
            return f"Excellent performance in {stage_name}. Continue current approach."
        elif score >= max_score * 0.6:
            return f"Good performance in {stage_name}. Focus on consistency."
        elif score >= max_score * 0.4:
            return f"Moderate performance in {stage_name}. Needs improvement in key areas."
        else:
            return f"Poor performance in {stage_name}. Requires significant focus and practice."
    
    def _generate_overall_analysis(self, scores: Dict[str, NEPQScore], 
                                 analysis_data: Dict) -> Dict:
        """Generate overall conversation analysis and recommendations"""
        
        # Calculate overall score
        total_score = sum(score.score for score in scores.values())
        max_possible = sum(score.max_score for score in scores.values())
        overall_score = (total_score / max_possible) * 100
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        improvement_suggestions = []
        next_conversation_focus = []
        
        for stage_name, score in scores.items():
            percentage = (score.score / score.max_score) * 100
            
            if percentage >= 80:
                strengths.append(f"Strong {stage_name} execution ({percentage:.1f}%)")
            elif percentage < 50:
                weaknesses.append(f"Weak {stage_name} execution ({percentage:.1f}%)")
                improvement_suggestions.append(f"Focus on improving {stage_name} techniques")
                next_conversation_focus.append(stage_name)
        
        # Add specific recommendations based on analysis
        if analysis_data['questions_asked'] < 5:
            improvement_suggestions.append("Ask more questions to engage prospects")
        
        if analysis_data['emotional_language_used'] < 2:
            improvement_suggestions.append("Use more emotional language (feel vs think)")
        
        if analysis_data['consequence_questions'] < 1:
            improvement_suggestions.append("Include more consequence questions for urgency")
        
        if analysis_data['objections_encountered'] > analysis_data['objections_resolved']:
            improvement_suggestions.append("Improve objection handling using 3-step formula")
        
        return {
            'overall_score': overall_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improvement_suggestions': improvement_suggestions,
            'next_conversation_focus': next_conversation_focus
        }
    
    def generate_report(self, analysis: ConversationAnalysis) -> str:
        """Generate detailed performance report"""
        report = f"""
# NEPQ Performance Analysis Report

**Conversation ID:** {analysis.conversation_id}
**Date:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Customer:** {analysis.customer_name} ({analysis.customer_phone})
**Agent Mode:** {analysis.agent_mode.title()}

## Overall Performance Score: {analysis.overall_score:.1f}/100

### NEPQ Stage Breakdown:
1. **Connection Stage:** {analysis.connection_score.score}/{analysis.connection_score.max_score}
2. **Problem Awareness:** {analysis.problem_awareness_score.score}/{analysis.problem_awareness_score.max_score}
3. **Consequence Discovery:** {analysis.consequence_discovery_score.score}/{analysis.consequence_discovery_score.max_score}
4. **Solution Awareness:** {analysis.solution_awareness_score.score}/{analysis.solution_awareness_score.max_score}
5. **Qualifying Questions:** {analysis.qualifying_questions_score.score}/{analysis.qualifying_questions_score.max_score}
6. **Objection Handling:** {analysis.objection_handling_score.score}/{analysis.objection_handling_score.max_score}
7. **Commitment Stage:** {analysis.commitment_stage_score.score}/{analysis.commitment_stage_score.max_score}

### Conversation Metrics:
- **Total Messages:** {analysis.conversation_length}
- **Questions Asked:** {analysis.questions_asked}
- **Objections Encountered:** {analysis.objections_encountered}
- **Objections Resolved:** {analysis.objections_resolved}

### Performance Analysis:

**Strengths:**
{chr(10).join(f"• {strength}" for strength in analysis.strengths)}

**Areas for Improvement:**
{chr(10).join(f"• {weakness}" for weakness in analysis.weaknesses)}

**Specific Recommendations:**
{chr(10).join(f"• {suggestion}" for suggestion in analysis.improvement_suggestions)}

**Next Conversation Focus:**
{chr(10).join(f"• {focus}" for focus in analysis.next_conversation_focus)}

### Stage-Specific Analysis:

**Connection Stage Notes:**
{analysis.connection_score.improvement_notes}

**Problem Awareness Notes:**
{analysis.problem_awareness_score.improvement_notes}

**Consequence Discovery Notes:**
{analysis.consequence_discovery_score.improvement_notes}

**Solution Awareness Notes:**
{analysis.solution_awareness_score.improvement_notes}

**Qualifying Questions Notes:**
{analysis.qualifying_questions_score.improvement_notes}

**Objection Handling Notes:**
{analysis.objection_handling_score.improvement_notes}

**Commitment Stage Notes:**
{analysis.commitment_stage_score.improvement_notes}

---
*Generated by NEPQ Scoring System v1.0*
"""
        return report
    
    def save_analysis(self, analysis: ConversationAnalysis, file_path: str = None):
        """Save analysis to JSON file"""
        if file_path is None:
            file_path = f"nepq_analysis_{analysis.conversation_id}.json"
        
        # Convert to dictionary for JSON serialization
        analysis_dict = asdict(analysis)
        
        # Handle datetime serialization
        analysis_dict['timestamp'] = analysis.timestamp.isoformat()
        
        with open(file_path, 'w') as f:
            json.dump(analysis_dict, f, indent=2)
        
        return file_path
    
    def load_analysis(self, file_path: str) -> ConversationAnalysis:
        """Load analysis from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Convert timestamp back to datetime
        data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
        
        # Reconstruct NEPQScore objects
        for score_key in ['connection_score', 'problem_awareness_score', 
                         'consequence_discovery_score', 'solution_awareness_score',
                         'qualifying_questions_score', 'objection_handling_score',
                         'commitment_stage_score']:
            if score_key in data:
                data[score_key] = NEPQScore(**data[score_key])
        
        return ConversationAnalysis(**data)