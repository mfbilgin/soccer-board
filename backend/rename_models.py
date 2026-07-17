import os, glob

files = glob.glob('backend/routers/*.py') + glob.glob('backend/*.py')
for f in files:
    if not f.endswith('.py'): continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = content.replace('PlayerClubStat', 'PlayerClubStat').replace('PlayerNationalStat', 'PlayerNationalStat')
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {f}")
