# Esquema de los ingredientes del repositorio

Cada ingrediente es un fichero `.yaml` en `ingredientes/`. El nombre del fichero (sin extensión) es su slug: minúsculas, sin acentos, con guiones (`yogur-griego-0.yaml`). Las recetas referencian ese slug en su campo `ingrediente` (ver `esquema-receta.md`).

## Campos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `nombre` | texto | sí | Nombre legible del ingrediente |
| `categoria` | texto | no | `lacteos`, `carne`, `pescado`, `huevo`, `legumbre`, `cereal`, `semilla`, `verdura`, `fruta`, `grasa`, `fruto-seco` u `otro` |
| `unidad_ref` | texto | sí | A qué cantidad se refieren las cifras de abajo, p. ej. `100 g`, `100 ml` o `1 unidad (60 g)` |
| `kcal` | número | sí | kcal por `unidad_ref` |
| `proteina_g` | número | sí | Proteína en gramos por `unidad_ref` |
| `grasa_g` | número | sí | Grasa total en gramos por `unidad_ref` |
| `grasa_saturada_g` | número | no | Grasa saturada en gramos por `unidad_ref` |
| `grasa_monoinsaturada_g` | número | no | Grasa monoinsaturada en gramos por `unidad_ref` |
| `grasa_poliinsaturada_g` | número | no | Grasa poliinsaturada en gramos por `unidad_ref` |
| `hidratos_g` | número | sí | Hidratos en gramos por `unidad_ref` |
| `azucares_g` | número | no | Azúcares en gramos por `unidad_ref` (parte de `hidratos_g`) |
| `fibra_g` | número | no | Fibra en gramos por `unidad_ref` |
| `sal_g` | número | no | Sal en gramos por `unidad_ref`, tal cual aparece en la etiqueta española (no confundir con sodio) |
| `omega3_g` | número | no | Omega-3 en gramos por `unidad_ref`, si la etiqueta lo indica |
| `otros` | mapa | no | Vitaminas y minerales que no tienen campo propio, p. ej. `calcio_mg`, `yodo_microgr`, `vitamina_d2_microgr`. La clave incluye la unidad |
| `nota` | texto | no | Aclaración útil, p. ej. la equivalencia en cucharadas (`una cucharada = 15 g`) o el peso de una unidad habitual |
| `fuente` | texto | sí | `etiqueta` (del envase real del usuario), una URL, o `estimado` si es un valor de referencia sin confirmar |

Ejemplo:

```yaml
nombre: Semillas de chía
categoria: semilla
unidad_ref: 100 g
kcal: 427
proteina_g: 21
grasa_g: 31
grasa_saturada_g: 3.1
grasa_monoinsaturada_g: 1.8
grasa_poliinsaturada_g: 24.5
hidratos_g: 0
azucares_g: 0
fibra_g: 32
sal_g: 0
omega3_g: 18.3
nota: una cucharada = 15 g
fuente: etiqueta
```

## Cómo se usa

- `receta-adaptada` busca primero en `ingredientes/` el slug de cada ingrediente de la receta. Si lo encuentra, usa esas cifras para la estimación de kcal/proteína y lo enlaza en el campo `ingrediente` de la receta. Si no existe, usa valores de referencia propios y lo marca como estimado, sin inventar un fichero nuevo en `ingredientes/` por su cuenta.
- El planificador y el cálculo de kcal de una receta solo necesitan `kcal`, `proteina_g`, `grasa_g`, `hidratos_g`, `fibra_g` y `sal_g`. El resto de campos (desglose de grasas, azúcares, omega-3, `otros`) son para consulta y no los usa ningún script.
- Cuando el usuario da el valor real de un ingrediente (de su propia etiqueta), ese valor manda sobre cualquier referencia genérica.
- Las cifras son estimaciones si `fuente: estimado`; con `fuente: etiqueta` se consideran fiables salvo que cambie el producto.
