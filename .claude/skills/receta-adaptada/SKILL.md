---
name: receta-adaptada
description: Adapta una receta de internet a la dieta hipocalórica del usuario (~1800 kcal/día), la escala para 2 personas, estima kcal por ración, valora su encaje y genera el fichero YAML para el repositorio de recetas. Si la receta de origen no está en español (inglés u otro idioma), la traduce, convierte sus unidades a métrico y regionaliza ingredientes poco comunes en España. Úsala siempre que el usuario pegue una receta (texto o enlace, en cualquier idioma), diga "valora esta receta", "adapta esta receta", "añade esta receta al repo" o pida un fichero de una receta, aunque no mencione la dieta de forma explícita.
---

# Receta adaptada

Convierte una receta cualquiera en una receta del repositorio personal del usuario: traducida si hace falta, adaptada a su dieta, escalada a 2 personas, valorada y guardada como YAML con un formato fijo que otra skill (`plan-semanal-comidas`) lee después. Responde siempre en español.

## Flujo

1. **Obtener la receta.** Texto pegado o enlace. Si solo hay un enlace y no se puede abrir, pide que pegue el texto en lugar de inventar los ingredientes.
2. **Traducir si no está en español.** Ingredientes, cantidades, temperaturas y pasos pasan a español y a unidades métricas (gramos, mililitros, litros, °C), nunca se dejan en el idioma ni las unidades de origen. Usa `references/conversion-unidades.md` para convertir unidades US/imperiales cuando la receta no dé ya el equivalente métrico entre paréntesis (si lo da, usa ese dato real en vez de la conversión genérica). Esto se hace a la vez que el resto de la adaptación, no es un paso aparte de traducción literal.
3. **Buscar los ingredientes en el repositorio.** Para cada ingrediente de la receta, comprueba si existe un fichero en `ingredientes/` (slug en minúsculas con guiones). Si existe, usa esas cifras en vez de un valor de referencia genérico y enlázalo con el campo `ingrediente` (ver `references/esquema-ingrediente.md`). Si no existe, usa tu valor de referencia y dilo como estimado; no crees tú el fichero de `ingredientes/` por tu cuenta.
4. **Adaptar.** Aplica las adaptaciones de abajo sin preguntar, porque son decisiones fijas del usuario, no sugerencias. Cambia solo lo necesario y conserva el carácter del plato.
5. **Regionalizar.** Si un ingrediente no es habitual o no se vende como tal en los supermercados españoles (p. ej. *panko*, *buttermilk*, *celery seeds*, sal *kosher* de marca concreta), propón el sustituto más parecido que sí se encuentra en España, conservando su función en la receta (textura, sabor, técnica). Esto es independiente de las adaptaciones de dieta del punto 4: anota cada cambio regional por separado para el informe del paso 8.
6. **Escalar a 2 personas** (el usuario y su pareja). Divide las cantidades y redondea a medidas prácticas. Si algo no se puede dividir con sentido (medio huevo, un cuarto de lata), mantén la unidad entera y dilo en una nota. `raciones: 2` en el fichero.
7. **Estimar kcal.** Tabla por ingrediente con rango y "qué puede variar", total de la receta y por ración (una ración = lo que come una persona). Añade proteína por ración y una valoración cualitativa del sodio (bajo/medio/alto), porque es el punto que más se pasa por alto en mezclas de especias, salsas y conservas.
8. **Valorar el encaje** en ~1800 kcal/día: pros, contras (densidad calórica, proteína, sodio), cómo colocarla en el día (guarnición o plato principal, qué complementar) y variantes aún más ligeras con kcal aproximadas. Las adaptaciones fijas ya están aplicadas, así que las variantes deben ir más allá de ellas. Si el paso 5 cambió algún ingrediente, añade al informe una sección **"Cambios de regionalización"** aparte de las adaptaciones de dieta: ingrediente original → sustituto → motivo, para que el usuario los valide antes de comitear.
9. **Generar el fichero** `.yaml` según `references/esquema-receta.md` y presentarlo con `present_files`. Ver `references/ejemplo-coliflor.yaml` como modelo exacto.

## Adaptaciones fijas

