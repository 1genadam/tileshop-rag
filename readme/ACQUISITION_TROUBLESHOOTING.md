# Acquisition Control Troubleshooting Guide

## Issue: Acquisition Counters Not Resetting to Zero

### Problem Description
After downloading a fresh sitemap, the acquisition control dashboard shows non-zero values for processed, successful, and error counts when they should all be at 0.

**Example:**
- Sitemap: 4,778 URLs discovered (fresh download)
- Dashboard shows: "Processed: 12 / 4778, Successful: 2, Errors: 10"
- Expected: "Processed: 0 / 4778, Successful: 0, Errors: 0"

### Root Cause
The acquisition dashboard combines data from multiple sources:

1. **PostgreSQL Database** - Contains products from previous scraping sessions
2. **Sitemap JSON File** - Tracks URL processing status ("pending", "completed", "failed")
3. **Recovery Checkpoint** - Maintains session recovery information
4. **Intelligence Manager** - Calculates statistics by mixing database and sitemap data

When starting fresh, old database records create inconsistent statistics.

### Data Sources Location

| Component | File/Location | Purpose |
|-----------|---------------|---------|
| Product Database | PostgreSQL `product_data` table | Stores scraped product information |
| Sitemap Status | `tileshop_sitemap.json` | URL processing status tracking |
| Recovery Data | `recovery_checkpoint.json` | Session recovery and progress |
| Scraper Status | `/tmp/tileshop_scraper_status.json` | Real-time processing status |

### Solution: Reset All Counters

To reset acquisition counters to zero for a fresh start:

#### Step 1: Clear Database
```bash
# Remove all products from previous sessions
docker exec relational_db psql -U postgres -c "DELETE FROM product_data;"
```

#### Step 2: Remove Recovery Files
```bash
# Clear recovery checkpoint
rm -f recovery_checkpoint.json

# Clear temporary scraper status
rm -f /tmp/tileshop_scraper_status.json
```

#### Step 3: Verify Sitemap Status
```bash
# Check that sitemap has all URLs marked as "pending"
python -c "
import json
with open('tileshop_sitemap.json', 'r') as f:
    data = json.load(f)
    pending = sum(1 for url in data['urls'] if url['status'] == 'pending')
    total = len(data['urls'])
    print(f'Pending: {pending}/{total}')
"
```

#### Step 4: Restart Dashboard
```bash
# Restart the dashboard to refresh statistics
python reboot_dashboard.py
```

### Verification

After reset, the acquisition control should show:
- **Processed: 0 / [total_urls]**
- **Successful: 0**
- **Errors: 0**
- **Pending: [total_urls]**

### Prevention

To avoid this issue in the future:

1. **Always clear database** when starting a new complete scraping session
2. **Use incremental mode** only when continuing an interrupted session
3. **Monitor recovery files** - delete them when starting fresh

### Technical Details

#### Dashboard Statistics Calculation

The dashboard calculates statistics in `/api/acquisition/status` endpoint:

```python
# From modules/intelligence_manager.py
def _enhance_stats_with_sitemap(self):
    # Combines database count with sitemap status
    # Can cause inconsistencies when database has old data
```

#### File Locations

- **Main Dashboard**: `reboot_dashboard.py`
- **Intelligence Manager**: `modules/intelligence_manager.py`
- **Sitemap Processing**: `download_sitemap.py`
- **Database Manager**: `modules/db_manager.py`

#### API Endpoints

- `GET /api/acquisition/status` - Current processing statistics
- `GET /api/acquisition/sitemap-status` - Sitemap progress summary
- `POST /api/acquisition/start` - Begin acquisition process

### Related Issues

- **Database/Sitemap URL Count Mismatch**: Normal variation due to sitemap changes
- **Recovery File Corruption**: Delete recovery files and restart fresh
- **Container Health**: Ensure PostgreSQL container is running before clearing database

### Emergency Reset

If the system becomes inconsistent:

```bash
# Nuclear option - reset everything
docker exec relational_db psql -U postgres -c "TRUNCATE product_data CASCADE;"
rm -f recovery_checkpoint.json /tmp/tileshop_scraper_status.json
python download_sitemap.py  # Re-download fresh sitemap
python reboot_dashboard.py  # Restart dashboard
```

