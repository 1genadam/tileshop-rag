# AOS Learning & Scoring System
## Conversation Effectiveness Measurement and Optimization

### Overview
This document describes the current and planned learning/scoring system for measuring AOS conversation effectiveness, tracking performance metrics, and optimizing conversion rates through data-driven insights.

---

## Current Scoring Implementation

### **Basic Effectiveness Tracking** (`modules/aos_conversation_engine.py`)

```python
class AOSConversationEngine:
    def __init__(self):
        self.learning_metrics = {
            "successful_conversions": [],
            "question_effectiveness": {},
            "customer_response_patterns": {}
        }
```

### **Conversation Quality Scoring**:
```python
@dataclass
class ConversationContext:
    project_type: str = ""
    customer_phase: str = "discovery"
    gathered_info: Dict[str, Any] = None
    phone_number: str = ""
    conversation_quality_score: float = 0.0  # Currently unused
```

---

## Required AOS Scoring Framework (1-4 Scale)

### **AOS Step Scoring Standards**:
- **4 (Great)**: Exceeds expectations, professional execution
- **3 (Good)**: Meets expectations, solid performance  
- **2 (Fair)**: Below expectations, needs improvement
- **1 (Low)**: Poor performance, requires immediate attention

---

## Step-by-Step Scoring Implementation Needed

### 1. **GREETING & CREDIBILITY Scoring (Score: 1-4)**

#### **Scoring Criteria**:
```python
def score_greeting_credibility(self, conversation_data: Dict) -> int:
    score = 1
    elements_present = []
    
    # Check required elements
    if conversation_data.get("customer_name_obtained"):
        elements_present.append("name")
        score += 0.5
    
    if conversation_data.get("credibility_established"):
        elements_present.append("credibility")
        score += 0.5
        
    if conversation_data.get("professional_tone"):
        elements_present.append("professional")
        score += 0.5
        
    if conversation_data.get("process_explained"):
        elements_present.append("process")
        score += 0.5
        
    if conversation_data.get("rapport_building"):
        elements_present.append("rapport")
        score += 0.5
        
    if conversation_data.get("experience_shared"):
        elements_present.append("experience")
        score += 0.5
    
    # Convert to 1-4 scale
    return min(4, max(1, round(score)))
```

#### **Required Tracking Elements**:
- Customer name obtained (Y/N)
- Professional appearance/communication (Y/N)
- Credibility building attempted (Y/N)
- Process explanation provided (Y/N)
- Rapport building evident (Y/N)
- Experience/credentials shared (Y/N)

### 2. **NEEDS ASSESSMENT Scoring (Score: 1-4)**

#### **Mandatory Four Questions Tracking**:
```python
def score_needs_assessment(self, conversation_data: Dict) -> int:
    mandatory_questions = {
        "what_collected": False,  # Project understanding + dimensions
        "who_collected": False,   # Decision makers + installation
        "when_collected": False,  # Timeline + urgency
        "how_much_collected": False  # Budget + investment
    }
    
    # CRITICAL: Dimensions must be collected for any score above 2
    if not conversation_data.get("dimensions_collected"):
        return min(2, base_score)
    
    questions_answered = sum(mandatory_questions.values())
    
    if questions_answered == 4 and conversation_data.get("dimensions_collected"):
        return 4  # Great
    elif questions_answered >= 3:
        return 3  # Good
    elif questions_answered >= 2:
        return 2  # Fair
    else:
        return 1  # Low
```

#### **Dimension Collection Requirements**:
```python
dimension_patterns = {
    "floor_dimensions": r"(\d+)\s*[x×]\s*(\d+)",
    "wall_dimensions": r"(\d+)\s*[x×]\s*(\d+)",
    "square_footage": r"(\d+)\s*sq\s*ft|(\d+)\s*square\s*feet"
}
```

### 3. **DESIGN & DETAILS Scoring (Score: 1-4)**

#### **Product Presentation Requirements**:
```python
def score_design_details(self, conversation_data: Dict) -> int:
    score_elements = {
        "specific_products_presented": 0,  # Must have SKUs
        "features_benefits_explained": 0,
        "tile_bomb_created": 0,  # 2-4 curated options
        "measurements_calculated": 0,
        "emotional_connection": 0,
        "test_closes_used": 0
    }
    
    # Calculate score based on elements present
    total_elements = len(score_elements)
    elements_present = sum(score_elements.values())
    
    percentage = elements_present / total_elements
    
    if percentage >= 0.9:
        return 4  # Great (90%+ elements)
    elif percentage >= 0.7:
        return 3  # Good (70-89% elements)
    elif percentage >= 0.5:
        return 2  # Fair (50-69% elements)
    else:
        return 1  # Low (<50% elements)
```

