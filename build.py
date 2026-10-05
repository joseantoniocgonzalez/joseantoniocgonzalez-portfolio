from pathlib import Path
from shutil import copytree, rmtree
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "proyectos"
ARTICLES_DIR = DATA_DIR / "articulos"
CERTIFICATIONS_DIR = DATA_DIR / "certificaciones"
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


def load_home_data_en() -> dict:
    return load_json(DATA_DIR / "home_en.json")


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


def localize_project_en(project: dict) -> dict:
    localized = dict(project)

    for field in ("title", "summary", "intro", "problem", "build", "automation"):
        en_key = f"{field}_en"
        if project.get(en_key):
            localized[field] = project[en_key]

    if project.get("highlights_en"):
        localized["highlights"] = project["highlights_en"]

    return localized


def localize_projects_en(projects: list[dict]) -> list[dict]:
    return [localize_project_en(project) for project in projects]


def load_articles() -> list[dict]:
    articles = []

    for article_file in ARTICLES_DIR.glob("*.json"):
        if article_file.name.startswith("_"):
            continue

        article_data = load_json(article_file)

        body_file = article_data.get("body_file")
        if body_file:
            body_path = ARTICLES_DIR / body_file
            if body_path.exists():
                article_data["content_html"] = body_path.read_text(encoding="utf-8")
            else:
                article_data["content_html"] = "<p>Contenido no disponible.</p>"
        else:
            article_data["content_html"] = "<p>Contenido no disponible.</p>"

        articles.append(article_data)

    articles.sort(key=lambda article: article.get("date", ""), reverse=True)
    return articles


def load_certifications() -> list[dict]:
    certifications = []

    for certification_file in CERTIFICATIONS_DIR.glob("*.json"):
        if certification_file.name.startswith("_"):
            continue

        certification_data = load_json(certification_file)
        certifications.append(certification_data)

    certifications.sort(
        key=lambda certification: certification.get("fecha_expedicion", ""),
        reverse=True
    )
    return certifications


def build_home(env: Environment, projects: list[dict], articles: list[dict]) -> None:
    template = env.get_template("index.html")

    home_data = load_home_data()
    latest_project = projects[0] if projects else None
    latest_articles = articles[:3]

    output = template.render(
        **home_data,
        latest_project=latest_project,
        latest_articles=latest_articles,
        search_projects=projects,
        search_articles=articles,
        search_certifications=load_certifications(),
        lang_switch_url="/en/"
    )

    (DIST_DIR / "index.html").write_text(output, encoding="utf-8")