---

## Issue: Product Fields Not Parsing (Edge Type, Box Quantity, Product Category)

### Problem Description
Product fields like Edge Type, Box Quantity, Material Type, and Product Category show as null in the dashboard despite being available on the product pages.

**Example:**
- Page shows: "Edge Type: Rectified", "Box Quantity: 6"  
- Dashboard shows: edge_type: null, box_quantity: null, product_category: null

### Root Cause
Multiple parsing system components can cause missing fields:

1. **Incorrect JSON Patterns**: Tileshop uses `{"Key":"PDPInfo_BoxQuantity","Value":"6"}` structure
2. **Overly Strict Validation**: Valid data filtered as "corrupted" (e.g., "Rectified" rejected)
3. **Missing Database Schema**: Fields extracted but not included in INSERT statements
4. **Skipped URL Processing**: Previously processed URLs marked as "completed" are skipped

### Solution Steps

#### Step 1: Verify Extraction Patterns
Check patterns in `enhanced_specification_extractor.py`:
```python
# Correct JSON patterns for Tileshop
"box_quantity": [
    r'"Key"\s*:\s*"PDPInfo_BoxQuantity"[^}]*"Value"\s*:\s*"([^"]+)"',  # Priority
    r'"PDPInfo_BoxQuantity"[^}]*"Value"\s*:\s*"([^"]+)"',
]

"edge_type": [
    r'"Key"\s*:\s*"PDPInfo_EdgeType"[^}]*"Value"\s*:\s*"([^"]+)"',  # Priority  
    r'"PDPInfo_EdgeType"[^}]*"Value"\s*:\s*"([^"]+)"',
]
```

#### Step 2: Fix Validation Logic
Add valid value bypasses in `_clean_specifications()`:
```python
# Allow valid edge type values regardless of other validation
if field.lower() in ['edge_type', 'edgetype'] and value.lower() in ['rectified', 'pressed', 'natural', 'polished']:
    cleaned[field] = value
    continue

# Allow valid product category values
if field.lower() in ['product_category', 'category'] and value.lower() in ['tile', 'tiles', 'grout', 'trim']:
    cleaned[field] = value  
    continue
```

#### Step 3: Verify Database Schema
Ensure all fields are in the INSERT statement (`tileshop_learner.py`):
```sql
INSERT INTO product_data (
    -- ... other fields ...
    box_quantity, edge_type, material_type, product_category,
    scraped_at
) VALUES (
    -- ... corresponding values ...
)
ON CONFLICT (url) DO UPDATE SET
    box_quantity = EXCLUDED.box_quantity,
    edge_type = EXCLUDED.edge_type,
    material_type = EXCLUDED.material_type,
    product_category = EXCLUDED.product_category,
    -- ... other updates ...
```

#### Step 4: Force Re-processing
To test fixes on existing products, reset their status:
```python
# Reset specific URL to pending for re-processing
python -c "
import json
with open('tileshop_sitemap.json', 'r') as f:
    data = json.load(f)
for url_entry in data['urls']:
    if 'YOUR_SKU' in url_entry['url']:
        url_entry['scrape_status'] = 'pending'
        url_entry['scraped_at'] = None
        break
with open('tileshop_sitemap.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# Then re-process
python acquire_from_sitemap.py 1
```

### Verification
Check database after re-processing:
```sql
SELECT sku, edge_type, product_category, box_quantity, material_type 
FROM product_data WHERE sku = 'YOUR_SKU';
```

### Common Patterns Fixed
- **PDPInfo JSON Structure**: `{"Key":"PDPInfo_FieldName","Value":"actual_value"}`
- **Edge Type Values**: "Rectified", "Pressed", "Natural", "Polished"  
- **Product Categories**: Extracted from titles (e.g., "Tile" from "Porcelain Wall and Floor Tile")
- **Box Quantities**: Numeric values from specifications section

---

*This guide addresses acquisition control statistics inconsistencies and product field parsing issues.*