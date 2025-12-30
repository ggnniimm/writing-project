import sys
import os
import pypdf

def split_pdf(path):
    reader = pypdf.PdfReader(path)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    mid = total_pages // 2
    
    writer1 = pypdf.PdfWriter()
    for i in range(mid):
        writer1.add_page(reader.pages[i])
        
    writer2 = pypdf.PdfWriter()
    for i in range(mid, total_pages):
        writer2.add_page(reader.pages[i])
        
    base = os.path.splitext(path)[0]
    p1 = f"{base}_part1.pdf"
    p2 = f"{base}_part2.pdf"
    
    with open(p1, "wb") as f:
        writer1.write(f)
    print(f"Created {p1}")
    
    with open(p2, "wb") as f:
        writer2.write(f)
    print(f"Created {p2}")

if __name__ == "__main__":
    split_pdf(sys.argv[1])
