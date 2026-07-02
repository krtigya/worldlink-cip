path = '/app/app/rag/rag_service.py'
with open(path) as f:
    content = f.read()

content = content.replace(
    'if row.bundle_flags else "No bundles."',
    'if row.bundle_flags else "No additional bundles."'
)
content = content.replace(
    '"Unlimited data."',
    '"Unlimited data, no FUP."'
)
content = content.replace(
    'else (f"FUP: {row.fup_gb} GB." if row.fup_gb else "")',
    'else (f"FUP limit: {row.fup_gb} GB per month." if row.fup_gb else "FUP terms not specified.")'
)
content = content.replace(
    'f"{row.isp_name} {row.normalized_name}.",',
    'f"{row.isp_name} internet plan: {row.normalized_name}.",\n            f"Provider: {row.isp_name}.",'
)
content = content.replace(
    'f"Speed: {row.download_mbps} Mbps download.",',
    'f"Speed: {row.download_mbps} Mbps download internet connection.",'
)
content = content.replace(
    'f"Price: NPR {row.price_monthly} per month.",',
    'f"Price: NPR {row.price_monthly} per month, monthly cost.",'
)
content = content.replace(
    'f"Plan type: {row.plan_type}.",',
    'f"Plan category: {row.plan_type} internet service.",'
)
content = content.replace(
    'f"Value: NPR {round(float(row.price_monthly) / row.download_mbps, 2)} per Mbps.",',
    'f"Cost efficiency: NPR {round(float(row.price_monthly) / row.download_mbps, 2)} per Mbps, price per megabit.",'
)

with open(path, 'w') as f:
    f.write(content)

print("PATCHED OK")
print("Provider lines:", content.count('Provider:'))