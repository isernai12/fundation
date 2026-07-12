with open('/workspaces/fundation/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

main_idx = -1
for i, line in enumerate(lines):
    if line.startswith("if __name__ == '__main__':"):
        main_idx = i
        break

if main_idx != -1:
    main_block = lines[main_idx:main_idx+3]
    del lines[main_idx:main_idx+3]
    
    # ensure it ends with newline
    if not lines[-1].endswith('\n'):
        lines[-1] += '\n'
        
    lines.extend(['\n'] + main_block)
    
    with open('/workspaces/fundation/app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Moved __main__ block to the end of the file.")
else:
    print("Could not find __main__ block.")
