# AOS Question Libraries
## Dynamic Question Management and Selection System

### Overview
This document describes the current question library structure in AOSConversationEngine and how questions are organized, prioritized, and selected for optimal AOS performance.

---

## Question Library Architecture

### **Current Structure** (`modules/aos_conversation_engine.py`)

```python
def _initialize_question_library(self) -> Dict[str, Dict[str, List[str]]]:
    return {
        "discovery": {...},
        "qualification": {...},
        "recommendation": {...},
        "closing": {...}
    }
```

---

## Phase-Based Question Organization

### 1. **DISCOVERY PHASE**
**Purpose**: Initial project understanding and rapport building

#### **Kitchen Projects**:
```python
"kitchen": [
    "What's your color scheme? Are your cabinets and countertops already selected?",
    "Do you prefer matte or polished finishes for your kitchen?",
    "Are you thinking warm tones like wood-look or cool tones like stone?",
    "What size kitchen are we working with? This helps with tile size recommendations.",
    "Are you renovating the whole kitchen or just the floor?",
    "Do you have kids or pets? This affects durability needs.",
    "What's your cooking style - lots of prep work or more casual?",
    "Are you considering a matching backsplash to tie everything together?"
]
```

#### **Bathroom Projects**:
```python
"bathroom": [
    "Is this for a master bathroom or guest bath?",
    "Are you looking for floor tile, shower tile, or both?",
    "What's your style preference - modern, traditional, or transitional?",
    "Do you prefer large format tiles or smaller mosaic styles?",
    "What's your color palette for the space?",
    "Are you doing a full renovation or just updating the tile?",
    "Do you want slip-resistant options for safety?"
]
```

#### **General Projects**:
```python
"general": [
    "What room are we tiling?",
    "What's driving this project - renovation, new construction, or repair?",
    "What's your timeline for starting the project?",
    "What's your style preference?",
    "Do you have any specific requirements or concerns?"
]
```

### 2. **QUALIFICATION PHASE**
**Purpose**: Assess budget, timeline, and decision-making process

#### **Timeline Questions**:
```python
"timeline": [
    "When are you planning to start the project?",
    "Is this project scheduled with a contractor or DIY?",
    "Do you need the tile delivered by a specific date?",
    "Are you working around any other renovations?"
]
```

#### **Budget Questions**:
```python
"budget": [
    "What's your budget range for this project?",
    "Are you looking for premium options or value-focused choices?",
    "Does your budget include installation materials?",
    "Are you interested in seeing options at different price points?"
]
```

#### **Decision Making Questions**:
```python
"decision_making": [
    "Who else is involved in this decision?",
    "What's most important to you - style, durability, or price?",
    "Have you looked at tiles elsewhere?",
    "What would make this the perfect solution for you?"
]
```

### 3. **RECOMMENDATION PHASE**
**Purpose**: Present targeted solutions and create emotional connection

#### **Product-Focused Questions**:
```python
"product_focused": [
    "Based on what you've told me, I have some perfect options. Want to see them?",
    "I'm thinking {product_type} would be ideal for your {project_type}. Here's why...",
    "Let me show you three options that fit your {criteria}.",
    "This tile checks all your boxes: {benefits}. What do you think?"
]
```

#### **Solution-Focused Questions**:
```python
"solution_focused": [
    "I can put together a complete package for your {project_type}.",
    "Would you like me to calculate everything you'll need for installation?",
    "I can show you how this will look in your {room_type}.",
    "Let me create a complete project plan for you."
]
```

### 4. **CLOSING PHASE**
**Purpose**: Create urgency and secure commitment

#### **Urgency Creation**:
```python
"urgency": [
    "I can reserve these tiles for you while you finalize your decision.",
    "These are popular - I'd recommend securing your quantity soon.",
    "Would you like me to save this quote with your phone number?",
    "When would you like to move forward with this?"
]
```

#### **Next Steps**:
```python
"next_steps": [
    "What questions can I answer to help you move forward?",
    "Would you like me to connect you with our installation team?",
    "I can have these ready for pickup or delivery. What works better?",
    "Shall we finalize the quantities and get this ordered?"
]
```

---

## Question Selection Logic

### **Primary Selection Algorithm**:
```python
def get_next_questions(self, context: ConversationContext, num_questions: int = 1) -> List[str]:
    # 1. Determine project type
    if not context.project_type:
        return ["What room are we tiling?"]
    
    # 2. Get phase-appropriate questions
    phase_questions = self.question_library.get(context.customer_phase, {})
    project_questions = phase_questions.get(context.project_type, phase_questions.get("general", []))
    
    # 3. Filter already answered questions
    available_questions = [q for q in project_questions if not self._already_answered(q, context.gathered_info)]
    
    # 4. Apply learning-based prioritization
    prioritized_questions = self._prioritize_questions(available_questions, context)
    
    return prioritized_questions[:num_questions]
```

### **Question Filtering** (`_already_answered`):
```python
question_keywords = {
    "color": ["color_scheme", "colors", "color_preferences", "cabinet_info", "countertop_info"],
    "cabinet": ["cabinet_info", "color_scheme_provided", "has_detailed_design_info"],
    "countertop": ["countertop_info", "color_scheme_provided"],
    "size": ["room_size", "square_feet", "dimensions"],
    "style": ["style", "design_preference", "style_preferences"],
    "timeline": ["timeline", "start_date"],
    "budget": ["budget", "price_range"],
    "finish": ["finish", "matte", "polished", "finish_preferences"]
}
```