def build_projects(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("proyectos.html")

    output = template.render(
        page_title="Proyectos | José Antonio Canalo González",
        site_title="José Antonio Canalo González",
        tagline="QA Automation, DevOps y Administración de Sistemas",
        projects=projects,
        lang_switch_url="/en/projects/"
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
            project=project,
            lang_switch_url=f'/en/projects/{project["slug"]}/'
        )

        project_dist_dir = DIST_DIR / "proyectos" / project["slug"]
        project_dist_dir.mkdir(parents=True, exist_ok=True)

        (project_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_articles(env: Environment, articles: list[dict]) -> None:
    template = env.get_template("articulos.html")

    output = template.render(
        page_title="Artículos | José Antonio Canalo González",
        site_title="José Antonio Canalo González",
        tagline="QA Automation, DevOps y Administración de Sistemas",
        articles=articles
    )

    articles_dist_dir = DIST_DIR / "articulos"
    articles_dist_dir.mkdir(parents=True, exist_ok=True)

    (articles_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_article_pages(env: Environment, articles: list[dict]) -> None:
    template = env.get_template("articulo.html")

    for article in articles:
        output = template.render(
            page_title=f'{article["title"]} | José Antonio Canalo González',
            site_title="José Antonio Canalo González",
            tagline="QA Automation, DevOps y Administración de Sistemas",
            article=article
        )

        article_dist_dir = DIST_DIR / "articulos" / article["slug"]
        article_dist_dir.mkdir(parents=True, exist_ok=True)

        (article_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_certifications(env: Environment, certifications: list[dict]) -> None:
    template = env.get_template("certificaciones.html")

    block_order = [
        "QA y testing",
        "DevOps / cloud / automatización",
        "Bases de datos",
        "Sistemas / redes / seguridad",
    ]

    grouped = {block: [] for block in block_order}

    for certification in certifications:
        block = certification.get("bloque", "Otros")
        grouped.setdefault(block, []).append(certification)

    certification_groups = [
        {"title": block, "items": grouped[block]}
        for block in block_order
        if grouped.get(block)
    ]

    extra_groups = [
        {"title": block, "items": items}
        for block, items in grouped.items()
        if block not in block_order and items
    ]

    certification_groups.extend(extra_groups)

    home_data = load_home_data()

    output = template.render(
        page_title="Certificaciones | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        certification_groups=certification_groups
    )

    certifications_dist_dir = DIST_DIR / "certificaciones"
    certifications_dist_dir.mkdir(parents=True, exist_ok=True)

    (certifications_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_contact(env: Environment) -> None:
    template = env.get_template("contacto.html")
    home_data = load_home_data()

    output = template.render(
        page_title="Contacto | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        contact=home_data["contact"],
        lang_switch_url="/en/contact/"
    )

    contact_dist_dir = DIST_DIR / "contacto"
    contact_dist_dir.mkdir(parents=True, exist_ok=True)

    (contact_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_curriculum(env: Environment) -> None:
    template = env.get_template("curriculum.html")
    home_data = load_home_data()

    output = template.render(
        page_title="Currículum | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        contact=home_data["contact"],
        lang_switch_url="/en/curriculum/"
    )

    curriculum_dist_dir = DIST_DIR / "curriculum"
    curriculum_dist_dir.mkdir(parents=True, exist_ok=True)

    (curriculum_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_home_en(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("index_en.html")

    home_data = load_home_data_en()
    latest_project = projects[0] if projects else None

    en_dist_dir = DIST_DIR / "en"
    en_dist_dir.mkdir(parents=True, exist_ok=True)

    output = template.render(
        page_title=home_data["page_title"],
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        summary=home_data["summary"],
        hero_links=home_data["hero_links"],
        latest_project=latest_project,
        contact=home_data["contact"],
        lang_switch_url="/"
    )

    (en_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_projects_en(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("projects_en.html")
    home_data = load_home_data_en()

    projects_dist_dir = DIST_DIR / "en" / "projects"
    projects_dist_dir.mkdir(parents=True, exist_ok=True)

    output = template.render(
        page_title="Projects | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        projects=projects,
        lang_switch_url="/proyectos/"
    )

    (projects_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_project_pages_en(env: Environment, projects: list[dict]) -> None:
    template = env.get_template("project_en.html")
    home_data = load_home_data_en()

    for project in projects:
        output = template.render(
            page_title=f'{project["title"]} | José Antonio Canalo González',
            site_title=home_data["site_title"],
            tagline=home_data["tagline"],
            project=project,
            lang_switch_url=f'/proyectos/{project["slug"]}/'
        )

        project_dist_dir = DIST_DIR / "en" / "projects" / project["slug"]
        project_dist_dir.mkdir(parents=True, exist_ok=True)

        (project_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_contact_en(env: Environment) -> None:
    template = env.get_template("contact_en.html")
    home_data = load_home_data_en()

    contact_dist_dir = DIST_DIR / "en" / "contact"
    contact_dist_dir.mkdir(parents=True, exist_ok=True)

    output = template.render(
        page_title="Contact | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        contact=home_data["contact"],
        lang_switch_url="/contacto/"
    )

    (contact_dist_dir / "index.html").write_text(output, encoding="utf-8")


def build_curriculum_en(env: Environment) -> None:
    template = env.get_template("curriculum_en.html")
    home_data = load_home_data_en()

    curriculum_dist_dir = DIST_DIR / "en" / "curriculum"
    curriculum_dist_dir.mkdir(parents=True, exist_ok=True)

    output = template.render(
        page_title="CV | José Antonio Canalo González",
        site_title=home_data["site_title"],
        tagline=home_data["tagline"],
        contact=home_data["contact"],
        lang_switch_url="/curriculum/"
    )

    (curriculum_dist_dir / "index.html").write_text(output, encoding="utf-8")


def main() -> None:
    env = create_environment()
    prepare_dist()

    projects = load_projects()
    en_projects = localize_projects_en(projects)
    articles = load_articles()
    certifications = load_certifications()

    build_home(env, projects, articles)
    build_projects(env, projects)
    build_project_pages(env, projects)
    build_articles(env, articles)
    build_article_pages(env, articles)
    build_certifications(env, certifications)
    build_contact(env)
    build_curriculum(env)

    build_home_en(env, en_projects)
    build_projects_en(env, en_projects)
    build_project_pages_en(env, en_projects)
    build_contact_en(env)
    build_curriculum_en(env)

    print("Sitio generado en dist/")


if __name__ == "__main__":
    main()
