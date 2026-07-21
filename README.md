# Monitor Financiero

Dashboard en Streamlit con datos de mercado vía [yfinance](https://ranaroussi.github.io/yfinance/):

- Watchlist de 5 tickers con variación diaria, MTD e YTD.
- Noticias recientes de los tickers seguidos, en carrusel.
- Panel de detalle por ticker: descripción, sector/industria, fundamentals y próximos earnings/dividendos.
- Calendario combinado de earnings y dividendos.
- Botón de actualización manual (limpia la caché de datos).

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run monitor_financiero.py
```

## Configuración

Editar la lista `TICKERS` al inicio de `monitor_financiero.py` para cambiar los instrumentos seguidos.
