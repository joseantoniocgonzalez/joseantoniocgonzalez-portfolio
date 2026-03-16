from pathlib import Path
from shutil import copytree, rmtree
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DIST_DIR = BASE_DIR / "dist"


def get_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"])
    )


def prepare_dist() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    static_dist = DIST_DIR / "static"
    if static_dist.exists():
        rmtree(static_dist)

    copytree(STATIC_DIR, static_dist)


def load_json(filename: str) -> dict:
    file_path = DATA_DIR / filename
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_home(env: Environment) -> None:
    template = env.get_template("index.html")
    home_data = load_json("home.json")

    output = template.render(**home_data)

    (DIST_DIR / "index.html").write_text(output, encoding="utf-8")


def main() -> None:
    env = get_environment()
    prepare_dist()
    build_home(env)
    print("Sitio generado en dist/index.html")


if __name__ == "__main__":
    main()
