# Tileshop Product Parsing Fixes - July 8, 2025

## Issues Resolved

Fixed critical parsing issues where product specifications were not being extracted from Tileshop product pages, specifically:

1. **Edge Type** - Previously showing null, now correctly extracts "Rectified"
2. **Box Quantity** - Previously showing null, now correctly extracts numeric values like "6"  
3. **Product Category** - Previously showing null, now correctly extracts "Tile" from product titles
4. **Material Type** - Already working, enhanced validation to prevent future issues

## Root Causes Identified

1. **Incorrect JSON Pattern Matching**: Tileshop uses `{"Key":"PDPInfo_FieldName","Value":"actual_value"}` structure
2. **Overly Strict Validation**: Valid data like "Rectified" was being filtered as corrupted due to broad pattern `'ed'`
3. **Missing Database Fields**: `product_category` was extracted but not included in INSERT/UPDATE statements
4. **URL Processing Logic**: Previously processed URLs marked as "completed" were being skipped during re-processing

## Technical Changes Made

### enhanced_specification_extractor.py
- **Fixed Box Quantity patterns**: Added correct JSON pattern `r'"Key"\s*:\s*"PDPInfo_BoxQuantity"[^}]*"Value"\s*:\s*"([^"]+)"'`
- **Fixed Edge Type patterns**: Added correct JSON pattern `r'"Key"\s*:\s*"PDPInfo_EdgeType"[^}]*"Value"\s*:\s*"([^"]+)"'`
- **Fixed Material Type patterns**: Added correct JSON pattern `r'"Key"\s*:\s*"PDPInfo_MaterialType"[^}]*"Value"\s*:\s*"([^"]+)"'`
- **Removed problematic validation**: Removed overly broad `'ed'` pattern from corrupted data filters
- **Added validation bypasses**: Valid edge types and product categories now bypass corruption filtering
- **Added product category extraction**: `_extract_category_from_title()` method extracts categories from product titles
- **Enhanced trim detection**: Added comprehensive trim keywords (GL, Great Lakes, L-channel, round edge, box edge, Somerset, Durand)

### tileshop_learner.py
- **Added product title parameter**: Pass product title to `extract_specifications()` for category extraction
- **Enhanced field mappings**: Added direct mappings for `box_quantity`, `edge_type`, `product_category`
- **Fixed database schema**: Added `product_category` to INSERT and UPDATE statements
- **Ensured proper field handling**: All extracted fields now properly saved to database

## Testing Results

Verified with SKU 684287 (Marmi Imperiali Zenobia Porcelain Wall and Floor Tile):

**Before:**
```sql
sku | edge_type | product_category | box_quantity | material_type
684287 |         |                  |              | porcelain
```

**After:**
```sql
sku | edge_type | product_category | box_quantity | material_type  
684287 | Rectified | Tile             |            6 | porcelain
```

## Documentation Updates

- **Updated ACQUISITION_TROUBLESHOOTING.md**: Added comprehensive section for "Product Fields Not Parsing" with step-by-step troubleshooting guide
- **Added parsing patterns examples**: Documented correct JSON structures and validation logic
- **Included verification steps**: SQL queries and testing procedures for future troubleshooting

## Validation Process

To ensure existing products get updated with fixed parsing:

1. **Reset URL status**: Change `scrape_status` from "completed" to "pending" in sitemap
2. **Re-process products**: Run `python acquire_from_sitemap.py 1` to test single product
3. **Verify database**: Check that all fields are properly populated
4. **Batch processing**: Can now safely run full acquisition with corrected parsing

## Impact

- **Immediate**: SKU 684287 and similar products now show complete specification data
- **Future**: All new product acquisitions will correctly extract Edge Type, Box Quantity, and Product Category
- **System reliability**: Reduced false positive corruption filtering
- **Troubleshooting**: Comprehensive documentation for future similar issues

## Files Modified

1. `enhanced_specification_extractor.py` - Core parsing logic fixes
2. `tileshop_learner.py` - Database save logic and field mapping fixes  
3. `readme/ACQUISITION_TROUBLESHOOTING.md` - Documentation updates
4. `parsing-fixes-2025-07-08.md` - This progress report

## Additional Fixes - Pricing Logic and Field Deduplication

### Pricing Logic Enhancement
**Issue**: Incorrect price_per_piece logic when both box and sqft pricing exist
- Standard tiles with both `$77.11/box` and `$12.99/Sq. Ft.` were incorrectly showing `price_per_piece: $77.11`
- Per-piece products like trim pieces were showing both `price_per_box` and `price_per_piece` values

**Solution**: Enhanced final pricing consolidation logic in `tileshop_learner.py`:
```python
# Standard tile products: Both box + sqft → price_per_piece = null
if price_per_box is not None and price_per_sqft is not None:
    data['price_per_piece'] = None

# Per-piece products: price_per_piece exists + no sqft → price_per_box = null  
elif price_per_piece is not None and price_per_sqft is None and price_per_box is not None:
    data['price_per_box'] = None
```

**Results**:
- SKU 684287 (Standard Tile): `price_per_box: $77.11, price_per_sqft: $12.98, price_per_piece: null` ✓
- SKU 684272 (Per-Piece Trim): `price_per_box: null, price_per_sqft: null, price_per_piece: $69.99` ✓

### Field Deduplication Fix
**Issue**: Edge type appeared twice as both `edge_type` and `edgetype` with same value "Rectified"

**Solution**: Added deduplication logic in `enhanced_specification_extractor.py`:
```python
# Remove duplicate edge type fields - keep only 'edge_type', remove 'edgetype'
if 'edgetype' in cleaned and 'edge_type' in cleaned:
    del cleaned['edgetype']
```

**Result**: Only `edge_type: "Rectified"` appears in specifications

### Testing Validation
- **Standard Tile (684287)**: ✅ Correct box+sqft pricing, null price_per_piece
- **Per-Piece Product (684272)**: ✅ Only price_per_piece populated, others null
- **Edge Type**: ✅ No more duplicates, single clean field

---

*Fixes validated and documented on July 8, 2025*