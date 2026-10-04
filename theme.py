"""Visual identity for VetAlign-AI.

Design notes
------------
* Light, professional dashboard: white cards on a soft grey canvas.
* The Indian flag is an inline SVG at correct 3:2 proportions with a 24-spoke
  navy Ashoka Chakra. It is shown whole and is never used as a control.
* No State Emblem, service crest or rank insignia is used: those require
  verified permission.
* No stock photographs of real service personnel are bundled, since reusing
  such images without licensing and consent is a legal and ethical risk.
"""

SAFFRON = "#FF9933"
INDIA_GREEN = "#138808"
NAVY = "#0B2447"
CHAKRA = "#000080"
INK = "#12263A"
MUTED = "#5B6B7B"


def flag_svg(width: int = 46) -> str:
    """Return an accurate 3:2 Indian flag as an inline SVG string."""
    height = width * 2 / 3
    band = height / 3
    cx, cy = width / 2, height / 2
    r = band * 0.40
    spokes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - r}" '
        f'stroke="{CHAKRA}" stroke-width="{r * 0.055:.3f}" '
        f'transform="rotate({i * 15} {cx} {cy})" />'
        for i in range(24)
    )
    return f"""<svg width="{width}" height="{height:.1f}" viewBox="0 0 {width} {height:.1f}"
 role="img" aria-label="Flag of India" xmlns="http://www.w3.org/2000/svg">
<rect width="{width}" height="{band:.2f}" y="0" fill="{SAFFRON}"/>
<rect width="{width}" height="{band:.2f}" y="{band:.2f}" fill="#FFFFFF"/>
<rect width="{width}" height="{band:.2f}" y="{band * 2:.2f}" fill="{INDIA_GREEN}"/>
<rect width="{width}" height="{height:.1f}" fill="none" stroke="#D8DEE6" stroke-width="0.6"/>
<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" stroke="{CHAKRA}" stroke-width="{r * 0.09:.3f}"/>
<circle cx="{cx}" cy="{cy}" r="{r * 0.12:.2f}" fill="{CHAKRA}"/>
{spokes}
</svg>"""


def hero_backdrop() -> str:
    """Original abstract 'service to civilian career' motif for the hero band."""
    return """<svg class="va-hero-art" viewBox="0 0 520 190" xmlns="http://www.w3.org/2000/svg"
 aria-hidden="true" focusable="false">
<defs>
  <linearGradient id="vaArc" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0%" stop-color="#FF9933"/><stop offset="100%" stop-color="#138808"/>
  </linearGradient>
</defs>
<path d="M20 165 C140 165 190 120 250 90 C320 55 400 45 500 45"
      fill="none" stroke="url(#vaArc)" stroke-width="6" stroke-linecap="round" opacity="0.7"/>
<g fill="#0B2447" opacity="0.09">
  <rect x="34" y="120" width="26" height="45" rx="4"/>
  <rect x="74" y="104" width="26" height="61" rx="4"/>
  <rect x="114" y="132" width="26" height="33" rx="4"/>
</g>
<g fill="#138808" opacity="0.15">
  <rect x="356" y="96" width="26" height="69" rx="4"/>
  <rect x="396" y="74" width="26" height="91" rx="4"/>
  <rect x="436" y="58" width="26" height="107" rx="4"/>
</g>
<circle cx="250" cy="90" r="13" fill="#FFFFFF" stroke="#FF9933" stroke-width="4"/>
</svg>"""


