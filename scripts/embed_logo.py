
import base64
from pathlib import Path

# Paths
base_dir = Path("/Users/wcagas/Tech/avid")
logo_path = base_dir / "src/ui/web/logo.png"
html_path = base_dir / "src/ui/web/index.html"

# Read logo
try:
    with open(logo_path, "rb") as f:
        logo_data = f.read()
        b64_logo = base64.b64encode(logo_data).decode("utf-8")
        data_uri = f"data:image/png;base64,{b64_logo}"
except FileNotFoundError:
    print(f"Error: logo.png not found at {logo_path}")
    exit(1)

# Read HTML
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace any src="logo.png" or logo-transparent.png with base64
targets = ['src="logo.png"', 'src="logo-transparent.png"']
replaced = False

for target in targets:
    if target in html_content:
        html_content = html_content.replace(target, f'src="{data_uri}"')
        replaced = True
        print(f"Replaced {target}")

if replaced:
    # Write back
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Logo embedded successfully.")
else:
    print("No logo src found to replace.")
