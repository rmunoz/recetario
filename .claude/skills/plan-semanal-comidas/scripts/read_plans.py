#!/usr/bin/env python3
"""Read every saved weekly plan and print which recipes/dishes were used when.

Usage: python read_plans.py <plan_directory>

Needs PyYAML (pip install pyyaml). Helps the planner avoid repeating a
recipe and pick something not used in recent weeks, per week, most
recent first.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing PyYAML. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

MEALS = ["comida", "merienda", "cena"]
DAYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


def read_plan(path):
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return None
    return data


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    folder = Path(sys.argv[1])
    files = sorted(folder.rglob("*.yaml"), reverse=True)
    if not files:
        print(f"No hay planes guardados todavía en {folder}")
        return

    warnings = []
    plans = []
    for f in files:
        try:
            data = read_plan(f)
        except yaml.YAMLError as e:
            warnings.append(f"{f.name}: YAML inválido ({e}), se ignora")
            continue
        if data is None:
            warnings.append(f"{f.name}: vacío o con formato inesperado, se ignora")
            continue
        plans.append((f, data))

    # Most recent fecha_inicio first, regardless of filename order.
    plans.sort(key=lambda item: item[1].get("fecha_inicio", ""), reverse=True)

    used_count = {}
    print("| semana | fecha_inicio | recetas usadas | platos habituales / pauta base |")
    print("|---|---|---|---|")
    for f, data in plans:
        recetas, otros = [], []
        dias = data.get("dias", {})
        if not isinstance(dias, dict):
            warnings.append(f"{f.name}: falta o formato inesperado en 'dias'")
            dias = {}
        for day_name in DAYS:
            day = dias.get(day_name)
            if not isinstance(day, dict):
                continue
            for meal_name in MEALS:
                meal = day.get(meal_name)
                if not isinstance(meal, dict):
                    continue
                if meal.get("tipo") == "receta" and meal.get("receta"):
                    recetas.append(meal["receta"])
                    used_count[meal["receta"]] = used_count.get(meal["receta"], 0) + 1
                elif meal.get("texto"):
                    otros.append(meal["texto"])
        print(f"| {data.get('semana', '?')} | {data.get('fecha_inicio', '?')} "
              f"| {', '.join(sorted(set(recetas))) or '(ninguna)'} "
              f"| {', '.join(sorted(set(otros))) or '(ninguno)'} |")

    if used_count:
        print("\nRecetas usadas en total, de más a menos veces (para evitar repetir o priorizar lo menos usado):")
        for slug, count in sorted(used_count.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"- {slug}: {count}")

    if warnings:
        print("\nAvisos:")
        for w in warnings:
            print(f"- {w}")


if __name__ == "__main__":
    main()