CSS = f"""
<style>
:root {{
  --va-saffron: {SAFFRON};
  --va-green: {INDIA_GREEN};
  --va-navy: {NAVY};
  --va-ink: {INK};
  --va-muted: {MUTED};
}}
.stApp {{ background: #F4F6F9; }}
.block-container {{ padding: 1.6rem 2.6rem 3rem; max-width: 1240px; }}
h1, h2, h3, h4 {{ color: var(--va-navy); }}

/* ---------------- Sidebar: brand + step rail ---------------- */
section[data-testid="stSidebar"] {{ background:#FFFFFF; border-right:1px solid #E3E8EF; }}
.va-brand {{ display:flex; align-items:center; gap:.55rem; }}
.va-brand-name {{ font-size:1.26rem; font-weight:800; color:var(--va-navy); letter-spacing:-.3px; }}
.va-brand-tag {{ color:var(--va-green); font-size:.82rem; font-weight:600;
  margin:.25rem 0 0; padding-bottom:.85rem; border-bottom:1px solid #E9EDF3; }}
.va-eyebrow {{ font-size:.7rem; font-weight:800; letter-spacing:1.1px;
  color:var(--va-muted); margin:1.1rem 0 .45rem; }}
.va-rail {{ display:flex; align-items:center; gap:.65rem; padding:.6rem .7rem;
  border-radius:9px; margin-bottom:.3rem; font-size:.9rem; color:var(--va-muted); font-weight:600; }}
.va-rail.on {{ background:#FFF6EC; color:var(--va-navy); }}
.va-rail.done {{ color:var(--va-navy); }}
.va-num {{ display:inline-flex; align-items:center; justify-content:center;
  width:24px; height:24px; border-radius:50%; font-size:.78rem; font-weight:800;
  background:#EDF1F6; color:var(--va-muted); flex:0 0 24px; }}
.va-rail.on .va-num {{ background:var(--va-saffron); color:#fff; }}
.va-rail.done .va-num {{ background:var(--va-green); color:#fff; }}
.va-sb-foot {{ color:var(--va-muted); font-size:.72rem; line-height:1.5;
  border-top:1px solid #E9EDF3; margin-top:1.2rem; padding-top:.8rem; }}

/* ---------------- Hero banner ---------------- */
.va-hero {{
  position: relative; overflow: hidden;
  background: linear-gradient(115deg, #FFFFFF 0%, #FFF6EC 48%, #EFF7EF 100%);
  border: 1px solid #E3E8EF; border-left: 6px solid var(--va-saffron);
  border-radius: 14px; padding: 1.35rem 1.6rem 1.4rem;
  box-shadow: 0 1px 3px rgba(16,24,40,.06); margin-bottom: 1.15rem;
}}
.va-hero-art {{ position:absolute; right:0; top:0; height:100%; width:34%;
  min-width:250px; opacity:.5; pointer-events:none; }}
.va-hero-inner {{ position:relative; z-index:2; display:flex; gap:.95rem; align-items:center; }}
.va-h1 {{ font-size:1.72rem; font-weight:800; color:var(--va-navy);
  margin:0; letter-spacing:-.4px; }}
.va-h1-sub {{ color:var(--va-muted); font-size:.94rem; margin:.25rem 0 0; }}
.va-hero-tag {{ color:var(--va-green); font-weight:700; }}
.va-chips {{ position:relative; z-index:2; margin-top:.8rem;
  display:flex; flex-wrap:wrap; gap:.4rem; }}
.va-chip {{ background:#FFFFFF; border:1px solid #DCE3EC; color:var(--va-navy);
  border-radius:999px; padding:.22rem .75rem; font-size:.78rem; font-weight:650; }}
.va-chip.s {{ border-color:#FFD9B0; background:#FFF6EC; }}
.va-chip.g {{ border-color:#BFE3BF; background:#F1F9F1; }}

/* ---------------- Cards ---------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background:#FFFFFF; border-radius:13px; border:1px solid #E3E8EF !important;
  box-shadow:0 1px 3px rgba(16,24,40,.05);
}}
.va-card-title {{ font-size:1.14rem; font-weight:750; color:var(--va-navy); margin:.1rem 0; }}
.va-card-note {{ color:var(--va-muted); font-size:.83rem; margin:.2rem 0 .9rem; }}
.va-req {{ color:#C2410C; font-weight:700; }}

/* ---------------- Metrics ---------------- */
div[data-testid="stMetric"] {{
  background:#FFFFFF; border:1px solid #E3E8EF; border-radius:11px;
  padding:.8rem .95rem .9rem; border-top:3px solid var(--va-saffron);
}}
div[data-testid="stMetricLabel"] p {{ font-size:.72rem !important; color:var(--va-muted) !important;
  font-weight:700 !important; text-transform:uppercase; letter-spacing:.4px; }}
div[data-testid="stMetricValue"] {{ font-size:1.42rem !important; color:var(--va-navy) !important; }}

/* ---------------- Buttons ---------------- */
div.stButton > button {{ border-radius:9px; font-weight:650; }}
div.stButton > button[kind="primary"] {{
  background: var(--va-saffron); border:none; color:#FFFFFF; padding:.6rem 1.1rem;
}}
div.stButton > button[kind="primary"]:hover {{ background:#E8832B; color:#FFFFFF; }}
div.stButton > button[kind="secondary"] {{ border:1px solid #D6DEE8; color:var(--va-navy); background:#fff; }}
div.stButton > button[kind="secondary"]:hover {{ border-color:var(--va-saffron); color:var(--va-navy); }}

/* Branch selector cards */
.va-branch div.stButton > button {{ height:54px; font-size:.95rem; }}
.va-branch div.stButton > button[kind="primary"] {{
  background:#F2FAF2; color:var(--va-navy); border:2px solid var(--va-green);
}}
.va-branch div.stButton > button[kind="primary"]:hover {{ background:#E9F6E9; color:var(--va-navy); }}

/* ---------------- Tabs, evidence, status ---------------- */
.stTabs [data-baseweb="tab-list"] {{ gap:.3rem; border-bottom:1px solid #E3E8EF; }}
.stTabs [data-baseweb="tab"] {{ font-weight:650; color:var(--va-muted); padding:.5rem .9rem; }}
.stTabs [aria-selected="true"] {{ color:var(--va-navy) !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background:var(--va-saffron); height:3px; }}
.va-evidence {{ border-left:3px solid var(--va-green); background:#F7FBF7;
  padding:.5rem .75rem; border-radius:0 8px 8px 0; margin:.35rem 0;
  font-size:.86rem; color:var(--va-ink); }}
.va-gap {{ border-left:3px solid var(--va-saffron); background:#FFF8F0;
  padding:.5rem .75rem; border-radius:0 8px 8px 0; margin:.35rem 0;
  font-size:.86rem; color:var(--va-ink); }}
.va-stale {{ background:#FFF8F0; border:1px solid #FFD9B0; color:#7A4A12;
  border-radius:9px; padding:.55rem .8rem; font-size:.85rem; font-weight:600;
  margin-bottom:.8rem; }}
.va-foot {{ color:var(--va-muted); font-size:.77rem; line-height:1.55;
  border-top:1px solid #E3E8EF; margin-top:1.6rem; padding-top:.85rem; }}
</style>
"""
