"""Extrae las 9 colecciones de la app de RH de OT (Firestore) y las deja como los 11 CSV del reto.

Uso:
    python extraer_firebase.py --credenciales clave_solo_lectura.json --listar     # solo muestra la estructura
    python extraer_firebase.py --credenciales clave_solo_lectura.json --salida datos_ot

Usa el SDK de administrador de Firebase con una cuenta de servicio que solo tenga el rol
"Cloud Datastore Viewer" (lectura). Nunca escribe en la base de OT.

Las listas que la app guarda dentro de otro documento (los proyectos dentro de cada cliente,
las asignaciones de cada colaborador, la matriz de habilidades y el historial de cada activo)
se aplanan en su propia tabla, con la llave del documento padre.
"""
import argparse, json, os, re
import pandas as pd

# Nombres confirmados en el código de la app (ot-apps-demo.web.app)
COLECCIONES = ['colaboradores', 'usuarios', 'habilidades', 'roles', 'departamentos',
               'matriz_habilidades', 'clientes', 'asignaciones', 'activos']

# Columnas que espera la limpieza de la etapa 3 (son las de los CSV del 16 nov 2026)
ESPERADAS = {
    'colaboradores': ['id', 'uid', 'nombre', 'genero', 'ciudad', 'estatus', 'fechainc', 'fechabaja', 'nomina', 'depto', 'puesto',
                      'sueldo_imss', 'sueldo_asimilados', 'sueldo_complementos', 'sueldo_neto_total', 'comision_nomina',
                      'impuestos_imss', 'sueldo_total_integrado', 'sgmm', 'segvida', 'formato_rh', 'aviso_infonavit',
                      'aviso_manutencion', 'tiene_rfc', 'tiene_curp', 'tiene_nss', 'tiene_email', 'tiene_telefono',
                      'docs_cargados', 'n_anexos'],
    'roles': ['codigo', 'nombre', 'nivel', 'depto', 'estatus', 'desc_igual_nombre', 'uid'],
    'departamentos': ['responsable', 'objetivo', 'estatus', 'nombre', 'codigo', 'centroCostos', 'uid'],
    'habilidades': ['estatus', 'tipo', 'descripcion', 'tecnologia', 'codigo', 'uid'],
    'matriz_habilidades': ['uid_colaborador', 'codigo_habilidad', 'nivel'],
    'clientes': ['pais', 'estado', 'direccion', 'codigo', 'estatus', 'contacto_email', 'contacto_nom', 'ciudad', 'uid', 'telefono',
                 'contacto_tel', 'nombre', 'industria', 'rfc', 'n_proyectos'],
    'proyectos': ['uid_cliente', 'cliente', 'inicio', 'tel_cli', 'resp_cli', 'fin', 'estatus', 'email_cli', 'nombre', 'pm_otc'],
    'asignaciones': ['uid_colaborador', 'rol', 'proyecto_val', 'tipo', 'inicio', 'fin', 'estatus'],
    'activos': ['codigo', 'tipo', 'marca', 'modelo', 'estatus', 'costo', 'esquema', 'uom', 'fcompra', 'fgarantia', 'proveedor',
                'tiene_serie', 'n_asig'],
    'activos_asignaciones': ['codigo_activo', 'uid_colab', 'f_ini', 'f_fin', 'tiene_notas'],
    'usuarios': ['login', 'rol', 'estatus', 'nombre', 'uid'],
}

# Datos personales: se cambian por 1/0 (lleno o vacío) o no se extraen
A_BANDERA = {'rfc': 'tiene_rfc', 'curp': 'tiene_curp', 'nss': 'tiene_nss', 'email': 'tiene_email', 'correo': 'tiene_email',
             'telefono': 'tiene_telefono', 'serie': 'tiene_serie', 'notas': 'tiene_notas'}
NO_EXTRAER = re.compile(r'(password|contrasena|contraseña|pass|token|domicilio|alergia|condicion|beneficiari|parentesco|'
                        r'fechanac|nacimiento)', re.I)


def conectar(credenciales):
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(credenciales))
    return firestore.client()


