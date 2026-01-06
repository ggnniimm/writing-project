import os

def combine_parts(source_dir, output_file, num_parts):
    print(f"🚀 Combining {num_parts} parts from {source_dir} into {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i in range(1, num_parts + 1):
            part_filename = f"part_{i:02d}.md"
            part_path = os.path.join(source_dir, part_filename)
            
            if not os.path.exists(part_path):
                print(f"⚠️ Warning: {part_filename} not found. Skipping.")
                continue
                
            print(f"📄 Adding {part_filename}...")
            with open(part_path, 'r', encoding='utf-8') as infile:
                content = infile.read().strip()
                if content:
                    outfile.write(content)
                    outfile.write("\n\n") # Add spacing between parts
                    
    print(f"✅ Successfully combined into {output_file}")

if __name__ == "__main__":
    source_dir = "etc/split_vol08"
    output_file = "references/court_rulings_books/administrative_court_rulings_vol_08.md"
    combine_parts(source_dir, output_file, 54)
