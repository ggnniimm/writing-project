#!/usr/bin/env python3
import requests

url = "https://www.admincourt.go.th/admincourt/Casefile/admcase/document/signed/pdf/2557/01012-570747-1f-601129-0000610732.pdf"
output_path = "raw_pdfs/sac_judge_1148_2560.pdf"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

print(f"📥 Downloading from: {url}")
response = requests.get(url, headers=headers, timeout=30)

print(f"📊 Status Code: {response.status_code}")
print(f"📦 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
print(f"📏 Content Length: {len(response.content)} bytes")

if response.status_code == 200:
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ Saved to: {output_path}")
    
    # Verify file
    import os
    file_size = os.path.getsize(output_path)
    print(f"✓ File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Check if it's actually a PDF
    with open(output_path, 'rb') as f:
        magic = f.read(4)
        if magic.startswith(b'%PDF'):
            print("✓ Valid PDF file confirmed")
        else:
            print(f"⚠️  Warning: File does not start with PDF magic bytes. Got: {magic}")
else:
    print(f"❌ Download failed with status code: {response.status_code}")
    print(f"Response preview: {response.text[:500]}")
