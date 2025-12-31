
import os
from pypdf import PdfReader, PdfWriter

def extract_text_page(page):
    return page.extract_text()

def recover_part_25():
    source_pdf = "etc/ref_research_admin_court_rulings_digest_v14_2569.pdf"
    output_pdf = "etc/split_v14_2569_40/part_25.pdf"
    
    reader = PdfReader(source_pdf)
    
    # Confirmed Part 26 Start is 525 (Page 542)
    p26_start_index = 525
    p25_end_index = p26_start_index - 1
    
    print(f"Assuming Part 25 End Index: {p25_end_index}")
    
    # Search for Part 24 End
    # Text: "เรียกให้นาย ว."
    p24_end_index = -1
    for i in range(500, 525):
        text = extract_text_page(reader.pages[i])
        if "เรียกให้นาย ว." in text:
            print(f"Found Part 24 End text at Index {i}")
            p24_end_index = i
            break
            
    if p24_end_index == -1:
        print("Could not find Part 24 End. Trying alternative text 'การกระทำของผู ้ ฟ ้ อ งคดี จ ึ ง เป็ น'")
        for i in range(500, 525):
            text = extract_text_page(reader.pages[i])
            # The text had spaces in pdftotext output: "ผู ้ ฟ ้ อ งคดี"
            # Try a partial match
            if "กระทำโดยประมาทเลินเล่อ" in text:
                 print(f"Found Part 24 End text (alt) at Index {i}")
                 p24_end_index = i
                 break
    
    if p24_end_index != -1:
        p25_start_index = p24_end_index + 1
        print(f"Part 25 Range: {p25_start_index} to {p25_end_index}")
        
        writer = PdfWriter()
        for i in range(p25_start_index, p25_end_index + 1):
            writer.add_page(reader.pages[i])
            
        with open(output_pdf, "wb") as f:
            writer.write(f)
        print(f"✅ Recovered {output_pdf}")
    else:
        print("❌ Failed to find Part 24 End.")

if __name__ == "__main__":
    recover_part_25()
