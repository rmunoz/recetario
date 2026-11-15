# Repositorio de recetas y plan de comidas

Repositorio personal de Ricardo para gestionar recetas, ingredientes y planes semanales dentro de una dieta hipocalórica. Se cocina para 2 personas (Ricardo y su mujer). Todo el contenido y las respuestas van **en español**.

## Estructura

```
.
├── CLAUDE.md                 # este fichero
├── dieta.md                  # reglas operativas de la dieta (fuente única)
├── dieta/
│   └── pauta-base.md         # pauta hipocalórica del endocrino (Dr. Palacios Latasa), como referencia
├── ingredientes/             # ingredientes habituales, un fichero .yaml por ingrediente
├── recetas/                  # una receta por fichero .yaml
├── plan/
│   └── YYYY/semanaXX.yaml    # (opcional) planes semanales guardados
├── scripts/
│   ├── generate_site.py      # genera docs/ a partir de recetas/*.yaml
│   └── templates/            # CSS y JS estáticos que el script copia tal cual
├── docs/                      # sitio generado (GitHub Pages sirve /docs en main); no editar a mano
└── .claude/skills/
    ├── receta-adaptada/      # adapta, escala y guarda una receta
    └── plan-semanal-comidas/ # monta el plan semanal
```

Los elementos marcados como "previsto" u "opcional" aún no existen o no se crean hasta que haga falta; créalos solo cuando Ricardo lo pida.

## Dieta y límites

Las reglas completas (kcal, proteína, aceite, desayuno fijo, cenas ligeras, ayuno intermitente, platos habituales fuera del repositorio y equilibrio semanal) viven en [`dieta.md`](dieta.md) — es la fuente única que usan las skills, no las repitas aquí. Resumen:

- Tope: **1800 kcal/día** (objetivo 1700-1800; no bajar de ~1600 sin que lo pida).
- Proteína: ~110 g/día. Aceite: máximo **4 cucharillas al día**.
- Desayuno fijo todos los días; cenas más ligeras que las comidas.
- **2-3 días por semana cena temprano (~17:00)** y ayuno intermitente hasta las 8:00 del día siguiente (sin merienda esos días).
- La pauta hipocalórica base procede del endocrino (Dr. Palacios Latasa), referencia completa en `dieta/pauta-base.md`. Mantén su estructura y no cambies sus criterios por iniciativa propia: las recetas del repositorio aportan variedad dentro de ella.

## Reglas al adaptar recetas de internet

Son decisiones fijas de Ricardo, no sugerencias:

- Lácteos al **0 %** manteniendo la proteína alta (yogur griego 0 %, skyr, queso batido 0 %).
- Aceite al mínimo y contado en cucharillas. Se eliminan los chorritos de remate.
- Ingredientes grasos por alternativas más ligeras (tahini → semillas de sésamo, nata → yogur 0 %, etc.).
- Escalar siempre a **2 personas** y poner `raciones: 2`.
- Los `pasos` se redactan siempre con palabras propias, nunca copiados tal cual de la fuente, para evitar problemas de derechos de autor sobre el texto original. Mismo orden, técnicas y tiempos; estilo directo como en las recetas propias.
- Las recetas propias de Ricardo (las que hace habitualmente) no se "adaptan": ya forman parte de su dieta. En ellas, pon `fuente: propia` en vez de omitir la clave.

## Formato de receta

Fichero `.yaml` en `recetas/`, nombre en slug (minúsculas, sin acentos, con guiones):

```yaml
titulo: Coliflor especiada con yogur y granada
tags: [coliflor, verdura, guarnicion, vegetariana, airfryer]
raciones: 2
kcal_racion: 115
proteina_racion_g: 9
aceite_cucharillas: 0.5
momento: [guarnicion, cena]   # opcional: desayuno, comida, cena, guarnicion, merienda
sodio: medio                  # opcional: bajo, medio, alto
ingredientes:
  - texto: "½ coliflor mediana (unos 500 g)"
  - texto: 1 yogur griego 0 % (alto en proteína)
    ingrediente: yogur-griego-0   # opcional: slug en ingredientes/, si existe
pasos:
  - Encender la airfryer a 180°C.
  - Mezclar el aliño y masajear la coliflor.
  - Cocinar 30-40 minutos y servir con la salsa de yogur.
fuente: https://ejemplo.com/receta-original   # opcional en recetas propias
imagen: https://ejemplo.com/foto.jpg          # opcional; si no hay, se omite la clave
```

