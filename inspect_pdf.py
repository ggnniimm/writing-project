
lines = open("part_08_pdf.txt").readlines()
print("--- PDF Text Lines 350-500 ---")
for i, line in enumerate(lines[350:500]):
    print(f"{350+i}: {line.strip()}")
