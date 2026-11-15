#!/usr/bin/env python3
"""Generate the static site in docs/ from the recipes in recetas/*.yaml.

Usage: python scripts/generate_site.py

No backend, no build step in the site itself: the output is plain
.html, .css and .js meant to be published with GitHub Pages serving
/docs on the main branch. Run it by hand and commit docs/ whenever a
recipe changes.

Needs PyYAML (pip install pyyaml).

The displayed page text (labels, headings) stays in Spanish on purpose:
the site is for Ricardo's own Spanish-language recipes. Only the code
itself (identifiers, comments, filenames) is in English.
"""
import html
import json
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

try:
    import yaml
except ImportError:
    print("Missing PyYAML. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "recetas"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
DOCS_DIR = ROOT / "docs"
RECIPES_HTML_DIR = DOCS_DIR / "recetas"
ASSETS_DIR = DOCS_DIR / "assets"

REQUIRED_FIELDS = [
    "titulo", "tags", "raciones", "kcal_racion", "proteina_racion_g",
    "aceite_cucharillas", "ingredientes", "pasos",
]


def normalize(text):
    """Lowercase and accent-free, so the search box doesn't depend on tildes."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def load_recipes():
    if not RECIPES_DIR.exists():
        print(f"Missing {RECIPES_DIR}", file=sys.stderr)
        sys.exit(1)
    recipes = []
    for path in sorted(RECIPES_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            print(f"Warning: {path.name} has an unexpected format, skipping.", file=sys.stderr)
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in data]
        if missing:
            print(f"Warning: {path.name} is missing {', '.join(missing)}; publishing it as-is.", file=sys.stderr)
        data["_slug"] = path.stem
        recipes.append(data)
    recipes.sort(key=lambda r: normalize(r.get("titulo", r["_slug"])))
    return recipes


def badge(text):
    return f'<span class="badge">{html.escape(str(text))}</span>' if text not in (None, "") else ""


def render_tags(tags, index_href="index.html"):
    """Tags as links to the recipe list filtered by that tag (?tag=...)."""
    pieces = []
    for t in tags or []:
        href = html.escape(f"{index_href}?tag={quote(t)}")
        pieces.append(f'<a class="tag" href="{href}">{html.escape(t)}</a>')
    return "".join(pieces)


def search_text(recipe):
    parts = [recipe.get("titulo", "")]
    parts += recipe.get("tags", []) or []
    parts += recipe.get("momento", []) or []
    if recipe.get("sodio"):
        parts.append(recipe["sodio"])
    return html.escape(normalize(" ".join(parts)))


def recipe_badges(recipe):
    kcal = recipe.get("kcal_racion")
    protein = recipe.get("proteina_racion_g")
    oil = recipe.get("aceite_cucharillas")
    servings = recipe.get("raciones")
    moment = ", ".join(recipe.get("momento", []) or []) or None
    pieces = [
        badge(f"{kcal} kcal/ración") if kcal is not None else "",
        badge(f"{protein} g proteína") if protein is not None else "",
        badge(f"{oil} cuch. aceite") if oil is not None else "",
        badge(f"{servings} {'ración' if servings == 1 else 'raciones'}") if servings is not None else "",
        badge(moment) if moment else "",
        badge(f"sodio {recipe['sodio']}") if recipe.get("sodio") else "",
    ]
    return "".join(p for p in pieces if p)


def render_card(recipe):
    slug = recipe["_slug"]
    title = recipe.get("titulo", slug)
    tags = recipe.get("tags") or []
    # The card itself is a link to the recipe, but tags are links too (to
    # filter by tag), and an <a> can't contain another <a>. card-link is an
    # invisible overlay instead, see .card/.card-link in style.css.
    return f"""<div class="card" data-search="{search_text(recipe)}" data-tags="{html.escape('|'.join(tags))}">
  <a class="card-link" href="recetas/{html.escape(slug)}.html" aria-label="{html.escape(title)}"></a>
  <h3>{html.escape(title)}</h3>
  <div class="badges">{recipe_badges(recipe)}</div>
  <div class="tags">{render_tags(tags, "index.html")}</div>
</div>"""


def render_index_html(recipes):
    cards_html = "\n".join(render_card(r) for r in recipes)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recetas de Ricardo</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header>
  <h1>Recetas de Ricardo</h1>
  <p class="subtitle">Dieta hipocalórica para 2 — {len(recipes)} recetas</p>
  <input id="search" type="search" placeholder="Buscar por título, tag o momento…" autofocus>
  <p id="counter" class="counter"></p>
</header>
<main class="grid">
{cards_html}
</main>
<footer>
  <p><a href="https://github.com/rmunoz/recetario">Código fuente en GitHub</a></p>
</footer>
<script src="assets/search.js" defer></script>
</body>
</html>
"""


def render_ingredient(item):
    if isinstance(item, dict):
        text = item.get("texto", "")
        link = item.get("ingrediente")
    else:
        text, link = str(item), None
    extra = f' <span class="ingredient-link">({html.escape(link)})</span>' if link else ""
    return f"<li>{html.escape(text)}{extra}</li>"


def render_recipe_html(recipe):
    title = recipe.get("titulo", recipe["_slug"])
    ingredients_html = "\n".join(render_ingredient(i) for i in recipe.get("ingredientes", []) or [])
    steps = recipe.get("pasos", []) or []
    steps_html = "\n".join(
        f'<li data-step-index="{i}">{html.escape(step)}</li>'
        for i, step in enumerate(steps)
    )
    steps_json = json.dumps(steps, ensure_ascii=False)

    extra = []
    fuente = recipe.get("fuente")
    if fuente == "propia":
        extra.append('<p class="source">Receta propia de Ricardo.</p>')
    elif fuente:
        source = html.escape(fuente)
        extra.append(
            f'<p class="source">Receta adaptada a mis preferencias a partir de '
            f'<a href="{source}">la receta original</a>.</p>'
        )
    if recipe.get("imagen"):
        image = html.escape(recipe["imagen"])
        extra.append(f'<img class="image" src="{image}" alt="{html.escape(title)}">')

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Recetas de Ricardo</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="back-link" href="../index.html">&larr; Todas las recetas</a>
<article>
<h1>{html.escape(title)}</h1>
<div class="badges">{recipe_badges(recipe)}</div>
<div class="tags">{render_tags(recipe.get("tags"), "../index.html")}</div>
{"".join(extra)}
<h2>Ingredientes ({recipe.get("raciones", "?")} ración/es)</h2>
<ul class="ingredients">
{ingredients_html}
</ul>
<h2>Pasos</h2>
<section class="voice-mode" id="voice-mode">
<p class="voice-privacy">
El modo voz usa el reconocimiento de voz del navegador. En Chrome, el audio
se envía a los servidores de Google para transcribirlo; en otros
navegadores puede procesarse en el propio dispositivo. Si prefieres no usar
el micrófono, los botones de abajo funcionan igual.
</p>
<div class="voice-controls">
<button type="button" class="voice-button" id="voice-start">🎙️ Empezar la receta</button>
<button type="button" class="voice-button voice-button-secondary" id="voice-stop" hidden>Detener</button>
</div>
<p class="voice-status" id="voice-status" aria-live="polite"></p>
</section>
<ol class="steps" id="steps">
{steps_html}
</ol>
<div class="step-nav" id="step-nav">
<button type="button" class="step-nav-button" id="step-prev">&larr; Paso anterior</button>
<span class="step-nav-current" id="step-nav-current"></span>
<button type="button" class="step-nav-button" id="step-next">Paso siguiente &rarr;</button>
</div>
<script type="application/json" id="steps-data">{steps_json}</script>
<script src="../assets/voice.js" defer></script>
</article>
</body>
</html>
"""


def copy_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "search.js", "voice.js"):
        shutil.copyfile(TEMPLATES_DIR / name, ASSETS_DIR / name)


def main():
    recipes = load_recipes()

    if RECIPES_HTML_DIR.exists():
        shutil.rmtree(RECIPES_HTML_DIR)
    RECIPES_HTML_DIR.mkdir(parents=True, exist_ok=True)
    copy_assets()

    for recipe in recipes:
        destination = RECIPES_HTML_DIR / f"{recipe['_slug']}.html"
        destination.write_text(render_recipe_html(recipe), encoding="utf-8")

    (DOCS_DIR / "index.html").write_text(render_index_html(recipes), encoding="utf-8")

    print(f"Generated {len(recipes)} recipes in {DOCS_DIR}")


if __name__ == "__main__":
    main()
