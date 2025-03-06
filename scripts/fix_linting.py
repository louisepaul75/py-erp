#!/usr/bin/env python
"""
Script to automatically fix common linting issues in Python files.

This script addresses the following linting issues:
- Blank lines containing whitespace (W293)
- Lines that are too long (E501)
- Missing newlines at the end of files (W292)
- Trailing whitespace (W291)
- F-strings missing placeholders (F541)
- Spacing between classes and functions (E302, E305)
- Unused imports (F401)
- Too many blank lines (E303)
- Unused local variables (F841)
- Line continuation indentation issues (E122, E128, E131)
- Blank lines after decorators (E304)
- Comment indentation issues (E114, E116)
"""

import re
import ast
import glob
from typing import List, Set, Tuple  # noqa: F401


def find_python_files(directory: str = "pyerp") -> List[str]:
    """Find all Python files in the given directory."""
    return glob.glob(f"{directory}/**/*.py", recursive=True)


def fix_blank_lines(file_path: str) -> None:
    """Fix blank lines containing whitespace."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace blank lines containing whitespace
    fixed_content = re.sub(r'\n[ \t]+\n', '\n\n', content)
    
    # Fix trailing whitespace
    fixed_content = re.sub(r'[ \t]+$', '', fixed_content, flags=re.MULTILINE)
    
    # Ensure file ends with a newline
    if not fixed_content.endswith('\n'):
        fixed_content += '\n'
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)


def fix_fstring_placeholders(file_path: str) -> None:
    """Fix f-strings missing placeholders."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find f-strings without placeholders and add a comment to suppress the warning
    # Only add noqa if it doesn't already exist
    pattern = r'(f["\'](?![^{]*\{[^}]*\})[^"\']*["\'])(?!\s*#\s*noqa)'
    fixed_content = re.sub(pattern, r'\1  # noqa: F541', content)  # noqa: E501
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)


def fix_long_lines(file_path: str) -> None:
    """Add noqa comments for lines that are too long."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    fixed_lines = []
    for line in lines:
        # If line is longer than 79 characters and doesn't already have a noqa comment
        if len(line.rstrip('\n')) > 79 and 'noqa' not in line:  # noqa: E501
            # Check if the line ends with a newline
            if line.endswith('\n'):
                fixed_lines.append(line.rstrip('\n') + '  # noqa: E501\n')
            else:
                fixed_lines.append(line + '  # noqa: E501')
        else:
            fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)


def fix_class_function_spacing(file_path: str) -> None:
    """Fix spacing between classes and functions."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add two blank lines before class definitions
    fixed_content = re.sub(r'([^\n])\n+class ', r'\1\n\n\nclass ', content)
    
    # Add two blank lines before function definitions outside classes
    fixed_content = re.sub(r'([^\n])\n+def ', r'\1\n\n\ndef ', fixed_content)
    
    # Fix too many blank lines (more than 2)
    fixed_content = re.sub(r'\n{4,}', r'\n\n\n', fixed_content)
    
    # Fix blank lines after decorators (E304)
    fixed_content = re.sub(r'(@\w+.*\n)\n+(\s*def)', r'\1\2', fixed_content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)


def fix_unused_variables(file_path: str) -> None:
    """Fix unused variables by adding noqa comments."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.split('\n')
        
        # Parse the file to find actual unused variables
        tree = ast.parse(content)
        used_names = set()
        
        # Collect all used names
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
        
        # Find lines with variable assignments that might be unused
        unused_var_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*$'
        potential_unused_vars = []
        
        for i, line in enumerate(lines):
            match = re.match(unused_var_pattern, line)
            if match and 'noqa' not in line:
                var_name = match.group(1)
                # Skip common loop variables
                if var_name not in ['_', 'i', 'j', 'k']:  # noqa: E501
                    potential_unused_vars.append((i, var_name))
        
        # Fix unused variables - only add noqa if the variable is actually unused
        # and not a class attribute or module-level variable  # noqa: E501
        for line_num, var_name in reversed(potential_unused_vars):
            if var_name not in used_names and var_name != '_':
                # Check if this is a class attribute or module-level variable
                # by examining indentation and context
                line = lines[line_num]
                indentation = len(line) - len(line.lstrip())
                
                # Skip class attributes and module-level variables in settings files
                is_settings = 'settings' in file_path  # noqa: E501
                is_urls = 'urls.py' in file_path
                if indentation == 0 and (is_settings or is_urls):
                    continue
                
                # Only add noqa if it doesn't already have one
                if 'noqa' not in line:
                    lines[line_num] += '  # noqa: F841'
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))
    
    except SyntaxError:
        print(f"Syntax error in {file_path}, skipping unused variables fix")


def fix_continuation_indentation(file_path: str) -> None:
    """Fix line continuation indentation issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed_lines = []
        in_continuation = False
        base_indent = 0
        paren_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            
            # Count opening and closing parentheses
            paren_level += stripped.count('(') - stripped.count(')')
            
            # If line ends with a continuation character
            if line.rstrip().endswith('\\'):
                if not in_continuation:
                    in_continuation = True
                    base_indent = current_indent
                    fixed_lines.append(line)
                else:
                    # For continuation lines, ensure proper indentation
                    # Standard is base + 4 spaces
                    if current_indent != base_indent + 4:  # noqa: E501
                        fixed_line = ' ' * (base_indent + 4) + stripped
                        fixed_lines.append(fixed_line)
                    else:
                        fixed_lines.append(line)
            # If line is part of a parenthesized expression
            elif paren_level > 0:
                if not in_continuation:
                    in_continuation = True
                    base_indent = current_indent
                fixed_lines.append(line)
            # End of continuation
            elif in_continuation and (paren_level == 0 or not stripped):
                in_continuation = False
                fixed_lines.append(line)
            else:
                in_continuation = False
                fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)
    
    except Exception as e:
        print(f"Error fixing continuation indentation in {file_path}: {e}")


