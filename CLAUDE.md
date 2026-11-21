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
├── imagenes/                  # fotos propias de recetas, referenciadas desde imagen: imagenes/<slug>.jpg
├── plan/
│   └── YYYY/semanaXX.yaml    # (opcional) planes semanales guardados
├── scripts/
│   ├── generate_site.py      # genera docs/ a partir de recetas/*.yaml (admite --output para validar sin tocar docs/)
│   ├── pre-commit            # hook de git: valida los YAML antes de comitear (instalar con install-hooks.sh)
│   ├── install-hooks.sh      # instala scripts/pre-commit en .git/hooks/
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
tags: [coliflor, verdura, guarnicion, vegetariana, horno]
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
  - Encender el horno a 200°C.
  - Mezclar el aliño y masajear la coliflor.
  - Cocinar 30-40 minutos y servir con la salsa de yogur.
fuente: https://ejemplo.com/receta-original   # opcional en recetas propias
imagen: imagenes/coliflor-especiada-con-yogur-y-granada.jpg   # opcional; URL externa o ruta en imagenes/; si no hay, se omite la clave
```

- Obligatorios: `titulo`, `tags`, `raciones`, `kcal_racion`, `proteina_racion_g`, `aceite_cucharillas`, `ingredientes`, `pasos`.
- `kcal_racion` y `proteina_racion_g` son **por persona**; `aceite_cucharillas` es de la receta completa.
- Tags en minúsculas, sin acentos, con guiones. Cifras como números, sin unidades.
- Cada elemento de `ingredientes` lleva `texto` (cantidad y nombre tal cual se usaría en la cocina) y, si el ingrediente existe en `ingredientes/`, su slug en `ingrediente`.
- `ingredientes` puede ser una lista plana o llevar **grupos** cuando la receta tiene partes distintas (relleno y salsa, puré y salsa...): un elemento `grupo: <nombre>` con su lista `items`, que se muestra con un subtítulo en la web. Los ingredientes sueltos y los grupos se pueden mezclar (los sueltos salen sin título), un grupo no puede contener otro grupo y debe tener al menos un ingrediente. Los `pasos` siguen siendo una lista lineal (el modo voz los recorre uno a uno), aunque los ingredientes estén agrupados. No uses líneas tipo `"Relleno:"` como ingrediente.

El esquema completo y un ejemplo están en `.claude/skills/receta-adaptada/references/`.

### Variantes de una receta

Una receta puede tener variantes (p. ej. judías verdes con tomate **y patata**, o el yogur con frutos rojos en versión más ligera). Cada variante es **un fichero `.yaml` completo** (sus propios ingredientes, pasos y cifras) con dos claves opcionales extra:

```yaml
variante_de: judias-verdes-con-tomate          # slug de la receta principal
variante_resumen: Con patata cocida, para que sea un plato más completo   # texto corto que se ve en la principal; si falta, se usa el título
```

- Una principal puede tener varias variantes, pero **una variante no puede tener otras variantes** ni apuntar a sí misma; `generate_site.py` aborta si `variante_de` apunta a algo inexistente o a otra variante.
- Las variantes **no salen en el listado** de la web, solo en la búsqueda (por título, tags, etc.). En la página de la receta principal aparece un recuadro "Variante(s)" con enlace y cifras, y la página de la variante enlaza de vuelta a la principal. Si la variante no tiene `imagen`, se usa la de la principal.
- Las variantes llevan sus cifras propias (`kcal_racion`, etc.) y se pueden usar en un plan semanal igual que cualquier receta (`receta: <slug de la variante>`).

## Formato de plan semanal guardado

Cuando se guarda un plan (lo pide Ricardo tras ajustar lo que la skill propuso en el chat), se crea `plan/YYYY/semanaXX.yaml`: cabecera con `semana` (id ISO `AAAA-Wnn`), `fecha_inicio`/`fecha_fin`, los 7 días (`dias.lunes`...`dias.domingo`) con `comida`/`merienda`/`cena` (cada una con `tipo`: `receta`, `plato_habitual` o `pauta_base`, `texto`, `kcal`, `proteina_g`, y `receta` con el slug si `tipo: receta`) y `totales` del día, más `recetas_nuevas`, `resumen_semanal` y `lista_compra` (opcional, orientativa) a nivel de semana. El esquema completo y un ejemplo están en `.claude/skills/plan-semanal-comidas/references/esquema-plan.md`.

Este fichero se publica tal cual en `docs/plan/` (ver "Sitio estático" más abajo): no incluyas en `resumen_semanal` ni en `lista_compra` nada que Ricardo no quiera ver en la web pública.

## Ingredientes

Fichero `.yaml` en `ingredientes/` por ingrediente, nombre en slug: `nombre`, `unidad_ref` (a qué cantidad se refieren las cifras), `kcal`, `proteina_g`, `grasa_g`, `hidratos_g` y `fuente` (`etiqueta` si el dato viene del envase real de Ricardo, o `estimado`). Campos opcionales: `categoria`, `grasa_saturada_g`/`grasa_monoinsaturada_g`/`grasa_poliinsaturada_g`, `azucares_g`, `fibra_g`, `sal_g`, `omega3_g`, `otros` (vitaminas/minerales sueltos) y `nota` (p. ej. equivalencia en cucharadas). Esquema completo y ejemplo en `.claude/skills/receta-adaptada/references/esquema-ingrediente.md`.

No inventes un ingrediente nuevo en este directorio por iniciativa propia: lo crea Ricardo con sus datos, o tú cuando él te los dicte explícitamente.

## Cálculo nutricional

1. Usa primero los valores de `ingredientes/` y, si falta un ingrediente, los valores de referencia del modelo, indicando cuáles son estimados.
2. Las cifras son **estimaciones**, no mediciones: el margen real puede ser de ±10 %. Di siempre cuáles son las más inciertas.
3. Revisa las sumas antes de escribirlas en el fichero.

## Skills

- `receta-adaptada`: se usa cuando Ricardo pega una receta o dicta una propia. Adapta (si procede), escala, estima kcal, valora el encaje y crea el fichero.
- `plan-semanal-comidas`: monta la semana con el desayuno fijo, comida, cena y merienda opcional, respetando los límites de arriba, e intenta incluir cada semana alguna receta que no se haya usado en semanas anteriores. Para leer las recetas usa `python .claude/skills/plan-semanal-comidas/scripts/read_recipes.py recetas/`, y para mirar el histórico de planes guardados, `python .claude/skills/plan-semanal-comidas/scripts/read_plans.py plan/` (ambos necesitan PyYAML). La generación del plan sigue siendo siempre a través de la skill (no automática), para poder ajustarlo antes de comitearlo.

Cuando cambie una convención, actualiza a la vez este fichero y la skill afectada para que no se contradigan.

## Sitio estático (GitHub Pages)

`scripts/generate_site.py` lee `recetas/*.yaml` y `plan/**/*.yaml` y genera `docs/`: un listado de recetas principales (`docs/index.html`; las variantes solo aparecen al buscar) con buscador en JS por título/tags/momento, una página por receta (`docs/recetas/<slug>.html`), y un histórico de planes semanales (`docs/plan/index.html`, con filtro rápido por año y mes, y `docs/plan/<slug>.html` por semana, enlazando a la receta cuando la comida es `tipo: receta`). Sin backend, sin dependencias externas, todo client-side. Si `plan/` no existe o está vacío, `docs/plan/index.html` se genera igual con un aviso de que no hay planes todavía. El código del generador (nombres, comentarios) está en inglés; el texto que se ve en la página sigue en español, como el resto del contenido del repositorio.

- Un workflow (`.github/workflows/generate-site.yml`) ejecuta `python scripts/generate_site.py` y comitea `docs/` automáticamente en cada push a `main` que toque `recetas/`, `ingredientes/`, `plan/` o `scripts/`. No hace falta regenerarlo a mano salvo para previsualizar en local antes de comitear.
- El mismo workflow corre también en los `pull_request` que tocan esas rutas, pero solo genera el sitio (sin comitear ni pushear) para que una receta con un YAML mal formado no se pueda fusionar a `main`. `scripts/generate_site.py` admite `--output <dir>` para generar en un directorio temporal sin tocar `docs/`, que es lo que usa el hook de pre-commit.
- Hook local de pre-commit (`scripts/pre-commit`, instálalo una vez con `scripts/install-hooks.sh`): antes de comitear, valida que los YAML tocados en `recetas/`, `ingredientes/` o `plan/` sean YAML válido y que `generate_site.py` los procese sin errores. `.git/hooks/` no se versiona, así que cada copia del repositorio necesita ese paso de instalación; el workflow de la PR es la red de seguridad para quien no lo tenga instalado.
- `docs/` es generado; no lo edites a mano. Los estilos y el JS "de verdad" están en `scripts/templates/` (`style.css`, `search.js`, `voice.js`, `plan.js`), que el script solo copia. Las fotos propias de `imagenes/` se copian igual a `docs/assets/imagenes/`.
- Para publicarlo: activar GitHub Pages en el repo apuntando a la carpeta `/docs` de `main`. El repositorio debe ser público (o tener un plan de pago) para que Pages sea gratuito. El histórico de planes semanales se publica tal cual, igual que las recetas.
- Modo voz (Web Speech API) en la página de receta, Fase 1 ya implementada: botón "Empezar la receta" dicta los pasos y acepta los comandos "siguiente", "atrás", "repite", "ingredientes" y "para" (con fuzzy matching simple en `scripts/templates/voice.js`). Hay aviso de privacidad fijo (en Chrome el audio va a los servidores de Google) y un fallback de botones "paso anterior/siguiente" siempre visible, que también lee el paso en voz alta, para navegadores sin `SpeechRecognition` o con el micro bloqueado.
- Previsto para más adelante (Fase 2 del modo voz, cuando Ricardo lo pida): Wake Lock API para mantener la pantalla encendida mientras se escucha, y `processLocally` para reconocimiento on-device cuando el navegador lo soporte. También sigue pendiente, sin relación con la voz: página de ingredientes.

## Cómo trabajar aquí

- Antes de crear estructura nueva (carpetas, formatos, scripts), propón el diseño a Ricardo y espera su confirmación.
- El código (scripts, nombres de fichero, identificadores, comentarios) va en **inglés**, aunque el resto del repositorio esté en español. El texto que ve Ricardo (contenido de recetas, dieta, y lo que se muestra en la web generada) sigue en español.
- No inventes datos que falten en una receta o ingrediente; pregunta o márcalos como estimación.
- Los cambios van en commits pequeños y con mensaje claro (por ejemplo `receta: añade lentejas con verduras`).
