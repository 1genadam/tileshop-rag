# The Tile Shop Product Page Structure Analysis

## Overview
This analysis examines the HTML structure of different product page types on tileshop.com to understand how they differ and identify patterns for specialized parsers.

## Product Page Types Analyzed

### 1. Marble Tile Page
**Example URL:** https://www.tileshop.com/products/volakas-honed-marble-wall-and-floor-tile-12-x-24-in.-681294

#### JSON-LD Structured Data
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Volakas Honed Marble Wall and Floor Tile - 12 x 24 in.",
  "price": "$287.04",
  "brand": "Rush River",
  "availability": "InStock"
}
```

#### Product Specifications Format
- **Dimensions:** 12 x 24 in.
- **Material:** Marble
- **Origin:** Greece
- **Finish:** Honed
- **Coverage:** 12.02 sq. ft. per Box
- **Box Weight:** 72.2 lbs

#### Price Display Pattern
- **Per Box pricing:** $287.04
- **Coverage-based:** Price includes sq. ft. coverage information
- **Currency:** USD explicitly stated

#### Image Structure
- **CDN:** scene7.com domain
- **Naming:** Product code (681294) + descriptive suffix
- **Types:** Product shots, installation views, lifestyle images

#### Navigation Breadcrumbs
- Simple two-level: Home > Product
- Structured as JSON-LD BreadcrumbList

#### Resources Available
- **Safety Data Sheet:** PDF available
- **URL Pattern:** https://s7d1.scene7.com/is/content/TileShop/pdf/safety-data-sheets/natural_stone_tile_sds_01012019.pdf

#### Unique Identifiers
- Product code in URL and throughout page
- Natural stone specific safety documentation
- Coverage and weight specifications prominent

---

### 2. Grout Product Page
**Example URL:** https://www.tileshop.com/products/superior-sanded-pro-grout-natural-25-lb-052001

#### JSON-LD Structured Data
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Superior Sanded Pro-Grout Natural - 25 lb",
  "price": "$24.29",
  "brand": "Superior",
  "sku": "052001"
}
```

#### Product Specifications Format
- **Approximate Size:** 25 lbs (weight-based)
- **Brand:** Superior
- **Color:** Grey
- **Directional Layout:** No

#### Price Display Pattern
- **Per unit pricing:** $24.29
- **Weight-based:** Price is per package/weight
- **No coverage calculation**

#### Image Structure
- **CDN:** scene7.com
- **Naming:** Product code (052001) + size parameter
- **URL Pattern:** https://tileshop.scene7.com/is/image/TileShop/052001?$ExtraLarge$

#### Navigation Breadcrumbs
- Home > Product navigation
- JSON-LD structured

#### Resources Available
- **Safety Data Sheet:** PDF
- **Product Data Sheet:** PDF
- **Sell Sheet:** PDF
- **Multiple documentation types**

#### Unique Identifiers
- Weight-based specifications
- Color as primary differentiator
- Multiple PDF resources (3 types)

---

### 3. Trim/Molding Product Page
**Example URL:** https://www.tileshop.com/products/andover-bayhill-blonde-luxury-vinyl-floor-tile-t-molding-1-77-x-94-in-682003

#### JSON-LD Structured Data
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Andover Bayhill Blonde® Luxury Vinyl Floor Tile T-Molding - 1.77 x 94 in.",
  "price": "$51.09",
  "sku": "682003"
}
```

#### Product Specifications Format
- **Dimensions:** 1.77 x 94 in. (length emphasis)
- **Box Quantity:** 20 pieces
- **Box Weight:** 52.9 lbs
- **Material Type:** Luxury Vinyl
- **Color:** Brown
- **Finish:** Matte
- **Country of Origin:** China

#### Price Display Pattern
- **Per box pricing:** $51.09
- **Quantity-based:** Box contains multiple pieces
- **Linear measurement focus**

#### Image Structure
- **CDN:** scene7.com
- **Naming:** Product code (682003)
- **URL Pattern:** https://tileshop.scene7.com/is/image/TileShop/682003

#### Navigation Breadcrumbs
- Home > Product structure
- JSON-LD BreadcrumbList

#### Resources Available
- **Installation Guidelines:** PDF
- **URL Pattern:** https://s7d1.scene7.com/is/content/TileShop/pdf/product-data-sheets/TTS_LVT_MSI_T_Molding_Installation_Guidelines.pdf

#### Unique Identifiers
- T-Molding specific product type
- Linear dimensions (length x width)
- Installation-focused documentation

---

### 4. Luxury Vinyl/Wood-Look Product Page
**Example URL:** https://www.tileshop.com/products/arbour-midlands-driftwood-oak-luxury-vinyl-tile-71-x-48-in-683847

#### JSON-LD Structured Data
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Arbour Midlands Driftwood Oak Luxury Vinyl Plank - 7.1 x 48 in.",
  "price": "$66.08",
  "sku": "683847"
}
```

#### Product Specifications Format
- **Dimensions:** 7.1 x 48 in.
- **Thickness:** 6mm
- **Wear Layer:** 22 MIL
- **Coverage:** 18.93 sq. ft. per Box
- **Material Type:** Luxury Vinyl
- **Installation:** Floating Click-And-Lock

