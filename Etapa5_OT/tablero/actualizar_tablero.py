"""Actualiza el tablero de Dirección de OT de punta a punta.

    Firebase  ->  11 CSV  ->  limpieza (etapa 3)  ->  estrella en SQL (etapa 5)  ->  public/datos_tablero.json

Uso:
    python actualizar_tablero.py --credenciales clave_solo_lectura.json     # extrae de Firebase y actualiza
    python actualizar_tablero.py --csv datos_ot                             # usa CSV que ya se extrajeron
Después:
    firebase deploy --only hosting:tablero
"""
import argparse, contextlib, datetime, io, json, os, shutil, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = 'https://raw.githubusercontent.com/rubendrt42-eng/SQL-Analitica-Ruben/main'
NB5_LOCAL = os.path.join(AQUI, '..', 'Etapa5_ModeloFisico_OT_Equipo1.ipynb')
NB5_URL = REPO + '/Etapa5_OT/Etapa5_ModeloFisico_OT_Equipo1.ipynb'


def celdas_pipeline():
    if os.path.exists(NB5_LOCAL):
        nb = json.load(open(NB5_LOCAL, encoding='utf-8'))
    else:
        nb = json.loads(urllib.request.urlopen(NB5_URL).read())
    return [''.join(c['source']) for c in nb['cells']
            if c['cell_type'] == 'code' and 'pipeline' in c.get('metadata', {}).get('tags', [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--credenciales', help='JSON de la cuenta de servicio de solo lectura')
    ap.add_argument('--csv', help='carpeta con los 11 CSV (si ya se extrajeron)')
    ap.add_argument('--corte', default=datetime.date.today().isoformat(), help='fecha de corte AAAA-MM-DD (hoy)')
    ap.add_argument('--sin-nombres', action='store_true', help='muestra el ID en lugar del nombre')
    a = ap.parse_args()

    trabajo = os.path.join(AQUI, '_trabajo')
    shutil.rmtree(trabajo, ignore_errors=True)
    os.makedirs(trabajo)
    if a.csv:
        shutil.copytree(a.csv, os.path.join(trabajo, 'datos_ot'))
    elif a.credenciales:
        sys.path.insert(0, AQUI)
        import extraer_firebase
        faltan = extraer_firebase.extraer(extraer_firebase.conectar(a.credenciales), os.path.join(trabajo, 'datos_ot'))
        if faltan:
            sys.exit('Se detuvo: los CSV no tienen las columnas que espera la limpieza (ver arriba).')
    else:
        sys.exit('Usa --credenciales o --csv')

    os.chdir(trabajo)
    import matplotlib
    matplotlib.use('Agg')
    g = {'__name__': 'pipeline', 'CORTE': a.corte, 'display': lambda *x, **k: None}
    for codigo in celdas_pipeline():
        with contextlib.redirect_stdout(io.StringIO()):
            exec(codigo, g)
    datos = g['datos_tablero'](g['con'], g['pro'], mostrar_nombres=not a.sin_nombres)
    destino = os.path.join(AQUI, 'public', 'datos_tablero.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, separators=(',', ':'))
    banca = [p for p in datos['personas'] if p['estado'] == 'En banca']
    print(f"Listo ({datos['corte']}): {len(datos['personas'])} personas, {len(banca)} en banca, "
          f"${sum(p['costo_mes'] or 0 for p in banca):,.0f} al mes. Archivo: {destino}")


if __name__ == '__main__':
    main()
