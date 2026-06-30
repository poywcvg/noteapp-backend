import json
data = json.load(open('schema.json', encoding='utf-8'))
pt = data['paths']
for path in sorted(pt.keys()):
    for method in pt[path]:
        tags = pt[path][method].get('tags', [])
        print(f'{path} [{method.upper()}]: {tags}')