#### Price Display Pattern
- **Per box pricing:** $66.08
- **Coverage included:** 18.93 sq. ft. per Box
- **Technical specifications prominent**

#### Image Structure
- **CDN:** scene7.com
- **Naming:** Product code + descriptive suffix
- **Example:** 683847_vendor_render_livingroom
- **Multiple lifestyle images**

#### Navigation Breadcrumbs
- Hierarchical navigation
- JSON-LD BreadcrumbList structure

#### Resources Available
- **Limited PDF documentation**
- **Focus on installation method**

#### Unique Identifiers
- Wear layer specifications (MIL)
- Click-and-lock installation method
- Wood-look appearance descriptors

---

### 5. Installation Product/Tool Page
**Example URL:** https://www.tileshop.com/products/goboard-backer-board-4-ft-x-8-ft-x-%C2%BD-in-350067

#### JSON-LD Structured Data
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "GoBoard Backer Board - 4 ft. x 8 ft. x ½ in.",
  "price": "$50.99",
  "sku": "350067"
}
```

#### Product Specifications Format
- **Dimensions:** 4 ft. x 8 ft. x ½ in.
- **Box Quantity:** 1 piece
- **Box Weight:** 4.7 lbs
- **Brand:** GoBoard
- **Country of Origin:** USA

#### Price Display Pattern
- **Per piece pricing:** $50.99
- **Single unit sales**
- **Lightweight emphasis**

#### Image Structure
- **CDN:** scene7.com
- **Naming:** Product code only (350067)
- **Size parameter:** $ExtraLarge$

#### Navigation Breadcrumbs
- Minimal structure
- Home > Product Name

#### Resources Available
- **Limited documentation**
- **Technical specifications in description**

#### Unique Identifiers
- Installation/construction product
- Waterproof properties emphasized
- Single-piece packaging

---

## Key Structural Differences Summary

### 1. Pricing Patterns
- **Tiles:** Per box with coverage (sq. ft.)
- **Grout:** Per package with weight
- **Trim:** Per box with piece count
- **Vinyl:** Per box with coverage and technical specs
- **Tools:** Per piece with dimensional specs

### 2. Specification Focus
- **Tiles:** Material origin, finish, coverage
- **Grout:** Weight, color, texture (sanded/unsanded)
- **Trim:** Linear dimensions, installation method
- **Vinyl:** Wear layer, thickness, installation system
- **Tools:** Dimensions, weight, technical properties

### 3. Documentation Patterns
- **Tiles:** Safety Data Sheets (especially natural stone)
- **Grout:** Multiple PDFs (Safety, Product Data, Sell Sheet)
- **Trim:** Installation Guidelines
- **Vinyl:** Limited documentation
- **Tools:** Technical specifications in description

### 4. Image Naming Conventions
- **Standard:** Product code + size parameter
- **Enhanced:** Product code + descriptive suffix (lifestyle images)
- **CDN:** Consistent scene7.com usage
- **Sizing:** $ExtraLarge$ parameter common

### 5. JSON-LD Structure
- **Consistent:** All pages use schema.org Product type
- **Variable:** Brand, SKU, availability status
- **Pricing:** All include price and currency
- **Breadcrumbs:** Consistent BreadcrumbList structure

## Unique Page Type Identifiers

### CSS Classes and Data Attributes
- **Product codes:** 6-digit numerical codes in URLs
- **Material types:** Referenced in specifications
- **Installation methods:** Mentioned in vinyl products
- **Weight vs. Coverage:** Different measurement focus

### Distinguishing Selectors
1. **Tile Pages:** 
   - Coverage information (sq. ft.)
   - Material origin specifications
   - Safety data sheets for natural stone

2. **Grout Pages:**
   - Weight-based specifications
   - Color as primary differentiator
   - Multiple PDF document types

3. **Trim Pages:**
   - Linear dimensions (length emphasis)
   - Installation guidelines
   - T-molding, bullnose terminology

4. **Vinyl Pages:**
   - Wear layer specifications
   - Click-and-lock installation
   - Thickness measurements

5. **Tool Pages:**
   - Single-piece packaging
   - Technical property emphasis
   - Installation/construction terminology

## Parser Design Recommendations

### 1. URL Pattern Recognition
- Use 6-digit product codes for initial categorization
- Implement fallback content-based detection

### 2. Specification Parsing
- Create separate parsers for each measurement type:
  - Coverage-based (tiles, vinyl)
  - Weight-based (grout)
  - Linear dimension-based (trim)
  - Technical specification-based (tools)

### 3. Resource Extraction
- Implement PDF link detection with type classification
- Pattern match for Scene7 CDN image URLs
- Extract multiple image variants when available

### 4. Price Normalization
- Detect pricing unit (per box, per piece, per weight)
- Extract coverage information when available
- Calculate per-unit pricing where applicable

### 5. Content Classification
- Use keyword detection for material types
- Implement installation method recognition
- Create category-specific validation rules

This analysis provides the foundation for creating specialized parsers that can handle the unique characteristics of each product type on The Tile Shop website.