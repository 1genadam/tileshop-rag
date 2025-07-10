# AOS Integration Guide
## How AOS Works with the Chat System Architecture

### Overview
This document explains how the AOS (Approach of Sale) methodology integrates with our chat system architecture, including tool calling sequences, database integration, real-time scoring, and troubleshooting guidance.

---

## System Architecture Integration

### **High-Level Flow**:
```
User Input → Chat Interface → SimpleTileAgent → AOS Engine → Tools → Database → Response
```

### **Detailed Architecture**:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Chat Frontend │────│   Flask API      │────│ SimpleTileAgent │
│   (chat.js)     │    │ (/api/chat/simple│    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────┐              │
                       │   Claude LLM    │◄─────────────┘
                       │   + System      │
                       │   Prompt        │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Tool Calling  │
                       │   System        │
                       └─────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼──────┐    ┌───────────▼────┐    ┌─────────────▼───┐
│ AOS Engine   │    │ RAG Manager    │    │ Database        │
│ (Questions)  │    │ (Products)     │    │ (Customers)     │
└──────────────┘    └────────────────┘    └─────────────────┘
```

---

## Tool Calling Sequence and Flow

### **AOS-Compliant Tool Sequence**:

#### **1. Initial Contact** (Greeting & Credibility):
```
User: "hi i'm looking for kitchen floor tile"

Tool Sequence:
1. get_aos_questions(project_type="kitchen", phase="discovery")
2. Response: Phone number request + credibility building
```

#### **2. Information Gathering** (Needs Assessment):
```
User: "my phone number is 847-302-2594"

Tool Sequence:
1. lookup_customer(phone_number="847-302-2594")
2. get_aos_questions(project_type="kitchen", phase="discovery", gathered_info="{phone_number: '847-302-2594'}")
3. Response: WHAT/WHO/WHEN/HOW MUCH questions
```

#### **3. Design Consultation** (Design & Details):
```
User: "the kitchen is 10x12, budget around $1500"

Tool Sequence:
1. get_aos_questions(phase="recommendation", gathered_info="{dimensions: '10x12', budget: '$1500'}")
2. search_products(query="kitchen floor tile 10x12 budget 1500")
3. Response: Tile bomb presentation with SKUs
```

#### **4. Project Calculation** (Professional Calculations):
```
Tool Sequence:
1. calculate_project_requirements(dimensions="10x12", tile_sku="ABC123")
2. get_installation_accessories(product_type="porcelain floor tile")
3. Response: Complete project cost breakdown
```

#### **5. Closing Attempt** (The Close):
```
Tool Sequence:
1. save_customer_project(phone_number="847-302-2594", project_info="kitchen 10x12 porcelain $1500")
2. Response: Direct close with urgency and next steps
```

---

## Database Integration Patterns

### **Customer Data Flow**:
```python
# 1. Customer Lookup/Creation
def handle_customer_data(phone_number: str):
    customer = self.db.get_or_create_customer(phone_number)
    purchases = self.db.get_customer_purchases(customer['customer_id'])
    return {"customer": customer, "purchases": purchases}
```

### **Conversation Persistence**:
```python
# 2. Save Conversation Progress
def save_conversation_state(phone_number: str, aos_data: Dict):
    conversation_record = {
        "customer_phone": phone_number,
        "project_type": aos_data.get("project_type"),
        "gathered_info": aos_data.get("gathered_info"),
        "current_phase": aos_data.get("current_phase"),
        "aos_scores": aos_data.get("scores", {}),
        "timestamp": datetime.now()
    }
    # Save to aos_conversation_tracking table
```

### **Product and Inventory Integration**:
```python
# 3. Product Search and Availability
def search_products_with_availability(query: str, location: str = None):
    products = self.rag.enhanced_chat(query, "product_search")
    # Add inventory checks
    # Add pricing calculations
    # Add delivery timing
    return enhanced_product_data
```

---

## Real-Time Scoring Integration

### **Live Scoring During Conversation**:
```python
class SimpleTileAgent:
    def chat(self, message: str, conversation_history: List[Dict] = None, phone_number: str = None):
        # Process conversation
        response = self.client.messages.create(...)
        
        # Calculate real-time AOS scores
        current_scores = self.calculate_aos_scores(conversation_history, message)
        
        # Check for red flags
        red_flags = self.detect_conversation_issues(current_scores)
        
        # Update database with scores
        self.update_conversation_scores(phone_number, current_scores)
        
        return {
            "success": True,
            "response": response_text,
            "aos_scores": current_scores,
            "red_flags": red_flags,
            "next_phase": recommended_next_phase
        }
```

### **Score Calculation Integration**:
```python
def calculate_aos_scores(self, conversation_history: List[Dict], current_message: str) -> Dict[str, int]:
    # Extract conversation data
    conversation_data = self.extract_scoring_data(conversation_history + [{"role": "user", "content": current_message}])
    
    # Calculate step scores
    scores = {}
    
    # Greeting & Credibility (Step 1)
    if conversation_data.get("customer_name_obtained"):
        scores["greeting_credibility"] = self.score_greeting_credibility(conversation_data)
    
    # Needs Assessment (Step 2)
    if conversation_data.get("project_questions_asked"):
        scores["needs_assessment"] = self.score_needs_assessment(conversation_data)
    
    # Design & Details (Step 3)
    if conversation_data.get("products_discussed"):
        scores["design_details"] = self.score_design_details(conversation_data)
    
    # Calculate overall performance
    completed_scores = [score for score in scores.values() if score > 0]
    scores["overall"] = sum(completed_scores) / len(completed_scores) if completed_scores else 0
    
    return scores
```

---

## System Prompt Integration

### **AOS-Enhanced System Prompt Structure**:
```python
self.system_prompt = f"""You are Alex, a professional tile specialist at The Tile Shop.

MANDATORY AOS PROTOCOL:
{self.load_aos_requirements()}

CURRENT CONVERSATION CONTEXT:
- Customer: {customer_name or 'Unknown'}
- Project: {project_type or 'Not specified'}
- Phase: {current_phase}
- Completed Steps: {completed_steps}
- Missing Requirements: {missing_requirements}

NEXT REQUIRED ACTION:
{self.determine_next_aos_action(current_phase, completed_steps)}

AVAILABLE TOOLS:
{self.format_tool_descriptions()}
"""
```

### **Dynamic Context Updates**:
```python
def update_conversation_context(self, conversation_data: Dict) -> str:
    context_updates = []
    
    if not conversation_data.get("customer_name"):
        context_updates.append("CRITICAL: Must obtain customer name immediately")
    
    if not conversation_data.get("dimensions_collected"):
        context_updates.append("CRITICAL: Must collect exact dimensions before product search")
    
    if not conversation_data.get("budget_established"):
        context_updates.append("Required: Establish budget range before recommendations")
    
    return "\n".join(context_updates)
```

---

## Error Handling and Recovery

### **AOS Compliance Checking**:
```python
def validate_aos_compliance(self, conversation_data: Dict, intended_action: str) -> Dict[str, Any]:
    compliance_issues = []
    
    # Check mandatory requirements
    if intended_action == "search_products" and not conversation_data.get("dimensions_collected"):
        compliance_issues.append({
            "type": "BLOCKING_ERROR",
            "message": "Cannot search products without dimensions",
            "required_action": "collect_dimensions_first"
        })
    
    if intended_action == "present_recommendations" and not conversation_data.get("budget_established"):
        compliance_issues.append({
            "type": "WARNING",
            "message": "Recommendations without budget may not align with customer expectations",
            "suggested_action": "establish_budget_first"
        })
    
    return {
        "compliant": len(compliance_issues) == 0,
        "issues": compliance_issues,
        "can_proceed": not any(issue["type"] == "BLOCKING_ERROR" for issue in compliance_issues)
    }
```

### **Conversation Recovery**:
```python
def recover_conversation_flow(self, missing_requirements: List[str]) -> str:
    recovery_actions = {
        "customer_name": "I don't believe I caught your name. May I have your name?",
        "dimensions": "To give you accurate recommendations, I need the exact dimensions. What are the length and width?",
        "budget": "What budget range are you working with for this project?",
        "timeline": "When are you hoping to start this project?",
        "close_attempt": "Based on everything we've discussed, should we move forward with this?"
    }
    
    priority_order = ["customer_name", "dimensions", "budget", "timeline", "close_attempt"]
    
    for requirement in priority_order:
        if requirement in missing_requirements:
            return recovery_actions[requirement]
    
    return "Let me make sure I have everything I need to help you..."
```

---

## Performance Monitoring

### **Real-Time Alerts**:
```python
def monitor_conversation_performance(self, aos_scores: Dict[str, int]) -> List[str]:
    alerts = []
    
    # Performance thresholds
    if aos_scores.get("overall", 0) < 2.0:
        alerts.append("PERFORMANCE_ALERT: Conversation quality below acceptable threshold")
    
    if aos_scores.get("needs_assessment", 0) < 3 and "dimensions" not in self.conversation_data:
        alerts.append("CRITICAL_ALERT: Dimensions not collected in needs assessment phase")
    
    if aos_scores.get("design_details", 0) < 2:
        alerts.append("COACHING_ALERT: Product presentation needs improvement")
    
    return alerts
```

### **Conversion Prediction**:
```python
def predict_conversion_likelihood(self, conversation_data: Dict) -> float:
    factors = {
        "phone_number_collected": 0.3,
        "dimensions_collected": 0.25,
        "budget_established": 0.2,
        "specific_products_discussed": 0.15,
        "timeline_confirmed": 0.1
    }
    
    likelihood = 0.0
    for factor, weight in factors.items():
        if conversation_data.get(factor):
            likelihood += weight
    
    return min(1.0, likelihood)
```

---

## API Response Format

### **Enhanced Response Structure**:
```json
{
    "success": true,
    "response": "Agent response text",
    "conversation_data": {
        "customer_name": "Sarah Johnson",
        "phone_number": "847-302-2594",
        "project_type": "kitchen",
        "current_phase": "needs_assessment",
        "dimensions_collected": true,
        "budget_established": false
    },
    "aos_scores": {
        "greeting_credibility": 4,
        "needs_assessment": 3,
        "design_details": 0,
        "overall": 3.5
    },
    "next_required_actions": [
        "establish_budget_range",
        "present_product_options"
    ],
    "red_flags": [],
    "conversion_likelihood": 0.75
}
```

---

## Troubleshooting Guide

### **Common Integration Issues**:

#### **1. Tool Calling Sequence Problems**:
```
Issue: Agent searches products before collecting dimensions
Solution: Enhance system prompt with stronger enforcement
Check: validate_aos_compliance() before tool execution
```

#### **2. Context Loss Between Messages**:
```
Issue: Agent doesn't remember previous conversation elements
Solution: Improve conversation history processing
Check: conversation_data extraction in chat() method
```

#### **3. Scoring Inconsistencies**:
```
Issue: AOS scores don't reflect actual conversation quality
Solution: Review scoring criteria and data extraction
Check: extract_scoring_data() accuracy
```

#### **4. Database Synchronization**:
```
Issue: Customer data not properly persisted
Solution: Check database connection and transaction handling
Check: save_customer_project() error handling
```

### **Debugging Commands**:
```python
# Test AOS compliance
def debug_aos_compliance(conversation_history: List[Dict]):
    conversation_data = extract_scoring_data(conversation_history)
    scores = calculate_aos_scores(conversation_data)
    compliance = validate_aos_compliance(conversation_data, "next_action")
    
    return {
        "conversation_data": conversation_data,
        "aos_scores": scores,
        "compliance": compliance,
        "missing_requirements": get_missing_requirements(conversation_data)
    }
```

---

## Integration Testing

### **AOS Flow Testing Script**:
```python
def test_full_aos_flow():
    agent = SimpleTileAgent(db_manager, rag_manager)
    
    # Test sequence following sample conversation
    test_messages = [
        "hi i'm looking for kitchen floor tile",
        "my name is Sarah and my phone is 847-302-2594",
        "the kitchen is 8x10 feet, we have black countertops and white cabinets",
        "our budget is around $800 to $1200",
        "we want to start in the next week or two"
    ]
    
    conversation_history = []
    for message in test_messages:
        result = agent.chat(message, conversation_history)
        print(f"Message: {message}")
        print(f"Response: {result['response'][:100]}...")
        print(f"AOS Scores: {result.get('aos_scores', {})}")
        print(f"Red Flags: {result.get('red_flags', [])}")
        print("---")
        
        conversation_history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": result["response"]}
        ])
    
    return conversation_history
```

This integration guide provides the framework for implementing professional AOS methodology throughout the chat system architecture, ensuring consistent 4/4 performance across all conversation phases.