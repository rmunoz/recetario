# Esquema del plan semanal guardado

Cuando el usuario pide guardar el plan, se crea `plan/YYYY/semanaXX.yaml` (`XX` el número de semana ISO con dos cifras, p. ej. `semana47.yaml`). El script `scripts/generate_site.py` lee estos campos para publicar el histórico en `docs/plan/`, y `scripts/read_plans.py` para que la skill pueda mirar semanas anteriores: no cambies sus nombres ni sus tipos.

## Campos de cabecera

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `semana` | texto | sí | Identificador ISO, `AAAA-Wnn` (p. ej. `2026-W47`) |
| `fecha_inicio` | fecha | sí | Lunes de esa semana, `AAAA-MM-DD` |
| `fecha_fin` | fecha | sí | Domingo de esa semana |
| `dias` | objeto | sí | Ver más abajo, una clave por día en español: `lunes`...`domingo` |
| `recetas_nuevas` | lista | no | Slugs de `recetas/` usados esta semana que no aparecían en semanas anteriores |
| `resumen_semanal` | texto | sí | 3-4 líneas sobre el equilibrio de la semana (pescado, legumbres, variedad...) |
| `lista_compra` | lista de texto | no | Orientativa; se omite la clave si no se generó |

## Cada día (`dias.lunes`, etc.)

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `ayuno` | booleano | sí | `true` si ese día es de cena temprana + ayuno intermitente (sin merienda) |
| `comida` | objeto | sí | Ver "cada comida" abajo |
| `merienda` | objeto | no | Se omite la clave entera si ese día no hay merienda |
| `cena` | objeto | sí | Ver "cada comida" abajo |
| `totales` | objeto | sí | `kcal`, `proteina_g`, `aceite_cucharillas` del día completo (incluye el desayuno fijo) |

El desayuno no se repite día a día: es fijo y ya está descrito en `dieta.md`; solo se refleja en `totales`.

## Cada comida (`comida`, `merienda`, `cena`)

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `tipo` | texto | sí | `receta` (viene de `recetas/`), `plato_habitual` (tabla de `dieta.md`) o `pauta_base` (menú de `dieta/pauta-base.md`) |
| `receta` | texto | solo si `tipo: receta` | Slug en `recetas/` |
| `texto` | texto | sí | Nombre a mostrar siempre, igual si es receta o plato habitual |
| `kcal` | número | sí | kcal de esa comida para una persona |
| `proteina_g` | número | sí | Proteína de esa comida para una persona |

## Ejemplo (un día)

```yaml
semana: 2026-W47
fecha_inicio: 2026-11-16
fecha_fin: 2026-11-22
dias:
  lunes:
    ayuno: false
    comida:
      tipo: receta
      receta: lentejas-vegetarianas
      texto: Lentejas vegetarianas
      kcal: 340
      proteina_g: 20
    merienda:
      tipo: plato_habitual
      texto: 80 g de caballa en conserva
      kcal: 140
      proteina_g: 18
    cena:
      tipo: pauta_base
      texto: Pescado blanco a la plancha con lechuga y tomate
      kcal: 230
      proteina_g: 30
    totales:
      kcal: 1210
      proteina_g: 91
      aceite_cucharillas: 1.5
  martes: {...}
  # ...resto de días hasta domingo
recetas_nuevas: [coliflor-especiada-con-yogur-y-granada]
resumen_semanal: >
  Semana con pescado blanco dos veces y legumbres una vez; sin carne roja.
  Falta pescado azul: la próxima semana convendría incluirlo.
lista_compra:
  - 3 cebollas
  - 1 coliflor mediana
  - ajo (varias recetas)
```

## Notas

- Las cifras de `kcal`/`proteina_g` son estimaciones (±10 % real), igual que en las recetas: no las presentes como exactas.
- `lista_compra` agrupa por ingrediente (usa el slug de `ingrediente:` cuando la receta lo tiene, si no el nombre normalizado); suma cantidades solo cuando son números simples con la misma unidad ("1 cebolla" + "2 cebollas" → "3 cebollas"). Si no son sumables a simple vista, se agrupan bajo el mismo ingrediente sin forzar un número.
- El fichero se publica tal cual en `docs/plan/`: el repositorio ya es público, así que no incluyas en `resumen_semanal` ni en `lista_compra` nada que el usuario no quiera ver en la web.
