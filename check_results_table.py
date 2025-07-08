#!/usr/bin/env python3
"""
Check parsing results in table format
"""

import subprocess

def get_product_results():
    """Get results for the 5 test products"""
    
    # URLs and their SKUs
    test_products = [
        ('https://www.tileshop.com/products/superior-premium-gold-stone-sealer-pint-220434', '220434'),
        ('https://www.tileshop.com/products/goboard-pro-sealant-20-oz-350051', '350051'),
        ('https://www.tileshop.com/products/ardex-t-7-ceramic-tile-sponge-12506', '12506'),
        ('https://www.tileshop.com/products/goboard-backer-board-4-ft-x-8-ft-x-%C2%BD-in-350067', '350067'),
        ('https://www.tileshop.com/products/wedi-screw-and-washer-fastener-kit-349133', '349133')
    ]
    
    print("📊 PARSING RESULTS TABLE")
    print("=" * 160)
    
    # Table header
    header = f"{'SKU':<7} {'Title':<40} {'Brand':<12} {'Material':<12} {'Category':<10} {'SubCat':<15} {'ProdCat':<10}"
    print(header)
    print("-" * 160)
    
    for url, sku in test_products:
        # Try different SKU formats
        sku_variants = [sku, sku.zfill(6)]
        
        found = False
        for sku_variant in sku_variants:
            check_cmd = [
                'docker', 'exec', 'relational_db', 'psql', '-U', 'postgres', '-d', 'postgres', '-t', '-c',
                f"""SELECT sku, title, brand, material_type, category, subcategory, product_category 
                    FROM product_data 
                    WHERE sku = '{sku_variant}' 
                    LIMIT 1;"""
            ]
            
            try:
                result = subprocess.run(check_cmd, capture_output=True, text=True, check=True)
                output = result.stdout.strip()
                
                if output and output != '(0 rows)':
                    parts = [p.strip() for p in output.split('|')]
                    if len(parts) >= 7:
                        db_sku = parts[0][:7]
                        title = parts[1][:40] 
                        brand = parts[2][:12] if parts[2] else 'None'
                        material = parts[3][:12] if parts[3] else 'None'
                        category = parts[4][:10] if parts[4] else 'None'
                        subcategory = parts[5][:15] if parts[5] else 'None'
                        product_cat = parts[6][:10] if parts[6] else 'None'
                        
                        row = f"{db_sku:<7} {title:<40} {brand:<12} {material:<12} {category:<10} {subcategory:<15} {product_cat:<10}"
                        print(row)
                        found = True
                        break
                        
            except subprocess.CalledProcessError:
                continue
        
        if not found:
            row = f"{sku:<7} {'NOT FOUND IN DATABASE':<40} {'---':<12} {'---':<12} {'---':<10} {'---':<15} {'---':<10}"
            print(row)
    
    print("-" * 160)
    
    # Expected results for comparison
    print("\n📋 EXPECTED RESULTS")
    print("=" * 160)
    
    expected = [
        ('220434', 'Superior Premium Gold Stone Sealer', 'Superior', 'sealer/chem', 'care_maint', 'cleaners', 'Sealer'),
        ('350051', 'GoBoard Pro Sealant', 'GoBoard', 'silicone', 'install_mat', 'caulk_seal', 'Sealer'), 
        ('12506', 'Ardex T-7 Ceramic Tile Sponge', 'Ardex', 'synthetic', 'tools', 'install_acc', 'Tool'),
        ('350067', 'GoBoard Backer Board', 'GoBoard', 'polystyrene', 'install_mat', 'substrate', 'Substrate'),
        ('349133', 'Wedi Screw and Washer Kit', 'Wedi', 'metal', 'tools', 'install_acc', 'Tool')
    ]
    
    header = f"{'SKU':<7} {'Expected Title':<40} {'Brand':<12} {'Material':<12} {'Category':<10} {'SubCat':<15} {'ProdCat':<10}"
    print(header)
    print("-" * 160)
    
    for exp in expected:
        row = f"{exp[0]:<7} {exp[1]:<40} {exp[2]:<12} {exp[3]:<12} {exp[4]:<10} {exp[5]:<15} {exp[6]:<10}"
        print(row)
    
    print("-" * 160)

if __name__ == "__main__":
    get_product_results()