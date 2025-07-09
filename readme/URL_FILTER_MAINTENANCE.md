# 🔧 URL Filter Maintenance Guide

## Overview
This guide documents the URL filtering system used in the TileShop scraping platform and provides maintenance procedures for updating filter criteria.

## Current Filter Criteria

### ✅ Include URLs that contain:
- `tileshop.com/products` (main product pages)

### ❌ Exclude URLs that contain:
- `tileshop.com/products/,-w-,` (special collection URLs)
- `https://www.tileshop.com/products/` (directory page)
- `sample` (sample pages)

## Filter Logic Implementation

The URL filtering logic is implemented in multiple files using identical patterns:

```python
if ("tileshop.com/products" in url and 
    "https://www.tileshop.com/products/,-w-," not in url and
    "https://www.tileshop.com/products/" not in url and
    "sample" not in url):
    # URL is accepted for processing
```

## File Locations Requiring Updates

When modifying filter criteria, **ALL** of the following files must be updated:

### 1. Core Scraping Files
- **`download_sitemap.py`** (lines 62-65)
  - Function: `filter_product_urls()`
  - Primary sitemap filtering logic

- **`dashboard_app.py`** (lines 684-687)
  - Function: sitemap processing route
  - Dashboard backend filtering

- **`acquire_all_products.py`** (lines 51-54)
  - Function: `filter_product_urls()`
  - Batch acquisition filtering

### 2. Dashboard Display
- **`templates/dashboard.html`** (lines 624-628)
  - Visual display of current filter criteria
  - Must be updated to reflect changes

## Maintenance Procedures

### Adding New Exclusion Pattern

1. **Update Python files** (3 locations):
   ```python
   # Add new exclusion condition
   if ("tileshop.com/products" in url and 
       "https://www.tileshop.com/products/,-w-," not in url and
       "https://www.tileshop.com/products/" not in url and
       "new_exclusion_pattern" not in url and  # NEW LINE
       "sample" not in url):
   ```

2. **Update dashboard template**:
   ```html
   • <code>new_exclusion_pattern</code> (description)<br>
   ```

3. **Update documentation** (this file)

### Recent Changes

#### 2025-07-08: Added Directory Page Exclusion
- **Problem**: `https://www.tileshop.com/products/` was causing scraping errors
- **Solution**: Added exclusion pattern for directory page URL
- **Impact**: Prevents "NoneType object is not subscriptable" errors
- **Files Updated**: All 4 locations listed above

## Error Prevention

### Common Issues:
1. **Inconsistent Updates**: Forgetting to update all 4 file locations
2. **Syntax Errors**: Incorrect boolean logic in filter conditions
3. **Display Mismatch**: Dashboard showing outdated filter criteria

### Best Practices:
- Always update ALL 4 files when changing filter criteria
- Test filter logic with sample URLs before deployment
- Verify dashboard display matches actual filtering logic
- Document all changes in this maintenance guide

## Testing Filter Changes

After updating filter criteria:

1. **Test with sample URLs**:
   ```python
   test_urls = [
       "https://www.tileshop.com/products/sample-tile",
       "https://www.tileshop.com/products/",
       "https://www.tileshop.com/products/valid-tile-123"
   ]
   ```

2. **Verify dashboard display** matches implemented logic

3. **Check scraping logs** for reduced error rates

## Technical Notes

- Filter logic originated from **n8n workflow** implementation
- All files use identical boolean logic for consistency
- Comments reference original n8n workflow source
- No centralized configuration system currently exists

## Future Improvements

### Recommended Enhancements:
1. **Centralized Configuration**: Create single config file for all filter criteria
2. **Dynamic Updates**: Allow filter changes without code modification
3. **Regex Support**: More flexible pattern matching
4. **Filter Statistics**: Track effectiveness of each exclusion pattern

## Contact Information

For questions about URL filtering or maintenance procedures, refer to:
- **Dashboard**: http://127.0.0.1:8080 (filter criteria display)
- **Logs**: `dashboard.log` (filter application results)
- **Documentation**: `readme/INDEX.md` (complete file listing)