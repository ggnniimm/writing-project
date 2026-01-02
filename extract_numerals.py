
import sys
import re
import pdfplumber

def extract_numerals(text):
    return re.findall(r'[๐-๙]+', text)

def main(file_path):
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += (page.extract_text() or '') + '\n'
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    numerals = extract_numerals(text)
    for num in numerals:
        print(num)

if __name__ == '__main__':
    main(sys.argv[1])