---

## Question Prioritization System

### **Current Prioritization Logic**:
```python
def _prioritize_questions(self, questions: List[str], context: ConversationContext) -> List[str]:
    priority_scores = {}
    for question in questions:
        score = 1.0
        
        # High priority elements
        if "phone number" in question.lower():
            score += 2.0  # Contact info is critical
        elif "color" in question.lower() or "style" in question.lower():
            score += 1.5  # Visual preferences convert well
        elif "timeline" in question.lower() or "start" in question.lower():
            score += 1.3  # Timeline indicates buying intent
        elif "budget" in question.lower():
            score += 1.2  # Budget helps qualification
        
        priority_scores[question] = score
    
    return sorted(questions, key=lambda q: priority_scores.get(q, 0), reverse=True)
```

### **Priority Ranking**:
1. **Phone Number Collection** (Score: +2.0) - Critical for follow-up
2. **Color/Style Preferences** (Score: +1.5) - High conversion indicators
3. **Timeline Questions** (Score: +1.3) - Buying intent signals
4. **Budget Questions** (Score: +1.2) - Qualification essentials
5. **General Questions** (Score: 1.0) - Standard information gathering

---

## Information Extraction System

### **Pattern Recognition**:
```python
def extract_info_from_response(self, customer_response: str, context: ConversationContext) -> Dict[str, Any]:
    info_patterns = {
        "phone_number": [r"(\d{3}[-.]?\d{3}[-.]?\d{4})", r"(\d{10})"],
        "room_size": [r"(\d+)\s*x\s*(\d+)", r"(\d+)\s*sq\s*ft"],
        "color_preferences": ["white", "gray", "grey", "black", "beige", "brown", "blue", "green", "charcoal", "neutral"],
        "style_preferences": ["modern", "traditional", "rustic", "farmhouse", "contemporary", "transitional"],
        "finish_preferences": ["matte", "polished", "satin", "glossy", "textured"],
        "timeline": ["asap", "this week", "next month", "spring", "summer", "fall", "winter"],
        "cabinet_info": ["cabinet", "cabinets", "upper", "lower", "charcoal", "white"],
        "countertop_info": ["countertop", "countertops", "blue", "white specs", "granite", "quartz"]
    }
```

### **Special Context Recognition**:
```python
# Comprehensive design information detection
if any(word in response_lower for word in ["cabinet", "countertop", "blue", "charcoal", "white"]):
    extracted["color_scheme_provided"] = True
    extracted["has_detailed_design_info"] = True
```

---

## Learning and Effectiveness Tracking

### **Success Pattern Analysis**:
```python
def _load_successful_patterns(self) -> Dict[str, Any]:
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
```

### **Question Effectiveness Metrics**:
```python
learning_metrics = {
    "successful_conversions": [],
    "question_effectiveness": {},
    "customer_response_patterns": {}
}
```

---

## Missing AOS-Required Questions

### **Mandatory Four Questions (Not Implemented)**:

#### **WHAT Questions** (Project Understanding):
- Exact dimensions collection (CRITICAL!)
- Surface specifications
- Complexity assessment
- Style preferences

#### **WHO Questions** (Decision Making & Installation):
- Installation method (DIY/contractor/designer)
- Experience level assessment
- Decision makers identification
- Support requirements

#### **WHEN Questions** (Timeline & Urgency):
- Project start date
- Completion target
- Scheduling constraints
- Urgency assessment

#### **HOW MUCH Questions** (Budget & Investment):
- Budget range establishment
- Value priorities
- Payment timing
- Investment comfort level

---

## Integration with Chat System

### **Tool Call Integration**:
```python
# In SimpleTileAgent.chat()
elif tool_name == "get_aos_questions":
    result = self.get_aos_questions(
        tool_input.get("project_type", ""),
        tool_input.get("customer_phase", "discovery"),
        tool_input.get("gathered_info", "{}"),
        history_text
    )
```

### **Response Integration**:
```python
if result.get("success"):
    questions = result.get("questions", [])
    if questions:
        limited_questions = questions[:2]
        if len(limited_questions) == 1:
            assistant_response += f"\n\n{limited_questions[0]}"
        else:
            assistant_response += f"\n\n{limited_questions[0]} Also, {limited_questions[1].lower()}"
```

---

## Improvements Needed for 4/4 AOS Performance

### **Critical Additions Required**:

1. **Mandatory Question Enforcement**
   - Force collection of WHAT/WHO/WHEN/HOW MUCH
   - Dimension collection requirements
   - Budget establishment

2. **AOS Phase Progression**
   - Structured phase advancement logic
   - Step completion verification
   - Performance scoring integration

3. **Professional Question Templates**
   - Sample conversation language
   - Specific SKU presentation formats
   - Calculation requirement templates

4. **Objection Handling Questions**
   - 4-step process templates
   - Common objection responses
   - Re-engagement strategies

5. **Closing Question Library**
   - Direct close templates
   - Urgency creation language
   - Next step confirmation

The current question library provides a foundation but requires significant enhancement to meet professional AOS standards and achieve consistent 4/4 scoring across all conversation phases.