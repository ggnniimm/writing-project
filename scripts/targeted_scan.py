def scan_context(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 1. Line 186/188: หมู่ที่ 5, ห้วยทรายขาว
        if "ทรายขาว" in line:
            print(f"MATCH (Line {i}): {line}")
        
        # 2. Line 378: ข้อ 5, อาคาร
        if "ข้อ" in line and "อาคาร" in line:
            print(f"MATCH (Line {i}): {line}")
            
        # 3. Line 633: ร้อยละ 7.5
        if "ร้อยละ" in line:
             print(f"MATCH (Line {i}): {line}")

scan_context("part_37_vol8.txt")
