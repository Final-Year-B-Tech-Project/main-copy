import os

modules_file = 'Backend Files/modules_content.txt'
target_file = 'Backend Files/app/student.py'

with open(modules_file, 'r') as f:
    new_modules_content = f.read()

with open(target_file, 'r') as f:
    target_content = f.read()

# Define markers
start_marker = "    # Comprehensive lesson content for each module\n    modules_content = {"
end_marker = "    module_data = modules_content.get(module_id)"

start_idx = target_content.find(start_marker)
end_idx = target_content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # We want to replace from start_marker to the last '}' before end_marker
    # Let's find the closing brace of the dictionary
    # It should be the last '}' before end_idx
    
    pre_end_content = target_content[:end_idx]
    last_brace_idx = pre_end_content.rfind('}')
    
    if last_brace_idx > start_idx:
        # Construct the new content
        # We take everything before start_marker
        # Add the new content (which includes the start_marker text effectively, as it starts with '    # Comprehensive...')
        # Add everything after last_brace_idx + 1
        
        # Wait, new_modules_content already includes "    # Comprehensive..." and "    modules_content = {" ?
        # Let's check modules_content.txt content.
        # Yes, it starts with indentation and the comment.
        
        updated_content = target_content[:start_idx] + new_modules_content + "\n\n" + target_content[end_idx:]
        
        with open(target_file, 'w') as f:
            f.write(updated_content)
        print("Successfully updated student.py")
    else:
        print("Could not find closing brace for modules_content dictionary")
else:
    print(f"Could not find markers. Start: {start_idx}, End: {end_idx}")