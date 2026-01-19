def scan_file(path, keywords):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Scanning {path} ({len(lines)} lines)...")
    for i, line in enumerate(lines):
        line = line.strip()
        # Check standard
        for kw in keywords:
            # Create a "spaced" regex for the keyword
            # e.g. "หาด" -> "ห.*า.*ด"
            pattern = ".*".join(list(kw))
            if re.search(pattern, line):
                 print(f"[{i}] {line}")

import re
keywords = ["หาด", "ปลูก", "ร้อย"]
scan_file("part_37_vol8.txt", keywords)
