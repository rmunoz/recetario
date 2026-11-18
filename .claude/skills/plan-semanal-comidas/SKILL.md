---
name: plan-semanal-comidas
description: Prepara un plan semanal de comidas (comida, merienda opcional y cena) para el usuario a partir de su repositorio de recetas en YAML, respetando su desayuno fijo, su tope de 1800 kcal/día, su objetivo de proteína y su límite de aceite. Úsala siempre que pida un "plan semanal", "menú de la semana", "qué comemos esta semana", "planifica las comidas" o una lista de la compra basada en el repositorio de recetas, aunque no mencione la dieta.
---

# Plan semanal de comidas

Combina las recetas del repositorio del usuario con su desayuno fijo y sus platos habituales para montar una semana equilibrada de lunes a domingo dentro de su dieta hipocalórica. Responde en español.

## Antes de empezar

1. **Localiza las recetas.** Pide al usuario que suba los `.yaml` del repositorio o la carpeta si no están en `/mnt/user-data/uploads`. Cuando los tengas, ejecuta:
   `python scripts/read_recipes.py <carpeta_de_recetas>`
   Te da una tabla con kcal, proteína, aceite, momento y tags, y avisa de campos que faltan. Si hay avisos, no inventes los datos que faltan: usa los que tengas, dilo y propón completarlos con la skill `receta-adaptada`.
2. **Mira el histórico.** Si existe `plan/`, ejecuta:
   `python scripts/read_plans.py <carpeta_plan>`
   Te da, semana a semana (más reciente primero), qué receta o plato se usó cada día, y un recuento total por receta. Úsalo para no repetir lo de la semana anterior y para saber qué recetas llevan más tiempo sin aparecer. Si `plan/` no existe o está vacío, es la primera semana: no hay nada que mirar.
3. **Carga las restricciones.** Lee `dieta.md` en la raíz del repositorio. Si no existe, lee `references/perfil-dieta.md` y avisa de que falta `dieta.md`.
4. **Pregunta solo lo que cambie el plan**, y como mucho una cosa: por ejemplo, días con comida fuera de casa o ingredientes que no quieren repetir. Si el usuario ya dio esa información, no preguntes.

## Cómo construir el plan

1. **Desayuno fijo** todos los días con las kcal y proteína del perfil.
2. **Comida y cena**: prioriza las recetas del repositorio, con ración por persona. Si el repositorio no tiene suficientes para la semana, rellena los huecos con los platos habituales de `dieta.md` o, si tampoco encajan, con el menú orientativo de `dieta/pauta-base.md`, marcando siempre sus cifras como estimaciones. Usa `momento` y `tags` para decidir dónde encaja cada receta; si falta `momento`, deduce el uso por las tags y por la carga calórica, y avísalo. Añade también el pan de acompañamiento del día (ver la ración en `dieta.md`) en la comida o cena que no lo lleve ya incluido (p. ej. una tostada), sin superar el tope diario.
3. **Al menos una receta nueva por semana**: usando lo que viste en `read_plans.py`, incluye alguna receta del repositorio que no se haya usado en semanas anteriores (o, si todas se han usado ya, la que lleve más tiempo sin repetirse). Si el repositorio no tiene ninguna sin usar, dilo en vez de forzarlo.
4. **Merienda opcional**: decide cada día según lo que quede de kcal tras comida y cena, y si ese día hay ayuno. Sin hueco o con ayuno ese día, se omite.
5. **Ayuno intermitente**: marca 2-3 días de la semana con cena temprana (~17:00) y sin merienda ni ingesta hasta el desayuno siguiente; el domingo suele encajar bien para esto, pero no lo fuerces si el resto de la semana ya queda descompensado.
6. **Comprobaciones por día** (haz las sumas con cuidado y revisa cada total antes de mostrarlo):
   - Total de kcal ≤ 1800 (objetivo 1700-1800).
   - Proteína cerca de 110 g; si un día se queda corto, sube la proteína de la cena o ajusta la merienda.
   - Aceite ≤ 4 cucharillas: suma `aceite_cucharillas / raciones` de cada receta del día más el aceite de los platos habituales.
7. **Comprobaciones de la semana**: cuenta pescado, legumbres, carne roja, huevos y repeticiones, y compáralas con el equilibrio orientativo del perfil. Cuando falten recetas para cumplirlo, di qué tipo de recetas convendría añadir al repositorio.

## Formato de salida

Muestra el plan en el chat, no en un fichero, salvo que el usuario pida guardarlo (entonces crea `plan/YYYY/semanaXX.yaml`, con `XX` el número de semana ISO con dos cifras). El esquema completo del fichero está en `references/esquema-plan.md`; síguelo al pie de la letra, porque `scripts/generate_site.py` lo lee para publicar el histórico en `docs/plan/` (el repositorio es público, así que ese fichero queda visible en la web) y `scripts/read_plans.py` lo usa en semanas siguientes.

1. Tabla semanal: filas de lunes a domingo, columnas de desayuno, comida, merienda y cena, con kcal y proteína entre paréntesis.
2. Totales por día: kcal, proteína y cucharillas de aceite.
3. Un resumen del equilibrio semanal en 3-4 líneas, sin repetir la tabla.
4. Una línea que indique qué cifras son estimaciones (platos habituales y desayuno) y cuáles vienen de recetas del repositorio.

Ofrece al final la lista de la compra para 2 personas, sin generarla si no la piden. Es orientativa, no exacta (el usuario ya sabe lo que tiene en la despensa): agrupa por ingrediente (usa el slug de `ingrediente:` cuando la receta lo tiene, si no el nombre normalizado) y suma solo cantidades simples con la misma unidad ("1 cebolla" + "2 cebollas" → "3 cebollas"); si no son sumables a simple vista, agrúpalas bajo el mismo ingrediente sin forzar un número. Si se guarda el plan en fichero, guarda también esta lista en `lista_compra`.

## Honestidad con los datos

- Las recetas del repositorio llevan estimaciones de kcal, no mediciones. No presentes un total como exacto: el margen real puede ser de ±10 %.
- Si no hay recetas suficientes para una semana variada, dilo en vez de repetir la misma receta; combina con platos habituales y sugiere qué añadir.
- Si no consigues cuadrar 1800 kcal o el objetivo de proteína sin saltarte el aceite, explica el conflicto y propón la salida más sencilla.
