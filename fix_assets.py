import os
import re

# Base directory
base_dir = r"c:\Users\user\Desktop\THINK-IN\IYRP_2026\WEB IYRP2026"
estilos_dir = os.path.join(base_dir, "estilos")

# Function to sanitize filename
def sanitize_filename(name):
    name = name.lower()
    name = name.replace(" ", "_").replace("-", "_")
    name = re.sub(r'[^a-z0-9_.]', '', name)
    return name

# Extensions to update
extensions_to_update = ['.html', '.css']

# 1. Collect all files and create mapping
file_mapping = {}
print("Scanning for files to rename...")

for root, dirs, files in os.walk(estilos_dir):
    for filename in files:
        old_path = os.path.join(root, filename)
        new_filename = sanitize_filename(filename)
        
        # Handle collision or same name
        if new_filename != filename.lower().replace(" ", "_").replace("-", "_") and new_filename != filename:
             # Just simple sanitization
             pass

        new_path = os.path.join(root, new_filename)
        
        # Relative path for replacement in code (e.g. estilos/logos/logo.png)
        # We need to handle both forward and backward slashes in the codebase potentially, 
        # but usually web dev uses forward slashes.
        rel_path_old = os.path.relpath(old_path, base_dir).replace("\\", "/")
        rel_path_new = os.path.relpath(new_path, base_dir).replace("\\", "/")
        
        file_mapping[old_path] = {
            'new_path': new_path,
            'rel_old': rel_path_old,
            'rel_new': rel_path_new,
            'filename_old': filename,
            'filename_new': new_filename
        }

# 2. Rename files on disk
print("Renaming files...")
for old_path, data in file_mapping.items():
    if old_path != data['new_path']:
        try:
            # Check if target exists (handling case insensitivity collisions if any, though on Windows rename handles it usually)
            if os.path.exists(data['new_path']) and old_path.lower() != data['new_path'].lower():
                print(f"Skipping {old_path} -> {data['new_path']} due to collision")
                continue
                
            os.rename(old_path, data['new_path'])
            print(f"Renamed: {data['filename_old']} -> {data['filename_new']}")
        except Exception as e:
            print(f"Error renaming {old_path}: {e}")

# 3. Update references in code
print("Updating references in HTML and CSS...")
for root, dirs, files in os.walk(base_dir):
    for filename in files:
        if any(filename.endswith(ext) for ext in extensions_to_update):
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                for old_full_path, data in file_mapping.items():
                    # We need to match the relative path usage.
                    # Files might be referenced as "estilos/logos/File Name.png" or "estilos\logos\File Name.png"
                    # Also URL encoding: "File%20Name.png"
                    
                    # 1. Standard relative path
                    pattern_straight = data['rel_old']
                    content = content.replace(pattern_straight, data['rel_new'])
                    
                    # 2. URL encoded relative path
                    pattern_encoded = data['rel_old'].replace(" ", "%20")
                    content = content.replace(pattern_encoded, data['rel_new'])
                    
                    # 3. Just the filename (risky, but sometimes used in same dir? No, structure seems to use full relative paths usually)
                    # Let's stick to relative paths starting with estilos/ for safety, unless we find otherwise.
                    
                    # 4. Case insensitive match for existing chaos?
                    # Python replace is case sensitive. We might need regex for case insensitive replacement 
                    # if the code has "Estilos/Logos/Logo.png" but file is "estilos/logos/logo.png"
                    
                    # Let's try to be smart. The regex should match the path part relative to base.
                    # Escape for regex
                    escaped_old_rel = re.escape(data['rel_old'])
                    # Allow for case insensitivity and URL encoding in the regex
                    # "estilos/logos/logo IYRP color.png" -> "estilos/logos/logo(?:\s|%20)IYRP(?:\s|%20)color\.png"
                    
                    # Simplistic regex construction for spaces
                    regex_pattern_str = escaped_old_rel.replace(r"\ ", r"(?: |%20)")
                    
                    # Compile regex with IGNORECASE
                    regex = re.compile(regex_pattern_str, re.IGNORECASE)
                    
                    content = regex.sub(data['rel_new'], content)

                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated references in: {filename}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print("Done.")
