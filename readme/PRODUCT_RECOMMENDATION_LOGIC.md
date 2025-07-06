# Product Recommendation Logic

## Overview
This document outlines the intelligent product recommendation system implemented in the Tileshop RAG chat assistant. The system provides context-aware material suggestions, upselling opportunities, and professional installation guidance to maximize customer satisfaction and store revenue.

## Core Recommendation Engine

### 1. Query Classification System

The system intelligently routes customer queries through multiple classification layers:

#### **Product Search Queries**
- Indicators: `['looking for', 'find', 'show me', 'need', 'want', 'search', 'tiles', 'tile', 'floor', 'wall']`
- Routes to: Database search with supporting materials
- Example: "blue tile for bathroom floor"

#### **Analytical Queries** 
- Indicators: `['cheapest', 'lowest', 'highest', 'most expensive', 'average', 'compare', 'best value']`
- Routes to: Claude API for data analysis
- Example: "what's the cheapest porcelain tile?"

#### **SKU-Specific Queries**
- Patterns: Direct SKU numbers, SKU references, contextual image requests
- Routes to: Direct product lookup
- Example: "show me SKU 484281" or "show me that tile"

#### **Subway Tile Upselling**
- Detection: Subway tile queries with project context
- Routes to: Specialized upselling flow with complete project packages
- Example: "subway tile for kitchen backsplash"

### 2. Supporting Materials Recommendation Engine

#### **Context Analysis Framework**

```python
# Application Area Detection
is_bathroom = ['bathroom', 'shower', 'wet', 'bath']
is_kitchen = ['kitchen', 'backsplash', 'counter'] 
is_basement = ['basement', 'below grade']
is_floor = ['floor', 'flooring']
is_wall = ['wall', 'backsplash']
is_heated = ['heated', 'heating', 'radiant']
```

#### **Tile Characteristic Analysis**

```python
# Large Format Detection (>12 inches)
large_format_sizes = ['24 x', '18 x', '16 x', '15 x', '14 x', '13 x']

# Material Type Detection
natural_stone = ['marble', 'travertine', 'limestone', 'granite', 'slate']
porcelain_tiles = ['porcelain'] # Takes precedence over stone keywords
```

#### **Intelligent Material Selection Logic**

