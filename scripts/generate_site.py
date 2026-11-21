#!/usr/bin/env python3
"""Generate the static site in docs/ from the recipes in recetas/*.yaml.

Usage: python scripts/generate_site.py

No backend, no build step in the site itself: the output is plain
.html, .css and .js meant to be published with GitHub Pages serving
/docs on the main branch. Run it by hand and commit docs/ whenever a
recipe changes.

Needs PyYAML (pip install pyyaml).

The displayed page text (labels, headings) stays in Spanish on purpose:
the site is for the user's own Spanish-language recipes. Only the code
itself (identifiers, comments, filenames) is in English.
"""
import argparse
import html
import json
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import quote

try:
    import yaml
except ImportError:
    print("Missing PyYAML. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "recetas"
PLAN_DIR = ROOT / "plan"
IMAGES_DIR = ROOT / "imagenes"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
DOCS_DIR = ROOT / "docs"
RECIPES_HTML_DIR = DOCS_DIR / "recetas"
PLAN_HTML_DIR = DOCS_DIR / "plan"
ASSETS_DIR = DOCS_DIR / "assets"

REQUIRED_FIELDS = [
    "titulo", "tags", "raciones", "kcal_racion", "proteina_racion_g",
    "aceite_cucharillas", "ingredientes", "pasos",
]
REQUIRED_PLAN_FIELDS = ["semana", "fecha_inicio", "fecha_fin", "dias", "resumen_semanal"]
DAY_KEYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
DAY_LABELS = {
    "lunes": "Lunes", "martes": "Martes", "miercoles": "Miércoles",
    "jueves": "Jueves", "viernes": "Viernes", "sabado": "Sábado", "domingo": "Domingo",
}
MONTH_ABBR_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MONTH_NAMES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
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


def validate_variants(recipes):
    """Check the variante_de links and return {parent slug: [variants]}.

    Rules: a variant points to an existing main recipe, never to itself, and
    never to another variant (a variant can't have variants). Broken links
    abort the run, so the pre-commit hook and the PR workflow catch them.
    """
    by_slug = {r["_slug"]: r for r in recipes}
    variants_by_parent = {}
    errors = []
    for recipe in recipes:
        parent = recipe.get("variante_de")
        if parent is None:
            continue
        slug = recipe["_slug"]
        if parent == slug:
            errors.append(f"{slug}: variante_de can't point to itself")
        elif parent not in by_slug:
            errors.append(f"{slug}: variante_de '{parent}' does not exist in recetas/")
        elif by_slug[parent].get("variante_de") is not None:
            errors.append(f"{slug}: variante_de '{parent}' is itself a variant (a variant can't have variants)")
        else:
            variants_by_parent.setdefault(parent, []).append(recipe)
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    return variants_by_parent


def variant_label(recipe):
    """Short text shown on the main recipe's page; falls back to the title."""
    return recipe.get("variante_resumen") or recipe.get("titulo", recipe["_slug"])


def load_plans():
    """Weekly plans are optional: no plan/ yet just means no history to show."""
    if not PLAN_DIR.exists():
        return []
    plans = []
    for path in sorted(PLAN_DIR.rglob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            print(f"Warning: {path} has an unexpected format, skipping.", file=sys.stderr)
            continue
        missing = [field for field in REQUIRED_PLAN_FIELDS if field not in data]
        if missing:
            print(f"Warning: {path.name} is missing {', '.join(missing)}; publishing it as-is.", file=sys.stderr)
        # Prefix with the year folder (plan/YYYY/semanaXX.yaml) so two different
        # years' "semana47" don't collide once flattened into docs/plan/*.html.
        data["_slug"] = f"{path.parent.name}-{path.stem}" if path.parent != PLAN_DIR else path.stem
        plans.append(data)
    plans.sort(key=lambda p: str(p.get("fecha_inicio", "")), reverse=True)
    return plans


def to_date(value):
    """PyYAML parses an unquoted YYYY-MM-DD as a date already; strings need parsing."""
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def format_date_range(inicio, fin):
    i, f = to_date(inicio), to_date(fin)
    if i.year == f.year and i.month == f.month:
        return f"{i.day}-{f.day} {MONTH_ABBR_ES[i.month - 1]} {i.year}"
    if i.year == f.year:
        return f"{i.day} {MONTH_ABBR_ES[i.month - 1]} - {f.day} {MONTH_ABBR_ES[f.month - 1]} {i.year}"
    return f"{i.day} {MONTH_ABBR_ES[i.month - 1]} {i.year} - {f.day} {MONTH_ABBR_ES[f.month - 1]} {f.year}"


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


def render_card(recipe, recipes_by_slug):
    slug = recipe["_slug"]
    title = recipe.get("titulo", slug)
    tags = recipe.get("tags") or []
    parent = recipes_by_slug.get(recipe.get("variante_de"))
    # A variant without its own photo borrows the main recipe's one.
    imagen = recipe.get("imagen") or (parent or {}).get("imagen")
    if imagen:
        image_html = (
            f'<img class="card-image" src="{html.escape(image_src(imagen))}" '
            f'alt="" loading="lazy">'
        )
    else:
        # Same reserved slot, plain accent background, so cards without a
        # photo still line up with the ones that have one.
        image_html = '<div class="card-image" aria-hidden="true"></div>'
    # The card itself is a link to the recipe, but tags are links too (to
    # filter by tag), and an <a> can't contain another <a>. card-link is an
    # invisible overlay instead, see .card/.card-link in style.css.
    # Variants stay out of the listing (hidden) and only show up when a
    # search matches them; search.js toggles the hidden attribute.
    variant_attr = " hidden data-variant" if parent else ""
    variant_badge = badge(f"variante de {parent.get('titulo', parent['_slug'])}") if parent else ""
    return f"""<div class="card" data-search="{search_text(recipe)}" data-tags="{html.escape('|'.join(tags))}"{variant_attr}>
  <a class="card-link" href="recetas/{html.escape(slug)}.html" aria-label="{html.escape(title)}"></a>
  {image_html}
  <div class="card-body">
    <h3>{html.escape(title)}</h3>
    <div class="badges">{variant_badge}{recipe_badges(recipe)}</div>
    <div class="tags">{render_tags(tags, "index.html")}</div>
  </div>
</div>"""


def render_index_html(recipes, recipes_by_slug):
    main_count = sum(1 for r in recipes if not r.get("variante_de"))
    cards_html = "\n".join(render_card(r, recipes_by_slug) for r in recipes)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recetario</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header>
  <h1>Recetario</h1>
  <p class="subtitle">Dieta hipocalórica para 2 — {main_count} recetas</p>
  <a class="plan-banner" href="plan/index.html">
    <span class="plan-banner-icon" aria-hidden="true">&#128197;</span>
    <span class="plan-banner-text">
      <strong>Planes semanales</strong>
      <span class="plan-banner-sub">Histórico de menús, totales diarios y lista de la compra de cada semana</span>
    </span>
    <span class="plan-banner-arrow" aria-hidden="true">&rarr;</span>
  </a>
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


def image_src(imagen):
    """URLs are used as-is; a local path (imagenes/foo.jpg) resolves to the
    copy of imagenes/ that copy_assets() places under docs/assets/."""
    if imagen.startswith("http://") or imagen.startswith("https://"):
        return imagen
    return f"../assets/{imagen}"


def render_variants_box(variants):
    items = []
    for v in variants:
        stats = []
        if v.get("kcal_racion") is not None:
            stats.append(f"{v['kcal_racion']} kcal/ración")
        if v.get("proteina_racion_g") is not None:
            stats.append(f"{v['proteina_racion_g']} g proteína")
        stats_html = f' <span class="variant-stats">({", ".join(stats)})</span>' if stats else ""
        items.append(
            f'<li><a href="{html.escape(v["_slug"])}.html">{html.escape(variant_label(v))}</a>{stats_html}</li>'
        )
    heading = "Variante" if len(variants) == 1 else "Variantes"
    return f'<section class="variants"><h2>{heading}</h2>\n<ul>\n{"".join(items)}\n</ul></section>'


def render_recipe_html(recipe, recipes_by_slug, variants_by_parent):
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
        extra.append('<p class="source">Receta propia.</p>')
    elif fuente:
        source = html.escape(fuente)
        extra.append(
            f'<p class="source">Receta adaptada a mis preferencias a partir de '
            f'<a href="{source}">la receta original</a>.</p>'
        )
    if recipe.get("imagen"):
        image = html.escape(image_src(recipe["imagen"]))
        extra.append(f'<img class="image" src="{image}" alt="{html.escape(title)}">')

    variant_html = ""
    parent = recipes_by_slug.get(recipe.get("variante_de"))
    if parent:
        variant_html = (
            f'<p class="variant-note">Variante de '
            f'<a href="{html.escape(parent["_slug"])}.html">{html.escape(parent.get("titulo", parent["_slug"]))}</a></p>'
        )
        if not recipe.get("imagen") and parent.get("imagen"):
            image = html.escape(image_src(parent["imagen"]))
            extra.append(f'<img class="image" src="{image}" alt="{html.escape(title)}">')
    variants = variants_by_parent.get(recipe["_slug"])
    if variants:
        variant_html += render_variants_box(variants)

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Recetario</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="back-link" href="../index.html">&larr; Todas las recetas</a>
<article>
<h1>{html.escape(title)}</h1>
{variant_html}
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


def render_meal_cell(meal, recipes_by_slug):
    if not meal:
        return '<span class="plan-empty">&mdash;</span>'
    texto = html.escape(str(meal.get("texto", "?")))
    stats = []
    if meal.get("kcal") is not None:
        stats.append(f"{meal['kcal']} kcal")
    if meal.get("proteina_g") is not None:
        stats.append(f"{meal['proteina_g']} g prot.")
    stats_html = f' <span class="plan-meal-stats">({", ".join(stats)})</span>' if stats else ""
    slug = meal.get("receta")
    if meal.get("tipo") == "receta" and slug in recipes_by_slug:
        return f'<a href="../recetas/{html.escape(slug)}.html">{texto}</a>{stats_html}'
    return f"{texto}{stats_html}"


def render_plan_week_html(plan, recipes_by_slug):
    semana = plan.get("semana", plan["_slug"])
    inicio, fin = plan.get("fecha_inicio"), plan.get("fecha_fin")
    date_range = format_date_range(inicio, fin) if inicio and fin else ""
    dias = plan.get("dias") or {}

    rows = []
    for key in DAY_KEYS:
        day = dias.get(key) or {}
        totales = day.get("totales") or {}
        total_parts = []
        if totales.get("kcal") is not None:
            total_parts.append(f"{totales['kcal']} kcal")
        if totales.get("proteina_g") is not None:
            total_parts.append(f"{totales['proteina_g']} g prot.")
        if totales.get("aceite_cucharillas") is not None:
            total_parts.append(f"{totales['aceite_cucharillas']} cuch. aceite")
        total_html = " &middot; ".join(total_parts) or "?"
        row_class = ' class="plan-day-ayuno"' if day.get("ayuno") else ""
        ayuno_badge = " " + badge("ayuno") if day.get("ayuno") else ""
        rows.append(f"""<tr{row_class}>
  <td>{html.escape(DAY_LABELS[key])}{ayuno_badge}</td>
  <td>{render_meal_cell(day.get("comida"), recipes_by_slug)}</td>
  <td>{render_meal_cell(day.get("merienda"), recipes_by_slug)}</td>
  <td>{render_meal_cell(day.get("cena"), recipes_by_slug)}</td>
  <td class="plan-total">{total_html}</td>
</tr>""")
    rows_html = "\n".join(rows)

    sections = []
    resumen = plan.get("resumen_semanal")
    if resumen:
        sections.append(f"<h2>Resumen de la semana</h2>\n<p>{html.escape(str(resumen))}</p>")

    nuevas = plan.get("recetas_nuevas") or []
    if nuevas:
        pills = "".join(
            f'<a class="tag" href="../recetas/{html.escape(slug)}.html">'
            f'{html.escape(recipes_by_slug.get(slug, {}).get("titulo", slug))}</a>'
            for slug in nuevas
        )
        sections.append(f'<h2>Receta nueva esta semana</h2>\n<div class="tags">{pills}</div>')

    compra = plan.get("lista_compra") or []
    if compra:
        items = "\n".join(
            f'<li><label><input type="checkbox" class="shopping-check" data-index="{i}">'
            f'<span>{html.escape(str(item))}</span></label></li>'
            for i, item in enumerate(compra)
        )
        sections.append(
            '<h2>Lista de la compra (orientativa)</h2>\n'
            '<p class="plan-note">Puedes ir marcando lo que ya tienes en el carro; se queda guardado en este navegador.</p>\n'
            f'<ul class="shopping-list" data-plan="{html.escape(plan["_slug"])}">\n{items}\n</ul>'
        )

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Semana {html.escape(str(semana))} &mdash; Recetario</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="back-link" href="index.html">&larr; Todos los planes</a>
<article>
<h1>Semana {html.escape(str(semana))}</h1>
<p class="subtitle">{html.escape(date_range)}</p>
<table class="plan-table">
<thead><tr><th>Día</th><th>Comida</th><th>Merienda</th><th>Cena</th><th>Total del día</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>
<p class="plan-note">Desayuno fijo todos los días, repartido durante la mañana hasta una hora antes de comer: café con leche de soja sin azúcar, yogur con frutos rojos y semillas, 20&nbsp;g de nueces y fruta de temporada. No cambia de una semana a otra, así que no se repite en la tabla; los totales de cada día ya lo incluyen. Las cifras son estimaciones, con un margen real de ±10&nbsp;%.</p>
{"".join(sections)}
</article>
<script src="../assets/shopping-list.js" defer></script>
</body>
</html>
"""


def render_plan_card(plan, recipes_by_slug):
    slug = plan["_slug"]
    semana = plan.get("semana", slug)
    inicio, fin = plan.get("fecha_inicio"), plan.get("fecha_fin")
    date_range = format_date_range(inicio, fin) if inicio and fin else ""
    year = str(to_date(inicio).year) if inicio else ""
    month = f"{to_date(inicio).month:02d}" if inicio else ""
    resumen = str(plan.get("resumen_semanal") or "")
    resumen_short = (resumen[:140].rsplit(" ", 1)[0] + "…") if len(resumen) > 140 else resumen
    nuevas = plan.get("recetas_nuevas") or []
    nuevas_badge = ""
    if nuevas:
        label = "1 receta nueva" if len(nuevas) == 1 else f"{len(nuevas)} recetas nuevas"
        nuevas_badge = badge(label)

    return f"""<div class="card week-card" data-year="{html.escape(year)}" data-month="{html.escape(month)}">
  <a class="card-link" href="{html.escape(slug)}.html" aria-label="Semana {html.escape(str(semana))}"></a>
  <div class="card-body">
    <h3>Semana {html.escape(str(semana))}</h3>
    <p class="week-dates">{html.escape(date_range)}</p>
    <div class="badges">{nuevas_badge}</div>
    <p class="week-summary">{html.escape(resumen_short)}</p>
  </div>
</div>"""


def render_plan_index_html(plans, recipes_by_slug):
    if not plans:
        filters_html = ""
        body_html = '<p class="empty-state">Todavía no hay planes semanales guardados.</p>'
    else:
        years = sorted(
            {str(to_date(p["fecha_inicio"]).year) for p in plans if p.get("fecha_inicio")}, reverse=True
        )
        months_present = sorted(
            {to_date(p["fecha_inicio"]).month for p in plans if p.get("fecha_inicio")}
        )
        year_chips = '<button type="button" class="chip active" data-filter-year="">Todos</button>' + "".join(
            f'<button type="button" class="chip" data-filter-year="{y}">{y}</button>' for y in years
        )
        month_chips = '<button type="button" class="chip active" data-filter-month="">Todos</button>' + "".join(
            f'<button type="button" class="chip" data-filter-month="{m:02d}">{MONTH_NAMES_ES[m - 1]}</button>'
            for m in months_present
        )
        filters_html = f"""<div class="plan-filters">
  <div class="chip-group" id="year-filters" aria-label="Filtrar por año">{year_chips}</div>
  <div class="chip-group" id="month-filters" aria-label="Filtrar por mes">{month_chips}</div>
</div>
<p id="plan-counter" class="counter"></p>
"""
        cards_html = "\n".join(render_plan_card(p, recipes_by_slug) for p in plans)
        body_html = f'<main class="grid" id="plan-grid">\n{cards_html}\n</main>'

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planes semanales &mdash; Recetario</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="back-link" href="../index.html">&larr; Recetas</a>
<header>
  <h1>Planes semanales</h1>
  <p class="subtitle">Histórico de menús semanales &mdash; {len(plans)} semana{"s" if len(plans) != 1 else ""}</p>
</header>
{filters_html}{body_html}
<footer>
  <p><a href="https://github.com/rmunoz/recetario">Código fuente en GitHub</a></p>
</footer>
<script src="../assets/plan.js" defer></script>
</body>
</html>
"""


def copy_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "search.js", "voice.js", "plan.js", "shopping-list.js"):
        shutil.copyfile(TEMPLATES_DIR / name, ASSETS_DIR / name)
    if IMAGES_DIR.exists():
        images_dest = ASSETS_DIR / "imagenes"
        if images_dest.exists():
            shutil.rmtree(images_dest)
        shutil.copytree(IMAGES_DIR, images_dest)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Override the output directory (default: docs/). Useful to validate "
             "the recipes without touching the real docs/ directory.",
    )
    return parser.parse_args()


