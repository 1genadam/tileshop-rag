# Customer Project Database Schema
## Auto-Scaling Database Design for AOS Customer Data Collection

### Overview
This schema captures all customer information gathered during AOS (Approach of Sale) conversations, supporting both simple inquiries and complex multi-room projects while maintaining data integrity and scalability.

---

## Core Tables

### 1. CUSTOMERS Table
**Purpose**: Store customer contact and basic information
```sql
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone_primary VARCHAR(20),
    phone_secondary VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'USA',
    customer_type ENUM('diy_homeowner', 'contractor', 'designer', 'builder') NOT NULL,
    pro_account_number VARCHAR(50),
    preferred_contact_method ENUM('phone', 'email', 'text') DEFAULT 'phone',
    marketing_opt_in BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT
);
```

### 2. PROJECTS Table
**Purpose**: Store high-level project information
```sql
CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id),
    project_name VARCHAR(255),
    project_status ENUM('inquiry', 'quoted', 'ordered', 'in_progress', 'completed', 'cancelled') DEFAULT 'inquiry',
    total_budget_min DECIMAL(10,2),
    total_budget_max DECIMAL(10,2),
    tile_budget DECIMAL(10,2),
    project_start_date DATE,
    project_completion_date DATE,
    installation_method ENUM('diy', 'contractor', 'designer_managed', 'unknown') NOT NULL,
    contractor_name VARCHAR(255),
    contractor_phone VARCHAR(20),
    contractor_email VARCHAR(255),
    designer_name VARCHAR(255),
    designer_company VARCHAR(255),
    urgency_level ENUM('low', 'medium', 'high', 'rush') DEFAULT 'medium',
    lead_source VARCHAR(100),
    sales_associate VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT
);
```

### 3. PROJECT_ROOMS Table
**Purpose**: Store individual room/area details within projects
```sql
CREATE TABLE project_rooms (
    room_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(project_id),
    room_name VARCHAR(100), -- 'Master Bathroom', 'Kitchen', 'Guest Bath', etc.
    room_type ENUM(
        'kitchen', 'bathroom', 'master_bathroom', 'guest_bathroom', 
        'powder_room', 'laundry_room', 'mudroom', 'entryway', 
        'living_room', 'dining_room', 'bedroom', 'basement', 
        'outdoor', 'commercial', 'other'
    ) NOT NULL,
    room_style VARCHAR(100), -- 'modern', 'traditional', 'farmhouse', etc.
    room_length_ft DECIMAL(8,2),
    room_width_ft DECIMAL(8,2),
    room_height_ft DECIMAL(8,2),
    room_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 4. SURFACES Table
**Purpose**: Store specific surface details within each room
```sql
CREATE TABLE surfaces (
    surface_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES project_rooms(room_id),
    surface_type ENUM(
        'floor', 'backsplash', 'shower_walls', 'shower_floor', 
        'tub_surround', 'accent_wall', 'fireplace', 'countertop',
        'wainscoting', 'ceiling', 'exterior_wall', 'other'
    ) NOT NULL,
    surface_area_sf DECIMAL(10,2) NOT NULL,
    length_ft DECIMAL(8,2),
    width_ft DECIMAL(8,2),
    height_ft DECIMAL(8,2),
    pattern_type ENUM(
        'straight_lay', 'brick_pattern', 'herringbone', 'diagonal',
        'basket_weave', 'chevron', 'versailles', 'pinwheel', 'other'
    ) DEFAULT 'straight_lay',
    complexity_level ENUM('simple', 'moderate', 'complex') DEFAULT 'simple',
    waste_factor DECIMAL(4,2) DEFAULT 0.10, -- 0.10 = 10%
    obstacles_count INTEGER DEFAULT 0,
    obstacles_description TEXT,
    prep_work_needed TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 5. SELECTED_PRODUCTS Table
**Purpose**: Store products selected for each surface
```sql
CREATE TABLE selected_products (
    selection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    surface_id UUID NOT NULL REFERENCES surfaces(surface_id),
    product_sku VARCHAR(50) NOT NULL,
    product_name VARCHAR(255),
    product_type ENUM(
        'tile', 'trim', 'grout', 'adhesive', 'underlayment',
        'sealant', 'caulk', 'spacers', 'tools', 'accessories'
    ) NOT NULL,
    quantity_needed DECIMAL(10,2),
    quantity_ordered DECIMAL(10,2),
    unit_of_measure ENUM('sf', 'box', 'linear_ft', 'piece', 'bag', 'tube', 'gallon') NOT NULL,
    box_coverage_sf DECIMAL(8,2), -- For tiles
    price_per_unit DECIMAL(10,2),
    total_price DECIMAL(10,2),
    selection_status ENUM('considered', 'selected', 'ordered', 'delivered') DEFAULT 'considered',
    selection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

### 6. CONVERSATION_LOG Table
**Purpose**: Track AOS conversation progress and outcomes
```sql
CREATE TABLE conversation_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(project_id),
    conversation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interaction_type ENUM('initial_inquiry', 'followup', 'quote_review', 'order_placement', 'support') NOT NULL,
    aos_phase ENUM(
        'greeting', 'credibility', 'needs_assessment', 'design_details',
        'close', 'objection_handling', 'negotiation', 'followup'
    ),
    aos_score_greeting INTEGER CHECK (aos_score_greeting BETWEEN 1 AND 4),
    aos_score_needs INTEGER CHECK (aos_score_needs BETWEEN 1 AND 4),
    aos_score_design INTEGER CHECK (aos_score_design BETWEEN 1 AND 4),
    aos_score_close INTEGER CHECK (aos_score_close BETWEEN 1 AND 4),
    aos_score_objection INTEGER CHECK (aos_score_objection BETWEEN 1 AND 4),
    aos_score_overall INTEGER CHECK (aos_score_overall BETWEEN 1 AND 4),
    outcome ENUM('information_gathered', 'quote_requested', 'order_placed', 'follow_up_scheduled', 'lost'),
    sales_associate VARCHAR(100),
    conversation_summary TEXT,
    next_action VARCHAR(255),
    next_contact_date DATE
);
```

### 7. QUOTES Table
**Purpose**: Store formal quotes generated from conversations
```sql
CREATE TABLE quotes (
    quote_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(project_id),
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    quote_date DATE NOT NULL,
    expiration_date DATE,
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    delivery_fee DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    quote_status ENUM('draft', 'sent', 'accepted', 'rejected', 'expired') DEFAULT 'draft',
    sales_associate VARCHAR(100),
    special_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## Supporting Tables

### 8. PRODUCT_CATALOG Table (Reference)
**Purpose**: Product information for selections
```sql
CREATE TABLE product_catalog (
    sku VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(100),
    brand VARCHAR(100),
    material VARCHAR(100),
    color VARCHAR(100),
    size_length DECIMAL(6,2),
    size_width DECIMAL(6,2),
    size_thickness DECIMAL(6,2),
    coverage_per_box DECIMAL(8,2),
    pieces_per_box INTEGER,
    price_retail DECIMAL(10,2),
    price_pro DECIMAL(10,2),
    in_stock BOOLEAN DEFAULT true,
    discontinued BOOLEAN DEFAULT false,
    special_order BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## Key Indexes for Performance

```sql
-- Customer lookup indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone_primary);
CREATE INDEX idx_customers_name ON customers(last_name, first_name);

