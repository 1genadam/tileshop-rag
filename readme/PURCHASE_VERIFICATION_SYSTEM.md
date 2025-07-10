# Purchase Verification System Documentation

## Overview
The Purchase Verification System is an intelligent enhancement to the RAG chat system that verifies customer purchases against their purchase history and provides smart product matching for installation assistance and support.

## Problem Solved
When customers mention they bought a product and need help, the system now:
1. **Prompts for phone number** to look up purchase history
2. **Verifies exact product match** against customer's actual purchases
3. **Provides intelligent matching** for similar products (e.g., customer says "permat" but bought "backer-lite")
4. **Delivers specific installation guidance** based on the verified product

## System Architecture

### Database Schema Enhancements

#### 1. `customer_purchases` Table
Tracks all customer purchases with detailed product information:
```sql
CREATE TABLE customer_purchases (
    purchase_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(customer_id),
    order_number VARCHAR(100),
    order_date DATE NOT NULL,
    product_sku VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_category VARCHAR(100),
    product_subcategory VARCHAR(100),
    quantity_purchased DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    purchase_source VARCHAR(50), -- 'online', 'store', 'phone'
    store_location VARCHAR(100),
    sales_associate VARCHAR(100),
    delivery_date DATE,
    installation_notes TEXT
);
```

#### 2. `product_categories` Table
Enables intelligent product matching:
```sql
CREATE TABLE product_categories (
    category_id UUID PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_keywords TEXT[], -- Keywords for matching
    related_products TEXT[], -- Related product names/SKUs
    installation_type VARCHAR(50) -- 'preparation', 'main_product', 'finishing'
);
```

**Pre-populated Categories:**
- **Anti-Fracture Mats**: Keywords: ['permat', 'anti-fracture', 'decoupling'] → Products: ['PERMAT', 'BACKER-LITE']
- **Heating Systems**: Keywords: ['heat mat', 'radiant heat'] → Products: ['HEAT MAT', 'RADIANT HEAT']
- **Adhesives**: Keywords: ['adhesive', 'mortar', 'thinset'] → Products: ['THINSET', 'ADHESIVE']

### Core Components

#### 1. Enhanced Information Extraction
```python
def extract_information_from_query(self, query: str) -> Dict:
    """Extract purchase indicators and product mentions"""
    extracted = {}
    
    # Detect purchase mentions
    purchase_indicators = ['bought', 'purchased', 'got from you', 'ordered']
    if any(indicator in query.lower() for indicator in purchase_indicators):
        extracted['mentions_purchase'] = True
        
        # Extract specific product mentions
        product_keywords = ['permat', 'backer-lite', 'heat mat', 'thinset']
        for keyword in product_keywords:
            if keyword in query.lower():
                extracted['mentioned_product'] = keyword
                break
    
    # Detect installation help requests
    installation_help_indicators = ['how to install', 'installation', 'instructions']
    if any(indicator in query.lower() for indicator in installation_help_indicators):
        extracted['needs_installation_help'] = True
    
    return extracted
```

#### 2. Purchase Verification Logic
```python
def handle_purchase_verification(self, query: str, extracted_info: Dict, customer: Dict = None) -> Dict:
    """Handle purchase verification and intelligent product matching"""
    
    # If customer mentions purchase but no customer info, request phone number
    if extracted_info.get('mentions_purchase') and not customer:
        return {
            'needs_phone_number': True,
            'response': "Could you please provide your phone number so I can look up your purchase history?"
        }
    
    # Get customer purchase history
    purchases = self.db.get_customer_purchases(customer['customer_id'])
    
    # Find product match using intelligent matching
    product_match = self.db.find_product_by_keyword(mentioned_product, purchases)
    
    if product_match['exact_match']:
        # Customer bought exactly what they mentioned
        return {'purchase_verified': True, 'exact_match': True}
    
    elif product_match['customer_has_related']:
        # Customer bought related products (smart matching)
        return {'purchase_verified': True, 'related_match': True}
    
    else:
        # No matching purchase found
        return {'purchase_verified': False}
```

#### 3. Intelligent Product Matching
```python
def find_product_by_keyword(self, keyword: str, customer_purchases: List[Dict]) -> Dict:
    """Find products using intelligent category-based matching"""
    
    # Check product categories for keyword matches
    category_matches = db.query("""
        SELECT category_name, related_products 
        FROM product_categories 
        WHERE %s = ANY(category_keywords)
    """, [keyword.lower()])
    
    # Check customer purchases against related products
    for purchase in customer_purchases:
        for category in category_matches:
            for related_product in category['related_products']:
                if related_product.upper() in purchase['product_name'].upper():
                    return {
                        'customer_has_related': [{
                            'purchased_product': purchase,
                            'related_to': related_product,
                            'category': category['category_name']
                        }]
                    }
    
    return {'exact_match': None, 'customer_has_related': []}
```

