
import sys

def dump_line(path, lineno):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if lineno - 1 < len(lines):
            line = lines[lineno - 1]
            print(f"Line {lineno}: {line}")
            print("Codepoints:")
            for char in line:
                print(f"'{char}' : {ord(char)}")

if __name__ == "__main__":
    dump_line(sys.argv[1], int(sys.argv[2]))