### 4. **THE CLOSE Scoring (Score: 1-4)**

#### **Close Attempt Tracking**:
```python
def score_close_attempt(self, conversation_data: Dict) -> int:
    close_elements = {
        "direct_ask_for_business": False,
        "buying_signals_recognized": False,
        "urgency_created": False,
        "value_summarized": False,
        "next_steps_defined": False
    }
    
    # Must have direct ask for any score above 1
    if not close_elements["direct_ask_for_business"]:
        return 1
    
    elements_present = sum(close_elements.values())
    
    if elements_present >= 4:
        return 4  # Great
    elif elements_present >= 3:
        return 3  # Good
    elif elements_present >= 2:
        return 2  # Fair
    else:
        return 1  # Low
```

### 5. **OBJECTION HANDLING Scoring (Score: 1-4)**

#### **4-Step Process Tracking**:
```python
def score_objection_handling(self, conversation_data: Dict) -> int:
    if not conversation_data.get("objection_encountered"):
        return None  # N/A if no objections
    
    four_step_process = {
        "clarify_step": False,      # 1. Understand objection
        "empathize_step": False,    # 2. Acknowledge concern
        "solution_step": False,     # 3. Provide new information
        "re_ask_step": False        # 4. Request business again
    }
    
    steps_completed = sum(four_step_process.values())
    
    if steps_completed == 4:
        return 4  # Perfect execution
    elif steps_completed == 3:
        return 3  # Good process
    elif steps_completed == 2:
        return 2  # Basic handling
    else:
        return 1  # Poor handling
```

---

## Learning System Architecture

### **Conversation Outcome Logging**:
```python
def log_conversation_outcome(self, context: ConversationContext, outcome: str, conversion_value: float = 0.0):
    conversation_record = {
        "timestamp": datetime.now().isoformat(),
        "project_type": context.project_type,
        "phases_completed": context.customer_phase,
        "info_gathered": context.gathered_info,
        "outcome": outcome,  # "converted", "qualified", "lost", "follow_up"
        "conversion_value": conversion_value,
        "aos_scores": {
            "greeting_credibility": 0,
            "needs_assessment": 0,
            "design_details": 0,
            "close": 0,
            "objection_handling": 0,
            "overall": 0
        }
    }
```

### **Question Effectiveness Tracking**:
```python
def _update_question_effectiveness(self, conversation_record: Dict[str, Any]):
    outcome = conversation_record["outcome"]
    if outcome in ["converted", "qualified"]:
        # Boost effectiveness of questions that led to positive outcomes
        for info_type in conversation_record["info_gathered"]:
            if info_type not in self.learning_metrics["question_effectiveness"]:
                self.learning_metrics["question_effectiveness"][info_type] = {
                    "score": 1.0, 
                    "count": 0
                }
            
            current = self.learning_metrics["question_effectiveness"][info_type]
            current["score"] = (current["score"] * current["count"] + 2.0) / (current["count"] + 1)
            current["count"] += 1
```

---

## Performance Analytics

### **Conversion Rate Calculation**:
```python
def _calculate_conversion_rate(self) -> float:
    conversations = self.learning_metrics["successful_conversions"]
    if not conversations:
        return 0.0
    
    converted = sum(1 for conv in conversations if conv["outcome"] == "converted")
    return converted / len(conversations)
```

### **AOS Step Completion Analysis**:
```python
def analyze_step_completion_rates(self) -> Dict[str, float]:
    conversations = self.learning_metrics["successful_conversions"]
    
    step_completion = {
        "greeting_credibility": 0,
        "needs_assessment": 0,
        "design_details": 0,
        "close": 0,
        "objection_handling": 0
    }
    
    for conv in conversations:
        aos_scores = conv.get("aos_scores", {})
        for step, score in aos_scores.items():
            if score >= 3:  # Good or Great performance
                step_completion[step] += 1
    
    total_conversations = len(conversations)
    return {step: count/total_conversations for step, count in step_completion.items()}
```

### **Critical Success Metrics**:
```python
def get_critical_metrics(self) -> Dict[str, float]:
    return {
        "dimensions_collection_rate": self._calculate_dimensions_rate(),
        "budget_establishment_rate": self._calculate_budget_rate(),
        "specific_products_presentation_rate": self._calculate_products_rate(),
        "close_attempt_rate": self._calculate_close_rate(),
        "follow_up_scheduling_rate": self._calculate_followup_rate(),
        "overall_conversion_rate": self._calculate_conversion_rate()
    }
```

---