#### 4. Installation Guidance System
```python
def _get_installation_guidance(self, verification_result: Dict) -> str:
    """Provide specific installation guidance based on verified purchase"""
    
    product = verification_result['exact_match']
    product_name = product['product_name'].upper()
    
    if 'ANTI-FRACTURE' in product_name or 'BACKER-LITE' in product_name:
        return """
**Installation Steps for Anti-Fracture Mat:**
1. **Surface Preparation**: Ensure substrate is clean, flat, and structurally sound
2. **Layout**: Roll out the mat and cut to fit your area
3. **Adhesive Application**: Apply appropriate adhesive with recommended trowel
4. **Mat Installation**: Place mat into wet adhesive, removing air bubbles
5. **Seam Treatment**: Overlap seams by 2" and seal with appropriate tape
6. **Tile Installation**: Wait for cure time, then install tile using polymer-modified thinset
"""
    
    elif 'HEAT MAT' in product_name:
        return """
**Installation Steps for Electric Heat Mat:**
1. **Electrical Planning**: Ensure proper GFCI protection and electrical capacity
2. **Floor Preparation**: Clean, level substrate
3. **Layout Planning**: Plan mat placement avoiding fixtures and cabinets
4. **Mat Installation**: Secure mat with adhesive or mechanical fasteners
5. **Sensor Installation**: Install floor temperature sensor
6. **Testing**: Test system before covering with tile
7. **Tile Installation**: Cover with appropriate thinset and tile
"""
```

## Conversation Flow Examples

### Example 1: Customer Mentions Purchase Without Phone Number
```
Customer: "i just bought permat from you guys and need to know how to install it"

System Response:
"I'd be happy to help you with your installation! To provide you with the most accurate guidance, could you please provide your phone number so I can look up your purchase history and make sure I'm giving you the right instructions for the specific product you bought?"

Phase: purchase_verification
Needs Phone Number: True
```

### Example 2: Exact Product Match
```
Customer: "i bought backer-lite from you and need installation help"
Phone: "847-302-2594"

System Response:
"Perfect! I can see you purchased BACKER-LITE Anti-Fracture Mat on 2025-06-15. I'll provide you with the specific installation instructions for this product.

**Installation Steps for Anti-Fracture Mat:**
1. Surface Preparation: Ensure substrate is clean, flat, and structurally sound
2. Layout: Roll out the mat and cut to fit your area
..."

Purchase Verified: True
Phase: installation_support
```

### Example 3: Smart Product Matching
```
Customer: "i bought permat from you guys and need to know how to install it"
Phone: "847-302-2594"

System Response:
"I see you mentioned 'permat', but I found that you actually purchased BACKER-LITE Anti-Fracture Mat on 2025-06-15, which is a Anti-Fracture Mats product - very similar to what you mentioned! Let me provide you with the correct installation instructions for the BACKER-LITE Anti-Fracture Mat that you actually bought."

Purchase Verified: True (Related Match)
Category: Anti-Fracture Mats
```

### Example 4: No Purchase Match Found
```
Customer: "i bought marble tile from you guys and need help"
Phone: "847-302-2594"

System Response:
"I don't see 'marble tile' in your recent purchase history. However, I do see you've purchased: Electric Heat Mat 120V, BACKER-LITE Anti-Fracture Mat, Thinset Adhesive Premium. Could you clarify which product you need installation help with, or would you like assistance with one of these items instead?"

Purchase Verified: False
```

## API Integration

### Enhanced `/api/chat/unified` Endpoint
```python
@app.route('/api/chat/unified', methods=['POST'])
def unified_chat_api():
    """Enhanced chat endpoint with purchase verification"""
    
    # Use purchase verification system for all messages
    chat_result = aos_chat.process_chat_with_purchase_verification(query, phone_number, first_name)
    
    # Handle phone number requests
    if chat_result.get('needs_phone_number'):
        return jsonify(chat_result)
    
    # Enhance installation support with RAG system
    if chat_result.get('phase') == 'installation_support':
        rag_response = simple_rag.search_and_respond(f"installation instructions {product_name}", user_id)
        if rag_response:
            chat_result['additional_info'] = rag_response['response']
    
    return jsonify(chat_result)
```

### Response Format
```json
{
    "success": true,
    "response": "Contextual response with installation guidance",
    "phase": "installation_support",
    "purchase_verified": true,
    "verification_result": {
        "exact_match": {
            "product_name": "BACKER-LITE Anti-Fracture Mat",
            "order_date": "2025-06-15",
            "product_category": "Anti-Fracture Mats"
        }
    },
    "needs_phone_number": false
}
```

## Database Operations

