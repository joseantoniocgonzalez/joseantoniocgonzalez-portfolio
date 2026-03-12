from pathlib import Path
from shutil import copytree, rmtree
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
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


def build_home(env: Environment) -> None:
    template = env.get_template("index.html")
    output = template.render(
        page_title="José Antonio Canalo González",
        site_title="José Antonio Canalo González",
        tagline="QA Automation, DevOps y Administración de Sistemas",
        summary="Portfolio personal con proyectos, artículos técnicos y certificaciones."
    )

    (DIST_DIR / "index.html").write_text(output, encoding="utf-8")


def main() -> None:
    env = get_environment()
    prepare_dist()
    build_home(env)
    print("Sitio generado en dist/index.html")


if __name__ == "__main__":
    main()
