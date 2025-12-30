
import os
import math

source_file = 'etc/ref_research_admin_court_rulings_digest_v14_2569.md'
output_dir = 'etc/split_md_40'
num_parts = 40

def split_markdown():
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    lines_per_part = math.ceil(total_lines / num_parts)

    print(f"Total lines: {total_lines}")
    print(f"Lines per part: {lines_per_part}")

    for i in range(num_parts):
        start_index = i * lines_per_part
        end_index = start_index + lines_per_part
        # Ensure we don't go out of bounds
        chunk = lines[start_index:end_index]
        
        if not chunk:
            break

        part_num = i + 1
        output_filename = os.path.join(output_dir, f"part_{part_num:02d}.md")
        
        with open(output_filename, 'w', encoding='utf-8') as out_f:
            out_f.writelines(chunk)
        
        print(f"Wrote {len(chunk)} lines to {output_filename}")

if __name__ == "__main__":
    split_markdown()
