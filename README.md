# Recetario

Repositorio personal de recetas, ingredientes y planes de comidas semanales dentro de una dieta hipocalórica. Genera un sitio estático, sin backend, publicable con GitHub Pages.

## Estructura

- `recetas/` — una receta por fichero `.yaml`.
- `ingredientes/` — datos nutricionales de ingredientes habituales.
- `plan/` — planes semanales guardados (`plan/AAAA/semanaNN.yaml`).
- `dieta.md` — reglas operativas de la dieta.
- `scripts/generate_site.py` — genera el sitio estático en `docs/` a partir de lo anterior.
- `docs/` — sitio generado (no se edita a mano); GitHub Pages lo sirve desde `main`.
- `.claude/skills/` — skills de Claude Code para adaptar recetas y montar el plan semanal.

## Generar el sitio en local

Requiere Python 3 y PyYAML:

```bash
pip install pyyaml
python scripts/generate_site.py
```

Esto regenera `docs/` a partir de `recetas/`, `ingredientes/` y `plan/`. Para previsualizarlo, sirve la carpeta con un servidor local, por ejemplo:

```bash
python -m http.server 8000
```

y abre `http://localhost:8000/docs/`.

## Publicar con GitHub Pages

En la configuración del repositorio, activa GitHub Pages apuntando a la carpeta `/docs` de la rama `main`. Un workflow de GitHub Actions regenera `docs/` automáticamente en cada push a `main` que modifique `recetas/`, `ingredientes/`, `plan/` o `scripts/`, así que no hace falta regenerarlo a mano salvo para previsualizar.

## Licencia

[MIT](LICENSE)
