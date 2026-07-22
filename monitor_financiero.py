import datetime as dt
import random
import time

import pandas as pd
import streamlit as st
import yfinance as yf

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

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

CACHE_TTL_PRICES = 300   # 5 min
CACHE_TTL_INFO = 900     # 15 min
CACHE_TTL_NEWS = 300     # 5 min

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

/* News carousel */
.news-scroll {
    display: flex; gap: 12px; overflow-x: auto; padding: 4px 2px 12px;
    scroll-snap-type: x mandatory;
}
.news-scroll::-webkit-scrollbar { height: 6px; }
.news-scroll::-webkit-scrollbar-thumb { background: #bfdbfe; border-radius: 4px; }
.news-card {
    flex: 0 0 260px; scroll-snap-align: start; background: white;
    border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;
    text-decoration: none; color: inherit; display: flex; flex-direction: column;
    transition: box-shadow 0.15s ease;
}
.news-card:hover { box-shadow: 0 4px 16px rgba(15,45,94,0.15); border-color: #93c5fd; }
.news-thumb { width: 100%; height: 110px; object-fit: cover; background: #eef2fb; }
.news-thumb-placeholder {
    width: 100%; height: 110px; background: linear-gradient(135deg, #eff6ff, #dbeafe);
    display: flex; align-items: center; justify-content: center; font-size: 28px;
}
.news-body { padding: 10px 12px 12px; }
.news-title {
    font-size: 0.78rem; font-weight: 600; color: #0f2d5e; line-height: 1.3;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    min-height: 3.1em;
}
.news-meta { font-size: 0.66rem; color: #94a3b8; margin-top: 8px; display: flex; justify-content: space-between; }
.news-meta b { color: #1a4fa8; }

/* Ticker cards */
.ticker-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 14px 16px 10px; margin-bottom: 4px;
}
.ticker-card.active { border: 2px solid #1a4fa8; background: #f8fbff; }
.ticker-sym { font-size: 1.05rem; font-weight: 800; color: #0f2d5e; font-family: 'IBM Plex Mono', monospace; }
.ticker-name { font-size: 0.68rem; color: #94a3b8; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ticker-price { font-size: 1.3rem; font-weight: 700; color: #1e293b; font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.ticker-deltas { display: flex; gap: 6px; flex-wrap: wrap; }
.pill {
    font-size: 0.66rem; font-weight: 700; padding: 3px 7px; border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
}
.pill-lbl { opacity: 0.65; font-weight: 500; margin-right: 3px; }
.pos { background: #dcfce7; color: #15803d; }
.neg { background: #fee2e2; color: #b91c1c; }
.flat { background: #f1f5f9; color: #64748b; }

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

.cal-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-radius: 8px; font-size: 0.78rem; }
.cal-row:nth-child(odd) { background: #f8fafc; }
.cal-tick { font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #0f2d5e; }
.cal-evt { color: #64748b; }
.cal-eps { color: #94a3b8; font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; }
.cal-date { font-weight: 700; color: #1a4fa8; }

/* Commodities grid */
.commodity-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 4px; }
.commodity-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 12px 14px 10px;
}
.commodity-sym { font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; }
.commodity-name { font-size: 0.86rem; font-weight: 700; color: #0f2d5e; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.commodity-price { font-size: 1.05rem; font-weight: 700; color: #1e293b; font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.commodity-deltas { display: flex; gap: 5px; flex-wrap: wrap; }

/* Tasa 10Y recuadro */
.rate-box {
    background: linear-gradient(135deg, #0f2d5e 0%, #1a4fa8 100%);
    color: white; border-radius: 14px; padding: 16px 20px; max-width: 260px;
    box-shadow: 0 6px 20px rgba(15,45,94,0.25);
}
.rate-box .rl { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.75; font-weight: 700; }
.rate-box .rv { font-size: 1.9rem; font-weight: 800; font-family: 'IBM Plex Mono', monospace; margin-top: 4px; }
.rate-box .rd { font-size: 0.74rem; margin-top: 6px; font-family: 'IBM Plex Mono', monospace; opacity: 0.95; }

.stButton>button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=CACHE_TTL_PRICES, show_spinner=False)
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


def _fetch_with_retries(fn, attempts=3):
    """Yahoo's quoteSummary endpoint (used by .get_info()/.calendar) is more
    prone to transient rate-limiting than the chart endpoint, especially from
    shared cloud IPs. Retry a few times with backoff before giving up."""
    for i in range(attempts):
        try:
            result = fn()
            if result:
                return result
        except Exception:
            pass
        if i < attempts - 1:
            time.sleep(1.0 * (i + 1) + random.uniform(0, 0.5))
    return {}


@st.cache_data(ttl=CACHE_TTL_INFO, show_spinner=False)
def load_info(ticker: str) -> dict:
    return _fetch_with_retries(lambda: yf.Ticker(ticker).get_info() or {})


@st.cache_data(ttl=CACHE_TTL_INFO, show_spinner=False)
def load_calendar(ticker: str) -> dict:
    return _fetch_with_retries(lambda: yf.Ticker(ticker).calendar or {})


@st.cache_data(ttl=CACHE_TTL_NEWS, show_spinner=False)
def load_news(tickers: tuple) -> list:
    items = []
    seen_titles = set()
    for t in tickers:
        try:
            raw = yf.Ticker(t).news or []
        except Exception:
            raw = []
        for n in raw:
            c = n.get("content", n)  # newer yfinance nests fields under "content"
            title = c.get("title")
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            link = (c.get("clickThroughUrl") or {}).get("url") \
                or (c.get("canonicalUrl") or {}).get("url") \
                or n.get("link", "")
            publisher = (c.get("provider") or {}).get("displayName") or n.get("publisher", "Yahoo Finance")
            pub_date = c.get("pubDate") or c.get("displayTime")
            thumb = None
            th = c.get("thumbnail")
            if th and th.get("resolutions"):
                thumb = th["resolutions"][-1]["url"]
            items.append({
                "ticker": t, "title": title, "link": link,
                "publisher": publisher, "pub_date": pub_date, "thumb": thumb,
            })
    def sort_key(it):
        return it["pub_date"] or ""
    items.sort(key=sort_key, reverse=True)
    return items[:15]


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


def time_ago(iso_str):
    if not iso_str:
        return ""
    try:
        ts = pd.Timestamp(iso_str)
        if ts.tzinfo is not None:
            ts = ts.tz_convert(None)
        delta = pd.Timestamp.now("UTC").tz_localize(None) - ts
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"hace {int(delta.total_seconds()//60)} min"
        if hours < 24:
            return f"hace {int(hours)} h"
        return f"hace {int(hours//24)} d"
    except Exception:
        return ""


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
            <p>Datos de mercado vía Yahoo Finance (yfinance) — 15-20 min de demora</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with head_r:
    st.write("")
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# NOTICIAS (deslizamiento horizontal)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Noticias</div>', unsafe_allow_html=True)
news_items = load_news(tuple(TICKERS))
if news_items:
    cards_html = ""
    for it in news_items:
        thumb_html = (f'<img class="news-thumb" src="{it["thumb"]}">' if it["thumb"]
                      else '<div class="news-thumb-placeholder">📰</div>')
        cards_html += (
            f'<a class="news-card" href="{it["link"]}" target="_blank" rel="noopener">'
            f'{thumb_html}'
            f'<div class="news-body">'
            f'<div class="news-title">{it["title"]}</div>'
            f'<div class="news-meta"><b>{it["ticker"]}</b><span>{it["publisher"]} · {time_ago(it["pub_date"])}</span></div>'
            f'</div></a>'
        )
    st.markdown(f'<div class="news-scroll">{cards_html}</div>', unsafe_allow_html=True)
else:
    st.caption("No hay noticias disponibles en este momento.")

# ─────────────────────────────────────────────────────────────────────────────
# TICKERS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Watchlist</div>', unsafe_allow_html=True)
ALL_SYMBOLS = TICKERS + [sym for sym, _ in COMMODITIES] + [TREASURY_10Y]
history = load_history(tuple(ALL_SYMBOLS))
changes_by_ticker = {}

cols = st.columns(len(TICKERS))
for col, ticker in zip(cols, TICKERS):
    ch = compute_changes(history.get(ticker, pd.Series(dtype=float)))
    changes_by_ticker[ticker] = ch
    with col:
        is_active = st.session_state.selected_ticker == ticker
        if ch is None:
            st.markdown(f"""
            <div class="ticker-card"><div class="ticker-sym">{ticker}</div>
            <div class="ticker-name">Sin datos</div></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ticker-card {'active' if is_active else ''}">
                <div class="ticker-sym">{ticker}</div>
                <div class="ticker-price">{fmt_money(ch['last'])}</div>
                <div class="ticker-deltas">
                    <span class="pill {pct_class(ch['daily'])}"><span class="pill-lbl">Día</span>{fmt_pct(ch['daily'])}</span>
                    <span class="pill {pct_class(ch['mtd'])}"><span class="pill-lbl">MTD</span>{fmt_pct(ch['mtd'])}</span>
                    <span class="pill {pct_class(ch['ytd'])}"><span class="pill-lbl">YTD</span>{fmt_pct(ch['ytd'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        label = "Ocultar detalle" if is_active else "Ver detalle"
        if st.button(label, key=f"sel_{ticker}", use_container_width=True):
            st.session_state.selected_ticker = None if is_active else ticker
            st.rerun()

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
commodity_cards_html = ""
for sym, name in COMMODITIES:
    ch = compute_changes(history.get(sym, pd.Series(dtype=float)))
    if ch is None:
        commodity_cards_html += (
            '<div class="commodity-card">'
            f'<div class="commodity-sym">{sym}</div>'
            f'<div class="commodity-name">{name}</div>'
            '<div class="commodity-price">—</div>'
            '</div>'
        )
    else:
        commodity_cards_html += (
            '<div class="commodity-card">'
            f'<div class="commodity-sym">{sym}</div>'
            f'<div class="commodity-name">{name}</div>'
            f'<div class="commodity-price">{fmt_money(ch["last"])}</div>'
            '<div class="commodity-deltas">'
            f'<span class="pill {pct_class(ch["daily"])}"><span class="pill-lbl">Día</span>{fmt_pct(ch["daily"])}</span>'
            f'<span class="pill {pct_class(ch["ytd"])}"><span class="pill-lbl">YTD</span>{fmt_pct(ch["ytd"])}</span>'
            '</div></div>'
        )
st.markdown(f'<div class="commodity-grid">{commodity_cards_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CALENDARIO + DETALLE
# ─────────────────────────────────────────────────────────────────────────────
selected = st.session_state.selected_ticker

def render_calendar():
    st.markdown('<div class="section-title">Calendario</div>', unsafe_allow_html=True)
    events = []
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
                events.append((d, t, label, eps_est))
    events.sort(key=lambda e: e[0])
    if not events:
        st.warning(
            "No se pudieron cargar los eventos del calendario. Yahoo Finance a veces "
            "limita temporalmente estas consultas desde servidores en la nube — probá "
            "tocar 🔄 Actualizar en un momento.",
            icon="⚠️",
        )
        return
    rows_html = ""
    for d, t, label, eps_est in events:
        evt_html = label
        if eps_est is not None:
            evt_html += f' <span class="cal-eps">EPS est. {eps_est:.2f}</span>'
        rows_html += (
            f'<div class="cal-row">'
            f'<span class="cal-tick">{t}</span>'
            f'<span class="cal-evt">{evt_html}</span>'
            f'<span class="cal-date">{fmt_date(d)}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="detail-card">{rows_html}</div>', unsafe_allow_html=True)


def render_detail(ticker):
    info = load_info(ticker)
    cal = load_calendar(ticker)
    ch = changes_by_ticker.get(ticker)

    if not info:
        st.warning(
            f"No se pudo obtener la información fundamental de {ticker} en este momento. "
            "Yahoo Finance a veces limita temporalmente estas consultas desde servidores "
            "en la nube — probá tocar 🔄 Actualizar en un momento.",
            icon="⚠️",
        )

    name = info.get("longName") or info.get("shortName") or ticker
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


if selected:
    left, right = st.columns([1, 1.7], gap="medium")
    with left:
        render_calendar()
    with right:
        st.markdown('<div class="section-title">Detalle</div>', unsafe_allow_html=True)
        render_detail(selected)
else:
    render_calendar()
