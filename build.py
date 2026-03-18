from pathlib import Path
from shutil import copytree, rmtree
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "proyectos"
DIST_DIR = BASE_DIR / "dist"


def create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"])
    )


def prepare_dist() -> None:
    if DIST_DIR.exists():
        rmtree(DIST_DIR)

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    static_dist = DIST_DIR / "static"
    copytree(STATIC_DIR, static_dist)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_home_data() -> dict:
    return load_json(DATA_DIR / "home.json")


def load_projects() -> list[dict]:
    projects = []

    for project_file in PROJECTS_DIR.glob("*.json"):
        if project_file.name.startswith("_"):
            continue

        project_data = load_json(project_file)

        if project_data.get("draft", False):
            continue

        if not project_data.get("date"):
            continue

        projects.append(project_data)

    projects.sort(key=lambda project: project["date"], reverse=True)
    return projects


def build_home(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("index.html")

    home_data = load_home_data()
    latest_project = projects[0] if projects else None

    output = template.render(
        **home_data,
        latest_project=latest_project
    )

    (DIST_DIR / "index.html").write_text(output, encoding="utf-8")


def build_projects(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("proyectos.html")

    output = template.render(
        page_title="Proyectos | José Antonio Canalo González",
        site_title="José Antonio Canalo González",
        tagline="QA Automation, DevOps y Administración de Sistemas",
        projects=projects
    )

    projects_dist_dir = DIST_DIR / "proyectos"
    projects_dist_dir.mkdir(parents=True, exist_ok=True)

    (projects_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_project_pages(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("proyecto.html")

    for project in projects:
        output = template.render(
            page_title=f'{project["title"]} | José Antonio Canalo González',
            site_title="José Antonio Canalo González",
            tagline="QA Automation, DevOps y Administración de Sistemas",
            project=project
        )

        project_dist_dir = DIST_DIR / "proyectos" / project["slug"]
        project_dist_dir.mkdir(parents=True, exist_ok=True)

        (project_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_contact(env: Environment) -> None:
    template = env.get_template("contacto.html")
    home_data = load_home_data()

    output = template.render(
        page_title="Contacto | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        contact=home_data["contact"]
    )

    contact_dist_dir = DIST_DIR / "contacto"
    contact_dist_dir.mkdir(parents=True, exist_ok=True)

    (contact_dist_dir / "index.html").write_text(output, encoding="utf-8")


def main() -> None:
    env = create_environment()
    prepare_dist()

    projects = load_projects()

    build_home(env, projects)
    build_projects(env, projects)
    build_project_pages(env, projects)
    build_contact(env)

    print("Sitio generado en dist/")


if __name__ == "__main__":
    main()
