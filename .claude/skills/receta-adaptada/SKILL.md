---
name: receta-adaptada
description: Adapta una receta de internet a la dieta hipocalórica de Ricardo (~1800 kcal/día), la escala para 2 personas, estima kcal por ración, valora su encaje y genera el fichero YAML para el repositorio de recetas. Úsala siempre que el usuario pegue una receta (texto o enlace), diga "valora esta receta", "adapta esta receta", "añade esta receta al repo" o pida un fichero de una receta, aunque no mencione la dieta de forma explícita.
---

# Receta adaptada

Convierte una receta cualquiera en una receta del repositorio personal de Ricardo: adaptada a su dieta, escalada a 2 personas, valorada y guardada como YAML con un formato fijo que otra skill (`plan-semanal-comidas`) lee después. Responde siempre en español.

## Flujo

1. **Obtener la receta.** Texto pegado o enlace. Si solo hay un enlace y no se puede abrir, pide que pegue el texto en lugar de inventar los ingredientes.
2. **Buscar los ingredientes en el repositorio.** Para cada ingrediente de la receta, comprueba si existe un fichero en `ingredientes/` (slug en minúsculas con guiones). Si existe, usa esas cifras en vez de un valor de referencia genérico y enlázalo con el campo `ingrediente` (ver `references/esquema-ingrediente.md`). Si no existe, usa tu valor de referencia y dilo como estimado; no crees tú el fichero de `ingredientes/` por tu cuenta.
3. **Adaptar.** Aplica las adaptaciones de abajo sin preguntar, porque son decisiones fijas de Ricardo, no sugerencias. Cambia solo lo necesario y conserva el carácter del plato.
4. **Escalar a 2 personas** (Ricardo y su mujer). Divide las cantidades y redondea a medidas prácticas. Si algo no se puede dividir con sentido (medio huevo, un cuarto de lata), mantén la unidad entera y dilo en una nota. `raciones: 2` en el fichero.
5. **Estimar kcal.** Tabla por ingrediente con rango y "qué puede variar", total de la receta y por ración (una ración = lo que come una persona). Añade proteína por ración y una valoración cualitativa del sodio (bajo/medio/alto), porque es el punto que más se pasa por alto en mezclas de especias, salsas y conservas.
6. **Valorar el encaje** en ~1800 kcal/día: pros, contras (densidad calórica, proteína, sodio), cómo colocarla en el día (guarnición o plato principal, qué complementar) y variantes aún más ligeras con kcal aproximadas. Las adaptaciones fijas ya están aplicadas, así que las variantes deben ir más allá de ellas.
7. **Generar el fichero** `.yaml` según `references/esquema-receta.md` y presentarlo con `present_files`. Ver `references/ejemplo-coliflor.yaml` como modelo exacto.

## Adaptaciones fijas

- **Lácteos al 0 %** manteniendo la proteína alta: yogur griego 0 % (alto en proteína), skyr o queso batido 0 %. La nata o crema se sustituye por yogur o queso batido 0 %; la leche, por la versión 0 % o por bebida de soja sin azúcar, que es la que Ricardo ya toma.
- **Aceite al mínimo.** Ricardo tiene un límite de **4 cucharillas de aceite para todo el día**, así que cada cucharilla cuenta. Reduce el aceite todo lo que la técnica permita (airfryer, horno con bandeja caliente, antiadherente, caldo o agua para sofreír) y elimina los chorritos de remate. Indica en el frontmatter cuántas cucharillas gasta la receta completa en `aceite_cucharillas`. Una cucharilla son unos 4-5 g (~40 kcal).
- **Ingredientes grasos por otros más ligeros**: tahini → semillas de sésamo, mantequilla → una parte mínima de aceite o yogur, nata → yogur 0 %, queso graso → versión light o menos cantidad. Explica el cambio en una línea cuando afecte al sabor o a la textura.
- **Nunca** añadas azúcar ni otros ingredientes calóricos para compensar.

Si una adaptación estropea el plato de verdad (por ejemplo, un postre que depende de la mantequilla), dilo con honestidad y propón qué conservar o si conviene no incluirla en el repositorio.

## Reglas del fichero

- `ingredientes` conserva el orden de la receta original, un elemento por ingrediente con su `texto` (cantidad y nombre tal cual se usaría en la cocina) y, cuando exista en el repositorio, el slug en `ingrediente`.
- `pasos` es una lista con un elemento por paso, en el mismo orden y con las mismas técnicas, tiempos y temperaturas que la receta original, pero **redactados siempre con tus propias palabras**, nunca copiados ni traducidos casi literalmente del texto fuente. Usa un estilo directo y práctico, como en `recetas/borraja-con-almejas.yaml` (receta propia de Ricardo). Esto aplica también cuando la fuente es un enlace que has leído tú mismo.
- Añade `fuente: <url>` con el enlace original. Si Ricardo dicta una receta propia (no viene de internet), pon `fuente: propia` en vez de omitir la clave.
- Añade `imagen: <url>` solo si el usuario da una URL. El campo es opcional: si no hay imagen, omite la clave entera (no escribas "pendiente" ni `null`).
- Nombre de fichero: slug en minúsculas, sin acentos ni eñes, con guiones (`coliflor-especiada-con-yogur-y-granada.yaml`).
- Tags en minúsculas, sin acentos, con guiones. Incluye ingrediente principal, tipo de plato, técnica y alguna etiqueta dietética relevante.
- Pon cifras (kcal, proteína, cucharillas) como números sin unidades.
- Las cifras son estimaciones: en el mensaje que acompaña al fichero, di cuáles son las más inciertas (normalmente la proteína del yogur o el peso real de las verduras).
