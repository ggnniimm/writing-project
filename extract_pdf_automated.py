#!/usr/bin/env python3
"""
Automated PDF Extractor using Playwright
Bypasses WAF and download dialogs by extracting PDF directly from browser memory
"""
import asyncio
import base64
from playwright.async_api import async_playwright

async def extract_pdf_from_browser():
    pdf_url = "https://www.admincourt.go.th/admincourt/Casefile/admcase/document/signed/pdf/2557/01012-570747-1f-601129-0000610732.pdf"
    output_path = "raw_pdfs/sac_o_1148_2560.pdf"
    
    print(f"🌐 Opening browser to: {pdf_url}")
    
    async with async_playwright() as p:
        # Launch browser (use chromium for better compatibility)
        browser = await p.chromium.launch(headless=False)  # Non-headless to bypass some WAF
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Navigate to PDF
            print("📄 Loading PDF...")
            await page.goto(pdf_url, wait_until="networkidle", timeout=60000)
            
            # Wait a bit for PDF to fully load
            await asyncio.sleep(3)
            
            # Extract PDF as base64 using JavaScript
            print("🔄 Extracting PDF data from browser memory...")
            base64_data = await page.evaluate("""
                async () => {
                    const response = await fetch(window.location.href);
                    const blob = await response.blob();
                    return new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            // Remove "data:application/pdf;base64," prefix
                            const base64 = reader.result.split(',')[1];
                            resolve(base64);
                        };
                        reader.onerror = reject;
                        reader.readAsDataURL(blob);
                    });
                }
            """)
            
            # Decode base64 to binary
            print("📦 Decoding base64 data...")
            pdf_binary = base64.b64decode(base64_data)
            
            # Write to file
            print(f"💾 Writing to: {output_path}")
            with open(output_path, 'wb') as f:
                f.write(pdf_binary)
            
            file_size_mb = len(pdf_binary) / (1024 * 1024)
            print(f"\n✅ SUCCESS!")
            print(f"📏 File size: {len(pdf_binary):,} bytes ({file_size_mb:.2f} MB)")
            
            # Verify it's a PDF
            if pdf_binary[:4] == b'%PDF':
                print("✓ Valid PDF file confirmed")
            else:
                print("⚠️ Warning: File may not be a valid PDF")
                print(f"First bytes: {pdf_binary[:20]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(extract_pdf_from_browser())
