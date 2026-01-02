#!/usr/bin/env python3
"""
Analyze PDF parts to classify complexity for hybrid extraction strategy
"""

import os
import sys
import pdfplumber
import re

def analyze_page_complexity(page):
    """Analyze a single page for complexity indicators."""
    text = page.extract_text()
    
    if not text:
        return {'type': 'empty', 'score': 0}
    
    # Count complexity indicators
    tables = len(page.find_tables())
    lines = len(text.splitlines())
    numerals = len(re.findall(r'[๐-๙]+', text))
    bullets = len(re.findall(r'[•\-\*]', text))
    
    # Calculate complexity score
    score = 0
    reasons = []
    
    if tables > 0:
        score += tables * 10
        reasons.append(f"{tables} tables")
    
    if numerals > 50:
        score += (numerals - 50) // 10
        reasons.append(f"{numerals} numerals")
    
    if bullets > 20:
        score += bullets // 5
        reasons.append(f"{bullets} bullet points")
    
    # Determine type
    if score > 20:
        return {'type': 'complex', 'score': score, 'reasons': reasons}
    elif score > 5:
        return {'type': 'moderate', 'score': score, 'reasons': reasons}
    else:
        return {'type': 'simple', 'score': score, 'reasons': reasons}

def analyze_pdf_part(pdf_path):
    """Analyze all pages in a PDF part."""
    with pdfplumber.open(pdf_path) as pdf:
        pages = []
        for i, page in enumerate(pdf.pages, 1):
            analysis = analyze_page_complexity(page)
            analysis['page'] = i
            pages.append(analysis)
        
        # Overall classification
        complex_pages = sum(1 for p in pages if p['type'] == 'complex')
        moderate_pages = sum(1 for p in pages if p['type'] == 'moderate')
        simple_pages = sum(1 for p in pages if p['type'] == 'simple')
        
        total_score = sum(p['score'] for p in pages)
        avg_score = total_score / len(pages) if pages else 0
        
        # Classify part
        if avg_score > 15 or complex_pages > len(pages) / 2:
            classification = 'GEMINI'
        elif avg_score > 5:
            classification = 'MIXED'
        else:
            classification = 'PDFPLUMBER'
        
        return {
            'path': pdf_path,
            'pages': pages,
            'complex_count': complex_pages,
            'moderate_count': moderate_pages,
            'simple_count': simple_pages,
            'avg_score': avg_score,
            'classification': classification
        }

def main():
    import glob
    
    parts_dir = "etc/Academic_280125_142653_parts"
    pdf_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_280125_142653_part_*.pdf")))
    
    print("="*80)
    print("PDF COMPLEXITY ANALYSIS")
    print("="*80)
    print(f"Analyzing {len(pdf_files)} PDF parts...\n")
    
    results = []
    
    for pdf_file in pdf_files:
        part_name = os.path.basename(pdf_file).replace('.pdf', '')
        print(f"📄 {part_name}...", end=" ")
        
        result = analyze_pdf_part(pdf_file)
        results.append(result)
        
        print(f"{result['classification']} (score: {result['avg_score']:.1f})")
    
    # Summary
    print("\n" + "="*80)
    print("EXTRACTION STRATEGY")
    print("="*80)
    
    gemini_parts = [r for r in results if r['classification'] == 'GEMINI']
    pdfplumber_parts = [r for r in results if r['classification'] == 'PDFPLUMBER']
    mixed_parts = [r for r in results if r['classification'] == 'MIXED']
    
    print(f"\n📊 Classification Summary:")
    print(f"   GEMINI (complex):      {len(gemini_parts)} parts")
    print(f"   PDFPLUMBER (simple):   {len(pdfplumber_parts)} parts")
    print(f"   MIXED (review needed): {len(mixed_parts)} parts")
    
    if gemini_parts:
        print(f"\n🔬 Parts for Gemini extraction:")
        for r in gemini_parts:
            part_name = os.path.basename(r['path']).replace('.pdf', '')
            print(f"   {part_name} (complex={r['complex_count']}, score={r['avg_score']:.1f})")
    
    if pdfplumber_parts:
        print(f"\n📝 Parts for pdfplumber extraction:")
        for r in pdfplumber_parts:
            part_name = os.path.basename(r['path']).replace('.pdf', '')
            print(f"   {part_name} (simple={r['simple_count']}, score={r['avg_score']:.1f})")
    
    if mixed_parts:
        print(f"\n⚠️  Mixed parts (recommend pdfplumber with careful verification):")
        for r in mixed_parts:
            part_name = os.path.basename(r['path']).replace('.pdf', '')
            print(f"   {part_name} (complex={r['complex_count']}, moderate={r['moderate_count']}, simple={r['simple_count']})")
    
    print(f"\n{'='*80}")

if __name__ == "__main__":
    main()
