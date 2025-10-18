from pathlib import Path

base_dir = Path(__file__).parent.parent

db_path = base_dir / "secretsanta.db"
static = base_dir / "static"
previews = static / "previews"

previews_url = "static/previews/"
default_preview_image_path = "static/previews/default_preview.png"

