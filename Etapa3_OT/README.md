# Etapa 3 · Limpieza y preparación de los datos de OT Consulting

**Equipo 1** · Soporte analítico para la toma de decisiones (TI2006B, Gpo 301) · Socio formador: OT Consulting México · noviembre 2026

- Rubén David Rodríguez Treviño · A01198984
- Erika Esquivel Correa · A00841206
- Iván Fundora Velasco · A01198822
- Julen Benages Díaz · A01832758

En la etapa 2 encontramos los errores de los datos de la app de OT. En esta etapa los corregimos con Python y SQL y armamos una sola tabla limpia, lista para conectarla al tablero.

**¿Qué hay en esta carpeta?**

- `Etapa3_Limpieza_OT_Equipo1.ipynb`: el notebook con todo el código y el resultado de cada celda.
- `antes_despues.png`: los problemas antes y después de la limpieza.
- `tarifa_minima.png`: la tarifa mínima que necesita cada facturable para dejar 20% sobre su costo.
- `metadata_tabla_acondicionada.csv`: qué es cada columna de la tabla final, de dónde sale y qué tan llena está.
- `bitacora_limpieza.csv`: cada arreglo que hicimos, con cuántos registros tocó.

Los CSV de OT no están aquí porque vienen de su app interna. Para correr el notebook en Colab hay que subir `datos_ot.zip` cuando lo pida.

## ¿Cómo lo trabajamos?

Cada problema terminó en uno de cuatro resultados:

- **Corregido:** el dato estaba mal y lo arreglamos (57 fechas de relleno, 49 textos con espacios de más, país mal escrito, marcas, proyectos sin código).
- **Eliminado:** el registro no tenía sentido (habilidades de personas dadas de baja o que no existen).
- **Estimado:** el dato no existía, pero lo pudimos deducir con una regla de OT (departamento, tipo de proyecto, rol, dedicación).
- **Marcado:** el dato falta y solo OT lo puede capturar (29 activos sin puesto, 5 sin costo, asignaciones sin horas ni tarifa).

La decisión más importante fue quién cuenta como facturable, porque de ahí sale la banca. A los que tienen puesto PENDIENTE pero están en un proyecto los contamos como consultores; los que no tienen ni puesto ni proyecto quedaron como "banca por confirmar".

Como la app no tiene tarifa, horas ni monto vendido, no inventamos el dinero: calculamos tres escenarios (40, 45 y 50 USD/h, que es lo que dijo el director que cobran hoy). También corregimos la fórmula del margen de la etapa 2: OT lo mide **sobre el costo**, no sobre la venta.

## ¿Cómo quedó la tabla final?

`tabla_acondicionada_ot`: 76 renglones × 51 columnas. Cada renglón es un colaborador activo en una asignación; quien no tiene proyecto aparece una vez, para no perder la banca. Cada renglón trae un semáforo de confianza (verde, amarillo o rojo) y dice qué campos le faltan.

## Lo que más nos llamó la atención

Por hora, casi todos los consultores salen rentables: la tarifa mínima mediana para dejar 20% es de 25 USD/h. Lo que se come el dinero es la banca: 22 facturables sin proyecto cuestan $1.36 millones al mes, y cobrando 40 USD/h eso es el 85% de lo que dejan los asignados. Es un escenario con supuestos y datos de prueba, pero apunta a dónde tiene que mirar el tablero.