def limpiar_campos(d, coleccion):
    fila = {}
    for k, v in d.items():
        if NO_EXTRAER.search(k):
            continue
        clave = k.lower()
        if coleccion in ('colaboradores', 'activos', 'activos_asignaciones') and clave in A_BANDERA:
            fila[A_BANDERA[clave]] = int(bool(v))
            continue
        fila[k] = v
    return fila


def aplanar(coleccion, docs):
    """docs: lista de (id, dict). Regresa {nombre_tabla: DataFrame}."""
    principal, hijas = [], {}
    for uid, d in docs:
        fila = {'uid': uid}
        for k, v in d.items():
            if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):      # lista anidada -> tabla hija
                for x in v:
                    hijas.setdefault(k, []).append({'uid_padre': uid, **x})
                fila[f'n_{k}'] = len(v)
            elif isinstance(v, dict) and coleccion == 'matriz_habilidades':           # {codigo: nivel}
                for codigo, nivel in v.items():
                    hijas.setdefault(k, []).append({'uid_colaborador': uid, 'codigo_habilidad': codigo, 'nivel': nivel})
            elif isinstance(v, (dict, list)):
                fila[k] = json.dumps(v, ensure_ascii=False, default=str)
            else:
                fila[k] = v
        principal.append(fila)
    tablas = {coleccion: pd.DataFrame([limpiar_campos(f, coleccion) for f in principal])}
    for k, filas in hijas.items():
        tablas[f'{coleccion}__{k}'] = pd.DataFrame([limpiar_campos(f, coleccion) for f in filas])
    return tablas


def leer(db, coleccion):
    return [(d.id, d.to_dict() or {}) for d in db.collection(coleccion).stream()]


def listar(db):
    for c in COLECCIONES:
        docs = leer(db, c)
        campos = {}
        for _, d in docs:
            for k, v in d.items():
                campos.setdefault(k, set()).add(type(v).__name__)
        print(f'\n{c}: {len(docs)} documentos')
        for k in sorted(campos):
            print(f'   {k}: {", ".join(sorted(campos[k]))}')


def extraer(db, salida):
    os.makedirs(salida, exist_ok=True)
    todas = {}
    for c in COLECCIONES:
        todas.update(aplanar(c, leer(db, c)))
    # nombres de archivo que usa la etapa 3
    destino = {'clientes__proyectos': 'proyectos', 'activos__historial': 'activos_asignaciones'}
    padre = {'proyectos': 'uid_cliente', 'asignaciones': 'uid_colaborador', 'activos_asignaciones': 'codigo_activo'}
    for nombre, t in todas.items():
        base = nombre.split('__')[0]
        archivo = destino.get(nombre, base if base in ('asignaciones', 'matriz_habilidades') and '__' in nombre else nombre)
        if archivo in padre and 'uid_padre' in t.columns:
            t = t.rename(columns={'uid_padre': padre[archivo]})
        t.to_csv(os.path.join(salida, f'{archivo}.csv'), index=False, encoding='utf-8')
    return validar(salida)


def validar(carpeta):
    """Compara los encabezados de los CSV contra lo que espera la limpieza. Regresa los que faltan."""
    faltan = {}
    for archivo, columnas in ESPERADAS.items():
        ruta = os.path.join(carpeta, f'{archivo}.csv')
        if not os.path.exists(ruta):
            faltan[archivo] = ['(no existe el archivo)']
            continue
        hay = set(pd.read_csv(ruta, nrows=0).columns)
        f = [c for c in columnas if c not in hay]
        if f:
            faltan[archivo] = f
    if faltan:
        print('Revisar nombres de campos antes de limpiar:')
        for a, f in faltan.items():
            print(f'   {a}.csv -> faltan {f}')
    else:
        print('Los 11 CSV tienen las columnas que espera la limpieza.')
    return faltan


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--credenciales', help='JSON de la cuenta de servicio (solo lectura)')
    ap.add_argument('--salida', default='datos_ot')
    ap.add_argument('--listar', action='store_true', help='solo muestra colecciones y campos, no guarda nada')
    ap.add_argument('--validar', metavar='CARPETA', help='solo revisa los encabezados de unos CSV ya extraídos')
    a = ap.parse_args()
    if a.validar:
        validar(a.validar)
    else:
        db = conectar(a.credenciales)
        listar(db) if a.listar else extraer(db, a.salida)