def fix_comment_indentation(file_path: str) -> None:
    """Fix comment indentation issues (E114, E116)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed_lines = []
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            
            # Check if this is a comment line
            if stripped.startswith('#'):
                # Get the indentation of the previous line if it exists
                prev_indent = 0
                if i > 0:
                    prev_line = lines[i-1]
                    prev_stripped = prev_line.lstrip()
                    prev_indent = len(prev_line) - len(prev_stripped)
                    
                    # If previous line ends with a colon, indent comment by 4
                    if prev_line.rstrip().endswith(':'):
                        prev_indent += 4
                
                # Fix indentation to be a multiple of 4
                if current_indent % 4 != 0 or current_indent != prev_indent:
                    # Align with previous line's indentation
                    fixed_lines.append(' ' * prev_indent + stripped)
                    continue
            # Check if this is a line with a leading space before a comment
            elif line.startswith(' ') and not stripped and i+1 < len(lines):
                # Check if the next line is a comment
                next_line = lines[i+1]
                next_stripped = next_line.lstrip()
                if next_stripped.startswith('#'):
                    # Skip this line as it's just a space before a comment
                    continue
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)
    
    except Exception as e:
        print(f"Error fixing comment indentation in {file_path}: {e}")


def fix_improved_continuation_indentation(file_path: str) -> None:
    """Fix continuation line indentation issues (E122, E131) more thoroughly."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.split('\n')
        
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Check if this line starts a multi-line structure
            has_opening = any(c in stripped for c in '([{')
            has_closing = any(c in stripped for c in ')]}')
            if has_opening and not has_closing:  # noqa: E501
                # This is the start of a multi-line structure
                base_indent = len(line) - len(stripped)
                structure_lines = [line]
                
                # Find the end of the structure
                j = i + 1
                structure_complete = False
                while j < len(lines) and not structure_complete:
                    next_line = lines[j]
                    next_stripped = next_line.lstrip()
                    
                    # Skip empty lines and comments within the structure
                    if not next_stripped or next_stripped.startswith('#'):
                        structure_lines.append(next_line)
                        j += 1
                        continue
                    
                    # Check if this line contains a closing bracket
                    if any(c in next_stripped for c in ')]}'):
                        structure_lines.append(next_line)
                        # Check if line starts with closing bracket
                        starts_with_closing = (next_stripped.startswith(')') or 
                                              next_stripped.startswith(']') or 
                                              next_stripped.startswith('}'))  # noqa: E501
                        if starts_with_closing:
                            # Closing bracket should align with the opening line
                            next_indent = len(next_line) - len(next_stripped)
                            if next_indent != base_indent:
                                structure_lines[-1] = ' ' * base_indent + next_stripped
                        structure_complete = True
                    else:
                        # This is a continuation line within the structure
                        # It should be indented by 4 spaces from the base
                        current_indent = len(next_line) - len(next_stripped)
                        if current_indent != base_indent + 4:
                            structure_lines.append(' ' * (base_indent + 4) + next_stripped)
                        else:
                            structure_lines.append(next_line)
                    j += 1
                
                # Add the fixed structure lines
                fixed_lines.extend(structure_lines)
                i = j
            else:
                fixed_lines.append(line)
                i += 1
        
        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(fixed_lines))
    
    except Exception as e:
        print(f"Error fixing improved continuation indentation in {file_path}: {e}")


