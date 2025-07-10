# AOS Current Implementation
## SimpleTileAgent + AOSConversationEngine Architecture

### Overview
This document describes how the current SimpleTileAgent system implements The Tile Shop's AOS (Approach of Sale) methodology using natural language processing and structured conversation management.

---

## Architecture Components

### 1. **SimpleTileAgent** (`modules/simple_tile_agent.py`)
**Primary Role**: Natural LLM-based conversation handler with AOS protocol integration

**Core Components**:
- **System Prompt**: Defines AOS methodology and conversation rules
- **Tool Integration**: Provides access to customer lookup, product search, and AOS questioning
- **Conversation Management**: Handles message history and context tracking
- **Response Generation**: Uses Claude's natural language capabilities

**Key Features**:
```python
class SimpleTileAgent:
    def __init__(self, db_manager, rag_manager):
        self.system_prompt = """AOS methodology instructions..."""
        self.aos_engine = AOSConversationEngine()
        self.client = anthropic.Anthropic()
```

### 2. **AOSConversationEngine** (`modules/aos_conversation_engine.py`)
**Primary Role**: Structured conversation logic and question management

**Core Features**:
- Dynamic question library organized by AOS phases
- Conversation context tracking and state management
- Learning-based question prioritization
- Information extraction from customer responses

**Architecture**:
```python
class AOSConversationEngine:
    def __init__(self):
        self.question_library = self._initialize_question_library()
        self.conversation_patterns = self._load_successful_patterns()
        self.learning_metrics = {"conversions": [], "effectiveness": {}}
```

---

## Current AOS Implementation Status

### ✅ **Implemented Features**

#### **Greeting & Credibility (Partial)**
- Professional greeting with name collection
- Credibility building through system prompt
- ❌ **Missing**: Explicit experience sharing, process explanation

#### **Needs Assessment (Basic)**
- Project type identification (kitchen, bathroom, etc.)
- Basic information gathering through dynamic questions
- ❌ **Missing**: Mandatory four questions (WHAT/WHO/WHEN/HOW MUCH)
- ❌ **Missing**: Dimension collection requirement

#### **Design & Details (Limited)**
- Product search capability through RAG system
- ❌ **Missing**: Structured "tile bomb" presentation
- ❌ **Missing**: Specific SKU presentation with benefits
- ❌ **Missing**: Calculation requirements

#### **Close (Not Implemented)**
- ❌ **Missing**: Direct close attempts
- ❌ **Missing**: Buying signal recognition
- ❌ **Missing**: Urgency creation

#### **Objection Handling (Not Implemented)**
- ❌ **Missing**: 4-step objection handling process
- ❌ **Missing**: Common objection responses

### 🔧 **Tool Integration**

#### **Available Tools**:
1. `lookup_customer` - Customer and purchase history retrieval
2. `search_products` - RAG-based product search
3. `get_installation_guide` - Product installation instructions
4. `get_aos_questions` - Dynamic question generation
5. `save_customer_project` - Customer information persistence
6. `get_installation_accessories` - Accessory recommendations

#### **Tool Flow**:
```
Customer Input → System Prompt → Tool Selection → Tool Execution → Response Generation
```

---

## Conversation Flow Management

### **Current Flow**:
1. **User Message** → SimpleTileAgent.chat()
2. **Context Building** → Message history compilation
3. **LLM Processing** → Claude with system prompt + tools
4. **Tool Execution** → Based on LLM decisions
5. **Response Generation** → Natural language with tool results

### **AOS Integration Points**:
- **System Prompt**: Contains AOS methodology instructions
- **get_aos_questions Tool**: Provides phase-appropriate questions
- **Conversation History**: Maintains context for scoring
- **Information Extraction**: Identifies customer details for progression

---

## Database Integration

### **Customer Data Storage**:
```python
# Customer lookup and creation
customer = self.db.get_or_create_customer(phone_number)
purchases = self.db.get_customer_purchases(customer['customer_id'])
```

### **Project Information**:
```python
# Project data persistence
result = self.save_customer_project(phone_number, project_info)
```

### **Missing Database Elements**:
- AOS phase tracking
- Conversation scoring storage
- Step completion tracking
- Performance metrics collection

---

## Question Library Structure

### **Current Organization**:
```python
question_library = {
    "discovery": {
        "kitchen": ["color scheme questions", "style questions"],
        "bathroom": ["room type questions", "style questions"],
        "general": ["basic project questions"]
    },
    "qualification": {
        "timeline": ["timing questions"],
        "budget": ["investment questions"],
        "decision_making": ["authority questions"]
    }
}
```

### **Question Prioritization**:
- Heuristic-based scoring (not ML-based yet)
- Contact information prioritized highest
- Style/color questions rated high for conversion
- Timeline questions indicate buying intent

---

## API Integration

### **Endpoint**: `/api/chat/simple`
```python
@app.route('/api/chat/simple', methods=['POST'])
def simple_chat_api():
    data = request.get_json()
    query = data.get('query', '')
    conversation_history = data.get('conversation_history', [])
    phone_number = data.get('phone_number', '')
    
    agent = SimpleTileAgent(db_manager, rag_manager)
    result = agent.chat(query, conversation_history, phone_number)
    return jsonify(result)
```

### **Response Format**:
```json
{
    "success": true,
    "response": "Agent response text",
    "tool_calls": [{"tool": "tool_name", "result": {}}],
    "conversation_updated": true
}
```

---

## Current Limitations vs AOS Requirements

### **Major Gaps**:

1. **No Systematic AOS Phase Tracking**
   - Current: Ad-hoc question generation
   - Required: Structured 9-step process

2. **Missing Mandatory Requirements**
   - No dimension collection enforcement
   - No budget establishment requirement
   - No close attempt tracking

3. **Incomplete Conversation Scoring**
   - No 1-4 scoring per AOS step
   - No performance metrics collection
   - No red flag detection

4. **Limited Objection Handling**
   - No structured 4-step process
   - No common objection responses
   - No re-ask mechanisms

5. **No Professional Calculations**
   - Missing waste factor calculations
   - No box quantity rounding
   - No complete project costing

---

## Technology Stack

### **Core Technologies**:
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Function Calling**: Anthropic's tool use API
- **Database**: MySQL with custom database manager
- **RAG System**: Custom implementation with vector search
- **Web Framework**: Flask with REST API

### **Integration Pattern**:
```
Frontend Chat → Flask API → SimpleTileAgent → Claude + Tools → Database/RAG → Response
```

---

## Performance Considerations

### **Current Strengths**:
- Natural conversation flow
- Flexible question adaptation
- Real-time tool integration
- Context preservation

### **Performance Issues**:
- No conversation quality measurement
- Missing AOS step completion tracking
- No conversion rate optimization
- Limited learning from interactions

---

## Next Steps for Full AOS Implementation

1. **Implement structured AOS phase tracking**
2. **Add mandatory requirement enforcement**
3. **Create conversation scoring system**
4. **Develop objection handling framework**
5. **Add professional calculation tools**
6. **Implement performance analytics**

This current implementation provides a solid foundation for natural conversation but requires significant enhancement to meet professional AOS standards and achieve consistent 4/4 performance across all steps.