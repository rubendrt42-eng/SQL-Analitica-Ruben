# Evidencia 1: Video individual de etapas iniciales

**Rubén David Rodríguez Treviño** (A01198984), Soporte analítico para la toma de decisiones (TI2006B, Gpo 301)

Socio formador: OT Consulting México, noviembre 2026

Desde esta carpeta arranco mi video. Aquí está la [presentación](Evidencia1_OT_RubenRodriguez.pdf) con lo que hicimos en las primeras cuatro etapas del reto, y abajo dejo dónde está cada cosa en el repositorio.

## Dónde está cada etapa

- Etapa 1, entendimiento del negocio (equipo): viene resumida en la presentación, diapositivas 2 a 5.
- Etapa 2, exploración de los datos (individual): [Etapa2_OT](../Etapa2_OT)
- Etapa 3, limpieza y preparación (equipo): [Etapa3_OT](../Etapa3_OT)
- Etapa 4, modelo dimensional (equipo): [Etapa4_OT](../Etapa4_OT)

## El código que explico en el video

1. Perfil de columnas, en el [notebook de la etapa 2](../Etapa2_OT/Etapa2_Exploracion_OT_RubenRodriguez.ipynb), sección 2. Hice la función `perfil()` para contar en cada columna los nulos, los valores de relleno (PENDIENTE, 1990-01-01), los distintos y los espacios de más. Con eso vi que PENDIENTE en realidad es un dato vacío.
2. Integridad entre tablas con SQL, etapa 2, sección 4. Paso las tablas a SQLite en memoria y con `LEFT JOIN ... WHERE ... IS NULL` busco registros que no tienen pareja en la otra tabla.
3. Reglas de negocio en el código, en el [notebook de la etapa 3](../Etapa3_OT/Etapa3_Limpieza_OT_Equipo1.ipynb), secciones 2 y 4. Las reglas de OT quedaron como constantes al principio (176 horas, 20% de carga, margen sobre costo y tarifas de escenario), `anota()` va guardando cada arreglo en la bitácora y `tipo_colaborador()` decide quién es facturable.
4. Validación final, etapa 3, sección 13. Revisamos con SQL que no hubiera duplicados colaborador-proyecto y sacamos el costo por estado de banca.
