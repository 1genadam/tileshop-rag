# Database Schema Enhancement Documentation
## Critical Data Extraction Improvements to Preserve

### 🎯 **Purpose**
This document preserves the important database schema and extraction enhancements from commit `ab408d2e` that must be reapplied after reverting to working extraction logic.

### 📊 **Enhanced Database Schema Fields**

Based on README requirements and schema updates, the following fields are critical for comprehensive data extraction:

#### **Core Product Data (Working)**
- `title` - Product title
- `sku` - Product SKU identifier  
- `url` - Product page URL
- `price_per_sqft` - Price per square foot
- `price_per_box` - Price per box
- `price_per_piece` - Price per piece

#### **Product Details (Enhanced)**
- `description` - Description tab content
- `specifications` - JSON specifications from specifications tab
- `coverage` - Coverage information
- `finish` - Product finish details
- `color` - Product color
- `size_shape` - Dimensions and shape information
- `slip_rating` - Slip resistance rating

#### **Visual & Resource Data (Schema Enhancements)**
- `images` - JSON array of all product images
- `primary_image` - Main product image URL
- `image_variants` - Color/finish image variations
- `color_images` - Color-specific images
- `resources` - JSON object containing:
  - PDFs and installation guides
  - Technical documentation
  - Care instructions
  - Warranty information
- `collection_links` - JSON array of related collection links

#### **Product Variations**
- `color_variations` - Available color options
- `brand` - Product brand information
- `product_category` - Product categorization

#### **Technical Fields**
- `raw_html` - Raw HTML content for debugging
- `raw_markdown` - Markdown extracted content
- `scraped_at` - Timestamp of data extraction
- `updated_at` - Last modification timestamp

### 🔧 **Key Schema Enhancement Features**

#### **1. Resource Extraction Logic**
From the schema update commit, enhanced extraction for:
- **PDF Documents**: Installation guides, technical specs, warranty docs
- **Image Collections**: All product images with variants
- **Structured Data**: JSON-LD product information
- **Tab Content**: Description, specifications, and resources tabs

#### **2. Database Field Mappings**
```sql
-- Enhanced fields added in schema update
images TEXT,                    -- JSON array of image URLs
primary_image TEXT,            -- Main product image
image_variants TEXT,           -- JSON color/finish variations  
color_images TEXT,             -- Color-specific images
resources TEXT,                -- JSON object with PDFs and guides
collection_links TEXT,         -- JSON array of collection links
color_variations TEXT,         -- Available color options
brand TEXT,                    -- Product brand
product_category TEXT,         -- Product categorization
raw_html TEXT,                 -- Raw HTML for debugging
raw_markdown TEXT,             -- Markdown content
```

#### **3. Resource Structure Example**
```json
{
  "installation_guides": [
    {"title": "Installation Guide", "url": "https://example.com/guide.pdf"}
  ],
  "care_instructions": [
    {"title": "Care Guide", "url": "https://example.com/care.pdf"}
  ],
  "spec_sheets": [
    {"title": "Technical Specs", "url": "https://example.com/specs.pdf"}
  ],
  "warranty_info": [
    {"title": "Warranty", "url": "https://example.com/warranty.pdf"}
  ]
}
```

### 📋 **Implementation Requirements**

#### **Phase 1: Revert to Working Extraction**
1. Identify last working commit before extraction broke
2. Revert acquisition logic to working state
3. Verify basic data extraction (title, price, description, specifications)

#### **Phase 2: Reapply Schema Enhancements**
1. **Database Schema Updates**:
   - Add missing image and resource columns
   - Update product_data table structure
   - Ensure JSON field handling

2. **Extraction Logic Enhancements**:
   - Image collection and processing
   - PDF and resource document extraction
   - Color variation detection
   - Brand and category extraction

3. **Data Quality Validation**:
   - Ensure all 27+ fields are properly extracted
   - Validate JSON structure for complex fields
   - Test resource URL accessibility

### 🎯 **Critical Data Points from README**

Based on user requirements in README lines 354-368:

#### **Priority 1 - Core Commerce Data**
- Title, SKU, price/sq ft, price/box ✅ (working)
- Product variations (finish, color, size/shape options) ⚠️ (needs enhancement)

#### **Priority 2 - Content Extraction**  
- Description tab content ⚠️ (partially working)
- Specifications tab ✅ (working)
- Resources tab ❌ (broken, needs enhancement)

#### **Priority 3 - Technical Specifications**
- Dimensions, material type, thickness ✅ (working in specifications)
- Technical specifications JSON ✅ (working)

#### **Priority 4 - Enhanced Features**
- Product images and variants ❌ (needs implementation)
- PDF resources and installation guides ❌ (needs implementation)
- Collection and category links ❌ (needs implementation)

### 🔄 **Restoration Strategy**

1. **First**: Revert to working basic extraction (before speed optimization)
2. **Second**: Gradually reapply database schema enhancements
3. **Third**: Implement image and resource extraction logic
4. **Fourth**: Test comprehensive data extraction with quality validation

### 📁 **Files to Enhance Post-Reversion**

1. **`tileshop_learner.py`** - Core extraction logic
2. **`acquire_from_sitemap.py`** - Crawling and data collection
3. **`modules/db_manager.py`** - Database schema and operations
4. **Database Schema** - Add missing columns for images and resources

This documentation ensures that after reverting to working extraction logic, we can systematically reapply the valuable enhancements for comprehensive data collection including images, PDFs, and technical resources.