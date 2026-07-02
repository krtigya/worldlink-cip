path = '/app/app/rag/rag_service.py'
with open(path) as f:
    content = f.read()

old = '''        sources = self.search(question, limit=8)

        if not sources:'''

new = '''        sources = self.search(question, limit=8)

        # Always inject WorldLink into context if not already present
        worldlink_in_sources = any(
            s.get("isp_name", "").lower() == "worldlink" or
            s.get("isp_id") == 1
            for s in sources
        )
        if not worldlink_in_sources:
            wl_sources = self.search(question, isp_ids=[1], limit=3)
            sources = sources[:5] + wl_sources

        if not sources:'''

if old in content:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print('PATCHED OK')
else:
    print('NOT FOUND')
    # Debug: show what we actually have
    idx = content.find('sources = self.search(question, limit=8)')
    print('Found search call at index:', idx)
    print('Context around it:', repr(content[idx:idx+100]))