def main():
    global DOCS_DIR, RECIPES_HTML_DIR, PLAN_HTML_DIR, ASSETS_DIR
    args = parse_args()
    if args.output:
        DOCS_DIR = args.output
        RECIPES_HTML_DIR = DOCS_DIR / "recetas"
        PLAN_HTML_DIR = DOCS_DIR / "plan"
        ASSETS_DIR = DOCS_DIR / "assets"

    recipes = load_recipes()
    recipes_by_slug = {r["_slug"]: r for r in recipes}
    variants_by_parent = validate_variants(recipes)

    if RECIPES_HTML_DIR.exists():
        shutil.rmtree(RECIPES_HTML_DIR)
    RECIPES_HTML_DIR.mkdir(parents=True, exist_ok=True)
    copy_assets()

    for recipe in recipes:
        destination = RECIPES_HTML_DIR / f"{recipe['_slug']}.html"
        destination.write_text(render_recipe_html(recipe, recipes_by_slug, variants_by_parent), encoding="utf-8")

    (DOCS_DIR / "index.html").write_text(render_index_html(recipes, recipes_by_slug), encoding="utf-8")

    plans = load_plans()
    if PLAN_HTML_DIR.exists():
        shutil.rmtree(PLAN_HTML_DIR)
    PLAN_HTML_DIR.mkdir(parents=True, exist_ok=True)

    for plan in plans:
        destination = PLAN_HTML_DIR / f"{plan['_slug']}.html"
        destination.write_text(render_plan_week_html(plan, recipes_by_slug), encoding="utf-8")

    (PLAN_HTML_DIR / "index.html").write_text(render_plan_index_html(plans, recipes_by_slug), encoding="utf-8")

    print(f"Generated {len(recipes)} recipes and {len(plans)} weekly plans in {DOCS_DIR}")


if __name__ == "__main__":
    main()
