# ROI de bibliotecas universitarias

Dashboard interactivo (réplica del informe Power BI `27_02_POWER_BI_ROI`) con la paleta institucional de la Universidad de Sevilla.
Dos páginas: **ROI** y **Servicios per cápita**, con filtros por año, biblioteca y servicio.

## Contenido

| Ruta | Descripción |
|---|---|
| `app.py` | Aplicación Streamlit |
| `data/indicadores.csv` | Costes, valor de servicios y ROI por biblioteca y año |
| `data/servicios.csv` | Ahorro por persona usuaria de cada servicio, biblioteca y año |
| `data/servicios_meta.csv` | Justificación, fórmula y valor estimado de cada servicio |
| `.streamlit/config.toml` | Tema de colores |

## Ejecutar en local

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Entrar en <https://share.streamlit.io> con la cuenta de GitHub.
2. **Create app** y elegir este repositorio, la rama `main` y el archivo principal `app.py`.
3. **Deploy**. La dirección pública queda del tipo `https://<nombre>.streamlit.app`.

## Notas sobre los datos

- El modelo original guarda el ROI redondeado a enteros, por lo que el ROI medio sale 2,17 en 2023 y en 2024. Con el
  interruptor **ROI exacto** (valor total ÷ coste total) sale 2,31 y 2,36. El texto introductorio del informe cita 2,31.
- La tabla de servicios original incluía una fila con los títulos de columna cargados como datos. Se ha excluido.
- Las tarjetas «ROI medio» ignoran el filtro de año y «Valor servicios en 2024» no responde al filtro de servicio, como en el informe.
