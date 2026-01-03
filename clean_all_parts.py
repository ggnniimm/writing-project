import os
import glob

# Pattern for all part files
files = glob.glob("etc/Academic_291121_112321_parts/Academic_291121_112321_part_*.md")

print(f"Found {len(files)} files to process.")

count_total_replacements = 0
files_modified = 0

for file_path in files:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for &nbsp;
    count = content.count("&nbsp;")
    
    if count > 0:
        new_content = content.replace("&nbsp;", " ")
        with open(file_path, 'w') as f:
            f.write(new_content)
        count_total_replacements += count
        files_modified += 1
        print(f"Cleaned {count} '&nbsp;' from {os.path.basename(file_path)}")

print(f"Processing complete.")
print(f"Total files modified: {files_modified}")
print(f"Total '&nbsp;' characters removed: {count_total_replacements}")