- Obligatorios: `titulo`, `tags`, `raciones`, `kcal_racion`, `proteina_racion_g`, `aceite_cucharillas`, `ingredientes`, `pasos`.
- `kcal_racion` y `proteina_racion_g` son **por persona**; `aceite_cucharillas` es de la receta completa.
- Tags en minúsculas, sin acentos, con guiones. Cifras como números, sin unidades.
- Cada elemento de `ingredientes` lleva `texto` (cantidad y nombre tal cual se usaría en la cocina) y, si el ingrediente existe en `ingredientes/`, su slug en `ingrediente`.

El esquema completo y un ejemplo están en `.claude/skills/receta-adaptada/references/`.

## Ingredientes

Fichero `.yaml` en `ingredientes/` por ingrediente, nombre en slug: `nombre`, `unidad_ref` (a qué cantidad se refieren las cifras), `kcal`, `proteina_g`, `grasa_g`, `hidratos_g` y `fuente` (`etiqueta` si el dato viene del envase real de Ricardo, o `estimado`). Campos opcionales: `categoria`, `grasa_saturada_g`/`grasa_monoinsaturada_g`/`grasa_poliinsaturada_g`, `azucares_g`, `fibra_g`, `sal_g`, `omega3_g`, `otros` (vitaminas/minerales sueltos) y `nota` (p. ej. equivalencia en cucharadas). Esquema completo y ejemplo en `.claude/skills/receta-adaptada/references/esquema-ingrediente.md`.

No inventes un ingrediente nuevo en este directorio por iniciativa propia: lo crea Ricardo con sus datos, o tú cuando él te los dicte explícitamente.

## Cálculo nutricional

1. Usa primero los valores de `ingredientes/` y, si falta un ingrediente, los valores de referencia del modelo, indicando cuáles son estimados.
2. Las cifras son **estimaciones**, no mediciones: el margen real puede ser de ±10 %. Di siempre cuáles son las más inciertas.
3. Revisa las sumas antes de escribirlas en el fichero.

## Skills

- `receta-adaptada`: se usa cuando Ricardo pega una receta o dicta una propia. Adapta (si procede), escala, estima kcal, valora el encaje y crea el fichero.
- `plan-semanal-comidas`: monta la semana con el desayuno fijo, comida, cena y merienda opcional, respetando los límites de arriba. Para leer las recetas usa `python .claude/skills/plan-semanal-comidas/scripts/read_recipes.py recetas/` (necesita PyYAML).

Cuando cambie una convención, actualiza a la vez este fichero y la skill afectada para que no se contradigan.

## Sitio estático (GitHub Pages)

`scripts/generate_site.py` lee `recetas/*.yaml` y genera `docs/`: un listado (`docs/index.html`) con buscador en JS por título/tags/momento (sin backend, sin dependencias externas) y una página por receta (`docs/recetas/<slug>.html`). Todo client-side. El código del generador (nombres, comentarios) está en inglés; el texto que se ve en la página sigue en español, como el resto del contenido del repositorio.

- Ejecútalo con `python scripts/generate_site.py` (necesita PyYAML) cada vez que una receta cambie, y comitea `docs/` junto con el cambio: no se regenera solo.
- `docs/` es generado; no lo edites a mano. Los estilos y el JS "de verdad" están en `scripts/templates/` (`style.css`, `search.js`), que el script solo copia.
- Para publicarlo: activar GitHub Pages en el repo apuntando a la carpeta `/docs` de `main`. Sin GitHub Actions.
- Previsto para más adelante, cuando Ricardo lo pida: página de ingredientes, planes semanales con enlaces a recetas, y en la página de receta un modo de voz (Web Speech API) que vaya dictando los pasos uno a uno. La página de receta ya deja los pasos en un `<script type="application/json" id="steps-data">` pensado para eso, pero no hay ninguna lógica de voz todavía.

## Cómo trabajar aquí

- Antes de crear estructura nueva (carpetas, formatos, scripts), propón el diseño a Ricardo y espera su confirmación.
- El código (scripts, nombres de fichero, identificadores, comentarios) va en **inglés**, aunque el resto del repositorio esté en español. El texto que ve Ricardo (contenido de recetas, dieta, y lo que se muestra en la web generada) sigue en español.
- No inventes datos que falten en una receta o ingrediente; pregunta o márcalos como estimación.
- Los cambios van en commits pequeños y con mensaje claro (por ejemplo `receta: añade lentejas con verduras`).
