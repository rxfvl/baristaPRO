import json
import re
import os

log_path = r'C:\Users\minec\.gemini\antigravity-ide\brain\8d83793f-1956-41aa-bb14-58956242ee95\.system_generated\logs\transcript.jsonl'
lines_1_800 = []
lines_800_964 = []

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'TOOL_RESPONSE' and 'dial_in_journal.py' in data.get('content', ''):
            content = data['content']
            if 'Showing lines 1 to 800' in content:
                code_part = content.split('Please note that any changes targeting the original code should remove the line number, colon, and leading space.\n')[1]
                code_part = code_part.split('\nThe above content does NOT show')[0]
                lines_1_800 = code_part.split('\n')
            elif 'Showing lines 800 to 964' in content:
                code_part = content.split('Please note that any changes targeting the original code should remove the line number, colon, and leading space.\n')[1]
                code_part = code_part.split('\nThe above content does NOT show')[0]
                lines_800_964 = code_part.split('\n')

final_lines = []
for l in lines_1_800 + lines_800_964:
    if not l:
        final_lines.append("")
        continue
    match = re.match(r"^\d+:(?: (.*))?$", l)
    if match:
        val = match.group(1)
        final_lines.append(val if val is not None else "")
    else:
        final_lines.append(l)

with open(r'c:\Users\minec\Desktop\baristaPRO\ui\dial_in_journal.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))

print("File restored")
