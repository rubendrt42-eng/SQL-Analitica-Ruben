# Evidencia 1 · Video individual de etapas iniciales

**Rubén David Rodríguez Treviño** (A01198984) · Soporte analítico para la toma de decisiones (TI2006B, Gpo 301)
Socio formador: OT Consulting México · noviembre 2026

Esta carpeta es el punto de partida de mi video. Aquí está la presentación en PDF con lo que hicimos en las primeras cuatro etapas del reto, y abajo dejo dónde está cada cosa en mi repositorio.

## Dónde está cada etapa

- **Etapa 1 · Entendimiento del negocio** (equipo): resumida en la presentación, diapositivas 2 a 5.
- **Etapa 2 · Exploración de los datos** (individual): [Etapa2_OT](../Etapa2_OT)
- **Etapa 3 · Limpieza y preparación** (equipo): [Etapa3_OT](../Etapa3_OT)
- **Etapa 4 · Modelo dimensional** (equipo): [Etapa4_OT](../Etapa4_OT)

## El código que explico en el video

1. **Perfilado de columnas** · [notebook de la Etapa 2](../Etapa2_OT/Etapa2_Exploracion_OT_RubenRodriguez.ipynb), sección 2. La función `perfil()` cuenta en cada columna los nulos, los valores de relleno (PENDIENTE, 1990-01-01), los distintos y los espacios de más. Así vi que PENDIENTE es un nulo disfrazado.
2. **Integridad entre tablas con SQL** · Etapa 2, sección 4. Cargo las tablas a SQLite en memoria y con `LEFT JOIN … WHERE … IS NULL` busco registros que no tienen pareja en la otra tabla.
3. **Reglas de negocio en código** · [notebook de la Etapa 3](../Etapa3_OT/Etapa3_Limpieza_OT_Equipo1.ipynb), secciones 2 y 4. Las reglas de OT son constantes al inicio (176 horas, 20% de carga, margen sobre costo, tarifas de escenario), `anota()` deja cada arreglo en la bitácora y `tipo_colaborador()` decide quién es facturable.
4. **Validación final** · Etapa 3, sección 13. Reviso con SQL que no haya duplicados colaborador-proyecto y saco el costo por estado de banca.