## Real-Time Scoring Integration

### **Live Conversation Scoring**:
```python
def calculate_live_score(self, conversation_history: List[Dict], current_phase: str) -> Dict[str, int]:
    """Calculate real-time AOS scores during conversation"""
    
    # Extract conversation data
    conversation_data = self._extract_scoring_data(conversation_history)
    
    # Calculate phase-specific scores
    scores = {}
    
    if current_phase in ["greeting", "credibility"]:
        scores["greeting_credibility"] = self.score_greeting_credibility(conversation_data)
    
    if current_phase in ["needs_assessment", "qualification"]:
        scores["needs_assessment"] = self.score_needs_assessment(conversation_data)
    
    if current_phase in ["design", "recommendation"]:
        scores["design_details"] = self.score_design_details(conversation_data)
    
    if current_phase in ["close", "closing"]:
        scores["close"] = self.score_close_attempt(conversation_data)
    
    # Calculate overall score
    completed_scores = [score for score in scores.values() if score > 0]
    scores["overall"] = sum(completed_scores) / len(completed_scores) if completed_scores else 0
    
    return scores
```

### **Red Flag Detection**:
```python
def detect_red_flags(self, conversation_data: Dict) -> List[str]:
    red_flags = []
    
    if not conversation_data.get("customer_name_obtained"):
        red_flags.append("No customer name collected")
    
    if not conversation_data.get("dimensions_collected"):
        red_flags.append("No dimensions obtained")
    
    if not conversation_data.get("specific_products_presented"):
        red_flags.append("No specific products presented")
    
    if not conversation_data.get("calculations_performed"):
        red_flags.append("No calculations performed")
    
    if not conversation_data.get("close_attempted"):
        red_flags.append("No close attempted")
    
    if not conversation_data.get("next_steps_defined"):
        red_flags.append("Customer left without next steps")
    
    return red_flags
```

---

## Database Schema for Scoring Storage

### **Conversation Scoring Table**:
```sql
CREATE TABLE aos_conversation_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id VARCHAR(255) UNIQUE,
    customer_phone VARCHAR(20),
    project_type VARCHAR(50),
    
    -- AOS Step Scores (1-4)
    greeting_credibility_score INT CHECK (greeting_credibility_score BETWEEN 1 AND 4),
    needs_assessment_score INT CHECK (needs_assessment_score BETWEEN 1 AND 4),
    design_details_score INT CHECK (design_details_score BETWEEN 1 AND 4),
    close_score INT CHECK (close_score BETWEEN 1 AND 4),
    objection_handling_score INT CHECK (objection_handling_score BETWEEN 1 AND 4),
    follow_up_score INT CHECK (follow_up_score BETWEEN 1 AND 4),
    
    -- Overall Performance
    overall_score DECIMAL(3,2),
    
    -- Critical Requirements Met
    customer_name_collected BOOLEAN DEFAULT FALSE,
    dimensions_collected BOOLEAN DEFAULT FALSE,
    budget_established BOOLEAN DEFAULT FALSE,
    specific_products_presented BOOLEAN DEFAULT FALSE,
    calculations_performed BOOLEAN DEFAULT FALSE,
    close_attempted BOOLEAN DEFAULT FALSE,
    
    -- Outcome Tracking
    outcome ENUM('converted', 'qualified', 'lost', 'follow_up') DEFAULT 'follow_up',
    conversion_value DECIMAL(10,2) DEFAULT 0.00,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## Implementation Status

### **✅ Currently Implemented**:
- Basic question effectiveness tracking
- Simple conversation outcome logging
- Heuristic question prioritization

### **❌ Missing Critical Components**:
- Real-time AOS step scoring (1-4 scale)
- Mandatory requirement enforcement
- Red flag detection system
- Performance analytics dashboard
- Database storage for scores
- ML-based question optimization

---

## Next Steps for Full Scoring Implementation

1. **Implement Real-Time Scoring System**
   - Add live AOS step scoring during conversations
   - Create scoring criteria for each step
   - Integrate with conversation flow

2. **Add Database Persistence**
   - Create conversation scoring tables
   - Store real-time scores and outcomes
   - Enable historical analysis

3. **Build Analytics Dashboard**
   - Performance metrics visualization
   - Conversion rate tracking
   - Step completion analysis

4. **Create Automated Coaching**
   - Real-time feedback during conversations
   - Red flag alerts for supervisors
   - Improvement recommendations

5. **Implement ML Optimization**
   - Question effectiveness learning
   - Conversation pattern recognition
   - Predictive conversion scoring

This scoring system will enable consistent 4/4 AOS performance measurement and continuous improvement through data-driven insights.