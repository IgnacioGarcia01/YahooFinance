import calendar as calmod
import datetime as dt
import time

import pandas as pd
import streamlit as st
import yfinance as yf

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
TICKERS = [
    "NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "TSM", "META", "MELI", "CEG",
    "FCX", "NU", "VALE", "B", "VST", "GLOB", "SKHY", "NFLX", "JPM", "IREN",
]

TICKER_NAMES = {
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "GOOGL": "Alphabet",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "TSM": "Taiwan Semiconductor",
    "META": "Meta Platforms",
    "MELI": "MercadoLibre",
    "CEG": "Constellation Energy",
    "FCX": "Freeport-McMoRan",
    "NU": "Nu Holdings",
    "VALE": "Vale",
    "B": "Barrick Mining",
    "VST": "Vistra",
    "GLOB": "Globant",
    "SKHY": "SK Hynix (ADR)",
    "NFLX": "Netflix",
    "JPM": "JPMorgan Chase",
    "IREN": "IREN Limited",
}

TICKER_DOMAINS = {
    "NVDA": "nvidia.com",
    "AAPL": "apple.com",
    "GOOGL": "abc.xyz",
    "MSFT": "microsoft.com",
    "AMZN": "amazon.com",
    "TSM": "tsmc.com",
    "META": "meta.com",
    "MELI": "mercadolibre.com",
    "CEG": "constellationenergy.com",
    "FCX": "fcx.com",
    "NU": "nu.com.br",
    "VALE": "vale.com",
    "B": "barrick.com",
    "VST": "vistracorp.com",
    "GLOB": "globant.com",
    "SKHY": "skhynix.com",
    "NFLX": "netflix.com",
    "JPM": "jpmorganchase.com",
    "IREN": "iren.com",
}

COMMODITIES = [
    ("CL=F", "WTI Crudo"),
    ("BZ=F", "Brent Crudo"),
    ("NG=F", "Gas Natural"),
    ("RB=F", "Gasolina RBOB"),
    ("GC=F", "Oro"),
    ("SI=F", "Plata"),
    ("HG=F", "Cobre"),
    ("ZS=F", "Soja"),
    ("ZC=F", "Maíz"),
    ("ZW=F", "Trigo Chicago"),
    ("KC=F", "Café"),
    ("CC=F", "Cacao"),
    ("LE=F", "Ganado Vivo"),
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
]

TREASURY_10Y = "^TNX"

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