**Essential Installation Materials:**
- **LFT Thinset Mortar** → Recommended for:
  - Large format tiles (>12")
  - Porcelain tiles
  - Superior bond strength applications
- **Standard Thinset** → For standard ceramic installations
- **Tile Spacers/Wedges** → Always recommended for consistent spacing
- **Grout** → Sanded for joints >1/8", unsanded for smaller joints

**Area-Specific Protection:**
- **Wet Areas** (Bathroom/Kitchen/Basement):
  - Backer-Lite Underlayment (moisture protection)
  - Waterproof Membrane (additional barrier)
- **Dry Areas** (Living rooms/bedrooms):
  - Permat Underlayment (crack isolation)

**Specialized Systems:**
- **Heated Floors** (when "heated" mentioned):
  - Heated Floor Mat & Cable
  - Uncoupling Membrane (thermal expansion protection)
- **Natural Stone** (when actual stone detected):
  - Stone Sealer (stain/moisture protection)
  - Stone-Safe Grout (non-acidic)

**Professional Finishing:**
- Tile Leveling System (lippage prevention)
- Trim Pieces (bullnose, edge trim)
- Grout Sealer (standard grout protection)

### 3. Upselling and Revenue Optimization

#### **Subway Tile Project Packages**

The system detects subway tile opportunities and creates complete project packages:

```python
# Package Components
essential_package = {
    'thinset': {'cost': 35.0, 'bags_needed': 2},
    'grout': {'cost': 25.0, 'bags_needed': 1}, 
    'spacers': {'cost': 15.0},
    'sealer': {'cost': 25.0}
}

premium_options = {
    'trim_package': {'cost': 45.0},
    'euro_trowel': {'cost': 85.0},
    'professional_tools': {'cost': 150.0}
}
```

#### **Dynamic Pricing Strategy**
- **Tiles Only**: Base product cost
- **Essential Package**: Base + installation materials
- **Premium Package**: Complete professional solution

#### **Value Proposition Messaging**
- Prevents costly return trips
- Ensures proper installation
- Professional tools create better results
- Warranty protection with complete system

### 4. Professional Installation Guidance

#### **Standard Tips (Always Included)**
- Purchase 10-15% extra tile for cuts and repairs
- Proper trowel sizing (1/4" wall, 3/8" floor)
- Cure times (24 hours to grout, 72 hours heavy use)

#### **Context-Specific Guidance**
- **Natural Stone**: "Seal before and after grouting"
- **Heated Floors**: "Install heating system before tile"
- **Large Format**: "Use appropriate support systems"

#### **Quantity Estimation Offer**
- "Need help calculating quantities? Our team can provide detailed material estimates."

## ROI Optimization Strategies

### 1. **Complete Project Thinking**
- Transform tile purchases into complete installation projects
- Increase average order value through bundling
- Reduce customer return visits

### 2. **Quality Tier Progression**
- Start with essential materials
- Present premium upgrade options
- Emphasize long-term value and warranty benefits

### 3. **Professional Credibility**
- Provide expert installation advice
- Reference industry standards and best practices
- Build trust through comprehensive knowledge

### 4. **Convenience Value**
- One-stop shopping experience
- Eliminate guesswork for customers
- Professional quantity calculations

## Implementation Architecture

### Query Processing Flow
```
Customer Query → Classification → Route Selection → Product Search → 
Supporting Materials Analysis → Response Generation → Customer Response
```

### Decision Trees

#### **Material Selection Decision Tree**
```
1. Analyze Tile Type
   ├── Porcelain? → LFT Thinset
   ├── Large Format? → LFT Thinset  
   └── Standard? → Premium Thinset

2. Analyze Application Area
   ├── Wet Area? → Backer-Lite + Waterproof Membrane
   ├── Dry Floor? → Permat Underlayment
   └── Wall? → Standard preparation

3. Check Special Requirements
   ├── Heated? → Heating System + Uncoupling Membrane
   ├── Natural Stone? → Stone Sealer + Stone-Safe Grout
   └── Standard? → Grout Sealer
```

#### **Query Routing Decision Tree**
```
Incoming Query
├── Contains SKU? → Direct Product Lookup
├── Subway + Project Context? → Upselling Flow
├── Analytical Indicators? → Claude Analysis
├── Product Search Terms? → Database Search + Materials
└── General Question? → Claude General Response
```

## Performance Metrics

### Success Indicators
- **Average Order Value**: Increase through bundling
- **Customer Satisfaction**: Complete project guidance
- **Return Rate**: Reduced through comprehensive planning
- **Conversion Rate**: Professional consultation approach

### Optimization Areas
- Material recommendation accuracy
- Project package relevance
- Price point progression
- Professional tip effectiveness

## Future Enhancements

### 1. **Dynamic Pricing Integration**
- Real-time inventory pricing
- Volume discount calculations
- Seasonal promotion integration

### 2. **Advanced Project Visualization**
- Room size calculations
- 3D project previews
- Material quantity precision

### 3. **Customer History Integration**
- Previous purchase patterns
- Preference learning
- Loyalty program integration

### 4. **Supplier Integration**
- Real-time availability
- Delivery scheduling
- Installation service coordination

## Technical Implementation Notes

### Key Files
- `simple_rag.py`: Core recommendation engine
- `_generate_supporting_materials_section()`: Materials logic
- `detect_subway_tile_query()`: Upselling detection
- `generate_upselling_response()`: Package creation

### Configuration
- Material costs and quantities
- Detection keywords and patterns
- Response templates and messaging
- Professional tip database

### Maintenance
- Regular keyword pattern updates
- Price point adjustments
- Customer feedback integration
- Performance metric monitoring

---

*This recommendation system transforms the tile shopping experience from simple product lookup to comprehensive project consultation, driving both customer satisfaction and business growth through intelligent upselling and professional guidance.*