- **Lácteos al 0 %** manteniendo la proteína alta: yogur griego 0 % (alto en proteína), skyr o queso batido 0 %. La nata o crema se sustituye por yogur o queso batido 0 %; la leche, por la versión 0 % o por bebida de soja sin azúcar, que es la que el usuario ya toma.
- **Aceite al mínimo.** El usuario tiene un límite de **4 cucharillas de aceite para todo el día**, así que cada cucharilla cuenta. Reduce el aceite todo lo que la técnica permita (horno con bandeja caliente, antiadherente, caldo o agua para sofreír) y elimina los chorritos de remate. Indica en el frontmatter cuántas cucharillas gasta la receta completa en `aceite_cucharillas`. Una cucharilla son unos 4-5 g (~40 kcal).
- **Ingredientes grasos por otros más ligeros**: tahini → semillas de sésamo, mantequilla → una parte mínima de aceite o yogur, nata → yogur 0 %, queso graso → versión light o menos cantidad. Explica el cambio en una línea cuando afecte al sabor o a la textura.
- **Nunca** añadas azúcar ni otros ingredientes calóricos para compensar.

Si una adaptación estropea el plato de verdad (por ejemplo, un postre que depende de la mantequilla), dilo con honestidad y propón qué conservar o si conviene no incluirla en el repositorio.

## Regionalización de ingredientes

Aparte de las adaptaciones de dieta, cuando la receta viene de fuera de España puede traer ingredientes que aquí no se encuentran igual:

- Si hay un equivalente directo en los supermercados españoles (p. ej. *cornstarch* → maicena, *all-purpose flour* → harina de trigo normal), traduce sin más, no hace falta anotarlo como cambio regional.
- Si no hay equivalente directo o la marca/variedad concreta no se vende aquí (p. ej. *panko* → pan rallado tipo panko si se encuentra, o pan rallado normal; sal *kosher* Diamond Crystal → sal fina, ajustando el peso porque el volumen no equivale; *buttermilk* → leche con unas gotas de limón o yogur líquido; *celery seeds* → apio fresco rallado fino o se omiten), propón el sustituto que conserve mejor el papel del ingrediente (sabor, textura, técnica) y anótalo en el informe.
- No regionalices por regionalizar: si el ingrediente original ya se vende en España con ese mismo nombre o uno muy parecido (ajo, chalota, perejil, caldo de pollo...), déjalo tal cual.

## Reglas del fichero

- `ingredientes` conserva el orden de la receta original, un elemento por ingrediente con su `texto` (cantidad y nombre tal cual se usaría en la cocina) y, cuando exista en el repositorio, el slug en `ingrediente`.
- Si la receta tiene partes claramente distintas (relleno y salsa, puré y salsa...), agrupa los ingredientes con `grupo` e `items` (ver `references/esquema-receta.md`); los `pasos` no se agrupan. En una receta de una sola parte, deja la lista plana.
- `pasos` es una lista con un elemento por paso, en el mismo orden y con las mismas técnicas, tiempos y temperaturas que la receta original, pero **redactados siempre con tus propias palabras**, nunca copiados ni traducidos casi literalmente del texto fuente. Usa un estilo directo y práctico, como en `recetas/borraja-con-almejas.yaml` (receta propia del usuario). Esto aplica también cuando la fuente es un enlace que has leído tú mismo.
- Añade `fuente: <url>` con el enlace original. Si el usuario dicta una receta propia (no viene de internet), pon `fuente: propia` en vez de omitir la clave.
- Añade `imagen: <url>` solo si el usuario da una URL. El campo es opcional: si no hay imagen, omite la clave entera (no escribas "pendiente" ni `null`).
- Si el usuario pide una variante de una receta que ya existe (añadir o quitar un ingrediente, versión más ligera...), crea un fichero nuevo con la receta completa y añade `variante_de: <slug de la principal>` y `variante_resumen` (ver `references/esquema-receta.md`). La principal no puede ser a su vez una variante. Recalcula las cifras de la variante, no las copies de la principal.
- Nombre de fichero: slug en minúsculas, sin acentos ni eñes, con guiones (`coliflor-especiada-con-yogur-y-granada.yaml`).
- Tags en minúsculas, sin acentos, con guiones. Incluye ingrediente principal, tipo de plato, técnica y alguna etiqueta dietética relevante.
- Pon cifras (kcal, proteína, cucharillas) como números sin unidades.
- Las cifras son estimaciones: en el mensaje que acompaña al fichero, di cuáles son las más inciertas (normalmente la proteína del yogur o el peso real de las verduras).