-- Project relationship indexes
CREATE INDEX idx_projects_customer ON projects(customer_id);
CREATE INDEX idx_projects_status ON projects(project_status);
CREATE INDEX idx_projects_date ON projects(created_at);

-- Room and surface relationship indexes
CREATE INDEX idx_rooms_project ON project_rooms(project_id);
CREATE INDEX idx_surfaces_room ON surfaces(room_id);
CREATE INDEX idx_products_surface ON selected_products(surface_id);

-- Conversation tracking indexes
CREATE INDEX idx_conversation_project ON conversation_log(project_id);
CREATE INDEX idx_conversation_date ON conversation_log(conversation_date);

-- Quote lookup indexes
CREATE INDEX idx_quotes_project ON quotes(project_id);
CREATE INDEX idx_quotes_number ON quotes(quote_number);
```

---

## Data Collection Integration Points

### AOS Phase 1: Greeting & Credibility
```sql
-- Capture basic customer info
INSERT INTO customers (first_name, last_name, phone_primary, customer_type)
VALUES (?, ?, ?, ?);

INSERT INTO projects (customer_id, installation_method, sales_associate)
VALUES (?, ?, ?);
```

### AOS Phase 2: Needs Assessment
```sql
-- Capture WHAT information
INSERT INTO project_rooms (project_id, room_type, room_name, room_style)
VALUES (?, ?, ?, ?);

INSERT INTO surfaces (room_id, surface_type, surface_area_sf, pattern_type)
VALUES (?, ?, ?, ?);

-- Capture WHO, WHEN, HOW MUCH
UPDATE projects SET 
    installation_method = ?,
    contractor_name = ?,
    project_start_date = ?,
    total_budget_min = ?,
    total_budget_max = ?
WHERE project_id = ?;
```

### AOS Phase 3: Design & Details
```sql
-- Capture product selections
INSERT INTO selected_products (
    surface_id, product_sku, product_type, quantity_needed, 
    price_per_unit, selection_status
) VALUES (?, ?, ?, ?, ?, 'considered');
```

### AOS Phase 4: Close & Follow-up
```sql
-- Update conversation outcome
INSERT INTO conversation_log (
    project_id, aos_phase, aos_score_overall, outcome, next_action
) VALUES (?, 'close', ?, ?, ?);
```

---

## Auto-Scaling Considerations

### 1. Horizontal Scaling
- Use UUID primary keys for easy sharding
- Partition tables by date for conversation_log and quotes
- Separate read replicas for reporting queries

### 2. Performance Optimization
- Implement database connection pooling
- Use materialized views for common aggregations
- Cache frequently accessed product catalog data

### 3. Data Archival Strategy
- Archive completed projects older than 2 years
- Maintain conversation_log for analytics but archive detailed notes
- Keep active customer data readily accessible

---

## Sample Queries

### Get Customer Project Summary
```sql
SELECT 
    c.first_name, c.last_name, c.email,
    p.project_name, p.project_status,
    COUNT(pr.room_id) as room_count,
    SUM(s.surface_area_sf) as total_sf,
    p.tile_budget
FROM customers c
JOIN projects p ON c.customer_id = p.customer_id
LEFT JOIN project_rooms pr ON p.project_id = pr.project_id
LEFT JOIN surfaces s ON pr.room_id = s.room_id
WHERE c.customer_id = ?
GROUP BY c.customer_id, p.project_id;
```

### Calculate Project Total
```sql
SELECT 
    p.project_id,
    SUM(sp.total_price) as project_total,
    COUNT(DISTINCT s.surface_id) as surface_count
FROM projects p
JOIN project_rooms pr ON p.project_id = pr.project_id
JOIN surfaces s ON pr.room_id = s.room_id
JOIN selected_products sp ON s.surface_id = sp.surface_id
WHERE p.project_id = ? AND sp.selection_status = 'selected'
GROUP BY p.project_id;
```

---

This schema provides a comprehensive, scalable foundation for capturing all customer data from AOS conversations while maintaining flexibility for different project types and complexity levels.