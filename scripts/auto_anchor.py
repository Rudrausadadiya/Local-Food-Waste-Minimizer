import os
import re
import sys
import json

EXCLUDED_DIRS = {'node_modules', 'venv', '.git', 'dist', 'build', '__pycache__', 'migrations'}

# Python Regexes
PY_FUNC_RE = re.compile(r'^(\s*)(?:async\s+)?def\s+([a-zA-Z_]\w*)\s*\(')
PY_CLASS_RE = re.compile(r'^(\s*)class\s+([a-zA-Z_]\w*)\s*(?:\(|:)')

# JS/JSX Regexes
JS_CLASS_RE = re.compile(r'^(\s*)(?:export\s+)?(?:default\s+)?class\s+([a-zA-Z_]\w*)\s*(?:extends|{)')
JS_FUNC_RE = re.compile(r'^(\s*)(?:export\s+)?(?:default\s+)?(?:async\s+)?function(?:\s*\*)?\s+([a-zA-Z_]\w*)\s*\(')
# arrow functions: const MyComponent = (props) => ... or export const foo = async () => ...
JS_ARROW_RE = re.compile(r'^(\s*)(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>')

# Function: is_pascal_case
def is_pascal_case(name):
    return name and name[0].isupper()

# Function: process_python_file
def process_python_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    anchors_added = 0
    modified = False
    
    for i, line in enumerate(lines):
        match_class = PY_CLASS_RE.match(line)
        match_func = PY_FUNC_RE.match(line)
        
        insert_comment = None
        indent = ""
        name = ""
        
        if match_class:
            indent = match_class.group(1)
            name = match_class.group(2)
            insert_comment = f"{indent}# Class: {name}\n"
        elif match_func:
            indent = match_func.group(1)
            name = match_func.group(2)
            # if indented, consider it a method
            if len(indent) > 0:
                insert_comment = f"{indent}# Method: {name}\n"
            else:
                insert_comment = f"{indent}# Function: {name}\n"
                
        if insert_comment:
            # Check for idempotency
            has_anchor_already = False
            if len(new_lines) > 0:
                prev_line = new_lines[-1].strip()
                if prev_line.startswith('# Class:') or prev_line.startswith('# Method:') or prev_line.startswith('# Function:'):
                    if name in prev_line:
                        has_anchor_already = True
                        
            # Also check if it already has descriptive doc comments or our anchor
            if not has_anchor_already:
                new_lines.append(insert_comment)
                anchors_added += 1
                modified = True
                
        new_lines.append(line)
        
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
    return modified, anchors_added

# Function: process_js_file
def process_js_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    anchors_added = 0
    modified = False
    
    for i, line in enumerate(lines):
        match_class = JS_CLASS_RE.match(line)
        match_func = JS_FUNC_RE.match(line)
        match_arrow = JS_ARROW_RE.match(line)
        
        insert_comment = None
        indent = ""
        name = ""
        
        if match_class:
            indent = match_class.group(1)
            name = match_class.group(2)
            insert_comment = f"{indent}// Class: {name}\n"
        elif match_func or match_arrow:
            match = match_func or match_arrow
            indent = match.group(1)
            name = match.group(2)
            
            # React components are usually PascalCase, regular functions are camelCase
            if is_pascal_case(name):
                insert_comment = f"{indent}// Component: {name}\n"
            else:
                insert_comment = f"{indent}// Function: {name}\n"
                
        if insert_comment:
            has_anchor_already = False
            if len(new_lines) > 0:
                prev_line = new_lines[-1].strip()
                if prev_line.startswith('// Class:') or prev_line.startswith('// Component:') or prev_line.startswith('// Function:'):
                    if name in prev_line:
                        has_anchor_already = True
                        
            if not has_anchor_already:
                new_lines.append(insert_comment)
                anchors_added += 1
                modified = True
                
        new_lines.append(line)
        
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
    return modified, anchors_added

# Function: main
def main():
    root_dir = "."
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
        
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'anchors_added': 0,
        'errors': []
    }
    
    for root, dirs, files in os.walk(root_dir):
        # Exclude directories in place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            try:
                if ext == '.py':
                    stats['files_processed'] += 1
                    modified, count = process_python_file(filepath)
                    if modified:
                        stats['files_modified'] += 1
                        stats['anchors_added'] += count
                elif ext in ['.js', '.jsx']:
                    stats['files_processed'] += 1
                    modified, count = process_js_file(filepath)
                    if modified:
                        stats['files_modified'] += 1
                        stats['anchors_added'] += count
            except Exception as e:
                stats['errors'].append({"file": filepath, "error": str(e)})
                
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