### Purchase History Lookup
```python
def get_customer_purchases(self, customer_id: str, days_back: int = 365) -> List[Dict]:
    """Get customer purchase history for verification"""
    return db.query("""
        SELECT product_sku, product_name, product_category, order_date, quantity_purchased
        FROM customer_purchases
        WHERE customer_id = %s 
          AND order_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY order_date DESC
    """, [customer_id, days_back])
```

### Sample Data Management
```python
def add_sample_purchase_data(self, customer_id: str) -> bool:
    """Add sample purchases for testing"""
    sample_purchases = [
        ('ORD-001', '2025-06-15', 'BL-001', 'BACKER-LITE Anti-Fracture Mat', 'Anti-Fracture Mats'),
        ('ORD-001', '2025-06-15', 'TS-002', 'Thinset Adhesive Premium', 'Adhesives'),
        ('ORD-002', '2025-07-01', 'HM-003', 'Electric Heat Mat 120V', 'Heating Systems')
    ]
```

## Testing Framework

### Test Script: `test_purchase_verification.py`
```python
def test_purchase_verification():
    """Comprehensive testing of purchase verification system"""
    
    # Test 1: Customer mentions purchase without phone number
    result1 = aos_chat.process_chat_with_purchase_verification(
        "i just bought permat from you guys and need to know how to install it"
    )
    assert result1['needs_phone_number'] == True
    
    # Test 2: Exact product match
    result2 = aos_chat.process_chat_with_purchase_verification(
        "i bought backer-lite from you and need installation help",
        phone_number="847-302-2594"
    )
    assert result2['purchase_verified'] == True
    
    # Test 3: Smart product matching (permat → backer-lite)
    result3 = aos_chat.process_chat_with_purchase_verification(
        "i bought permat from you guys and need to know how to install it",
        phone_number="847-302-2594"
    )
    assert result3['purchase_verified'] == True
    assert 'BACKER-LITE' in result3['response']
```

## Performance Considerations

### Database Indexing
```sql
-- Optimized indexes for fast lookup
CREATE INDEX idx_purchases_customer ON customer_purchases(customer_id);
CREATE INDEX idx_purchases_sku ON customer_purchases(product_sku);
CREATE INDEX idx_categories_keywords ON product_categories USING GIN(category_keywords);
```

### Caching Strategy
- Customer purchase history cached for 15 minutes
- Product category mappings cached indefinitely
- Purchase verification results cached per session

## Error Handling

### Common Scenarios
1. **Customer not found**: Create new customer record
2. **No purchase history**: Offer general assistance
3. **Multiple similar products**: Present options for clarification
4. **Database connection issues**: Graceful fallback to general support

### Logging
```python
logger.info(f"Purchase verification: {customer_id} mentioned '{product}' → verified: {verified}")
logger.info(f"Smart matching: '{mentioned}' → found '{actual_product}' in category '{category}'")
```

## Future Enhancements

### Planned Features
1. **Multi-store Purchase Tracking**: Track purchases across different store locations
2. **Advanced Product Relationships**: Machine learning for product similarity
3. **Installation Progress Tracking**: Follow up on installation completion
4. **Warranty and Return Integration**: Connect with warranty systems
5. **Personalized Recommendations**: Suggest complementary products based on purchase history

### Integration Opportunities
1. **CRM Integration**: Sync with existing customer relationship management systems
2. **Inventory Management**: Real-time product availability checking
3. **Order Management**: Direct integration with order fulfillment systems
4. **Mobile App**: Extend verification to mobile applications

## Security and Privacy

### Data Protection
- Customer purchase data encrypted at rest
- Phone number normalization and hashing for lookup
- Purchase history limited to recent transactions (configurable)
- GDPR compliance for data retention and deletion

### Access Control
- Purchase verification requires customer phone number
- Staff access logged for audit trails
- Customer consent for data usage

## Monitoring and Analytics

### Key Metrics
- **Verification Success Rate**: Percentage of successful purchase verifications
- **Smart Matching Accuracy**: Accuracy of related product matching
- **Installation Support Completion**: Customer satisfaction with provided guidance
- **Phone Number Prompt Response Rate**: Customer willingness to provide phone numbers

### Dashboards
- Real-time verification statistics
- Product category matching performance
- Customer support resolution rates
- Installation guidance effectiveness

## Conclusion

The Purchase Verification System transforms the RAG chat experience by:

- ✅ **Intelligent Purchase Verification** - Automatically verifies customer purchases
- ✅ **Smart Product Matching** - Recognizes related products (permat → backer-lite)
- ✅ **Targeted Installation Guidance** - Provides specific instructions for verified products
- ✅ **Natural Conversation Flow** - Seamlessly requests phone numbers when needed
- ✅ **Comprehensive Product Database** - Maintains detailed purchase and category information

This system ensures customers receive accurate, personalized installation guidance based on their actual purchases while maintaining a natural, helpful conversation experience.

---

*Last Updated: 2025-07-10*
*Version: 1.0*
*Author: Claude Code Assistant*