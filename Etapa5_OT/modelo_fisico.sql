-- Modelo dimensional físico · OT Consulting · Equipo 1 (TI2006B Gpo 301)
-- Estrella de la Etapa 4 (fact_asignacion + 6 dimensiones) + puente de habilidades.
-- Escrito en SQL estándar; corre igual en SQLite, PostgreSQL o BigQuery cambiando los tipos.

CREATE TABLE dim_colaborador (
    sk_colaborador          INTEGER PRIMARY KEY,
    id_colaborador          TEXT    NOT NULL UNIQUE,          -- llave natural de la app (OTC###)
    nombre                  TEXT    NOT NULL,
    tipo_colaborador        TEXT    NOT NULL,
    es_facturable           INTEGER NOT NULL CHECK (es_facturable IN (0, 1)),
    puesto                  TEXT    NOT NULL,
    nivel                   TEXT,
    departamento            TEXT,
    depto_origen            TEXT    NOT NULL,
    ciudad                  TEXT,
    nomina                  TEXT,
    antiguedad_anios        REAL,
    baja_programada         INTEGER NOT NULL CHECK (baja_programada IN (0, 1)),
    sueldo_total_integrado  REAL,
    costo_faltante          INTEGER NOT NULL CHECK (costo_faltante IN (0, 1)),
    costo_mensual           REAL,
    costo_hora              REAL,
    tarifa_min_usd_20       REAL,
    tarifa_min_usd_30       REAL,
    n_habilidades           INTEGER NOT NULL,
    n_avanzado_experto      INTEGER NOT NULL,
    tecnologia_principal    TEXT,
    captura_masiva          INTEGER NOT NULL CHECK (captura_masiva IN (0, 1)),
    estado_banca            TEXT    NOT NULL
        CHECK (estado_banca IN ('Asignado', 'En banca', 'Por confirmar', 'No facturable'))
);

CREATE TABLE dim_proyecto (
    sk_proyecto      INTEGER PRIMARY KEY,                     -- 0 = Sin asignación
    codigo_proyecto  TEXT NOT NULL UNIQUE,
    proyecto         TEXT NOT NULL,
    tipo_proyecto    TEXT NOT NULL
);

CREATE TABLE dim_cliente (
    sk_cliente      INTEGER PRIMARY KEY,                      -- 0 = Sin cliente
    codigo_cliente  TEXT NOT NULL UNIQUE,
    cliente         TEXT NOT NULL
);

CREATE TABLE dim_fecha (
    sk_fecha    INTEGER PRIMARY KEY,                          -- AAAAMMDD; -1 = Sin fecha
    fecha       TEXT,
    anio        INTEGER,
    trimestre   INTEGER CHECK (trimestre BETWEEN 1 AND 4),
    mes         INTEGER CHECK (mes BETWEEN 1 AND 12),
    nombre_mes  TEXT NOT NULL,
    dia         INTEGER,
    dia_semana  TEXT NOT NULL
);

CREATE TABLE dim_detalle_asignacion (
    sk_detalle_asignacion  INTEGER PRIMARY KEY,               -- 0 = No aplica
    rol_en_proyecto        TEXT,                              -- vacío = la app no tiene rol ni puesto
    rol_origen             TEXT NOT NULL,
    es_indefinida          INTEGER CHECK (es_indefinida IN (0, 1)),
    asignacion_vigente     INTEGER CHECK (asignacion_vigente IN (0, 1)),
    ventana_liberacion     TEXT NOT NULL,
    fuera_de_periodo       INTEGER CHECK (fuera_de_periodo IN (0, 1))
);

CREATE TABLE dim_calidad (
    sk_calidad          INTEGER PRIMARY KEY,
    semaforo            TEXT NOT NULL CHECK (semaforo IN ('Verde', 'Amarillo', 'Rojo')),
    campos_por_revisar  TEXT
);

CREATE TABLE dim_habilidad (
    sk_habilidad      INTEGER PRIMARY KEY,
    codigo_habilidad  TEXT NOT NULL UNIQUE,
    descripcion       TEXT NOT NULL,
    tecnologia        TEXT NOT NULL,
    tipo              TEXT NOT NULL,
    nombre_completo   TEXT NOT NULL
);

CREATE TABLE fact_asignacion (
    id_hecho               INTEGER PRIMARY KEY,
    sk_colaborador         INTEGER NOT NULL REFERENCES dim_colaborador (sk_colaborador),
    sk_proyecto            INTEGER NOT NULL REFERENCES dim_proyecto (sk_proyecto),
    sk_cliente             INTEGER NOT NULL REFERENCES dim_cliente (sk_cliente),
    sk_fecha_inicio        INTEGER NOT NULL REFERENCES dim_fecha (sk_fecha),
    sk_fecha_fin           INTEGER NOT NULL REFERENCES dim_fecha (sk_fecha),
    sk_fecha_corte         INTEGER NOT NULL REFERENCES dim_fecha (sk_fecha),
    sk_detalle_asignacion  INTEGER NOT NULL REFERENCES dim_detalle_asignacion (sk_detalle_asignacion),
    sk_calidad             INTEGER NOT NULL REFERENCES dim_calidad (sk_calidad),
    dedicacion             REAL,
    horas_mes              REAL,
    costo_asignacion_mes   REAL,
    ingreso_mes_40usd      REAL,
    ingreso_mes_45usd      REAL,
    ingreso_mes_50usd      REAL,
    margen_40usd           REAL,
    margen_45usd           REAL,
    margen_50usd           REAL,
    costo_banca_mes        REAL,
    dias_para_liberarse    INTEGER,
    cuenta_persona         INTEGER NOT NULL CHECK (cuenta_persona IN (0, 1)),
    puntaje_confianza      REAL    NOT NULL CHECK (puntaje_confianza BETWEEN 0 AND 1)
);

-- Puente (bridge) de Kimball: una persona tiene muchas habilidades y una habilidad la tienen muchas personas
CREATE TABLE puente_colaborador_habilidad (
    sk_colaborador  INTEGER NOT NULL REFERENCES dim_colaborador (sk_colaborador),
    sk_habilidad    INTEGER NOT NULL REFERENCES dim_habilidad (sk_habilidad),
    nivel           TEXT    NOT NULL CHECK (nivel IN ('Básico', 'Intermedio', 'Avanzado', 'Experto')),
    nivel_num       INTEGER NOT NULL CHECK (nivel_num BETWEEN 1 AND 4),
    PRIMARY KEY (sk_colaborador, sk_habilidad)
);

-- Índices para los filtros que más usa el tablero
CREATE INDEX ix_fact_colaborador ON fact_asignacion (sk_colaborador);
CREATE INDEX ix_fact_proyecto    ON fact_asignacion (sk_proyecto);
CREATE INDEX ix_fact_cliente     ON fact_asignacion (sk_cliente);
CREATE INDEX ix_fact_corte       ON fact_asignacion (sk_fecha_corte);
CREATE INDEX ix_puente_habilidad ON puente_colaborador_habilidad (sk_habilidad, nivel_num);
