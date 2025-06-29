#!/bin/bash
# Extract HTML content to file for analysis
docker exec n8n-postgres psql -U postgres -t -c "SELECT raw_html FROM product_data WHERE sku = '484963';" > /tmp/tileshop_sample.html