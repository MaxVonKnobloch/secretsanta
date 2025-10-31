from pathlib import Path
import os

base_dir = Path(__file__).parent.parent

# In Docker, use /app/db for the database volume; otherwise use the root directory
if os.path.exists("/app/db"):
    db_path = Path("/app/db") / "secretsanta.db"
else:
    db_path = base_dir / "secretsanta.db"

static = base_dir / "static"
previews = static / "previews"

previews_url = "static/previews/"
default_preview_image_path = "static/previews/default_preview.png"