st.set_page_config(
    page_title="Monitor Financiero",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] > .main { background: #f0f2f7; }
[data-testid="block-container"] { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
#MainMenu, header, footer { visibility: hidden; }

.app-header {
    background: linear-gradient(135deg, #0f2d5e 0%, #1a4fa8 100%);
    color: white; padding: 18px 28px; border-radius: 12px; margin-bottom: 16px;
    display: flex; align-items: center; justify-content: space-between;
}
.app-header h1 { font-size: 1.3rem; margin: 0; font-weight: 700; }
.app-header p { font-size: 0.75rem; opacity: 0.7; margin: 3px 0 0; }

.section-title {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; color: #64748b; margin: 18px 0 8px;
}

.pill {
    font-size: 0.66rem; font-weight: 700; padding: 3px 7px; border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
}
.pos { background: #dcfce7; color: #15803d; }
.neg { background: #fee2e2; color: #b91c1c; }
.flat { background: #f1f5f9; color: #64748b; }

/* Tablas (watchlist / commodities) */
.tbl-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 4px; }
.tbl-header {
    display: grid; align-items: center; column-gap: 10px; padding: 10px 16px;
    background: linear-gradient(135deg, #0f2d5e 0%, #1a4fa8 100%); color: white;
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px;
}
.tbl-header-standalone {
    border: 1px solid #0f2d5e; border-bottom: none; border-radius: 14px 14px 0 0;
}
.tbl-row {
    display: grid; align-items: center; column-gap: 10px; padding: 9px 16px;
    border-bottom: 1px solid #f1f5f9; font-size: 0.84rem; color: #1e293b;
}
.tbl-row:last-child { border-bottom: none; }
.tbl-row:hover { background: #f8fbff; }
.tbl-logo {
    width: 22px; height: 22px; border-radius: 5px; object-fit: contain;
    background: white; border: 1px solid #eef2f7; padding: 2px;
    font-size: 0; color: transparent;
}
.tbl-ticker { font-weight: 800; color: #0f2d5e; font-family: 'IBM Plex Mono', monospace; }
.tbl-price { font-family: 'IBM Plex Mono', monospace; font-weight: 600; }
.tbl-pct { font-family: 'IBM Plex Mono', monospace; font-weight: 700; }
.tbl-pct.pos { color: #15803d; }
.tbl-pct.neg { color: #b91c1c; }
.tbl-pct.flat { color: #64748b; }

/* Filas clickeables del watchlist (botón real disfrazado de link) */
.st-key-wl_rows { background: white; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 14px 14px; padding: 4px 6px; }
.st-key-wl_rows [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-wl_rows [data-testid="stHorizontalBlock"] {
    align-items: center; column-gap: 10px; padding: 6px 10px;
    border-bottom: 1px solid #f1f5f9;
}
.st-key-wl_rows [data-testid="stHorizontalBlock"]:last-child { border-bottom: none; }
.st-key-wl_rows [data-testid="stHorizontalBlock"]:hover { background: #f8fbff; border-radius: 8px; }
.st-key-wl_rows [data-testid="stButton"] button {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #0f2d5e !important; font-weight: 800 !important; font-family: 'IBM Plex Mono', monospace !important;
    padding: 2px 0 !important; text-align: left !important; justify-content: flex-start !important;
}
.st-key-wl_rows [data-testid="stButton"] button:hover { color: #1a4fa8 !important; text-decoration: underline; }
.st-key-wl_rows [data-testid="stButton"] button p { font-size: 0.86rem !important; }

/* Botón cerrar detalle (X) */
.st-key-detail_close button {
    background: #f1f5f9 !important; border: none !important; border-radius: 50% !important;
    color: #475569 !important; font-weight: 700 !important; width: 34px !important; height: 34px !important;
    padding: 0 !important;
}
.st-key-detail_close button:hover { background: #e2e8f0 !important; color: #0f2d5e !important; }

/* Detail panel */
.detail-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 22px 24px; margin-bottom: 14px; }
.detail-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.detail-sym { font-size: 1.6rem; font-weight: 800; color: #0f2d5e; font-family: 'IBM Plex Mono', monospace; }
.detail-name { font-size: 0.85rem; color: #475569; margin-bottom: 6px; }
.detail-tags span {
    display: inline-block; background: #eff6ff; color: #1a4fa8; border: 1px solid #bfdbfe;
    font-size: 0.68rem; font-weight: 600; padding: 3px 9px; border-radius: 20px; margin-right: 6px;
}
.detail-price { text-align: right; }
.detail-price .p { font-size: 1.6rem; font-weight: 800; font-family: 'IBM Plex Mono', monospace; color: #1e293b; }
.detail-summary { font-size: 0.82rem; color: #475569; line-height: 1.55; margin-top: 12px; }

.fund-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 8px; }
.fund-item { background: #f8fafc; border: 1px solid #eef2f7; border-radius: 10px; padding: 10px 12px; }
.fund-item .k { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.6px; color: #94a3b8; font-weight: 700; }
.fund-item .v { font-size: 0.95rem; font-weight: 700; color: #0f2d5e; font-family: 'IBM Plex Mono', monospace; margin-top: 2px; }

.earn-box { background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 10px; padding: 12px 14px; margin-top: 6px; }
.earn-box .k { font-size: 0.68rem; color: #4338ca; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; }
.earn-box .v { font-size: 0.95rem; color: #312e81; font-weight: 700; margin-top: 2px; }

/* Tasa 10Y recuadro */
.rate-box {
    background: linear-gradient(135deg, #0f2d5e 0%, #1a4fa8 100%);
    color: white; border-radius: 14px; padding: 16px 20px; max-width: 260px;
    box-shadow: 0 6px 20px rgba(15,45,94,0.25);
}
.rate-box .rl { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.75; font-weight: 700; }
.rate-box .rv { font-size: 1.9rem; font-weight: 800; font-family: 'IBM Plex Mono', monospace; margin-top: 4px; }
.rate-box .rd { font-size: 0.74rem; margin-top: 6px; font-family: 'IBM Plex Mono', monospace; opacity: 0.95; }

/* Calendario mensual */
.cal-months { display: flex; flex-wrap: wrap; gap: 16px; }
.cal-month-card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px 16px; flex: 1 1 320px; min-width: 300px; }
.cal-month-title { font-size: 0.84rem; font-weight: 800; color: #0f2d5e; margin-bottom: 8px; }
.cal-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; margin-bottom: 4px; }
.cal-weekday { font-size: 0.6rem; font-weight: 700; text-align: center; color: #94a3b8; text-transform: uppercase; }
.cal-days { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; }
.cal-day { min-height: 54px; border-radius: 6px; padding: 3px 2px; background: #f8fafc; }
.cal-day-out { opacity: 0.3; }
.cal-day-has { background: #eff6ff; border: 1px solid #bfdbfe; }
.cal-daynum { font-size: 0.64rem; font-weight: 700; color: #475569; text-align: right; padding-right: 2px; }
.cal-events { display: flex; flex-direction: column; gap: 1px; margin-top: 2px; }
.cal-badge {
    font-size: 0.52rem; font-weight: 700; padding: 1px 3px; border-radius: 4px; text-align: center;
    font-family: 'IBM Plex Mono', monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    cursor: default;
}
.cal-badge.earn { background: #dbeafe; color: #1e40af; }
.cal-badge.div { background: #dcfce7; color: #15803d; }
.cal-badge.exdiv { background: #fef3c7; color: #92400e; }
.cal-badge.more { background: #f1f5f9; color: #64748b; }
.cal-legend { display: flex; gap: 14px; margin: 4px 0 14px; font-size: 0.7rem; color: #64748b; }
.cal-legend span { display: inline-flex; align-items: center; gap: 5px; }
.cal-legend i { width: 9px; height: 9px; border-radius: 3px; display: inline-block; }

.stButton>button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA HELPERS
# (sin ttl: los datos solo se refrescan cuando se presiona "Actualizar",
#  que llama a st.cache_data.clear())
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_history(tickers: tuple) -> dict:
    data = yf.download(list(tickers), period="2y", interval="1d",
                        group_by="ticker", auto_adjust=False, progress=False)
    out = {}
    for t in tickers:
        try:
            close = data[t]["Close"].dropna()
        except Exception:
            close = pd.Series(dtype=float)
        out[t] = close
    return out


def _fetch_with_retries(fn, attempts=2):
    """Yahoo's quoteSummary endpoint (used by .get_info()/.calendar) is often
    hard-blocked (not just transient) from shared cloud IPs, so this stays
    cheap: one quick retry, no long backoff — with ~19 tickers a slow retry
    loop would stall the whole page for a minute or more."""
    for i in range(attempts):
        try:
            result = fn()
            if result:
                return result
        except Exception:
            pass
        if i < attempts - 1:
            time.sleep(0.4)
    return {}


@st.cache_data(show_spinner=False)
def load_info(ticker: str) -> dict:
    return _fetch_with_retries(lambda: yf.Ticker(ticker).get_info() or {})


@st.cache_data(show_spinner=False)
def load_calendar(ticker: str) -> dict:
    return _fetch_with_retries(lambda: yf.Ticker(ticker).calendar or {})


def compute_changes(close: pd.Series):
    close = close.dropna()
    if close.empty:
        return None
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) > 1 else last
    daily = (last / prev - 1) * 100 if prev else 0.0

    last_date = close.index[-1]
    month_start = last_date.replace(day=1)
    prior_month = close[close.index < month_start]
    mtd_base = float(prior_month.iloc[-1]) if len(prior_month) else float(close.iloc[0])
    mtd = (last / mtd_base - 1) * 100 if mtd_base else 0.0

    year_start = last_date.replace(month=1, day=1)
    prior_year = close[close.index < year_start]
    ytd_base = float(prior_year.iloc[-1]) if len(prior_year) else float(close.iloc[0])
    ytd = (last / ytd_base - 1) * 100 if ytd_base else 0.0

    return {"last": last, "prev": prev, "daily": daily, "mtd": mtd, "ytd": ytd}


def fmt_pct(v):
    return f"{v:+.2f}%"


def pct_class(v):
    if v > 0.005:
        return "pos"
    if v < -0.005:
        return "neg"
    return "flat"


def fmt_money(v, decimals=2):
    if v is None:
        return "—"
    return f"$ {v:,.{decimals}f}"


def fmt_big(v):
    if v is None:
        return "—"
    v = float(v)
    for unit, div in [("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)]:
        if abs(v) >= div:
            return f"{v/div:,.2f}{unit}"
    return f"{v:,.0f}"


def fmt_date(d):
    if d is None:
        return "—"
    if isinstance(d, (list, tuple)):
        d = d[0] if d else None
    if d is None:
        return "—"
    if isinstance(d, dt.datetime):
        d = d.date()
    if isinstance(d, dt.date):
        return d.strftime("%d %b %Y")
    return str(d)


def pct_html(v):
    if v is None:
        return '<span class="tbl-pct flat">—</span>'
    return f'<span class="tbl-pct {pct_class(v)}">{fmt_pct(v)}</span>'


def logo_html(ticker):
    domain = TICKER_DOMAINS.get(ticker)
    if not domain:
        return ""
    url = f"https://logo.clearbit.com/{domain}?size=64"
    return f'<img class="tbl-logo" src="{url}" onerror="this.style.visibility=\'hidden\'">'


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────────────────────────────────────────
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
head_l, head_r = st.columns([5, 1])
with head_l:
    st.markdown("""
    <div class="app-header">
        <div>
            <h1>📈 Monitor Financiero</h1>
            <p>Datos de mercado vía Yahoo Finance (yfinance) — se actualiza solo al presionar Actualizar</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with head_r:
    st.write("")
    if st.button("🔄 Actualizar", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# WATCHLIST
# ─────────────────────────────────────────────────────────────────────────────
ALL_SYMBOLS = TICKERS + [sym for sym, _ in COMMODITIES] + [TREASURY_10Y]
history = load_history(tuple(ALL_SYMBOLS))
changes_by_ticker = {t: compute_changes(history.get(t, pd.Series(dtype=float))) for t in TICKERS}

WL_COLS = [0.45, 1.3, 2.4, 1.5, 1.15, 1.15]


def render_watchlist():
    cols_css = " ".join(f"{c}fr" for c in WL_COLS)
    st.markdown(
        f'<div class="tbl-header tbl-header-standalone" style="grid-template-columns: {cols_css};">'
        '<div></div><div>Ticker</div><div>Empresa</div><div>Precio</div><div>Día %</div><div>YTD %</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.container(key="wl_rows"):
        for ticker in TICKERS:
            ch = changes_by_ticker.get(ticker)
            logo_c, tick_c, name_c, price_c, day_c, ytd_c = st.columns(WL_COLS)
            with logo_c:
                st.markdown(logo_html(ticker), unsafe_allow_html=True)
            with tick_c:
                if st.button(ticker, key=f"wl_btn_{ticker}"):
                    st.session_state.selected_ticker = ticker
                    st.rerun()
            with name_c:
                st.markdown(TICKER_NAMES.get(ticker, ticker))
            with price_c:
                price_html = fmt_money(ch["last"]) if ch else "—"
                st.markdown(f'<span class="tbl-price">{price_html}</span>', unsafe_allow_html=True)
            with day_c:
                st.markdown(pct_html(ch["daily"] if ch else None), unsafe_allow_html=True)
            with ytd_c:
                st.markdown(pct_html(ch["ytd"] if ch else None), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DETALLE (solo si hay un ticker seleccionado)
# ─────────────────────────────────────────────────────────────────────────────
def render_detail(ticker):
    info = load_info(ticker)
    cal = load_calendar(ticker)
    ch = changes_by_ticker.get(ticker)

    title_col, close_col = st.columns([6, 1])
    with title_col:
        st.markdown('<div class="section-title" style="margin:0 0 8px;">Detalle</div>', unsafe_allow_html=True)
    with close_col:
        with st.container(key="detail_close"):
            if st.button("✕", key="detail_close_btn"):
                st.session_state.selected_ticker = None
                st.rerun()

    if not info:
        st.warning(
            f"No se pudo obtener la información fundamental de {ticker} en este momento. "
            "Yahoo Finance a veces limita temporalmente estas consultas desde servidores "
            "en la nube — probá tocar 🔄 Actualizar en un momento.",
            icon="⚠️",
        )

    name = info.get("longName") or info.get("shortName") or TICKER_NAMES.get(ticker, ticker)
    sector = info.get("sector")
    industry = info.get("industry")
    summary = info.get("longBusinessSummary") or "Sin descripción disponible."
    price = ch["last"] if ch else info.get("currentPrice")
    daily = ch["daily"] if ch else None

    tags = ""
    if sector:
        tags += f"<span>{sector}</span>"
    if industry:
        tags += f"<span>{industry}</span>"

    price_html = fmt_money(price) if price is not None else "—"
    daily_html = (f'<div class="pill {pct_class(daily)}" style="display:inline-block;margin-top:4px;">'
                  f'{fmt_pct(daily)} hoy</div>') if daily is not None else ""

    st.markdown(f"""
    <div class="detail-card">
        <div class="detail-head">
            <div>
                <div class="detail-sym">{ticker}</div>
                <div class="detail-name">{name}</div>
                <div class="detail-tags">{tags}</div>
            </div>
            <div class="detail-price">
                <div class="p">{price_html}</div>
                {daily_html}
            </div>
        </div>
        <div class="detail-summary">{summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # Fundamentals
    fund_items = [
        ("Market Cap", fmt_big(info.get("marketCap"))),
        ("P/E (trailing)", f"{info.get('trailingPE'):.2f}" if info.get("trailingPE") else "—"),
        ("P/E (forward)", f"{info.get('forwardPE'):.2f}" if info.get("forwardPE") else "—"),
        ("EPS (TTM)", fmt_money(info.get("trailingEps")) if info.get("trailingEps") else "—"),
        ("Dividend Yield", f"{info.get('dividendYield'):.2f}%" if info.get("dividendYield") else "—"),
        ("Beta", f"{info.get('beta'):.2f}" if info.get("beta") else "—"),
        ("52w High", fmt_money(info.get("fiftyTwoWeekHigh"))),
        ("52w Low", fmt_money(info.get("fiftyTwoWeekLow"))),
        ("Margen neto", f"{info.get('profitMargins')*100:.1f}%" if info.get("profitMargins") else "—"),
        ("ROE", f"{info.get('returnOnEquity')*100:.1f}%" if info.get("returnOnEquity") else "—"),
        ("Revenue (TTM)", fmt_big(info.get("totalRevenue"))),
        ("Empleados", f"{info.get('fullTimeEmployees'):,}" if info.get("fullTimeEmployees") else "—"),
    ]
    fund_html = "".join(
        f'<div class="fund-item"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in fund_items
    )
    st.markdown(f"""
    <div class="detail-card">
        <div class="section-title" style="margin-top:0;">Fundamentals</div>
        <div class="fund-grid">{fund_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # Earnings / dividendos
    earn_date = fmt_date(cal.get("Earnings Date"))
    div_date = fmt_date(cal.get("Dividend Date"))
    exdiv_date = fmt_date(cal.get("Ex-Dividend Date"))
    eps_est = cal.get("Earnings Average")
    st.markdown(f"""
    <div class="detail-card">
        <div class="section-title" style="margin-top:0;">Próximos eventos</div>
        <div class="earn-box">
            <div class="k">Próximo earnings</div>
            <div class="v">{earn_date}{f' · EPS est. {eps_est:.2f}' if eps_est else ''}</div>
        </div>
        <div style="display:flex; gap:10px; margin-top:10px;">
            <div class="earn-box" style="flex:1;"><div class="k">Dividend Date</div><div class="v">{div_date}</div></div>
            <div class="earn-box" style="flex:1;"><div class="k">Ex-Dividend Date</div><div class="v">{exdiv_date}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if st.session_state.selected_ticker:
    wl_col, detail_col = st.columns([1, 1.3], gap="large")
    with wl_col:
        st.markdown('<div class="section-title">Watchlist</div>', unsafe_allow_html=True)
        render_watchlist()
    with detail_col:
        render_detail(st.session_state.selected_ticker)
else:
    st.markdown('<div class="section-title">Watchlist</div>', unsafe_allow_html=True)
    render_watchlist()

# ─────────────────────────────────────────────────────────────────────────────
# TASA UST 10Y (recuadro chico)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Tasa de referencia</div>', unsafe_allow_html=True)
rate_col, _ = st.columns([1, 3])
with rate_col:
    rate_ch = compute_changes(history.get(TREASURY_10Y, pd.Series(dtype=float)))
    if rate_ch is None:
        st.markdown(
            '<div class="rate-box"><div class="rl">UST 10Y</div>'
            '<div class="rv">—</div><div class="rd">Sin datos</div></div>',
            unsafe_allow_html=True,
        )
    else:
        bps = (rate_ch["last"] - rate_ch["prev"]) * 100
        st.markdown(
            '<div class="rate-box">'
            '<div class="rl">Tasa UST 10Y</div>'
            f'<div class="rv">{rate_ch["last"]:.2f}%</div>'
            f'<div class="rd">{bps:+.0f} pb hoy · YTD {fmt_pct(rate_ch["ytd"])}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# COMMODITIES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Commodities</div>', unsafe_allow_html=True)
COM_COLS_CSS = "2.6fr 1.5fr 1.2fr 1.2fr"
commodity_html = (
    f'<div class="tbl-header" style="grid-template-columns: {COM_COLS_CSS};">'
    '<div>Empresa</div><div>Precio</div><div>Día %</div><div>YTD %</div></div>'
)
for sym, name in COMMODITIES:
    ch = compute_changes(history.get(sym, pd.Series(dtype=float)))
    price_html = fmt_money(ch["last"]) if ch else "—"
    commodity_html += (
        f'<div class="tbl-row" style="grid-template-columns: {COM_COLS_CSS};">'
        f'<div>{name}</div>'
        f'<div class="tbl-price">{price_html}</div>'
        f'<div>{pct_html(ch["daily"] if ch else None)}</div>'
        f'<div>{pct_html(ch["ytd"] if ch else None)}</div>'
        '</div>'
    )
st.markdown(f'<div class="tbl-card">{commodity_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CALENDARIO (formato calendario mensual)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Calendario</div>', unsafe_allow_html=True)

today = dt.date.today()
cal_events = []
for t in TICKERS:
    cal = load_calendar(t)
    if not cal:
        continue
    for label, key in [("Earnings", "Earnings Date"), ("Dividendo", "Dividend Date"),
                        ("Ex-Dividendo", "Ex-Dividend Date")]:
        val = cal.get(key)
        if not val:
            continue
        dates = val if isinstance(val, (list, tuple)) else [val]
        eps_est = cal.get("Earnings Average") if key == "Earnings Date" else None
        for d in dates:
            if d is None:
                continue
            if isinstance(d, dt.datetime):
                d = d.date()
            # Yahoo a veces devuelve la última fecha de dividendo histórica (no
            # la próxima) para papeles sin calendario regular de dividendos —
            # se descartan eventos pasados para que el calendario muestre solo
            # lo que viene.
            if d < today:
                continue
            cal_events.append((d, t, label, eps_est))

if not cal_events:
    st.warning(
        "No se pudieron cargar los eventos del calendario. Yahoo Finance a veces "
        "limita temporalmente estas consultas desde servidores en la nube — probá "
        "tocar 🔄 Actualizar en un momento.",
        icon="⚠️",
    )
else:
    events_by_date = {}
    for d, t, label, eps_est in cal_events:
        events_by_date.setdefault(d, []).append((t, label, eps_est))

    st.markdown(
        '<div class="cal-legend">'
        '<span><i style="background:#1e40af;"></i>Earnings</span>'
        '<span><i style="background:#15803d;"></i>Dividendo</span>'
        '<span><i style="background:#92400e;"></i>Ex-Dividendo</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    months = sorted({(d.year, d.month) for d in events_by_date})
    cal_gen = calmod.Calendar(firstweekday=0)

    month_cards_html = ""
    for year, month in months:
        weeks = cal_gen.monthdatescalendar(year, month)
        weekday_html = "".join(f'<div class="cal-weekday">{w}</div>' for w in DIAS_ES)
        days_html = ""
        for week in weeks:
            for day in week:
                in_month = day.month == month
                day_events = events_by_date.get(day, [])
                badges = ""
                for t, label, eps_est in day_events[:3]:
                    cls = "earn" if label == "Earnings" else ("div" if label == "Dividendo" else "exdiv")
                    tip = f"{t} · {label}"
                    if eps_est is not None:
                        tip += f" · EPS est. {eps_est:.2f}"
                    badges += f'<span class="cal-badge {cls}" title="{tip}">{t}</span>'
                extra = len(day_events) - 3
                if extra > 0:
                    badges += f'<span class="cal-badge more">+{extra}</span>'
                cell_cls = "cal-day"
                if not in_month:
                    cell_cls += " cal-day-out"
                if day_events:
                    cell_cls += " cal-day-has"
                days_html += (
                    f'<div class="{cell_cls}">'
                    f'<div class="cal-daynum">{day.day}</div>'
                    f'<div class="cal-events">{badges}</div>'
                    f'</div>'
                )
        month_cards_html += (
            f'<div class="cal-month-card">'
            f'<div class="cal-month-title">{MESES_ES[month]} {year}</div>'
            f'<div class="cal-weekdays">{weekday_html}</div>'
            f'<div class="cal-days">{days_html}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="cal-months">{month_cards_html}</div>', unsafe_allow_html=True)