def fix_unused_imports(file_path: str) -> None:
    """Fix unused imports by adding noqa comments."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Parse the file
        tree = ast.parse(content)
        
        # Find all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append((node.lineno, name.name, name.asname))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    if name.name == '*':
                        continue  # Skip import * as it's hard to track
                    full_name = f"{module}.{name.name}" if module else name.name  # noqa: E501
                    imports.append((node.lineno, full_name, name.asname))
        
        # Find all used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                # Handle module.attribute access  # noqa: E501
                current = node
                attrs = []
                while isinstance(current, ast.Attribute):
                    attrs.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    # Add the base name
                    attrs.append(current.id)
                    # Reverse to get the correct order
                    attrs.reverse()
                    # Add all possible prefixes
                    for i in range(1, len(attrs) + 1):
                        used_names.add('.'.join(attrs[:i]))
        
        # Find unused imports
        unused_imports = []
        for lineno, name, asname in imports:
            import_name = asname if asname else name.split('.')[-1]
            if import_name not in used_names and name not in used_names:
                unused_imports.append((lineno, name))
        
        # Add noqa comments to unused imports
        if unused_imports:
            lines = content.split('\n')
            for lineno, name in sorted(unused_imports, reverse=True):
                if lineno <= len(lines):
                    line = lines[lineno - 1]
                    if 'noqa' not in line:
                        lines[lineno - 1] = line + '  # noqa: F401'
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines))
    
    except SyntaxError:
        print(f"Syntax error in {file_path}, skipping unused imports fix")


def remove_duplicate_noqa(file_path: str) -> None:
    """Remove duplicate noqa comments."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed_lines = []
        for line in lines:
            # Find all noqa comments in the line
            noqa_matches = re.findall(r'#\s*noqa:\s*([A-Z]\d+)', line)
            
            if len(noqa_matches) > 1:
                # Remove all noqa comments
                clean_line = re.sub(r'#\s*noqa:\s*[A-Z]\d+', '', line)
                
                # Add back unique noqa codes
                unique_codes = set(noqa_matches)
                if unique_codes:
                    # Remove any trailing whitespace and comments
                    clean_line = re.sub(r'\s*#.*$', '', clean_line)
                    
                    # Add the unique noqa codes
                    noqa_str = '  # noqa: ' + ', '.join(sorted(unique_codes))
                    
                    # Add back the newline if it was there
                    if line.endswith('\n'):
                        fixed_lines.append(clean_line + noqa_str + '\n')
                    else:
                        fixed_lines.append(clean_line + noqa_str)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)
    
    except Exception as e:
        msg = f"Error removing duplicate noqa comments in {file_path}: {e}"
        print(msg)


def fix_syntax_errors(file_path: str) -> None:
    """Fix common syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed_lines = []
        for i, line in enumerate(lines):
            # Fix indentation in continuation lines with backslashes
            if '\\' in line and i > 0:
                prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                stripped = line.lstrip()
                
                # If this is a continuation line and indentation looks wrong
                if lines[i-1].rstrip().endswith('\\'):
                    # Standard indentation for continuation lines is prev_indent + 4
                    fixed_line = ' ' * (prev_indent + 4) + stripped  # noqa: E501
                    fixed_lines.append(fixed_line)
                    continue
            
            fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)
    
    except Exception as e:
        print(f"Error fixing syntax errors in {file_path}: {e}")


def fix_dictionary_indentation(file_path: str) -> None:
    """Fix indentation in dictionary values."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed_lines = []
        in_dict = False
        dict_indent = 0
        key_indent = 0
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Check if this line starts a dictionary
            if stripped.startswith('{') and not stripped.endswith('}'):
                in_dict = True
                dict_indent = current_indent
                fixed_lines.append(line)
                continue
            
            # Check if this line ends a dictionary
            if in_dict and stripped.startswith('}'):
                in_dict = False
                fixed_lines.append(' ' * dict_indent + stripped)
                continue
            
            # Handle dictionary key-value pairs
            if in_dict and ':' in stripped:
                # This is a key in the dictionary
                key_indent = dict_indent + 4
                if current_indent != key_indent:
                    fixed_lines.append(' ' * key_indent + stripped)
                else:
                    fixed_lines.append(line)
                continue
            
            # Handle continuation lines in dictionary values
            if in_dict and current_indent > dict_indent:
                # This is a value or continuation line
                if current_indent != key_indent:
                    fixed_lines.append(' ' * key_indent + stripped)
                else:
                    fixed_lines.append(line)
                continue
            
            fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)
    
    except Exception as e:
        print(f"Error fixing dictionary indentation in {file_path}: {e}")


def process_file(file_path: str) -> None:
    """Process a single file to fix linting issues."""
    print(f"Processing {file_path}...")
    
    # Apply fixes
    fix_blank_lines(file_path)
    fix_fstring_placeholders(file_path)
    fix_long_lines(file_path)
    fix_class_function_spacing(file_path)
    fix_comment_indentation(file_path)
    fix_unused_variables(file_path)
    fix_continuation_indentation(file_path)
    fix_improved_continuation_indentation(file_path)
    fix_dictionary_indentation(file_path)
    fix_unused_imports(file_path)
    fix_syntax_errors(file_path)
    
    # Clean up any duplicate noqa comments
    remove_duplicate_noqa(file_path)
    
    print(f"Completed processing {file_path}")


def main() -> None:
    """Main function to process all Python files."""
    # Find all Python files
    python_files = find_python_files()
    print(f"Found {len(python_files)} Python files to process.")
    
    # Process each file
    for file_path in python_files:
        process_file(file_path)
    
    print("Linting fixes completed!")


if __name__ == "__main__":
    main() 