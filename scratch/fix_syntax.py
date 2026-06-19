with open('C:/BotRedaman/scratch/build_installer.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Make the f-string a regular string
c = c.replace('script_content = f"""#!/bin/bash', 'script_content = """#!/bin/bash')

# Revert all the double brackets I mistakenly added
c = c.replace('{{', '{').replace('}}', '}')

# Replace the payload string substitution dynamically
c = c.replace('{formatted_payload}', '{formatted_payload_placeholder}')
c = c.replace('"""\n\n    # Ensure LF line endings', '"""\n    script_content = script_content.replace("{formatted_payload_placeholder}", formatted_payload)\n\n    # Ensure LF line endings')

with open('C:/BotRedaman/scratch/build_installer.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Fixed build_installer.py syntax!")
