# Esquema de las recetas del repositorio

Cada receta es un fichero `.yaml` en `recetas/`. La skill `plan-semanal-comidas` lee estos campos, así que no cambies sus nombres ni sus tipos.

## Campos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `titulo` | texto | sí | Título de la receta |
| `tags` | lista | sí | Etiquetas en minúsculas, sin acentos, con guiones |
| `raciones` | número | sí | Siempre 2 salvo que el usuario diga otra cosa |
| `kcal_racion` | número | sí | kcal por ración (una persona) |
| `proteina_racion_g` | número | sí | Gramos de proteína por ración |
| `aceite_cucharillas` | número | sí | Cucharillas de aceite de la receta completa (admite decimales, 0 si no lleva) |
| `momento` | lista | no | Cualquiera de: `desayuno`, `comida`, `cena`, `guarnicion`, `merienda` |
| `sodio` | texto | no | `bajo`, `medio` o `alto` |
| `ingredientes` | lista | sí | Ver más abajo |
| `pasos` | lista de texto | sí | Un elemento por paso, en orden |
| `fuente` | texto | sí | URL original, o `propia` si es una receta propia del usuario (no viene de internet) |
| `imagen` | texto | no | URL de la imagen, o ruta relativa a un fichero en `imagenes/` (p. ej. `imagenes/<slug>.jpg`). Si no hay, se omite la clave entera (nunca `null` ni "pendiente") |

### `ingredientes`

Lista de ingredientes de la receta completa (para `raciones` personas), en orden. Cada elemento es:

```yaml
- texto: "½ coliflor mediana (unos 500 g)"   # obligatorio: como se lee en la receta
  ingrediente: coliflor                       # opcional: slug en ingredientes/, si existe
```

- `texto` es siempre obligatorio y es lo que se muestra: cantidad y nombre tal cual se usarían en la cocina.
- `ingrediente` es opcional y enlaza con un fichero de `ingredientes/` (ver `esquema-ingrediente.md`) cuando ese ingrediente está en el repositorio. Sirve para poder recalcular o comprobar las kcal más adelante; no es obligatorio tenerlo para todos los ingredientes (especias, sal, agua... normalmente no lo necesitan).

Ejemplo completo:

```yaml
titulo: Coliflor especiada con yogur y granada
tags: [coliflor, verdura, guarnicion, vegetariana, horno]
raciones: 2
kcal_racion: 115
proteina_racion_g: 9
aceite_cucharillas: 0.5
momento: [guarnicion, cena]
sodio: medio
ingredientes:
  - texto: "½ coliflor mediana (unos 500 g)"
  - texto: 1 yogur griego 0 % (alto en proteína)
    ingrediente: yogur-griego-0
  - texto: 1 cucharadita de semillas de sésamo
pasos:
  - Encender el horno a 200°C.
  - Mezclar el aliño y masajear la coliflor.
  - Cocinar 30-40 minutos y servir con la salsa de yogur.
fuente: https://ejemplo.com/receta-original
```

Ver `references/ejemplo-coliflor.yaml` como modelo exacto, con la receta completa.

## Notas

- `kcal_racion` y `proteina_racion_g` son por persona. Si `raciones` es 2, la receta completa es el doble.
- `aceite_cucharillas` es de la receta completa, no por ración. El planificador lo divide entre `raciones` para calcular el aceite que consume cada persona en el día.
- Nombre de fichero: slug en minúsculas, sin acentos ni eñes, con guiones (`coliflor-especiada-con-yogur-y-granada.yaml`).
