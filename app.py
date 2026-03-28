"""
BØK 3423 Finans — AI-drevet eksamenstrener
Streamlit-app for Nicholas, BI Handelshøyskolen
"""

import streamlit as st
import anthropic
import math
from datetime import date, datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="BØK 3423 Eksamenstrener", page_icon="🎓", layout="wide")

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Mørkt tema */
    .stApp { background-color: #080e1c; color: #e2eeff; }
    section[data-testid="stSidebar"] { background-color: #0f1826; }

    /* Kort/panel */
    .card {
        background: #0f1826; border: 1px solid #1a2840; border-radius: 12px;
        padding: 1.2rem; margin-bottom: 1rem;
    }
    .card-blue { border-left: 4px solid #1e5a96; }
    .card-green { border-left: 4px solid #4ade80; }
    .card-red { border-left: 4px solid #f87171; }
    .card-yellow { border-left: 4px solid #f5a623; }

    /* Nedtelling */
    .countdown { font-size: 64px; font-weight: bold; color: #1e5a96; line-height: 1; }
    .countdown-sub { color: #5a7a9a; font-size: 16px; }

    /* Formelkort */
    .formula-card {
        background: #0f1826; border: 1px solid #1a2840; border-radius: 8px;
        padding: 0.8rem 1rem; margin-bottom: 0.6rem;
    }
    .formula-name { font-size: 11px; text-transform: uppercase; color: #5a7a9a; letter-spacing: 1px; }
    .formula-expr { font-family: monospace; font-size: 16px; color: #60a5fa; margin: 4px 0; }
    .formula-note { font-size: 12px; color: #5a7a9a; }

    /* Chat-bobler */
    .bubble-ai {
        background: #0f1826; border: 1px solid #1a2840; border-radius: 12px;
        padding: 1rem; margin: 0.5rem 0; max-width: 85%;
    }
    .bubble-user {
        background: #1e5a96; border-radius: 12px; padding: 1rem;
        margin: 0.5rem 0 0.5rem auto; max-width: 85%; text-align: right;
    }

    /* Knapper */
    .stButton > button {
        border: 1px solid #1a2840; background: #0f1826; color: #e2eeff;
        border-radius: 8px; transition: all 0.2s;
    }
    .stButton > button:hover { border-color: #1e5a96; background: #142036; }

    /* Frekvens-stjerner */
    .stars { color: #f5a623; letter-spacing: 2px; }

    /* Resultatboks kalkulator */
    .result-box {
        background: #0a2e1a; border: 2px solid #4ade80; border-radius: 12px;
        padding: 1.5rem; text-align: center; font-size: 28px; font-weight: bold;
        color: #4ade80; margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATA ────────────────────────────────────────────────────────────────────

TOPICS = [
    {"id": "tidsverdi",  "name": "Pengenes tidsverdi",    "freq": 5,
     "subs": ["PV & FV", "NPV-kalkyle", "IRR", "Annuitet & terminbeløp", "Perpetuitet", "EAR / effektiv rente"]},
    {"id": "capm",       "name": "CAPM & SML",             "freq": 5,
     "subs": ["CAPM-formel & krav", "Beta og risiko", "SML: over/under linjen", "Jensens alfa", "Markedspremie"]},
    {"id": "portefolje", "name": "Porteføljeteori",        "freq": 4,
     "subs": ["Forventet avkastning E(r)", "Varians & std.avvik", "Kovarians & korrelasjon", "Sharpe-ratio", "Diversifisering"]},
    {"id": "wacc",       "name": "Kapitalstruktur & WACC", "freq": 4,
     "subs": ["WACC-kalkyle", "EK-kostnad via CAPM", "Skatteskjold", "MM uten skatt", "MM med skatt"]},
    {"id": "oblig",      "name": "Obligasjoner & aksjer",  "freq": 4,
     "subs": ["Obligasjonspris", "YTM (effektiv rente)", "Par/underkurs/overkurs", "Gordon Growth Model", "Dividendevekst"]},
    {"id": "lan",        "name": "Lån",                    "freq": 3,
     "subs": ["Annuitetslån — PMT", "Serielån — terminbeløp", "Restgjeld", "Total rentekostnad", "Månedlig vs. årlig rente"]},
    {"id": "invest",     "name": "Investeringsanalyse",    "freq": 3,
     "subs": ["FCF-beregning", "CAPEX & avskrivning", "Arbeidskapital (NWC)", "Terminalverdi", "DCF & selskapsverdi"]},
]

MODES = [
    {"id": 1, "icon": "🧮", "name": "Beregningsoppgave",
     "instr": "Lag en beregningsoppgave med tabell (tomme celler markert med ?). Still ett spørsmål av gangen. Etter svar: vis INTUISJON, FORMEL, STEG 1/2/3, SVAR og VANLIG FEIL."},
    {"id": 2, "icon": "🔘", "name": "Flervalg",
     "instr": "Lag en flervalgsoppgave: SPØRSMÅL med 4 alternativer (A/B/C/D). Vent på svar. Riktig: forklar. Feil: ett hint, la studenten prøve igjen."},
    {"id": 3, "icon": "🧩", "name": "Feiljakten",
     "instr": "Presenter en komplett løsning med én bevisst feil. Be studenten finne den. Funnet: bekreft. Feil: gi hint om steg."},
    {"id": 4, "icon": "💬", "name": "Forklar tilbake",
     "instr": "Be studenten forklare et konsept på maks 5 setninger som til en venn uten finansbakgrunn. Vurder: 1) Riktig? 2) Tydelig?"},
    {"id": 5, "icon": "⚡", "name": "Lynquiz",
     "instr": "Lag en lynquiz med 5 raske spørsmål. Kun riktig/feil + én linje per svar. Oppsummer svakeste tema til slutt."},
    {"id": 6, "icon": "📋", "name": "Eksamensimulering",
     "instr": "Eksamensimulering: gi oppgave, ingen hint underveis. Full tilbakemelding til slutt: riktig / feil / vil koste poeng."},
]

LEARN_CONTENT = {
    "tidsverdi": {
        "intuition": "En krone i dag er mer verdt enn en krone i fremtiden — fordi du kan investere den. NPV > 0 betyr at prosjektet skaper verdi. IRR er renten der NPV = 0.",
        "formulas": [
            ("FV — Fremtidig verdi", "FV = PV × (1 + r)ⁿ", "Hva pengene vokser til"),
            ("PV — Nåverdi", "PV = FV / (1 + r)ⁿ", "Hva fremtidige penger er verdt i dag"),
            ("NPV — Netto nåverdi", "NPV = Σ CFₜ/(1+r)ᵗ − I₀", "Summen av diskonterte kontantstrømmer minus investering"),
            ("Annuitet (PV)", "PV = PMT × [1−(1+r)⁻ⁿ] / r", "Nåverdi av like betalinger"),
            ("Perpetuitet", "PV = CF / r", "Uendelig rekke av like betalinger"),
            ("EAR", "EAR = (1 + APR/m)ᵐ − 1", "Effektiv årlig rente med m perioder"),
        ],
        "tips": [
            ("t=0 diskonteres aldri — det er i dag", False),
            ("IRR finner du med COMP I/YR på kalkulatoren", False),
            ("PMT er alltid konstant i en annuitet", False),
            ("Eksamen kombinerer ofte NPV og IRR — forstå begge!", True),
        ],
    },
    "capm": {
        "intuition": "CAPM gir avkastningskravet basert på systematisk risiko (beta). Aksjer over SML er underpriset (kjøp!), under SML er overpriset (selg).",
        "formulas": [
            ("CAPM", "E(Ri) = Rf + βᵢ × [E(Rm) − Rf]", "Forventet avkastning basert på beta"),
            ("Beta", "β = Cov(Ri,Rm) / Var(Rm)", "Mål på systematisk risiko"),
            ("Jensens alfa", "α = Ra − [Rf + β(Rm−Rf)]", "Meravkastning utover CAPM"),
        ],
        "tips": [
            ("SML starter alltid i punktet (0, Rf)", False),
            ("Vanligste feil: gange β med Rm i stedet for (Rm − Rf)", True),
            ("β > 1 betyr høyere risiko enn markedet", False),
            ("Alfa > 0 = fondsforvalteren har slått markedet", False),
        ],
    },
    "portefolje": {
        "intuition": "Kombiner aksjer med lav korrelasjon — du kan redusere risiko uten å ofre forventet avkastning. Det er gratis lunsj!",
        "formulas": [
            ("Forventet porteføljeavkastning", "E(rp) = Σ wᵢ × E(rᵢ)", "Vektet snitt av avkastningene"),
            ("Porteføljevarians (2 aktiva)", "σp² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂σ₁₂", "Husk det tredje leddet!"),
            ("Kovarians", "σ₁₂ = ρ₁₂ × σ₁ × σ₂", "Samvariasjon mellom to aksjer"),
            ("Sharpe-ratio", "Sharpe = (E(rp)−Rf) / σp", "Avkastning per enhet risiko"),
        ],
        "tips": [
            ("Kovarians = ρ × σ₁ × σ₂ — enkel omregning", False),
            ("Glem aldri det tredje leddet 2w₁w₂σ₁₂ i variansformelen!", True),
            ("ρ = −1 gir perfekt hedge, ρ = +1 gir ingen diversifisering", False),
            ("Sharpe-ratio brukes til å rangere porteføljer", False),
        ],
    },
    "wacc": {
        "intuition": "WACC er den vektede kapitalkostnaden. Gjeld er billigst fordi renter gir skatteskjold. Mer gjeld → lavere WACC (opp til et punkt).",
        "formulas": [
            ("WACC", "WACC = (E/V)×Re + (D/V)×Rd×(1−T)", "Vektet snitt av EK- og gjeldskostnad"),
            ("EK-kostnad via CAPM", "Re = Rf + β×(Rm−Rf)", "Egenkapitalkravet"),
            ("MM med skatt", "VL = VU + T×D", "Gjeldsfinansiering øker selskapsverdien"),
        ],
        "tips": [
            ("ALLTID gang Rd med (1−T) — skatteskjoldet er nøkkelen", True),
            ("V = E + D — totalverdien er EK pluss gjeld", False),
            ("MM uten skatt: kapitalstruktur er irrelevant", False),
            ("MM med skatt: mer gjeld = høyere verdi (pga. skatteskjold)", False),
        ],
    },
    "oblig": {
        "intuition": "Obligasjonsprisen er nåverdien av alle kontantstrømmer (kuponger + pålydende). Rente opp → pris ned. YTM er internrenten.",
        "formulas": [
            ("Obligasjonspris", "P = Σ C/(1+r)ᵗ + F/(1+r)ⁿ", "PV av kuponger + PV av pålydende"),
            ("Gordon Growth Model", "P₀ = D₁ / (r − g)", "Aksjepris med konstant dividendevekst"),
        ],
        "tips": [
            ("YTM finner du med COMP I/YR: legg inn N, PV, PMT, FV", False),
            ("Glem aldri PV av pålydende — det er en stor kontantstrøm på slutten!", True),
            ("Kupong > YTM → overkurs, Kupong < YTM → underkurs", False),
            ("Gordon forutsetter g < r — ellers gir formelen ikke mening", False),
        ],
    },
    "lan": {
        "intuition": "Annuitetslån: konstant terminbeløp (PMT), synkende rente, økende avdrag. Serielån: konstant avdrag, synkende terminbeløp.",
        "formulas": [
            ("Annuitet PMT", "PMT = PV × r(1+r)ⁿ / [(1+r)ⁿ−1]", "Konstant terminbeløp"),
            ("Serielån avdrag", "Avdrag = Lånebeløp / n", "Like store avdrag hver termin"),
        ],
        "tips": [
            ("HP 10bII+: N, I/YR, PV, FV=0 → COMP PMT", False),
            ("Månedlig rente = årsrente / 12 — ikke glem!", True),
            ("Serielån: renten beregnes på gjenstående gjeld", False),
            ("Total rentekostnad = sum PMT × n − lånebeløp (annuitet)", False),
        ],
    },
    "invest": {
        "intuition": "FCF = faktiske penger selskapet genererer. Start ALLTID fra EBIT, ikke nettoresultat. Terminalverdi utgjør typisk 70-80% av selskapsverdi.",
        "formulas": [
            ("FCF", "FCF = EBIT×(1−T) + Avskr − CAPEX − ΔNWC", "Fri kontantstrøm"),
            ("Terminalverdi", "TV = FCFₙ×(1+g) / (WACC−g)", "Verdi etter prognoseperioden"),
        ],
        "tips": [
            ("Start ALLTID fra EBIT, ikke nettoresultat", False),
            ("Avskrivning legges tilbake (ikke-kontant kostnad)", False),
            ("ΔNWC = endring i arbeidskapital, positiv = kapitalbinding", False),
            ("Terminalverdi er svært sensitiv for WACC og g — vis forsiktighet!", True),
        ],
    },
}

ALL_FORMULAS = [
    {"group": "Pengenes tidsverdi", "color": "#3b82f6", "formulas": [
        ("FV", "FV = PV × (1 + r)ⁿ", "Fremtidig verdi"),
        ("PV", "PV = FV / (1 + r)ⁿ", "Nåverdi"),
        ("NPV", "NPV = Σ CFₜ/(1+r)ᵗ − I₀", "Netto nåverdi"),
        ("Annuitet PV", "PV = PMT × [1−(1+r)⁻ⁿ] / r", "Nåverdi av annuitet"),
        ("Perpetuitet", "PV = CF / r", "Uendelig rekke"),
        ("EAR", "EAR = (1 + APR/m)ᵐ − 1", "Effektiv årlig rente"),
    ]},
    {"group": "CAPM & SML", "color": "#a78bfa", "formulas": [
        ("CAPM", "E(Ri) = Rf + βᵢ × [E(Rm) − Rf]", "Forventet avkastning"),
        ("Beta", "β = Cov(Ri,Rm) / Var(Rm)", "Systematisk risiko"),
        ("Jensens alfa", "α = Ra − [Rf + β(Rm−Rf)]", "Meravkastning"),
    ]},
    {"group": "Porteføljeteori", "color": "#34d399", "formulas": [
        ("E(rp)", "E(rp) = Σ wᵢ × E(rᵢ)", "Forventet porteføljeavkastning"),
        ("Porteføljevarians", "σp² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂σ₁₂", "2 aktiva"),
        ("Kovarians", "σ₁₂ = ρ₁₂ × σ₁ × σ₂", "Samvariasjon"),
        ("Sharpe", "Sharpe = (E(rp)−Rf) / σp", "Risikojustert avkastning"),
    ]},
    {"group": "WACC & Kapitalstruktur", "color": "#f59e0b", "formulas": [
        ("WACC", "WACC = (E/V)×Re + (D/V)×Rd×(1−T)", "Vektet kapitalkostnad"),
        ("EK-kostnad", "Re = Rf + β×(Rm−Rf)", "Via CAPM"),
        ("MM med skatt", "VL = VU + T×D", "Modigliani-Miller"),
    ]},
    {"group": "Obligasjoner & aksjer", "color": "#f87171", "formulas": [
        ("Obligasjonspris", "P = Σ C/(1+r)ᵗ + F/(1+r)ⁿ", "PV av kuponger + pålydende"),
        ("Gordon Growth", "P₀ = D₁ / (r − g)", "Dividendemodell"),
    ]},
    {"group": "Lån", "color": "#60a5fa", "formulas": [
        ("Annuitet PMT", "PMT = PV × r(1+r)ⁿ / [(1+r)ⁿ−1]", "Terminbeløp"),
        ("Serielån avdrag", "Avdrag = Lånebeløp / n", "Konstant avdrag"),
    ]},
    {"group": "Investeringsanalyse", "color": "#fb923c", "formulas": [
        ("FCF", "FCF = EBIT×(1−T) + Avskr − CAPEX − ΔNWC", "Fri kontantstrøm"),
        ("Terminalverdi", "TV = FCFₙ×(1+g) / (WACC−g)", "Gordons vekstmodell"),
    ]},
]

# ─── SESSION STATE ───────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "points": 0,
        "sessions": 0,
        "studied": [],
        "sub_stats": {},
        "study_msgs": [],
        "chat_msgs": [],
        "sel_topic": None,
        "sel_sub": None,
        "sel_mode": 1,
        "api_key": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── AI CLIENT ───────────────────────────────────────────────────────────────

def get_client():
    key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
    if not key:
        key = st.session_state.get("api_key", "")
    if not key:
        return None
    return anthropic.Anthropic(api_key=key)


def call_ai(client, messages: list[dict], system: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system,
        messages=messages,
    )
    return response.content[0].text

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def stars(freq):
    return "★" * freq + "☆" * (5 - freq)


def topic_by_id(tid):
    for t in TOPICS:
        if t["id"] == tid:
            return t
    return None


def spaced_rep_score(topic_id, subtopic):
    key = f"{topic_id}::{subtopic}"
    stat = st.session_state.sub_stats.get(key)
    if not stat:
        return 100
    days_since = (datetime.now() - datetime.fromisoformat(stat["last"])).days
    accuracy = stat["correct"] / max(1, stat["attempts"])
    return (1 - accuracy) * 60 + min(days_since, 10) * 4


def get_recommendations():
    items = []
    for t in TOPICS:
        for s in t["subs"]:
            score = spaced_rep_score(t["id"], s)
            items.append((score, t["id"], t["name"], s))
    items.sort(key=lambda x: -x[0])
    return items[:3]


def record_correct():
    tid = st.session_state.sel_topic
    sub = st.session_state.sel_sub
    if not tid or not sub:
        return
    key = f"{tid}::{sub}"
    old = st.session_state.sub_stats.get(key, {"correct": 0, "attempts": 0, "last": None})
    st.session_state.sub_stats[key] = {
        "correct": old["correct"] + 1,
        "attempts": old["attempts"] + 1,
        "last": datetime.now().isoformat(),
    }


def record_attempt():
    tid = st.session_state.sel_topic
    sub = st.session_state.sel_sub
    if not tid or not sub:
        return
    key = f"{tid}::{sub}"
    old = st.session_state.sub_stats.get(key, {"correct": 0, "attempts": 0, "last": None})
    st.session_state.sub_stats[key] = {
        "correct": old["correct"],
        "attempts": old["attempts"] + 1,
        "last": datetime.now().isoformat(),
    }

# ─── TVM KALKULATOR ─────────────────────────────────────────────────────────

def solve_tvm(n, iyr, pv, pmt, fv):
    unknowns = sum(1 for x in [n, iyr, pv, pmt, fv] if x is None)
    if unknowns != 1:
        return {"error": "Nøyaktig ett felt må være tomt (ukjent)."}

    if iyr is not None:
        r = iyr / 100
    else:
        r = None

    try:
        if fv is None:
            if r == 0:
                return {"var": "FV", "value": -pv - pmt * n}
            return {"var": "FV", "value": -pv * (1 + r) ** n - pmt * (((1 + r) ** n - 1) / r)}

        if pv is None:
            if r == 0:
                return {"var": "PV", "value": -fv - pmt * n}
            return {"var": "PV", "value": (-fv - pmt * (((1 + r) ** n - 1) / r)) / (1 + r) ** n}

        if pmt is None:
            if r == 0:
                return {"var": "PMT", "value": -(fv + pv) / n}
            return {"var": "PMT", "value": -(fv + pv * (1 + r) ** n) * r / ((1 + r) ** n - 1)}

        if n is None:
            if r == 0:
                if pmt == 0:
                    return {"error": "Kan ikke beregne N når r=0 og PMT=0."}
                return {"var": "N", "value": -(fv + pv) / pmt}
            num = (pmt / r - fv)
            den = (pv + pmt / r)
            if num <= 0 or den <= 0 or (num / den) <= 0:
                return {"error": "Ingen gyldig løsning for N med disse verdiene."}
            return {"var": "N", "value": math.log(num / den) / math.log(1 + r)}

        if iyr is None:
            # Newton-Raphson
            r_guess = 0.1
            for _ in range(300):
                if r_guess == 0:
                    r_guess = 0.001
                factor = (1 + r_guess) ** n
                f_val = pv * factor + pmt * (factor - 1) / r_guess + fv
                # Derivative
                dfactor = n * (1 + r_guess) ** (n - 1)
                df_val = pv * dfactor + pmt * (dfactor * r_guess - (factor - 1)) / (r_guess ** 2)
                if abs(df_val) < 1e-20:
                    break
                r_new = r_guess - f_val / df_val
                if abs(r_new - r_guess) < 1e-10:
                    r_guess = r_new
                    break
                r_guess = r_new
            return {"var": "I/YR", "value": r_guess * 100}

    except Exception as e:
        return {"error": f"Beregningsfeil: {e}"}

# ─── TABS ────────────────────────────────────────────────────────────────────

tabs = st.tabs(["🏠 Hjem", "🧮 Øv", "📖 Lær", "📐 Formler", "💬 Chat", "📊 Fremgang", "🔢 Kalkulator"])

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 1 — HJEM
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[0]:
    exam_date = date(2026, 6, 1)
    days_left = (exam_date - date.today()).days

    # Nedtelling
    st.markdown(f'<div class="countdown">{days_left}</div>', unsafe_allow_html=True)
    st.markdown('<div class="countdown-sub">dager til eksamen · 1. juni 2026</div>', unsafe_allow_html=True)
    st.markdown("")

    # Studiemodus
    if days_left > 42:
        mode_label, mode_color = "Bygg forståelse 📖", "#4ade80"
    elif days_left > 21:
        mode_label, mode_color = "Blandet øving 📐", "#facc15"
    elif days_left > 7:
        mode_label, mode_color = "Repetisjon ⏩", "#f97316"
    else:
        mode_label, mode_color = "INTENSIV 🔥", "#f87171"

    st.markdown(f'<span style="background:{mode_color}22; color:{mode_color}; padding:6px 16px; border-radius:20px; font-weight:600;">{mode_label}</span>', unsafe_allow_html=True)
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        studied_count = len(st.session_state.studied)
        st.progress(studied_count / 7, text=f"{studied_count}/7 temaer øvd")
    with col2:
        st.metric("Poeng ⚡", st.session_state.points)

    # Anbefalt i dag
    st.markdown("### Anbefalt i dag")
    recs = get_recommendations()
    colors = ["#f87171", "#f5a623", "#facc15"]
    for i, (score, tid, tname, sub) in enumerate(recs):
        key = f"{tid}::{sub}"
        stat = st.session_state.sub_stats.get(key)
        if stat and stat["attempts"] > 0:
            acc = round(stat["correct"] / stat["attempts"] * 100)
            if acc >= 70:
                acc_color = "#4ade80"
            elif acc >= 40:
                acc_color = "#facc15"
            else:
                acc_color = "#f87171"
            acc_text = f'<span style="color:{acc_color}">{acc}%</span>'
        else:
            acc_text = '<span style="color:#5a7a9a">Ikke øvd</span>'

        st.markdown(f"""<div class="card" style="border-left: 4px solid {colors[i]};">
            <span style="color:{colors[i]}; font-weight:bold;">#{i+1}</span>
            <strong>{sub}</strong> <span style="color:#5a7a9a; font-size:13px;">— {tname}</span>
            <span style="float:right;">{acc_text}</span>
        </div>""", unsafe_allow_html=True)

    # API-nøkkel input
    api_key_from_secrets = ""
    try:
        api_key_from_secrets = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass

    if not api_key_from_secrets:
        with st.expander("🔑 API-nøkkel"):
            key = st.text_input("Anthropic API-nøkkel", type="password")
            if key:
                st.session_state["api_key"] = key
                st.success("API-nøkkel lagret for denne økten!")

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 2 — ØV
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.markdown("### Velg tema")
    cols = st.columns(4)
    for i, t in enumerate(TOPICS):
        with cols[i % 4]:
            selected = st.session_state.sel_topic == t["id"]
            label = f"{'▶ ' if selected else ''}{t['name']}"
            if st.button(label, key=f"topic_{t['id']}", use_container_width=True):
                st.session_state.sel_topic = t["id"]
                st.session_state.sel_sub = None
                st.rerun()

    # Undertema
    if st.session_state.sel_topic:
        topic = topic_by_id(st.session_state.sel_topic)
        st.markdown(f"**{topic['name']}** <span class='stars'>{stars(topic['freq'])}</span>", unsafe_allow_html=True)
        st.markdown("##### Undertema (valgfritt)")
        sub_cols = st.columns(3)
        for j, s in enumerate(topic["subs"]):
            with sub_cols[j % 3]:
                sel = st.session_state.sel_sub == s
                if st.button(f"{'▶ ' if sel else ''}{s}", key=f"sub_{s}", use_container_width=True):
                    st.session_state.sel_sub = s if not sel else None
                    st.rerun()

    # Modus
    st.markdown("### Velg modus")
    mode_cols = st.columns(3)
    for k, m in enumerate(MODES):
        with mode_cols[k % 3]:
            sel = st.session_state.sel_mode == m["id"]
            if st.button(f"{'▶ ' if sel else ''}{m['icon']} {m['name']}", key=f"mode_{m['id']}", use_container_width=True):
                st.session_state.sel_mode = m["id"]
                st.rerun()

    # Start-knapp
    if st.session_state.sel_topic:
        topic = topic_by_id(st.session_state.sel_topic)
        mode = next(m for m in MODES if m["id"] == st.session_state.sel_mode)
        start_label = f"▶ Start {mode['name']} — {topic['name']}"

        if st.button(start_label, type="primary", use_container_width=True):
            client = get_client()
            if not client:
                st.warning("Legg inn API-nøkkel på Hjem-fanen for å bruke AI-funksjoner.")
            else:
                st.session_state.sessions += 1
                st.session_state.points += 10
                if topic["id"] not in st.session_state.studied:
                    st.session_state.studied.append(topic["id"])

                sub_text = f", undertema: {st.session_state.sel_sub}" if st.session_state.sel_sub else ""
                user_msg = (
                    f"Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. "
                    f"{mode['instr']} "
                    f"Tema: {topic['name']}{sub_text}. Start nå."
                )
                st.session_state.study_msgs = [{"role": "user", "content": user_msg}]

                with st.spinner("Henter oppgave..."):
                    try:
                        system = (
                            "Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. "
                            "Gi aldri fasit direkte — la studenten prøve først. "
                            "Avslutt alltid med neste steg eller ett spørsmål til. "
                            "Riktig svar: «Riktig — og dette er akkurat det eksamen tester»."
                        )
                        reply = call_ai(client, st.session_state.study_msgs, system)
                        st.session_state.study_msgs.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"API-feil: {e}")
                st.rerun()

    # Vis meldinger (hopp over første brukermelding)
    if st.session_state.study_msgs:
        for msg in st.session_state.study_msgs[1:]:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)

        # Hurtigknapper
        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1:
            if st.button("✅ Riktig +15", use_container_width=True):
                st.session_state.points += 15
                record_correct()
                st.session_state.study_msgs.append({"role": "user", "content": "Jeg svarte riktig."})
                client = get_client()
                if client:
                    system = "Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. Gi aldri fasit direkte — la studenten prøve først. Avslutt alltid med neste steg eller ett spørsmål til. Riktig svar: «Riktig — og dette er akkurat det eksamen tester»."
                    try:
                        reply = call_ai(client, st.session_state.study_msgs, system)
                        st.session_state.study_msgs.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"API-feil: {e}")
                st.rerun()
        with qc2:
            if st.button("❓ Hint", use_container_width=True):
                st.session_state.study_msgs.append({"role": "user", "content": "Kan du gi meg et hint?"})
                client = get_client()
                if client:
                    system = "Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. Gi aldri fasit direkte — la studenten prøve først. Avslutt alltid med neste steg eller ett spørsmål til."
                    try:
                        reply = call_ai(client, st.session_state.study_msgs, system)
                        st.session_state.study_msgs.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"API-feil: {e}")
                st.rerun()
        with qc3:
            if st.button("⏭ Ny oppgave +5", use_container_width=True):
                st.session_state.points += 5
                record_attempt()
                st.session_state.study_msgs.append({"role": "user", "content": "Gi meg en ny oppgave."})
                client = get_client()
                if client:
                    system = "Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. Gi aldri fasit direkte — la studenten prøve først. Avslutt alltid med neste steg eller ett spørsmål til."
                    try:
                        reply = call_ai(client, st.session_state.study_msgs, system)
                        st.session_state.study_msgs.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"API-feil: {e}")
                st.rerun()
        with qc4:
            if st.button("💡 Forklar", use_container_width=True):
                st.session_state.study_msgs.append({"role": "user", "content": "Kan du forklare løsningen grundig?"})
                client = get_client()
                if client:
                    system = "Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. Gi en grundig forklaring."
                    try:
                        reply = call_ai(client, st.session_state.study_msgs, system)
                        st.session_state.study_msgs.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"API-feil: {e}")
                st.rerun()

        # Fritekst
        user_input = st.chat_input("Skriv svar...")
        if user_input:
            st.session_state.points += 3
            st.session_state.study_msgs.append({"role": "user", "content": user_input})
            client = get_client()
            if client:
                system = "Du er eksamenstutor for BØK 3423 Finans (BI). Svar alltid på norsk. Gi aldri fasit direkte — la studenten prøve først. Avslutt alltid med neste steg eller ett spørsmål til. Riktig svar: «Riktig — og dette er akkurat det eksamen tester»."
                try:
                    reply = call_ai(client, st.session_state.study_msgs, system)
                    st.session_state.study_msgs.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"API-feil: {e}")
            st.rerun()

        # Nullstill
        if st.button("🔄 Nullstill økt"):
            st.session_state.study_msgs = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 3 — LÆR
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[2]:
    st.markdown("### 📖 Pensumoversikt")

    for t in TOPICS:
        content = LEARN_CONTENT.get(t["id"])
        if not content:
            continue
        with st.expander(f"{t['name']}  ({stars(t['freq'])})"):
            st.info(f"💡 **Kjerneintuisjon:** {content['intuition']}")

            st.markdown("**📐 Nøkkelformler:**")
            for fname, fexpr, fnote in content["formulas"]:
                st.markdown(f"""<div class="formula-card">
                    <div class="formula-name">{fname}</div>
                    <div class="formula-expr">{fexpr}</div>
                    <div class="formula-note">{fnote}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("**⭐ Eksamenstips:**")
            for tip_text, is_warning in content["tips"]:
                if is_warning:
                    st.warning(f"⚠️ {tip_text}")
                else:
                    st.success(f"✅ {tip_text}")

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 4 — FORMLER
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[3]:
    st.markdown("### 📐 Formelsamling")
    search = st.text_input("Søk formel...", placeholder="f.eks. NPV, CAPM, annuitet")

    for group in ALL_FORMULAS:
        search_lower = search.lower() if search else ""
        matching = []
        for fname, fexpr, fnote in group["formulas"]:
            if not search or any(
                search_lower in x.lower()
                for x in [fname, fexpr, fnote, group["group"]]
            ):
                matching.append((fname, fexpr, fnote))

        if matching:
            st.markdown(f'<h4 style="color:{group["color"]}; margin-top:1.5rem;">{group["group"]}</h4>', unsafe_allow_html=True)
            for fname, fexpr, fnote in matching:
                st.markdown(f"""<div class="formula-card" style="border-left: 3px solid {group['color']};">
                    <div class="formula-name">{fname}</div>
                    <div class="formula-expr">{fexpr}</div>
                    <div class="formula-note">{fnote}</div>
                </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 5 — CHAT
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[4]:
    st.markdown("### 💬 Fri chat med AI-tutor")

    CHAT_SYSTEM = (
        "Du er finanstutor for BØK 3423 Finans (BI). Svar alltid på norsk, "
        "direkte og komplett. Bruk formler og eksempler der det hjelper."
    )

    # Forslagsknapper hvis tom
    if not st.session_state.chat_msgs:
        suggestions = [
            "Forklar CAPM med eksempel",
            "Hva er forskjellen på IRR og NPV?",
            "Beregn WACC steg for steg",
            "Gordon Growth Model — når brukes den?",
            "Modigliani-Miller med og uten skatt",
            "Sharpe-ratio vs. beta",
        ]
        sg_cols = st.columns(3)
        for idx, sug in enumerate(suggestions):
            with sg_cols[idx % 3]:
                if st.button(sug, key=f"sug_{idx}", use_container_width=True):
                    st.session_state.chat_msgs.append({"role": "user", "content": sug})
                    client = get_client()
                    if client:
                        try:
                            reply = call_ai(client, st.session_state.chat_msgs, CHAT_SYSTEM)
                            st.session_state.chat_msgs.append({"role": "assistant", "content": reply})
                        except Exception as e:
                            st.error(f"API-feil: {e}")
                    else:
                        st.warning("Legg inn API-nøkkel på Hjem-fanen for å bruke AI-funksjoner.")
                    st.rerun()

    # Vis meldinger
    for msg in st.session_state.chat_msgs:
        with st.chat_message("human" if msg["role"] == "user" else "ai"):
            st.markdown(msg["content"])

    # Input
    chat_input = st.chat_input("Spør om hva som helst...")
    if chat_input:
        st.session_state.chat_msgs.append({"role": "user", "content": chat_input})
        client = get_client()
        if client:
            try:
                reply = call_ai(client, st.session_state.chat_msgs, CHAT_SYSTEM)
                st.session_state.chat_msgs.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"API-feil: {e}")
        else:
            st.warning("Legg inn API-nøkkel på Hjem-fanen.")
        st.rerun()

    # Tøm
    if st.session_state.chat_msgs:
        if st.button("🗑 Tøm chat"):
            st.session_state.chat_msgs = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 6 — FREMGANG
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[5]:
    st.markdown("### 📊 Fremgang")

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.metric("Totalpoeng ⚡", st.session_state.points)
    with mc2:
        st.metric("Fullførte økter 📚", st.session_state.sessions)
    with mc3:
        days_left_p = (date(2026, 6, 1) - date.today()).days
        if days_left_p <= 14:
            st.metric("Dager igjen 📅", days_left_p, delta=f"-{days_left_p}", delta_color="inverse")
        else:
            st.metric("Dager igjen 📅", days_left_p)

    st.markdown("---")
    st.markdown("### Pensumoversikt")

    for t in TOPICS:
        subs = t["subs"]
        subs_done = [s for s in subs if f"{t['id']}::{s}" in st.session_state.sub_stats]
        total_corr = sum(st.session_state.sub_stats.get(f"{t['id']}::{s}", {}).get("correct", 0) for s in subs)
        total_att = sum(st.session_state.sub_stats.get(f"{t['id']}::{s}", {}).get("attempts", 0) for s in subs)
        accuracy = round(total_corr / total_att * 100) if total_att > 0 else None
        pct = len(subs_done) / len(subs)

        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.progress(pct, text=f"{t['name']} ({len(subs_done)}/{len(subs)} undertemaer)")
        with col_b:
            if accuracy is not None:
                if accuracy >= 70:
                    st.markdown(f'<span style="color:#4ade80; font-weight:bold;">{accuracy}%</span>', unsafe_allow_html=True)
                elif accuracy >= 40:
                    st.markdown(f'<span style="color:#facc15; font-weight:bold;">{accuracy}%</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span style="color:#f87171; font-weight:bold;">{accuracy}%</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#5a7a9a;">—</span>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FANE 7 — KALKULATOR
# ═══════════════════════════════════════════════════════════════════════════════

with tabs[6]:
    st.markdown("### 🔢 TVM-kalkulator (HP 10bII+)")
    st.caption("La feltet stå tomt for den ukjente variabelen.")

    with st.form("tvm_form"):
        fc1, fc2, fc3, fc4, fc5 = st.columns(5)
        with fc1:
            n_val = st.text_input("N (perioder)", placeholder="tom = ukjent")
        with fc2:
            iyr_val = st.text_input("I/YR (%)", placeholder="tom = ukjent")
        with fc3:
            pv_val = st.text_input("PV", placeholder="tom = ukjent")
        with fc4:
            pmt_val = st.text_input("PMT", placeholder="tom = ukjent")
        with fc5:
            fv_val = st.text_input("FV", placeholder="tom = ukjent")

        submitted = st.form_submit_button("▶ Beregn", use_container_width=True)

    if submitted:
        def parse_val(v):
            v = v.strip().replace(",", ".").replace(" ", "")
            return float(v) if v else None

        try:
            n_p = parse_val(n_val)
            iyr_p = parse_val(iyr_val)
            pv_p = parse_val(pv_val)
            pmt_p = parse_val(pmt_val)
            fv_p = parse_val(fv_val)
        except ValueError:
            st.error("Ugyldig tallverdi. Bruk tall, f.eks. 300000 eller 6.5")
            n_p = iyr_p = pv_p = pmt_p = fv_p = 0  # prevent unbound

        result = solve_tvm(n_p, iyr_p, pv_p, pmt_p, fv_p)
        if "error" in result:
            st.error(result["error"])
        else:
            val = result["value"]
            var = result["var"]
            formatted = f"{val:,.2f}".replace(",", " ").replace(".", ",")
            st.markdown(f'<div class="result-box">{var} = {formatted}</div>', unsafe_allow_html=True)

    # Brukerveiledning
    st.markdown("---")
    st.markdown("#### Eksempler")

    st.markdown("**Annuitetslån:**")
    st.code("N=3, I/YR=6, PV=300000, FV=0 → COMP PMT = -112 297 kr")
    st.markdown("**Obligasjon YTM:**")
    st.code("N=4, PV=-932255, PMT=50000, FV=1000000 → COMP I/YR = YTM")
    st.info("💡 **Fortegn:** Negativ verdi = utbetaling fra deg (låntaker/investor). Positiv = innbetaling til deg.")
