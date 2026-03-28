"""
BØK 3423 Finans — AI-drevet eksamenstrener
Streamlit-app for Nicholas, BI Handelshøyskolen

Pedagogiske prinsipper:
1. Adaptiv vanskelighetsgrad  2. Interleaving  3. Tvungen gjenhenting
4. Feil = læringsmomenter  5. Eksamensformat  6. Intuisjon før formler
7. Kalkulator-integrert  8. Microlearning  9. Motiverende fremgang
10. Tid-til-eksamen styrer alt
"""

import streamlit as st
import anthropic
import math
import random
import plotly.graph_objects as go
from datetime import date, datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="BØK 3423 Eksamenstrener", page_icon="🎓", layout="wide")

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── BASE: Dark, clean, typographic ── */
    .stApp { background-color: #0b0f19; color: #f0f0f0; }
    section[data-testid="stSidebar"] { background-color: #0f1420; }

    /* Typography hierarchy — size and weight do all the work */
    h1, h2, h3, h4, h5, h6, p, li, span, label, .stMarkdown,
    .stSelectbox label, .stTextInput label, .stNumberInput label,
    .stTextArea label, .stRadio label { color: #f0f0f0 !important; }
    h1 { font-size: 2rem !important; font-weight: 700 !important; letter-spacing: -0.5px; margin-bottom: 1.5rem !important; }
    h2 { font-size: 1.5rem !important; font-weight: 600 !important; margin-top: 2rem !important; margin-bottom: 1rem !important; }
    h3 { font-size: 1.2rem !important; font-weight: 600 !important; margin-top: 1.5rem !important; }
    p, li { font-size: 1rem; line-height: 1.7; color: #d4d4d8 !important; }

    /* Muted secondary text */
    .meta { color: #71717a; font-size: 0.85rem; }

    /* ── COUNTDOWN ── */
    .days-number { font-size: 4.5rem; font-weight: 800; color: #ffffff; line-height: 1; letter-spacing: -2px; }
    .days-label { color: #71717a; font-size: 0.9rem; margin-top: 0.25rem; }
    .phase-tag { display: inline-block; padding: 4px 14px; border-radius: 100px; font-size: 0.8rem; font-weight: 600; margin-top: 0.75rem; }

    /* ── PROGRESS: always visible, thin stripe above tabs ── */
    .top-progress { height: 3px; background: #1e293b; border-radius: 2px; margin-bottom: 0.5rem; overflow: hidden; position: sticky; top: 0; z-index: 1000; }
    .top-progress-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }

    /* ── BUTTONS: consistent, minimal ── */
    .stButton > button {
        background: transparent; border: 1px solid #27272a; color: #f0f0f0;
        border-radius: 8px; padding: 0.6rem 1.2rem; font-size: 0.9rem;
        font-weight: 500; transition: border-color 0.15s, background 0.15s;
    }
    .stButton > button:hover { border-color: #52525b; background: #18181b; }

    /* ── FORMULA: whitespace-driven, no card border ── */
    .formula-block { margin: 1.5rem 0; padding: 1.5rem 0; border-top: 1px solid #1e293b; }
    .formula-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: #71717a; margin-bottom: 0.3rem; }
    .formula-text { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 1.1rem; color: #93c5fd; line-height: 1.8; }
    .formula-note { font-size: 0.85rem; color: #71717a; margin-top: 0.3rem; }

    /* ── FEEDBACK: green=correct, red=wrong, amber=warning. Always. ── */
    .feedback-correct {
        background: #052e1622; border-left: 3px solid #22c55e;
        padding: 1rem 1.25rem; margin: 1rem 0; border-radius: 0 6px 6px 0;
        color: #f0f0f0; line-height: 1.6;
    }
    .feedback-wrong {
        background: #450a0a22; border-left: 3px solid #ef4444;
        padding: 1rem 1.25rem; margin: 1rem 0; border-radius: 0 6px 6px 0;
        color: #f0f0f0; line-height: 1.6;
    }
    .feedback-insight {
        background: #1e1b4b22; border-left: 3px solid #818cf8;
        padding: 1rem 1.25rem; margin: 0.5rem 0; border-radius: 0 6px 6px 0;
        color: #d4d4d8; line-height: 1.6;
    }
    .feedback-warn {
        background: #451a0322; border-left: 3px solid #f59e0b;
        padding: 1rem 1.25rem; margin: 0.5rem 0; border-radius: 0 6px 6px 0;
        color: #d4d4d8; line-height: 1.6;
    }

    /* ── CALC STEPS ── */
    .calc-step {
        font-family: 'SF Mono', monospace; font-size: 0.9rem;
        color: #fbbf24; background: #18181b; padding: 0.6rem 1rem;
        border-radius: 6px; margin: 0.4rem 0; line-height: 1.5;
    }

    /* ── STEP-BY-STEP ── */
    .solve-step {
        padding: 0.8rem 0; border-bottom: 1px solid #1e293b;
        color: #d4d4d8; line-height: 1.6;
    }
    .solve-step:last-child { border-bottom: none; }

    /* ── RESULT ── */
    .result-display {
        font-size: 2rem; font-weight: 700; color: #22c55e;
        text-align: center; padding: 2rem 0; margin: 1rem 0;
        border-top: 1px solid #1e293b; border-bottom: 1px solid #1e293b;
    }

    /* ── CHAT ── */
    .msg-ai { padding: 1rem 0; border-bottom: 1px solid #1e293b; color: #d4d4d8; line-height: 1.7; }
    .msg-user { padding: 1rem 0; border-bottom: 1px solid #1e293b; color: #f0f0f0; text-align: right; line-height: 1.7; }

    /* ── TOPIC SELECTOR ── */
    .topic-item { padding: 0.75rem 0; border-bottom: 1px solid #1e293b; cursor: pointer; }
    .topic-item:hover { background: #18181b; }
    .topic-active { color: #ffffff; font-weight: 600; }
    .topic-inactive { color: #71717a; }

    /* ── TABS: clean, no color except selected ── */
    /* Sticky tab-bar — always accessible */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; border-bottom: 1px solid #1e293b;
        position: sticky; top: 0; z-index: 999;
        background: #0b0f19; padding-top: 0.5rem;
        overflow-x: auto; flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch;
    }
    .stTabs [data-baseweb="tab"] {
        color: #71717a; font-size: 0.85rem; font-weight: 500;
        padding: 0.75rem 1rem; border-bottom: 2px solid transparent;
        white-space: nowrap; flex-shrink: 0;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important; border-bottom: 2px solid #ffffff !important;
    }

    /* ── SPACING: generous whitespace ── */
    .block-container { padding: 2rem 2rem 4rem 2rem !important; max-width: 900px; }
    .stExpander { border: none !important; border-bottom: 1px solid #1e293b !important; }
    .stExpander > details > summary { color: #f0f0f0 !important; font-weight: 500; padding: 0.75rem 0; }

    /* ── PROGRESS BAR override ── */
    .stProgress > div > div { background-color: #1e293b; }
    .stProgress > div > div > div { background-color: #22c55e; }

    /* ── METRICS ── */
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #71717a !important; }

    /* ── SELECTBOX / DROPDOWN: dark theme ── */
    .stSelectbox > div > div { background-color: #111827 !important; color: #ffffff !important; border: 1px solid #27272a !important; border-radius: 8px; }
    .stSelectbox > div > div > div { color: #ffffff !important; }
    .stSelectbox > div > div > div > div { color: #ffffff !important; }
    .stSelectbox svg { fill: #ffffff !important; }
    [data-baseweb="select"] { background-color: #111827 !important; }
    [data-baseweb="select"] * { color: #ffffff !important; }
    [data-baseweb="popover"] { background-color: #0f1520 !important; border: 1px solid #27272a !important; }
    [data-baseweb="popover"] * { color: #ffffff !important; }
    [data-baseweb="menu"] { background-color: #0f1520 !important; }
    [data-baseweb="menu"] * { color: #ffffff !important; }
    [data-baseweb="menu"] li { color: #ffffff !important; background-color: #0f1520 !important; padding: 0.6rem 1rem !important; }
    [data-baseweb="menu"] li:hover { background-color: #1e293b !important; }
    [data-baseweb="menu"] li[aria-selected="true"] { background-color: #1e293b !important; }
    [role="listbox"] { background-color: #0f1520 !important; }
    [role="listbox"] * { color: #ffffff !important; }
    [role="option"] { color: #ffffff !important; background-color: #0f1520 !important; }
    [role="option"]:hover { background-color: #1e293b !important; }

    /* ── TEXT INPUT: dark theme ── */
    .stTextInput > div > div > input { background-color: #111827 !important; color: #f0f0f0 !important; border: 1px solid #27272a !important; }
    .stNumberInput > div > div > input { background-color: #111827 !important; color: #f0f0f0 !important; border: 1px solid #27272a !important; }
    .stTextArea > div > div > textarea { background-color: #111827 !important; color: #f0f0f0 !important; border: 1px solid #27272a !important; }

    /* ── RADIO: dark theme ── */
    .stRadio > div { color: #f0f0f0 !important; }
    .stRadio label span { color: #d4d4d8 !important; }
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
    {"id": 1, "icon": "🧮", "name": "Beregningsoppgave", "time": "8-10 min",
     "instr": "Lag en eksamenslik beregningsoppgave med realistiske tall. Presenter som tabell med tomme celler (?). Still ETT spørsmål. Etter svar: vis 1) INTUISJON (hvorfor dette konseptet finnes), 2) FORMEL, 3) HP 10bII+ tastetrykk steg for steg, 4) SVAR, 5) VANLIG EKSAMENSFEIL og hvorfor studenter gjør den."},
    {"id": 2, "icon": "🔘", "name": "Flervalg", "time": "3-5 min",
     "instr": "Lag en eksamenslik flervalgsoppgave med 4 alternativer (A/B/C/D). Alternativene skal inneholde typiske feilsvar som studenter velger. Vent på svar. Riktig: forklar HVORFOR det er riktig og hva intuisjonen er. Feil: forklar nøyaktig hva studenten misforsto, vis den vanlige tankefellen, gi ett hint, la studenten prøve igjen."},
    {"id": 3, "icon": "🧩", "name": "Feiljakten", "time": "5-7 min",
     "instr": "Presenter en komplett eksamensbesvarelse med én bevisst feil som studenter typisk gjør. Be studenten finne feilen. Funnet: bekreft og forklar hvorfor dette er en vanlig feil. Feil: gi hint om hvilket steg feilen er i."},
    {"id": 4, "icon": "💬", "name": "Forklar tilbake", "time": "3-5 min",
     "instr": "Be studenten forklare et konsept på maks 5 setninger som til en venn uten finansbakgrunn. Vurder: 1) Er intuisjonen riktig? 2) Er det tydelig? 3) Mangler noe viktig? Gi konkret tilbakemelding på hva som var bra og hva som mangler."},
    {"id": 5, "icon": "⚡", "name": "Lynquiz", "time": "3 min",
     "instr": "5 raske spørsmål, bland ulike undertemaer innen temaet. For hvert svar: riktig/feil + én setning med intuisjon. Oppsummer svakeste område til slutt med anbefaling."},
    {"id": 6, "icon": "📋", "name": "Eksamensimulering", "time": "12-15 min",
     "instr": "Gi en realistisk eksamensoppgave med samme format, tallstørrelser og språk som BI bruker. Inkluder tabell hvis relevant. Ingen hint underveis. Etter fullstendig svar: detaljert tilbakemelding — riktig/feil per steg, poengvurdering, typiske feil andre gjør, HP 10bII+ tastetrykk for løsningen."},
]

# ─── QUESTION BANK (med vanskelighetsgrad, kalkulatorsteg, eksamensfokus) ────

QUESTION_BANK = {
    "tidsverdi": {
        "flervalg": [
            {"q": "Du setter inn 10 000 kr til 5 % årlig rente. Hva er verdien etter 3 år?",
             "choices": ["A) 11 500 kr", "B) 11 576 kr", "C) 11 025 kr", "D) 12 500 kr"],
             "answer": 1, "difficulty": 1,
             "explanation": "FV = 10 000 × (1,05)³ = 11 576 kr. A er feil fordi det er enkel rente (3 × 500). Rentes rente gir mer.",
             "misconception": "Vanlig feil: Bruke enkel rente (PV × r × n) i stedet for rentes rente (PV × (1+r)ⁿ).",
             "intuition": "Penger vokser eksponentielt, ikke lineært — du tjener rente på renten.",
             "formula": "FV = PV × (1 + r)ⁿ",
             "calc_steps": "10000 [PV] → 5 [I/YR] → 3 [N] → 0 [PMT] → [COMP] [FV] = −11 576"},
            {"q": "Hva betyr NPV > 0 for et prosjekt?",
             "choices": ["A) Prosjektet taper penger", "B) Prosjektet skaper verdi utover kravet", "C) IRR < kapitalkostnad", "D) Investeringen er risikofri"],
             "answer": 1, "difficulty": 1,
             "explanation": "NPV > 0 betyr at nåverdien overstiger investeringen. Prosjektet gir MER enn avkastningskravet.",
             "misconception": "Noen tror NPV > 0 betyr risikofritt. Det betyr bare at forventet avkastning overstiger kravet.",
             "intuition": "NPV er prosjektets verdi i kroner i dag. Positiv = du blir rikere av å gjøre det.",
             "formula": "NPV = Σ CFₜ/(1+r)ᵗ − I₀", "calc_steps": ""},
            {"q": "Investering: 100 000 kr. CF₁ = 50 000, CF₂ = 70 000. r = 10 %. NPV?",
             "choices": ["A) 20 000 kr", "B) 3 306 kr", "C) −3 306 kr", "D) 10 000 kr"],
             "answer": 1, "difficulty": 2,
             "explanation": "NPV = 50 000/1,10 + 70 000/1,21 − 100 000 = 45 455 + 57 851 − 100 000 = 3 306 kr.",
             "misconception": "Feil A: Glemmer å diskontere (bare summerer CF − I₀). Feil C: Diskonterer med feil eksponent.",
             "intuition": "Du spør: Er 50k om 1 år + 70k om 2 år verdt mer enn 100k i dag? Ja, men bare 3 306 kr mer.",
             "formula": "NPV = Σ CFₜ/(1+r)ᵗ − I₀",
             "calc_steps": "50000 ÷ 1.10 = 45 455 → 70000 ÷ 1.21 = 57 851 → 45 455 + 57 851 − 100 000 = 3 306"},
            {"q": "Hva er IRR?",
             "choices": ["A) Renten der NPV = 1", "B) Renten der NPV = 0", "C) Alltid > WACC", "D) Risikofri rente + premie"],
             "answer": 1, "difficulty": 1,
             "explanation": "IRR er diskonteringsrenten som gjør NPV = 0. Det er prosjektets innebygde avkastning.",
             "misconception": "IRR er IKKE alltid > WACC — det gjelder bare for lønnsomme prosjekter.",
             "intuition": "IRR svarer: Hvilken rente gir dette prosjektet deg? Er den høyere enn kravet ditt?",
             "formula": "NPV = 0 → finn r = IRR", "calc_steps": "Legg inn CF₀, CF₁...CFₙ → [COMP] [I/YR]"},
            {"q": "PV av 500 000 kr om 10 år, r = 4 %?",
             "choices": ["A) 337 834 kr", "B) 350 000 kr", "C) 410 000 kr", "D) 300 000 kr"],
             "answer": 0, "difficulty": 2,
             "explanation": "PV = 500 000 / (1,04)¹⁰ = 500 000 / 1,4802 = 337 834 kr.",
             "misconception": "Feil B: Bruker enkel diskontering (500k − 10×4%×500k). Feil D: Avrunder for mye.",
             "intuition": "337 834 kr i dag vokser til nøyaktig 500 000 kr om 10 år med 4 % rente.",
             "formula": "PV = FV / (1 + r)ⁿ",
             "calc_steps": "500000 [FV] → 4 [I/YR] → 10 [N] → 0 [PMT] → [COMP] [PV] = −337 834"},
            {"q": "Perpetuitet: 20 000 kr/år, r = 8 %. Nåverdi?",
             "choices": ["A) 160 000 kr", "B) 200 000 kr", "C) 250 000 kr", "D) 180 000 kr"],
             "answer": 2, "difficulty": 1,
             "explanation": "PV = 20 000 / 0,08 = 250 000 kr. Så enkelt er det.",
             "misconception": "Feil A/B: Multipliserer feil, eller blander med annuitet.",
             "intuition": "Hvis du setter 250 000 i banken til 8 %, får du 20 000 hvert år — for alltid.",
             "formula": "PV = CF / r", "calc_steps": "20000 ÷ 0.08 = 250 000"},
        ],
        "beregning": [
            {"q": "Et prosjekt koster 200 000 kr og gir 80 000 kr/år i 4 år. Avkastningskrav: 12 %. Beregn NPV. Bør prosjektet gjennomføres?",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: Er fire betalinger à 80 000 kr verdt mer enn 200 000 kr i dag?",
                 "Formel: NPV = PV(annuitet) − I₀ = PMT × [1−(1+r)⁻ⁿ]/r − I₀",
                 "Steg 1: PV-faktor = [1−(1,12)⁻⁴]/0,12 = [1−0,6355]/0,12 = 3,0373",
                 "Steg 2: PV = 80 000 × 3,0373 = 242 986 kr",
                 "Steg 3: NPV = 242 986 − 200 000 = 42 986 kr",
                 "Konklusjon: NPV > 0 → JA, gjennomfør prosjektet.",
             ],
             "calc_steps": [
                 "80000 [PMT] → 12 [I/YR] → 4 [N] → 0 [FV] → [COMP] [PV] = −242 986",
                 "242 986 − 200 000 = 42 986 kr",
             ],
             "answer": 42986, "tolerance": 500,
             "formula": "NPV = PV(annuitet) − I₀",
             "common_mistake": "Vanlig feil: Glemmer å diskontere — summerer bare 4×80 000 = 320 000 og trekker fra 200 000. Det gir 120 000 (alt for høyt)."},
            {"q": "Annuitetslån: 1 000 000 kr, 6 % rente, 20 år. Beregn årlig terminbeløp.",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: Hva er det faste beløpet som betaler ned både rente og avdrag over 20 år?",
                 "Formel: PMT = PV × r(1+r)ⁿ / [(1+r)ⁿ−1]",
                 "Steg 1: (1,06)²⁰ = 3,2071",
                 "Steg 2: Teller = 0,06 × 3,2071 = 0,19243",
                 "Steg 3: Nevner = 3,2071 − 1 = 2,2071",
                 "Steg 4: PMT = 1 000 000 × 0,19243 / 2,2071 = 87 185 kr",
             ],
             "calc_steps": [
                 "1000000 [PV] → 6 [I/YR] → 20 [N] → 0 [FV] → [COMP] [PMT] = −87 185",
             ],
             "answer": 87185, "tolerance": 500,
             "formula": "PMT = PV × r(1+r)ⁿ / [(1+r)ⁿ−1]",
             "common_mistake": "Vanlig feil: Deler bare lånet på 20 (= 50 000). Det er serielån-avdraget, ikke annuitetens PMT."},
        ],
        "case": [
            {"scenario": "**Eksamen BØK 3423 — Oppgave 2 (25 poeng)**\n\nSolvik Energi AS vurderer å investere i et solcelleanlegg. Investeringskostnaden er 500 000 kr. Forventede kontantstrømmer:\n\n| År | CF (kr) |\n|---|---|\n| 1 | 120 000 |\n| 2 | 150 000 |\n| 3 | 180 000 |\n| 4 | 200 000 |\n\nAvkastningskravet er 10 %.",
             "questions": [
                 {"q": "a) Beregn NPV (10 p)", "answer": "NPV = 120k/1,10 + 150k/1,21 + 180k/1,331 + 200k/1,4641 − 500k = 109 091 + 123 967 + 135 237 + 136 602 − 500 000 = **4 897 kr**\n\nHP 10bII+: Diskontér hver CF individuelt og summer."},
                 {"q": "b) Bør Solvik investere? Begrunn (5 p)", "answer": "Ja — NPV > 0 (4 897 kr). Prosjektet skaper verdi utover 10 % avkastningskrav. Merk: NPV er lav, så prosjektet er marginalt. Sensitiv for endringer i CF eller rente."},
                 {"q": "c) Hva skjer med NPV hvis kravet øker til 12 %? Forklar intuisjonen (10 p)", "answer": "NPV blir negativ (ca. −18 000 kr). Intuisjon: Høyere krav = fremtidige CF er «verdt mindre» i dag. De siste årenes CF rammes hardest fordi de diskonteres mest. Prosjektet er ikke robust nok til å tåle økt krav."},
             ]},
        ],
    },
    "capm": {
        "flervalg": [
            {"q": "Rf = 3 %, E(Rm) = 10 %, β = 1,5. Avkastningskrav?",
             "choices": ["A) 13,5 %", "B) 15,0 %", "C) 18,0 %", "D) 10,5 %"],
             "answer": 0, "difficulty": 1,
             "explanation": "E(Ri) = 3 + 1,5 × (10−3) = 3 + 10,5 = 13,5 %",
             "misconception": "Feil B: Ganger β med Rm (1,5×10=15). DU MÅ gange med PREMIEN (Rm−Rf)!",
             "intuition": "Du starter med risikofri rente og legger til kompensasjon for risiko — jo høyere beta, jo mer.",
             "formula": "E(Ri) = Rf + β × [E(Rm) − Rf]", "calc_steps": "10 − 3 = 7 → 1.5 × 7 = 10.5 → 3 + 10.5 = 13.5"},
            {"q": "Aksje over SML — hva gjør du?",
             "choices": ["A) Selg — overpriset", "B) Kjøp �� underpriset", "C) Korrekt priset", "D) Negativ beta"],
             "answer": 1, "difficulty": 1,
             "explanation": "Over SML = faktisk avkastning > CAPM-kravet = du får mer enn du burde for risikoen = UNDERPRISET.",
             "misconception": "Mange snur dette. Husk: OVER linjen = UNDER priset. Høyere avkastning enn forventet = billig aksje.",
             "intuition": "SML er «normalprisen» for risiko. Over = du får en deal. Under = du betaler for mye.",
             "formula": "α = Ra − [Rf + β(Rm−Rf)]", "calc_steps": ""},
            {"q": "β = 0,8. Markedet stiger 10 %. Hvor mye stiger aksjen?",
             "choices": ["A) 10 %", "B) 8 %", "C) 12,5 %", "D) 80 %"],
             "answer": 1, "difficulty": 1,
             "explanation": "β = 0,8 betyr aksjen beveger seg 80 % av markedet. 0,8 × 10 % = 8 %.",
             "misconception": "β er IKKE prosent av noe — det er en multiplikator for markedsbevegelsen.",
             "intuition": "Beta er aksjens «følsomhet». β<1 = defensiv, β>1 = aggressiv, β=1 = følger markedet.",
             "formula": "ΔAksje ≈ β × ΔMarked", "calc_steps": ""},
            {"q": "Hva er markedsporteføljens beta?",
             "choices": ["A) 0", "B) 0,5", "C) 1,0", "D) Varierer"],
             "answer": 2, "difficulty": 1,
             "explanation": "Markedet har per definisjon β = 1,0. Alt måles relativt til markedet.",
             "misconception": "Noen tror beta varierer med markedsforhold. Nei — markedets beta er ALLTID 1,0 per definisjon.",
             "intuition": "Beta måler «hvor mye svinger du sammenlignet med markedet?» Markedet sammenlignet med seg selv = 1.",
             "formula": "β_marked = 1,0", "calc_steps": ""},
        ],
        "beregning": [
            {"q": "Fond A: 14 % avkastning. Rf = 3 %, Rm = 11 %, β = 1,2. Beregn Jensens alfa. Har fondet slått markedet?",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: Alfa måler om fondsforvalteren er dyktig — gir fondet mer enn beta tilsier?",
                 "Steg 1: CAPM-krav = 3 + 1,2 × (11−3) = 3 + 9,6 = 12,6 %",
                 "Steg 2: α = Faktisk − Forventet = 14 − 12,6 = 1,4 %",
                 "Steg 3: α > 0 → Ja, fondet slo markedet med 1,4 prosentpoeng etter risikojustering.",
             ],
             "calc_steps": ["11 − 3 = 8 → 1.2 × 8 = 9.6 → 3 + 9.6 = 12.6 → 14 − 12.6 = 1.4"],
             "answer": 1.4, "tolerance": 0.1,
             "formula": "α = Ra − [Rf + β(Rm−Rf)]",
             "common_mistake": "Vanlig feil: Sammenligner direkte med markedet (14−11=3%). Det ignorerer at β=1,2 betyr høyere risiko."},
        ],
        "case": [
            {"scenario": "**Eksamen BØK 3423 — Oppgave 3 (20 poeng)**\n\nNordsjø Invest analyserer tre aksjer:\n\n| Aksje | β | Faktisk avk. |\n|---|---|---|\n| Equinor | 1,1 | 14 % |\n| Telenor | 0,7 | 9 % |\n| Nel ASA | 1,8 | 18 % |\n\nRf = 2,5 %, E(Rm) = 10 %.",
             "questions": [
                 {"q": "a) Beregn CAPM-kravet for hver aksje (9 p)", "answer": "Markedspremie = 10−2,5 = 7,5 %\nEquinor: 2,5 + 1,1×7,5 = **10,75 %**\nTelenor: 2,5 + 0,7×7,5 = **7,75 %**\nNel: 2,5 + 1,8×7,5 = **16,0 %**"},
                 {"q": "b) Hvilke aksjer ligger over SML? Hva anbefaler du? (6 p)", "answer": "Alle tre over SML:\nEquinor: 14 > 10,75 (α = 3,25 %)\nTelenor: 9 > 7,75 (α = 1,25 %)\nNel: 18 > 16,0 (α = 2,0 %)\nAlle er underpriset — kjøp! Equinor har høyest alfa."},
                 {"q": "c) Hva betyr det at Nel har β = 1,8? Forklar for en som ikke kan finans (5 p)", "answer": "Når markedet går opp 10 %, går Nel opp ca. 18 %. Men når markedet faller 10 %, faller Nel ca. 18 %. Nel svinger nesten dobbelt så mye som markedet — høy risiko, men også mulighet for høy avkastning."},
             ]},
        ],
    },
    "portefolje": {
        "flervalg": [
            {"q": "ρ = −1 mellom to aksjer. Hva kan du oppnå?",
             "choices": ["A) Dobbelt risiko", "B) Null risiko mulig", "C) Ingen diversifisering", "D) Høyere avkastning"],
             "answer": 1, "difficulty": 1,
             "explanation": "ρ = −1 = perfekt negativ korrelasjon. Med riktige vekter: σp = 0. Perfekt hedge.",
             "misconception": "ρ = −1 betyr ikke at aksjene alltid faller — det betyr at de alltid beveger seg motsatt.",
             "intuition": "Tenk paraply-selskap og solkrem-selskap. Regn = bra for én, dårlig for den andre. Sammen: stabil.",
             "formula": "σp² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂", "calc_steps": ""},
            {"q": "A: E(r)=12%, σ=20%. B: E(r)=10%, σ=12%. Rf=3%. Best Sharpe?",
             "choices": ["A) A: Sharpe=0,45", "B) B: Sharpe=0,58", "C) Like", "D) Kan ikke beregnes"],
             "answer": 1, "difficulty": 2,
             "explanation": "A: (12−3)/20=0,45. B: (10−3)/12=0,58. B gir mer avkastning per enhet risiko.",
             "misconception": "Vanlig feil: Velge A fordi den har høyest avkastning. Sharpe justerer for risiko!",
             "intuition": "Sharpe = «bang for the buck». B gir mer per krone risiko du tar.",
             "formula": "Sharpe = (E(rp)−Rf) / σp", "calc_steps": "A: (12−3)÷20=0.45 | B: (10−3)÷12=0.58"},
        ],
        "beregning": [
            {"q": "X: E(r)=15%, σ=25%. Y: E(r)=10%, σ=15%. ρ=0,3. Portefølje: 60/40. Beregn E(rp) og σp.",
             "difficulty": 3,
             "steps": [
                 "Intuisjon: Ved å kombinere X og Y får vi lavere risiko enn vektet snitt, fordi ρ < 1.",
                 "Steg 1: E(rp) = 0,6×15 + 0,4×10 = 9 + 4 = 13 %",
                 "Steg 2: σp² = (0,6²×25²) + (0,4²×15²) + 2×0,6×0,4×0,3×25×15",
                 "Steg 3: σp² = (0,36×625) + (0,16×225) + (2×0,072×375)",
                 "Steg 4: σp² = 225 + 36 + 54 = 315",
                 "Steg 5: σp = √315 = 17,75 %",
                 "Merk: Vektet snitt σ ville vært 0,6×25+0,4×15 = 21 %. Diversifisering sparte 3,25 %!",
             ],
             "calc_steps": ["0.6² × 25² = 225 → 0.4² × 15² = 36 → 2×0.6×0.4×0.3×25×15 = 54 → √(225+36+54) = √315 = 17.75"],
             "answer": 17.75, "tolerance": 0.5,
             "formula": "σp² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂",
             "common_mistake": "Vanlig feil: Glemme det tredje leddet (2w₁w₂ρσ₁σ₂). Da får du √(225+36) = 16,16 % — for lavt."},
        ],
        "case": [],
    },
    "wacc": {
        "flervalg": [
            {"q": "Hvorfor (1−T) på gjeldskostnaden i WACC?",
             "choices": ["A) Gjeld er risikofri", "B) Skattefradrag på renter", "C) EK er dyrere", "D) Konvensjon"],
             "answer": 1, "difficulty": 1,
             "explanation": "Renter gir skattefradrag ��� reell gjeldskostnad = Rd×(1−T). Skatten «subsidierer» gjelden.",
             "misconception": "Det er ikke at gjeld er billigere «fordi den er tryggere» — det er skatteeffekten som gjør den billigere.",
             "intuition": "Betaler du 5 % rente med 22 % skatt, koster gjelden deg egentlig bare 3,9 %. Staten tar resten.",
             "formula": "WACC = (E/V)×Re + (D/V)×Rd×(1−T)", "calc_steps": "5 × (1−0.22) = 5 × 0.78 = 3.9"},
        ],
        "beregning": [
            {"q": "EK = 600M, Gjeld = 400M. Re = 12 %, Rd = 5 %, Skatt = 22 %. Beregn WACC.",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: WACC er hva det koster selskapet å skaffe kapital — et vektet snitt av EK og gjeld.",
                 "Steg 1: V = E + D = 600 + 400 = 1 000M",
                 "Steg 2: E/V = 0,6 — D/V = 0,4",
                 "Steg 3: WACC = 0,6×12 + 0,4×5×(1−0,22)",
                 "Steg 4: = 7,20 + 0,4×3,90 = 7,20 + 1,56 = 8,76 %",
             ],
             "calc_steps": ["600÷1000=0.6 → 0.6×12=7.2 → 5×0.78=3.9 → 0.4×3.9=1.56 → 7.2+1.56=8.76"],
             "answer": 8.76, "tolerance": 0.05,
             "formula": "WACC = (E/V)×Re + (D/V)×Rd×(1−T)",
             "common_mistake": "Glemmer (1−T): 0,6×12 + 0,4×5 = 9,2 %. Uten skattejustering overvurderer du kapitalkostnaden."},
        ],
        "case": [],
    },
    "oblig": {
        "flervalg": [
            {"q": "Kupong 6 %, YTM 8 %. Handles til...?",
             "choices": ["A) Overkurs", "B) Underkurs", "C) Pari", "D) Umulig å si"],
             "answer": 1, "difficulty": 1,
             "explanation": "Kupong < YTM → obligasjonen gir for lite kupong → investorer krever rabatt → underkurs.",
             "misconception": "Husk regelen: Kupong < YTM = Under, Kupong > YTM = Over, Kupong = YTM = Pari.",
             "intuition": "Markedet krever 8 % men obligasjonen betaler bare 6 %. For å kompensere MÅ prisen være lavere.",
             "formula": "P = Σ C/(1+r)ᵗ + F/(1+r)ⁿ", "calc_steps": ""},
        ],
        "beregning": [
            {"q": "Obligasjon: Pålydende 1 000 000, kupong 5 %, 3 år, YTM 7 %. Pris?",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: Prisen er hva du bør betale i dag for kuponger + pålydende tilbake.",
                 "Steg 1: Kupong = 1 000 000 × 5 % = 50 000 kr/år",
                 "Steg 2: P = 50 000/1,07 + 50 000/1,07² + 50 000/1,07³ + 1 000 000/1,07³",
                 "Steg 3: = 46 729 + 43 672 + 40 816 + 816 298",
                 "Steg 4: P = 947 515 kr (underkurs: kupong 5 % < YTM 7 %)",
             ],
             "calc_steps": ["50000 [PMT] → 1000000 [FV] → 7 [I/YR] → 3 [N] → [COMP] [PV] = −947 515"],
             "answer": 947515, "tolerance": 1000,
             "formula": "P = Σ C/(1+r)ᵗ + F/(1+r)ⁿ",
             "common_mistake": "Glemmer PV av pålydende. Bare kupongene gir 131 217 — men pålydende er 816 298! Det er hoveddelen."},
        ],
        "case": [],
    },
    "lan": {
        "flervalg": [
            {"q": "Annuitetslån vs. serielån — hva stemmer?",
             "choices": ["A) Annuitet: konstant PMT, serie: konstant avdrag", "B) Omvendt", "C) Begge konstant PMT", "D) Serie har null rente"],
             "answer": 0, "difficulty": 1,
             "explanation": "Annuitet: fast PMT (rente synker, avdrag øker). Serie: fast avdrag (rente synker, PMT synker).",
             "misconception": "Mange blander. Husk: ANNUITET = du betaler det SAMME hver gang. SERIE = du betaler NED det SAMME.",
             "intuition": "Annuitet = forutsigbart budsjett. Serie = du betaler mer i starten men totalt mindre rente.",
             "formula": "Annuitet: PMT=konst. Serie: Avdrag=Lån/n", "calc_steps": ""},
        ],
        "beregning": [
            {"q": "Serielån: 600 000 kr, 6 % rente, 3 år. Sett opp nedbetalingsplan (terminbeløp alle 3 år).",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: Serielån = like avdrag, rente på gjenstående gjeld.",
                 "Avdrag = 600 000/3 = 200 000/år",
                 "År 1: Rente = 600 000×6% = 36 000. PMT = 200 000+36 000 = 236 000",
                 "År 2: Rente = 400 000×6% = 24 000. PMT = 200 000+24 000 = 224 000",
                 "År 3: Rente = 200 000×6% = 12 000. PMT = 200 000+12 000 = 212 000",
                 "Total rente = 36+24+12 = 72 000 kr",
             ],
             "calc_steps": ["600000÷3=200000(avdrag) → 600000×0.06=36000 → 400000×0.06=24000 → 200000×0.06=12000"],
             "answer": 236000, "tolerance": 100,
             "formula": "Terminbeløp = Avdrag + Rente på restgjeld",
             "common_mistake": "Bruker annuitetsformelen. Serielån beregnes manuelt med tabell — det er enklere enn du tror."},
        ],
        "case": [],
    },
    "invest": {
        "flervalg": [
            {"q": "Hvorfor legges avskrivninger tilbake i FCF?",
             "choices": ["A) Inntekt", "B) Ikke-kontant kostnad", "C) Investering", "D) Øke skatt"],
             "answer": 1, "difficulty": 1,
             "explanation": "Avskrivninger trekkes fra i resultatregnskapet (reduserer skatt) men er ikke en utbetaling.",
             "misconception": "Avskrivning er bokføring, ikke penger ut av kontoen. Den gir skattefordel uten kontanteffekt.",
             "intuition": "Du kjøpte en maskin for 3 år siden. Avskrivningen er «papirkostnad» — pengene gikk ut da du kjøpte den.",
             "formula": "FCF = EBIT×(1−T) + Avskr − CAPEX − ΔNWC", "calc_steps": ""},
        ],
        "beregning": [
            {"q": "EBIT=500k, Skatt=22%, Avskr=80k, CAPEX=50k, ΔNWC=20k. Beregn FCF.",
             "difficulty": 2,
             "steps": [
                 "Intuisjon: FCF = ekte penger selskapet genererer etter drift og investering.",
                 "Steg 1: NOPAT = EBIT × (1−T) = 500 000 × 0,78 = 390 000",
                 "Steg 2: + Avskrivninger (tilbakeføring) = 390 000 + 80 000 = 470 000",
                 "Steg 3: − CAPEX (ny investering) = 470 000 − 50 000 = 420 000",
                 "Steg 4: − ΔNWC (kapitalbinding) = 420 000 − 20 000 = 400 000 kr",
             ],
             "calc_steps": ["500000×0.78=390000 → +80000=470000 → −50000=420000 → −20000=400000"],
             "answer": 400000, "tolerance": 100,
             "formula": "FCF = EBIT×(1−T) + Avskr − CAPEX − ΔNWC",
             "common_mistake": "Starter fra nettoresultat i stedet for EBIT. Nettoresultat inkluderer rentekostnader, men FCF skal være uavhengig av finansiering."},
        ],
        "case": [],
    },
}

# ─── VISUAL CHARTS ───────────────────────────────────────────────────────────

CT = dict(template="plotly_dark", paper_bgcolor="#0b0f19", plot_bgcolor="#111827",
    font=dict(color="#f0f0f0", size=13),
    title_font=dict(color="#f0f0f0", size=14),
    legend=dict(font=dict(color="#f0f0f0", size=12)),
    xaxis=dict(color="#f0f0f0", tickfont=dict(color="#a1a1aa"), title_font=dict(color="#d4d4d8"), gridcolor="#1e293b"),
    yaxis=dict(color="#f0f0f0", tickfont=dict(color="#a1a1aa"), title_font=dict(color="#d4d4d8"), gridcolor="#1e293b"),
    margin=dict(l=40, r=20, t=40, b=40),
)

def chart_tidsverdi():
    years = list(range(0, 31))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=[10000*(1.05)**t for t in years], name="Rentes rente 5%", line=dict(color="#22c55e", width=3)))
    fig.add_trace(go.Scatter(x=years, y=[10000*(1+0.05*t) for t in years], name="Enkel rente 5%", line=dict(color="#f59e0b", width=2, dash="dash")))
    fig.update_layout(title="Rentes-rente vs. enkel rente: 10 000 kr", xaxis_title="År", yaxis_title="kr", height=300, **CT)
    return fig

def chart_npv_irr():
    rates = [r/100 for r in range(0, 26)]
    cf = [-100000, 40000, 40000, 40000, 40000]
    npvs = [sum(c/(1+r)**t if r > 0 else c for t, c in enumerate(cf)) for r in rates]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r*100 for r in rates], y=npvs, line=dict(color="#60a5fa", width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="#ef4444")
    fig.update_layout(title="NPV vs. rente — IRR der kurven krysser null", xaxis_title="r (%)", yaxis_title="NPV", height=300, **CT)
    return fig

def chart_sml():
    betas = [0, 0.5, 1.0, 1.5, 2.0]
    sml = [3 + b*7 for b in betas]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=betas, y=sml, name="SML", line=dict(color="#3b82f6", width=3)))
    fig.add_trace(go.Scatter(x=[0.8,1.2,1.5], y=[12,9,16], mode="markers+text", text=["Kjøp!","Selg!","Kjøp!"],
        textposition="top center", textfont=dict(color="#fff"), marker=dict(size=14, color=["#22c55e","#ef4444","#22c55e"])))
    fig.update_layout(title="SML: Over=underpriset, Under=overpriset", xaxis_title="β", yaxis_title="E(r) %", height=350, **CT)
    return fig

def chart_diversification():
    n = list(range(1, 31))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=n, y=[15+30/i for i in n], line=dict(color="#60a5fa", width=3), fill="tozeroy", fillcolor="rgba(96,165,250,0.1)"))
    fig.add_hline(y=15, line_dash="dash", line_color="#ef4444", annotation_text="Systematisk", annotation_font_color="#fff")
    fig.update_layout(title="Diversifisering: usystematisk risiko forsvinner", xaxis_title="Aksjer", yaxis_title="σ %", height=300, **CT)
    return fig

def chart_wacc():
    fig = go.Figure(go.Bar(x=["EK-del","Gjeld-del","WACC"], y=[7.2,1.56,8.76], marker_color=["#22c55e","#60a5fa","#f59e0b"],
        text=["7,20%","1,56%","8,76%"], textposition="outside", textfont=dict(color="#fff", size=14)))
    fig.update_layout(title="WACC: 60%EK(12%) + 40%Gjeld(5%,T=22%)", yaxis_title="%", height=300, **CT)
    return fig

def chart_bond():
    ys = [r/10 for r in range(10, 151)]
    ps = [50000*(1-(1+y/100)**(-5))/(y/100)+1000000/(1+y/100)**5 for y in ys]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ys, y=ps, line=dict(color="#ef4444", width=3)))
    fig.add_hline(y=1000000, line_dash="dash", line_color="#94a3b8", annotation_text="Pari", annotation_font_color="#fff")
    fig.update_layout(title="Rente↑ = Pris↓", xaxis_title="YTM%", yaxis_title="Pris", height=300, **CT)
    return fig

def chart_loan():
    loan, rate, n = 600000, 0.06, 5
    sp = [loan/n + (loan-(i-1)*loan/n)*rate for i in range(1, n+1)]
    pmt = loan*rate*(1+rate)**n/((1+rate)**n-1)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(1,n+1)), y=[pmt]*n, name="Annuitet", marker_color="#22c55e"))
    fig.add_trace(go.Bar(x=list(range(1,n+1)), y=sp, name="Serie", marker_color="#60a5fa"))
    fig.update_layout(title="Annuitet(konst) vs Serie(synkende)", xaxis_title="År", yaxis_title="PMT", barmode="group", height=300, **CT)
    return fig

def chart_fcf():
    fig = go.Figure(go.Waterfall(x=["EBIT","−Skatt","NOPAT","+Avskr","−CAPEX","−ΔNWC","FCF"],
        y=[500000,-110000,390000,80000,-50000,-20000,400000], measure=["absolute","relative","total","relative","relative","relative","total"],
        connector={"line":{"color":"#2d3a4f"}}, increasing={"marker":{"color":"#22c55e"}},
        decreasing={"marker":{"color":"#ef4444"}}, totals={"marker":{"color":"#3b82f6"}},
        textposition="outside", text=[f"{v:+,.0f}" for v in [500000,-110000,390000,80000,-50000,-20000,400000]], textfont=dict(color="#fff")))
    fig.update_layout(title="FCF Waterfall", yaxis_title="kr", height=350, **CT)
    return fig

CHARTS = {
    "tidsverdi": [
        (chart_tidsverdi, "Denne grafen viser forskjellen mellom rentes rente og enkel rente over 30 år. Med enkel rente vokser pengene lineært — du får 500 kr ekstra hvert år. Med rentes rente vokser de eksponentielt — du tjener rente på renten, og gapet blir større og større. Etter 30 år er forskjellen over 10 000 kr. Dette er grunnen til at tid er den viktigste faktoren i sparing."),
        (chart_npv_irr, "Grafen viser NPV som funksjon av diskonteringsrenten. Når renten er lav, er NPV høy — fordi fremtidige kontantstrømmer er «verdt mer» i dag. Etterhvert som renten øker, synker NPV. Der kurven krysser nullinjen finner du IRR — den renten som gjør prosjektet akkurat verdt investeringen. Prosjektet er lønnsomt for alle renter under IRR, og ulønnsomt for alle over."),
    ],
    "capm": [
        (chart_sml, "Security Market Line (SML) viser sammenhengen mellom beta og forventet avkastning. Linjen starter i risikofri rente (der beta er null) og stiger jevnt. Aksje A og C ligger over linjen — de gir mer avkastning enn CAPM-kravet for sin risiko, og er derfor underpriset (kjøp!). Aksje B ligger under linjen — den gir for lite avkastning for risikoen, og er overpriset (selg!)."),
    ],
    "portefolje": [
        (chart_diversification, "Grafen viser at porteføljerisikoen synker raskt når du legger til flere aksjer. Det blå området over den røde linjen er usystematisk risiko — bedriftsspesifikk risiko som forsvinner med diversifisering. Den røde linjen er systematisk risiko (markedsrisiko) som du aldri kan bli kvitt, uansett hvor mange aksjer du eier. Allerede med 15-20 aksjer har du fjernet det meste av den usystematiske risikoen."),
    ],
    "wacc": [
        (chart_wacc, "Søylediagrammet bryter ned WACC i to komponenter. Den grønne søylen viser EK-bidraget: 60 % egenkapitalandel ganget med 12 % avkastningskrav = 7,20 %. Den blå søylen viser gjeldsbidraget: 40 % gjeldsandel ganget med 5 % rente etter skatt (5 % × 0,78) = 1,56 %. Summen er WACC = 8,76 %. Legg merke til at gjelden er mye billigere enn egenkapitalen — det er skatteskjoldet i aksjon."),
    ],
    "oblig": [
        (chart_bond, "Grafen illustrerer den inverse sammenhengen mellom markedsrente og obligasjonspris. Når renten stiger, faller prisen — fordi de faste kupongene blir relativt mindre attraktive sammenlignet med nye obligasjoner med høyere rente. Den grå linjen markerer pålydende (pari). Når YTM er lik kupongrenten (5 %) handles obligasjonen til pari. Under 5 % handles den til overkurs, over 5 % til underkurs."),
    ],
    "lan": [
        (chart_loan, "Søylene sammenligner terminbeløpene for annuitetslån og serielån over 5 år. De grønne søylene (annuitet) er like høye hvert år — konstant terminbeløp. De blå søylene (serielån) starter høyt og synker — fordi avdraget er konstant mens renten beregnes på en stadig lavere restgjeld. Serielån gir høyere betalinger i starten, men lavere total rentekostnad over lånets levetid."),
    ],
    "invest": [
        (chart_fcf, "Waterfall-diagrammet viser steg for steg hvordan du kommer fra EBIT til fri kontantstrøm (FCF). Du starter med EBIT (500 000), trekker fra skatt for å få NOPAT, legger tilbake avskrivninger (fordi de ikke er en reell utbetaling), og trekker fra CAPEX og endring i arbeidskapital. Resultatet — FCF = 400 000 — er de faktiske pengene selskapet har tilgjengelig for aksjonærer og kreditorer."),
    ],
}

# ─── FORMLER ─────────────────────────────────────────────────────────────────

ALL_FORMULAS = [
    {"group":"Pengenes tidsverdi","color":"#3b82f6","formulas":[("FV","FV = PV × (1 + r)ⁿ","Fremtidig verdi"),("PV","PV = FV / (1 + r)ⁿ","Nåverdi"),("NPV","NPV = Σ CFₜ/(1+r)ᵗ − I₀","Netto nåverdi"),("Annuitet","PV = PMT × [1−(1+r)⁻ⁿ]/r","Nåverdi annuitet"),("Perpetuitet","PV = CF / r","Uendelig rekke"),("EAR","EAR = (1+APR/m)ᵐ−1","Effektiv rente")]},
    {"group":"CAPM & SML","color":"#a78bfa","formulas":[("CAPM","E(Ri) = Rf + β×[E(Rm)−Rf]","Forventet avkastning"),("Beta","β = Cov(Ri,Rm)/Var(Rm)","Systematisk risiko"),("Alfa","α = Ra−[Rf+β(Rm−Rf)]","Meravkastning")]},
    {"group":"Porteføljeteori","color":"#22c55e","formulas":[("E(rp)","E(rp) = Σ wᵢ×E(rᵢ)","Porteføljeavkastning"),("σp²","σp²=w₁²σ₁²+w₂²σ₂²+2w₁w₂σ₁₂","Varians 2 aktiva"),("Kovarians","σ₁₂=ρ₁₂×σ₁×σ₂","Samvariasjon"),("Sharpe","(E(rp)−Rf)/σp","Risikojustert")]},
    {"group":"WACC","color":"#f59e0b","formulas":[("WACC","(E/V)×Re+(D/V)×Rd×(1−T)","Kapitalkostnad"),("MM","VL = VU + T×D","Med skatt")]},
    {"group":"Obligasjoner","color":"#ef4444","formulas":[("Oblig","P=Σ C/(1+r)ᵗ+F/(1+r)ⁿ","Pris"),("Gordon","P₀=D₁/(r−g)","Dividendemodell")]},
    {"group":"Lån","color":"#60a5fa","formulas":[("PMT","PV×r(1+r)ⁿ/[(1+r)ⁿ−1]","Annuitet"),("Serie","Avdrag=Lån/n","Serielån")]},
    {"group":"Investering","color":"#fb923c","formulas":[("FCF","EBIT×(1−T)+Avskr−CAPEX−ΔNWC","Fri kontantstrøm"),("TV","FCFₙ×(1+g)/(WACC−g)","Terminalverdi")]},
]

# ─── LEARN CONTENT ───────────────────────────────────────────────────────────

LEARN = {
    "tidsverdi": {"title":"Pengenes tidsverdi",
        "intro":"Dette er det mest grunnleggende konseptet i hele finansfaget. Hele poenget er enkelt: en krone du har i dag er mer verdt enn en krone du f\u00e5r i fremtiden. Hvorfor? Fordi du kan investere kronen i dag og la den vokse. Denne enkle innsikten er fundamentet for alt annet i B\u00d8K 3423 \u2014 fra prosjektvurdering til obligasjonsprising til l\u00e5neberegning.",
        "concepts":[
            {"name":"Fremtidig verdi (FV) og N\u00e5verdi (PV)",
             "text":"Tenk deg at du setter 10 000 kr i banken til 5 % \u00e5rlig rente. Hva skjer?\n\n- Etter 1 \u00e5r har du 10 000 \u00d7 1,05 = 10 500 kr\n- Etter 2 \u00e5r: 10 500 \u00d7 1,05 = 11 025 kr \u2014 her ser du rentes rente i aksjon! Du tjener rente p\u00e5 renten fra \u00e5ret f\u00f8r.\n- Etter 3 \u00e5r: 11 025 \u00d7 1,05 = 11 576 kr\n\nDette kalles rentes-rente-effekten (compounding), og det er det som gj\u00f8r at penger vokser eksponentielt, ikke line\u00e6rt. Jo lenger tid, jo kraftigere blir effekten \u2014 etter 30 \u00e5r ville 10 000 kr blitt til over 43 000 kr.\n\nFV (fremtidig verdi) svarer p\u00e5: Hva blir pengene mine verdt i fremtiden?\nPV (n\u00e5verdi) svarer p\u00e5 det motsatte: Hva er fremtidige penger verdt i dag?\n\nDiskontering er det samme som rentes rente, bare baklengs \u2014 du spoler tilbake fremtidige penger til i dag. Disse to konseptene henger ul\u00f8selig sammen. Kan du det ene, kan du det andre.",
             "formula":"FV = PV \u00d7 (1 + r)\u207f  |  PV = FV / (1 + r)\u207f",
             "tip":"Diskontering er bare rentes rente i revers. Kalkulatoren gj\u00f8r jobben \u2014 du trenger bare forst\u00e5 retningen.",
             "calc":"Legg inn 3 av 4: [PV] [FV] [N] [I/YR] \u2192 trykk [COMP] p\u00e5 den manglende"},
            {"name":"NPV \u2014 Netto n\u00e5verdi",
             "text":"NPV er kanskje det viktigste beslutningsverkt\u00f8yet i finans. Det svarer p\u00e5 et enkelt sp\u00f8rsm\u00e5l: Skaper dette prosjektet verdi?\n\nSlik fungerer det: Du tar alle fremtidige kontantstr\u00f8mmer prosjektet genererer, diskonterer dem tilbake til i dag (slik at de er sammenlignbare), og trekker fra investeringskostnaden. Det du sitter igjen med er NPV \u2014 prosjektets verdi i kroner, i dag.\n\nBeslutningsregelen er enkel:\n- NPV > 0 \u2192 Prosjektet gir mer enn avkastningskravet. Gjennomf\u00f8r det!\n- NPV < 0 \u2192 Prosjektet gir mindre enn kravet. La det v\u00e6re.\n- NPV = 0 \u2192 Prosjektet gir n\u00f8yaktig kravet. Du er likegyldig.\n\nEt viktig poeng: NPV > 0 betyr ikke at prosjektet er risikofritt. Det betyr at forventet avkastning overstiger kravet du har satt, gitt risikoen.\n\nKlassisk eksamensfeil: Kontantstr\u00f8mmen ved t=0 diskonteres IKKE \u2014 den er allerede i dag.",
             "formula":"NPV = \u03a3 CF\u209c/(1+r)\u1d57 \u2212 I\u2080",
             "tip":"CF ved t=0 diskonteres ALDRI. Og NPV > 0 betyr ikke risikofritt \u2014 bare at forventet avkastning overstiger kravet.",
             "calc":"Diskont\u00e9r hver CF: CF\u2081\u00f71,r + CF\u2082\u00f71,r\u00b2 osv. Summ\u00e9r, trekk fra I\u2080."},
            {"name":"IRR \u2014 Internrenten",
             "text":"IRR er den diskonteringsrenten som gj\u00f8r at NPV blir n\u00f8yaktig null. Med andre ord: det er prosjektets innebygde avkastning \u2014 den renten prosjektet faktisk gir deg.\n\nTenk p\u00e5 det slik: Hvis du setter pengene i banken til IRR-renten, ville du f\u00e5tt n\u00f8yaktig samme avkastning som prosjektet gir.\n\nBeslutningsregelen:\n- IRR > avkastningskravet \u2192 Godta!\n- IRR < avkastningskravet \u2192 Avsl\u00e5.\n\nIRR og NPV gir vanligvis samme anbefaling. Men i noen spesialtilfeller kan de gi ulike svar. N\u00e5r det skjer, stol alltid p\u00e5 NPV. NPV m\u00e5ler verdi i kroner, IRR i prosent \u2014 og kroner er det som teller.",
             "formula":"NPV = 0 \u2192 finn r = IRR",
             "tip":"Ved motstrid mellom IRR og NPV: stol alltid p\u00e5 NPV. NPV m\u00e5ler verdi i kroner, IRR i prosent.",
             "calc":"Legg inn CF\u2080 (negativ), CF\u2081, CF\u2082... \u2192 [COMP] [I/YR] = IRR"},
            {"name":"Annuitet og Perpetuitet",
             "text":"En annuitet er en serie med like store betalinger over et bestemt antall perioder. Eksempler inkluderer boligl\u00e5n, forsikringspremier og leasingavtaler. Annuitetsformelen lar deg finne n\u00e5verdien av alle betalingene i \u00e9n beregning.\n\nEn perpetuitet er en annuitet som aldri stopper \u2014 den betaler det samme bel\u00f8pet for alltid. Formelen er den enkleste i hele faget: PV = CF / r. Den dukker opp overalt \u2014 inkludert i terminalverdi-beregninger.\n\nKalkulatoren gj\u00f8r annuiteten for deg: Legg inn PMT, N, I/YR, trykk COMP PV.",
             "formula":"PV(annuitet) = PMT \u00d7 [1\u2212(1+r)\u207b\u207f] / r\nPV(perpetuitet) = CF / r",
             "tip":"Perpetuitetsformelen er den enkleste i faget, men dukker opp overalt \u2014 ogs\u00e5 i terminalverdi.",
             "calc":"[PMT] [N] [I/YR] [FV=0] \u2192 [COMP] [PV] gir n\u00e5verdien av annuiteten"},
        ]},
    "capm": {"title":"CAPM & Security Market Line",
        "intro":"Capital Asset Pricing Model (CAPM) er en av de mest sentrale modellene i finans. Den svarer p\u00e5 et fundamentalt sp\u00f8rsm\u00e5l: Gitt risikoen til en aksje, hva B\u00d8R den forventede avkastningen v\u00e6re? CAPM kobler risiko og avkastning sammen p\u00e5 en presis, matematisk m\u00e5te.",
        "concepts":[
            {"name":"CAPM-formelen",
             "text":"CAPM sier at forventet avkastning bestemmes av tre ting:\n\n1. Risikofri rente (Rf) \u2014 minimumsavkastningen alle krever, uten risiko.\n2. Markedspremien (Rm \u2212 Rf) \u2014 ekstra avkastning for \u00e5 ta markedsrisiko.\n3. Beta (\u03b2) \u2014 hvor mye aksjen svinger relativt til markedet. Skalerer premien.\n\nIntuisjonen: Start med risikofri rente, legg til kompensasjon for risiko. Jo h\u00f8yere beta, jo mer risiko, jo h\u00f8yere krav.\n\nEksempel: Rf = 3 %, \u03b2 = 1,2, Rm = 10 %\nE(Ri) = 3 + 1,2 \u00d7 (10 \u2212 3) = 3 + 8,4 = 11,4 %\n\nDen absolutt vanligste eksamensfeilen er \u00e5 gange beta med Rm i stedet for markedspremien (Rm \u2212 Rf). Trekk ALLTID fra Rf f\u00f8rst!",
             "formula":"E(Ri) = Rf + \u03b2 \u00d7 [E(Rm) \u2212 Rf]",
             "tip":"Vanligste eksamensfeil: \u03b2 \u00d7 Rm i stedet for \u03b2 \u00d7 (Rm \u2212 Rf). ALLTID trekk fra Rf f\u00f8rst!",
             "calc":"Steg 1: Rm \u2212 Rf = premie. Steg 2: \u03b2 \u00d7 premie. Steg 3: + Rf = avkastningskrav."},
            {"name":"Beta \u2014 Systematisk risiko",
             "text":"Beta m\u00e5ler hvor mye en aksje svinger relativt til markedet \u2014 det er et m\u00e5l p\u00e5 systematisk risiko.\n\n- \u03b2 = 1,0 \u2192 Likt med markedet\n- \u03b2 > 1 \u2192 Mer volatil (aggressiv). \u03b2 = 1,5: markedet opp 10 % \u2192 aksjen opp 15 %\n- \u03b2 < 1 \u2192 Mindre volatil (defensiv). Typisk Orkla, Telenor\n- \u03b2 = 0 \u2192 Risikofri\n\nBeta fanger bare systematisk risiko \u2014 den du IKKE kan diversifisere bort. Bedriftsspesifikk risiko er usystematisk og kan fjernes med diversifisering. CAPM bel\u00f8nner deg derfor bare for systematisk risiko.",
             "formula":"\u03b2 = Cov(Ri, Rm) / Var(Rm)",
             "tip":"Markedsportef\u00f8ljen har \u03b2 = 1 per definisjon. Statsobligasjoner \u2248 0.",
             "calc":"Beta oppgis vanligvis i oppgaven \u2014 du beregner den sjelden selv."},
            {"name":"SML og Jensens alfa",
             "text":"Security Market Line (SML) er CAPM som graf: beta p\u00e5 x-aksen, forventet avkastning p\u00e5 y. Linjen starter i (0, Rf) og stiger med markedspremien.\n\nPlott aksjer i diagrammet for \u00e5 se om de er riktig priset:\n- Over SML \u2192 Gir MER enn CAPM-kravet \u2192 Underpriset \u2192 KJ\u00d8P!\n- Under SML \u2192 Gir MINDRE enn kravet \u2192 Overpriset \u2192 SELG!\n- P\u00e5 SML \u2192 Korrekt priset\n\nHuskeregel: OVER linjen = UNDER priset. H\u00f8yere avkastning enn forventet = billig aksje.\n\nJensens alfa er differansen mellom faktisk og forventet avkastning. \u03b1 > 0 betyr at en forvalter har sl\u00e5tt markedet etter risikojustering.",
             "formula":"\u03b1 = Ra \u2212 [Rf + \u03b2(Rm \u2212 Rf)]",
             "tip":"OVER SML = UNDER priset. Klassisk forvirring p\u00e5 eksamen!",
             "calc":"Beregn CAPM-krav f\u00f8rst, trekk fra faktisk avkastning = alfa."},
        ]},
    "portefolje": {"title":"Portef\u00f8ljeteori",
        "intro":"Portef\u00f8ljeteori handler om \u00e5 kombinere investeringer smart. Hovedinnsikten: du kan redusere risiko uten \u00e5 ofre avkastning \u2014 bare ved \u00e5 kombinere aksjer som ikke beveger seg helt likt. Harry Markowitz fikk Nobelprisen for dette.",
        "concepts":[
            {"name":"Forventet portef\u00f8ljeavkastning E(rp)",
             "text":"Forventet avkastning er det vektede gjennomsnittet av enkeltaksjene. Her er ingen magi \u2014 60 % i aksje A (15 %) og 40 % i B (10 %) gir:\n\nE(rp) = 0,6 \u00d7 15 + 0,4 \u00d7 10 = 9 + 4 = 13 %\n\nPortef\u00f8ljeavkastningen ligger alltid mellom den h\u00f8yeste og laveste enkeltaksjen. Du kan ikke skape avkastning ved \u00e5 kombinere \u2014 men du KAN redusere risiko, og det er det neste konseptet handler om.",
             "formula":"E(rp) = \u03a3 w\u1d62 \u00d7 E(r\u1d62)",
             "tip":"Vektene m\u00e5 summeres til 1,0. Avkastningen er alltid mellom enkeltaksjene.",
             "calc":"w\u2081 \u00d7 E(r\u2081) + w\u2082 \u00d7 E(r\u2082)"},
            {"name":"Portef\u00f8ljerisiko og korrelasjon",
             "text":"Her skjer magien! I motsetning til avkastning er portef\u00f8ljerisikoen IKKE et enkelt vektet snitt. Den avhenger av korrelasjonen mellom aksjene.\n\nFormelen har tre ledd. Det tredje (2w\u2081w\u2082\u03c1\u03c3\u2081\u03c3\u2082) fanger samvariasjonen:\n- \u03c1 = +1: Aksjene beveger seg helt likt. Ingen diversifisering.\n- \u03c1 = 0: God diversifisering. Risikoen er vesentlig lavere.\n- \u03c1 = \u22121: Perfekt negativ korrelasjon. Med riktige vekter: null risiko!\n\nI praksis: \u03c1 mellom aksjer er vanligvis 0,3\u20130,7. Nok til betydelig diversifiseringseffekt.\n\nDen vanligste eksamensfeilen er \u00e5 glemme det tredje leddet. Uten det er det ikke portef\u00f8ljeteori.",
             "formula":"\u03c3p\u00b2 = w\u2081\u00b2\u03c3\u2081\u00b2 + w\u2082\u00b2\u03c3\u2082\u00b2 + 2w\u2081w\u2082\u03c1\u03c3\u2081\u03c3\u2082",
             "tip":"GLEM ALDRI det tredje leddet! Regn hvert ledd separat, summ\u00e9r, ta \u221a.",
             "calc":"Ledd 1: w\u2081\u00b2\u00d7\u03c3\u2081\u00b2. Ledd 2: w\u2082\u00b2\u00d7\u03c3\u2082\u00b2. Ledd 3: 2\u00d7w\u2081\u00d7w\u2082\u00d7\u03c1\u00d7\u03c3\u2081\u00d7\u03c3\u2082. Summ\u00e9r \u2192 \u221a"},
            {"name":"Sharpe-ratio",
             "text":"Sharpe-ratio m\u00e5ler meravkastning (utover risikofri rente) per enhet risiko. Den mest brukte metoden for \u00e5 rangere portef\u00f8ljer \u2014 fordi den gj\u00f8r det mulig \u00e5 sammenligne portef\u00f8ljer med ulik risiko.\n\nEksempel: A har 12 %/20 % og B har 10 %/12 %. Med Rf=3 %:\nSharpe A = (12\u22123)/20 = 0,45 vs. Sharpe B = (10\u22123)/12 = 0,58\nB er bedre \u2014 mer avkastning per krone risiko.\n\nTommelregel: Sharpe > 0,5 er god, > 1,0 er utmerket.",
             "formula":"Sharpe = (E(rp) \u2212 Rf) / \u03c3p",
             "tip":"Sharpe sammenligner portef\u00f8ljer uavhengig av risiko. Velg alltid h\u00f8yest Sharpe.",
             "calc":"(Portef\u00f8ljeavkastning \u2212 Rf) \u00f7 standardavvik"},
        ]},
    "wacc": {"title":"Kapitalstruktur & WACC",
        "intro":"WACC er den vektede gjennomsnittlige kapitalkostnaden \u2014 hva det koster selskapet \u00e5 finansiere virksomheten. WACC brukes som diskonteringsrente i DCF-verdsettelse, og er derfor direkte koblet til selskapsverdien.",
        "concepts":[
            {"name":"WACC \u2014 Vektet kapitalkostnad",
             "text":"Et selskap finansieres med egenkapital (EK) og gjeld. Hver har sin kostnad:\n- EK-kostnad (Re): Hva aksjon\u00e6rene krever. Beregnes med CAPM.\n- Gjeldskostnad (Rd): Hva banken tar i rente.\n\nWACC er det vektede snittet \u2014 men gjeldskostnaden justeres med (1\u2212T) fordi renter er fradragsberettiget. Staten subsidierer gjelden din gjennom skattefradrag (skatteskjoldet).\n\nEksempel: 5 % rente med 22 % skatt \u2192 reell kostnad = 5 \u00d7 0,78 = 3,9 %. Staten tar de siste 1,1 prosentpoengene.\n\nDerfor er gjeld billigere enn EK \u2014 skatten subsidierer den. Den vanligste eksamensfeilen er \u00e5 glemme (1\u2212T).",
             "formula":"WACC = (E/V) \u00d7 Re + (D/V) \u00d7 Rd \u00d7 (1\u2212T)",
             "tip":"ALLTID (1\u2212T) p\u00e5 Rd. Glemmer du skattejusteringen = garantert feil. V = E + D.",
             "calc":"V=E+D \u2192 E/V\u00d7Re + D/V\u00d7Rd\u00d7(1\u2212T) = WACC"},
            {"name":"Modigliani-Miller",
             "text":"MM Proposisjon I UTEN skatt: Kapitalstruktur er irrelevant. VL = VU. Uansett hvordan du deler pizzaen, er det like mye pizza.\n\nMM Proposisjon I MED skatt: Gjeld skaper verdi gjennom skatteskjold! VL = VU + T\u00d7D. Mer gjeld \u2192 st\u00f8rre skatteskjold \u2192 h\u00f8yere verdi.\n\nI praksis finnes en optimal gjeldsgrad der skatteskjold balanseres mot konkurskostnader. For mye gjeld \u00f8ker konkursrisikoen.",
             "formula":"VL = VU + T \u00d7 D",
             "tip":"MM er teoretisk. I virkeligheten: optimal gjeldsgrad der skatteskjold balanserer konkurskostnad.",
             "calc":"VU + skattesats \u00d7 gjeld = verdi bel\u00e5nt selskap"},
        ]},
    "oblig": {"title":"Obligasjoner & aksjer",
        "intro":"En obligasjon er et l\u00e5n med faste kuponger. Obligasjonsprisen er n\u00e5verdien av alle fremtidige kontantstr\u00f8mmer \u2014 kuponger pluss tilbakebetaling av p\u00e5lydende. Forst\u00e5r du tidsverdi, forst\u00e5r du obligasjoner.",
        "concepts":[
            {"name":"Obligasjonsprising",
             "text":"En obligasjon betaler to typer kontantstr\u00f8mmer:\n1. Kuponger \u2014 faste rentebetalinger hvert \u00e5r (p\u00e5lydende \u00d7 kupongrente)\n2. P\u00e5lydende \u2014 hovedstolen tilbake ved forfall\n\nPrisen = PV av alle kuponger + PV av p\u00e5lydende.\n\nSammenhengen mellom kupong og markedsrente (YTM):\n- Kupong = YTM \u2192 Pari (pris = p\u00e5lydende)\n- Kupong > YTM \u2192 Overkurs (for mye kupong \u2192 investorer byr opp)\n- Kupong < YTM \u2192 Underkurs (for lite kupong \u2192 krever rabatt)\n\nGenerell regel: Rente opp \u2192 Pris ned. Invers sammenheng.\n\nKlassisk feil: Glemme PV av p\u00e5lydende. Kupongene alene er bare en del \u2014 p\u00e5lydende ved forfall er ofte den st\u00f8rste kontantstr\u00f8mmen.",
             "formula":"P = \u03a3 C/(1+r)\u1d57 + F/(1+r)\u207f",
             "tip":"GLEM ALDRI PV av p\u00e5lydende! Og husk: rente opp = pris ned.",
             "calc":"[PMT=kupong] [FV=p\u00e5lydende] [I/YR=YTM] [N] \u2192 [COMP] [PV]"},
            {"name":"Gordon Growth Model",
             "text":"For aksjer med stabil, voksende dividende. Prisen = neste dividende delt p\u00e5 (krav minus vekst).\n\nEksempel: D\u2081 = 5 kr, r = 10 %, g = 3 %\nP\u2080 = 5 / (0,10 \u2212 0,03) = 71,43 kr\n\nForutsetninger: g M\u00c5 v\u00e6re < r (ellers uendelig pris). D\u2081 er NESTE dividende \u2014 hvis oppgaven gir D\u2080, beregn D\u2081 = D\u2080 \u00d7 (1+g) f\u00f8rst.",
             "formula":"P\u2080 = D\u2081 / (r \u2212 g)",
             "tip":"D\u2081 er NESTE dividende! Har du D\u2080: D\u2081 = D\u2080 \u00d7 (1+g). Og g M\u00c5 < r.",
             "calc":"D\u2080 \u00d7 (1+g) = D\u2081 \u2192 D\u2081 \u00f7 (r \u2212 g) = aksjepris"},
        ]},
    "lan": {"title":"L\u00e5n",
        "intro":"L\u00e5n er noe de fleste m\u00f8ter \u2014 boligl\u00e5n, bill\u00e5n, studiel\u00e5n. Kjerneforskjellen mellom de to hovedtypene er enkel: Annuitetsl\u00e5n har konstant terminbel\u00f8p, seriel\u00e5n har konstant avdrag. Begge testes jevnlig p\u00e5 eksamen.",
        "concepts":[
            {"name":"Annuitetsl\u00e5n",
             "text":"Du betaler n\u00f8yaktig samme bel\u00f8p (PMT) hver termin. Men sammensetningen endrer seg:\n- I starten: Mesteparten er rente, lite avdrag (gjelden er h\u00f8y)\n- Mot slutten: Nesten alt er avdrag, lite rente (gjelden er lav)\n\nFordel: Forutsigbart budsjett. Ulempe: Mer total rente enn seriel\u00e5n (gjelden betales ned saktere).\n\nViktig for eksamen: Ved m\u00e5nedlige terminer m\u00e5 du konvertere \u2014 r = \u00e5rsrente/12 og n = \u00e5r \u00d7 12.",
             "formula":"PMT = PV \u00d7 r(1+r)\u207f / [(1+r)\u207f \u2212 1]",
             "tip":"M\u00e5nedlig: r = \u00e5rsrente/12, n = antall m\u00e5neder. Glem aldri \u00e5 konvertere!",
             "calc":"[PV=l\u00e5nebel\u00f8p] [I/YR=rente] [N=perioder] [FV=0] \u2192 [COMP] [PMT]"},
            {"name":"Seriel\u00e5n",
             "text":"Like store avdrag = l\u00e5n/n. Renten beregnes p\u00e5 gjenstende gjeld \u2192 synker. Terminbel\u00f8pet er h\u00f8yest i starten, synker over tid.\n\nEksempel: 600 000 kr, 6 %, 3 \u00e5r:\n- Avdrag = 200 000/\u00e5r (konstant)\n- \u00c5r 1: Rente=36 000, PMT=236 000\n- \u00c5r 2: Rente=24 000, PMT=224 000\n- \u00c5r 3: Rente=12 000, PMT=212 000\nTotal rente: 72 000 kr (lavere enn annuitet).\n\nTips: L\u00f8s seriel\u00e5n med tabell \u2014 Restgjeld, Rente, Avdrag, Terminbel\u00f8p per termin.",
             "formula":"Avdrag = L\u00e5n / n\nRente = Restgjeld \u00d7 r",
             "tip":"Seriel\u00e5n l\u00f8ses best med tabell. Kolonner: Restgjeld \u2192 Rente \u2192 Avdrag \u2192 PMT.",
             "calc":"Manuelt: avdrag = l\u00e5n\u00f7n. Rente = restgjeld\u00d7r. PMT = avdrag+rente."},
        ]},
    "invest": {"title":"Investeringsanalyse",
        "intro":"Investeringsanalyse handler om \u00e5 verdsette selskaper gjennom diskontert kontantstr\u00f8m (DCF). Kjernen: estimer fri kontantstr\u00f8m (FCF), diskont\u00e9r med WACC. Terminalverdien dominerer vanligvis \u2014 70-80 % av total verdi.",
        "concepts":[
            {"name":"Fri kontantstr\u00f8m (FCF)",
             "text":"FCF = de faktiske pengene et selskap genererer etter drift og investeringer. Start ALLTID fra EBIT (ikke nettoresultat \u2014 det inkluderer renter som allerede er i WACC).\n\nStegene:\n1. EBIT \u00d7 (1\u2212T) = NOPAT \u2014 driftsresultat etter skatt\n2. + Avskrivninger \u2014 bokf\u00f8ring, ikke kontant. Legges tilbake.\n3. \u2212 CAPEX \u2014 faktiske investeringer i anleggsmidler\n4. \u2212 \u0394NWC \u2014 \u00f8kt arbeidskapital binder penger\n\nVanligste feil: Starte fra nettoresultat i stedet for EBIT. Nettoresultat inkluderer renter, men de er allerede i WACC \u2014 du teller dem dobbelt.",
             "formula":"FCF = EBIT \u00d7 (1\u2212T) + Avskr \u2212 CAPEX \u2212 \u0394NWC",
             "tip":"Start fra EBIT, ALDRI nettoresultat. Avskrivninger tilbake fordi de ikke er kontante.",
             "calc":"EBIT \u00d7 (1\u2212skattesats) + avskrivninger \u2212 CAPEX \u2212 \u0394NWC"},
            {"name":"Terminalverdi og DCF",
             "text":"DCF-modellen har to deler:\n1. Prognoseperiode (5-10 \u00e5r): Estimer FCF per \u00e5r, diskont\u00e9r med WACC\n2. Terminalverdi: Verdi av ALT etter prognosen (FCF vokser konstant med g)\n\nOverraskende: Terminalverdien utgj\u00f8r typisk 70-80 % av selskapsverdien! Det meste av verdien kommer fra perioden du IKKE har detaljerte prognoser for.\n\nDerfor er TV ekstremt sensitiv: Med FCF=100, g=2 %, WACC=10 %: TV=1 275. Endrer du WACC til 9 %: TV=1 457. \u00c9n prosentpoengs endring = 14 % verdiforskjell!\n\nSelskapsverdi = PV(prognose-FCF) + PV(terminalverdi)",
             "formula":"TV = FCF\u2099 \u00d7 (1+g) / (WACC \u2212 g)",
             "tip":"TV er SV\u00c6RT sensitiv for WACC og g. Sm\u00e5 endringer = store utslag i verdi.",
             "calc":"FCF siste \u00e5r \u00d7 (1+g) \u00f7 (WACC \u2212 g). Diskont\u00e9r tilbake til i dag."},
        ]},
}

# ─── SESSION STATE ───────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "points": 0, "sessions": 0, "studied": [], "sub_stats": {},
        "study_msgs": [], "chat_msgs": [],
        "sel_topic": None, "sel_sub": None, "sel_mode": 1, "api_key": "",
        "fv_idx": 0, "fv_score": 0, "fv_total": 0, "calc_idx": 0, "case_idx": 0,
        "learn_topic": None, "learn_sub": None,
        # Adaptiv: historikk per tema {topic_id: [{"date":iso,"correct":int,"total":int}]}
        "history": {},
        # Interleaving: smart økt state
        "smart_queue": [], "smart_idx": 0, "smart_score": 0, "smart_total": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── ADAPTIVE ENGINE ─────────────────────────────────────────────────────────

def get_difficulty(topic_id):
    """Returner adaptiv vanskelighetsgrad 1-3 basert på historikk"""
    stats = st.session_state.sub_stats
    topic_keys = [k for k in stats if k.startswith(f"{topic_id}::")]
    if not topic_keys:
        return 1  # Aldri øvd → lett
    total_c = sum(stats[k].get("correct", 0) for k in topic_keys)
    total_a = sum(stats[k].get("attempts", 0) for k in topic_keys)
    if total_a == 0:
        return 1
    acc = total_c / total_a
    if acc >= 0.8:
        return 3  # Mestrer → vanskelig
    elif acc >= 0.5:
        return 2  # Middels
    return 1  # Sliter → lett


def get_topic_accuracy(topic_id):
    stats = st.session_state.sub_stats
    keys = [k for k in stats if k.startswith(f"{topic_id}::")]
    if not keys:
        return None
    tc = sum(stats[k].get("correct", 0) for k in keys)
    ta = sum(stats[k].get("attempts", 0) for k in keys)
    return round(tc / ta * 100) if ta > 0 else None


def record_history(topic_id, correct, total):
    if topic_id not in st.session_state.history:
        st.session_state.history[topic_id] = []
    st.session_state.history[topic_id].append({
        "date": datetime.now().isoformat(), "correct": correct, "total": total
    })


def build_smart_queue():
    """Bygg interleaved oppgavekø basert på spaced repetition + adaptiv vanskelighet"""
    items = []
    for t in TOPICS:
        bank = QUESTION_BANK.get(t["id"], {})
        diff = get_difficulty(t["id"])
        flervalg = bank.get("flervalg", [])
        # Filtrer på vanskelighetsgrad (±1 nivå)
        suitable = [q for q in flervalg if abs(q.get("difficulty", 1) - diff) <= 1]
        if not suitable:
            suitable = flervalg
        for q in suitable:
            # Vekt: eksamensfrekvens × spaced rep score
            score = t["freq"] * 2
            acc = get_topic_accuracy(t["id"])
            if acc is None:
                score += 10  # Aldri øvd = høy prioritet
            elif acc < 50:
                score += 8  # Sliter = høy prioritet
            elif acc < 75:
                score += 4
            items.append((score + random.random()*3, t["id"], t["name"], q))
    items.sort(key=lambda x: -x[0])
    return items[:10]  # 10 spørsmål per smart økt


def spaced_rep_score(topic_id, subtopic):
    key = f"{topic_id}::{subtopic}"
    stat = st.session_state.sub_stats.get(key)
    if not stat:
        return 100
    days = (datetime.now() - datetime.fromisoformat(stat["last"])).days
    acc = stat["correct"] / max(1, stat["attempts"])
    return (1 - acc) * 60 + min(days, 10) * 4


def get_recommendations():
    items = []
    for t in TOPICS:
        for s in t["subs"]:
            items.append((spaced_rep_score(t["id"], s), t["id"], t["name"], s))
    items.sort(key=lambda x: -x[0])
    return items[:3]


def record_correct(tid=None, sub=None):
    tid = tid or st.session_state.sel_topic
    sub = sub or st.session_state.sel_sub
    if not tid or not sub: return
    key = f"{tid}::{sub}"
    old = st.session_state.sub_stats.get(key, {"correct":0,"attempts":0,"last":None})
    st.session_state.sub_stats[key] = {"correct":old["correct"]+1,"attempts":old["attempts"]+1,"last":datetime.now().isoformat()}


def record_attempt(tid=None, sub=None):
    tid = tid or st.session_state.sel_topic
    sub = sub or st.session_state.sel_sub
    if not tid or not sub: return
    key = f"{tid}::{sub}"
    old = st.session_state.sub_stats.get(key, {"correct":0,"attempts":0,"last":None})
    st.session_state.sub_stats[key] = {"correct":old["correct"],"attempts":old["attempts"]+1,"last":datetime.now().isoformat()}

# ─── AI & HELPERS ────────────────────────────────────────────────────────────

def get_client():
    key = ""
    try: key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except: pass
    if not key: key = st.session_state.get("api_key", "")
    return anthropic.Anthropic(api_key=key) if key else None

def call_ai(client, messages, system):
    return client.messages.create(model="claude-sonnet-4-6", max_tokens=1200, system=system, messages=messages).content[0].text

def stars(f): return "★"*f + "☆"*(5-f)
def topic_by_id(tid):
    for t in TOPICS:
        if t["id"] == tid: return t

def days_left():
    return (date(2026, 6, 1) - date.today()).days

def study_phase():
    d = days_left()
    if d > 42: return "build", "Bygg forståelse 📖", "#22c55e"
    elif d > 21: return "mix", "Blandet øving 📐", "#eab308"
    elif d > 7: return "repeat", "Repetisjon ⏩", "#f97316"
    return "intense", "INTENSIV 🔥", "#ef4444"

def solve_tvm(n, iyr, pv, pmt, fv):
    unknowns = sum(1 for x in [n, iyr, pv, pmt, fv] if x is None)
    if unknowns != 1: return {"error": "Nøyaktig ett felt tomt."}
    r = iyr/100 if iyr is not None else None
    try:
        if fv is None:
            if r==0: return {"var":"FV","value":-pv-pmt*n}
            return {"var":"FV","value":-pv*(1+r)**n-pmt*(((1+r)**n-1)/r)}
        if pv is None:
            if r==0: return {"var":"PV","value":-fv-pmt*n}
            return {"var":"PV","value":(-fv-pmt*(((1+r)**n-1)/r))/(1+r)**n}
        if pmt is None:
            if r==0: return {"var":"PMT","value":-(fv+pv)/n}
            return {"var":"PMT","value":-(fv+pv*(1+r)**n)*r/((1+r)**n-1)}
        if n is None:
            if r==0: return {"var":"N","value":-(fv+pv)/pmt} if pmt!=0 else {"error":"Umulig"}
            num,den = pmt/r-fv, pv+pmt/r
            if num<=0 or den<=0: return {"error":"Ingen løsning."}
            return {"var":"N","value":math.log(num/den)/math.log(1+r)}
        if iyr is None:
            rg = 0.1
            for _ in range(300):
                if rg==0: rg=0.001
                f = (1+rg)**n
                fv2 = pv*f + pmt*(f-1)/rg + fv
                df = n*(1+rg)**(n-1)
                dfv = pv*df + pmt*(df*rg-(f-1))/(rg**2)
                if abs(dfv)<1e-20: break
                rn = rg - fv2/dfv
                if abs(rn-rg)<1e-10: rg=rn; break
                rg = rn
            return {"var":"I/YR","value":rg*100}
    except Exception as e: return {"error":str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════

# Global progress strip (always visible)
studied_pct = len(st.session_state.studied) / 7
pct_color = "#22c55e" if studied_pct > 0.7 else "#f59e0b" if studied_pct > 0.3 else "#ef4444"
st.markdown(f'<div class="top-progress"><div class="top-progress-fill" style="width:{studied_pct*100}%;background:{pct_color};"></div></div>', unsafe_allow_html=True)

tabs = st.tabs(["Hjem", "Lær", "Oppgaver", "Smart økt", "AI-trener", "Formler", "Chat", "Fremgang", "Kalkulator"])

# ─── HJEM ────────────────────────────────────────────────────────────────────

with tabs[0]:
    dl = days_left()
    phase, phase_label, phase_color = study_phase()

    st.markdown(f'<div class="days-number">{dl}</div>', unsafe_allow_html=True)
    st.markdown('<div class="days-label">dager til eksamen · 1. juni 2026</div>', unsafe_allow_html=True)
    st.markdown("")
    st.markdown(f'<span class="phase-tag" style="background:{phase_color}22;color:{phase_color};">{phase_label}</span>', unsafe_allow_html=True)

    # Fase-spesifikke anbefalinger (prinsipp 10)
    if phase == "build":
        st.caption("Fokus: Forstå konseptene. Bruk Lær-fanen og AI-treneren med «Forklar tilbake».")
    elif phase == "mix":
        st.caption("Fokus: Bland temaer! Bruk Smart økt for interleaving. Beregningsoppgaver med kalkulator.")
    elif phase == "repeat":
        st.caption("Fokus: Repeter svake temaer. Eksamensimulering. Flervalg under tidspress.")
    else:
        st.caption("SISTE UKE: Kun eksamensimulering og formler. Du kan dette!")

    st.markdown("")
    c1, c2 = st.columns(2)
    with c1: st.progress(len(st.session_state.studied)/7, text=f"{len(st.session_state.studied)}/7 temaer")
    with c2: st.metric("Poeng ⚡", st.session_state.points)

    st.markdown("### Anbefalt i dag")
    for i, (sc, tid, tn, sub) in enumerate(get_recommendations()):
        key = f"{tid}::{sub}"
        stat = st.session_state.sub_stats.get(key)
        cols = ["#ef4444","#f59e0b","#eab308"]
        if stat and stat["attempts"]>0:
            acc = round(stat["correct"]/stat["attempts"]*100)
            ac = "#22c55e" if acc>=70 else "#eab308" if acc>=40 else "#ef4444"
            at = f'<span style="color:{ac}">{acc}%</span>'
        else:
            at = '<span style="color:#94a3b8">Ikke øvd</span>'
        st.markdown(f'<div class="topic-item" style="border-left:4px solid {cols[i]};"><span style="color:{cols[i]};font-weight:bold;">#{i+1}</span> <strong>{sub}</strong> <span style="color:#94a3b8;font-size:13px;">— {tn}</span><span style="float:right;">{at}</span></div>', unsafe_allow_html=True)

    try:
        if not st.secrets.get("ANTHROPIC_API_KEY", ""):
            raise Exception()
    except:
        with st.expander("🔑 API-nøkkel"):
            k = st.text_input("Anthropic API-nøkkel", type="password")
            if k: st.session_state["api_key"] = k; st.success("Lagret!")

# ─── LÆR ────────────────────────────────────────────────────────────────────

with tabs[1]:
    st.markdown("## Lær")

    # Tema og undertema som kaskade-dropdowns
    topic_names = [t["name"] for t in TOPICS]
    learn_sel = st.selectbox("Tema", topic_names, key="learn_tema_sel", index=0)
    learn_tid = next(t["id"] for t in TOPICS if t["name"] == learn_sel)
    learn_topic_obj = topic_by_id(learn_tid)

    sub_options = ["Alle konsepter"] + learn_topic_obj["subs"]
    learn_sub_sel = st.selectbox("Undertema", sub_options, key="learn_sub_sel", index=0)
    st.session_state.learn_topic = learn_tid
    st.session_state.learn_sub = learn_sub_sel if learn_sub_sel != "Alle konsepter" else None

    topic = learn_topic_obj
    tid = learn_tid
    st.markdown("---")

    content = LEARN.get(tid)
    if content:
        st.markdown(f"## {content['title']}")
        st.markdown(f"*{content['intro']}*")
        # Charts with explanatory text
        for chart_item in CHARTS.get(tid, []):
            cfn, explanation = chart_item
            st.plotly_chart(cfn(), use_container_width=True)
            st.markdown(f'<p style="color:#a1a1aa; font-size:0.9rem; line-height:1.6; margin-top:-0.5rem; margin-bottom:2rem;">{explanation}</p>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Nøkkelkonsepter")
        concepts = content["concepts"]
        if st.session_state.learn_sub:
            sub_lower = st.session_state.learn_sub.lower()
            filtered = [c for c in concepts if sub_lower in c["name"].lower() or sub_lower in c["text"].lower()]
            if filtered:
                concepts = filtered
        for i, c in enumerate(concepts):
            with st.expander(f"{i+1}. {c['name']}", expanded=(i == 0)):
                st.markdown(c["text"])
                st.markdown(f'<div class="formula-block" style="border-left:3px solid #3b82f6;"><div class="formula-label">FORMEL</div><div class="formula-text">{c["formula"]}</div></div>', unsafe_allow_html=True)
                if c.get("calc"):
                    st.markdown(f'<div class="calc-step">HP 10bII+: {c["calc"]}</div>', unsafe_allow_html=True)
                st.info(f"💡 {c['tip']}")
        # Mini-quiz
        st.markdown("---")
        st.markdown("### Test deg selv")
        bank = QUESTION_BANK.get(tid, {}).get("flervalg", [])
        if bank:
            qk = f"lq_{tid}"
            if qk not in st.session_state:
                st.session_state[qk] = random.sample(range(len(bank)), min(2, len(bank)))
            for qi in st.session_state[qk]:
                q = bank[qi]
                st.markdown(f"**{q['q']}**")
                sel = st.radio("Svar:", q["choices"], key=f"lr_{tid}_{qi}", index=None)
                if sel:
                    idx = q["choices"].index(sel)
                    if idx == q["answer"]:
                        st.markdown(f'<div class="feedback-correct">✅ {q["explanation"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="feedback-wrong">❌ {q["misconception"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="feedback-insight">💡 Intuisjon: {q["intuition"]}</div>', unsafe_allow_html=True)
                    if q.get("calc_steps"):
                        st.markdown(f'<div class="calc-step">HP 10bII+: {q["calc_steps"]}</div>', unsafe_allow_html=True)
                st.markdown("")
            if st.button("🔄 Nye spørsmål", key=f"ln_{tid}"):
                st.session_state[qk] = random.sample(range(len(bank)), min(2, len(bank))); st.rerun()

# ─── OPPGAVER ────────────────────────────────────────────────────────────────

with tabs[2]:
    st.markdown("## Oppgaver")
    tc1, tc2 = st.columns(2)
    with tc1: test_topic = st.selectbox("Tema", [t["name"] for t in TOPICS], key="test_sel")
    with tc2: test_type = st.selectbox("Type", ["Flervalg", "Beregning", "Case"], key="type_sel")
    test_tid = next(t["id"] for t in TOPICS if t["name"] == test_topic)
    diff = get_difficulty(test_tid)
    st.caption(f"Adaptiv vanskelighetsgrad: {'⭐'*diff} (basert på din historikk)")
    bank = QUESTION_BANK.get(test_tid, {})
    tmap = {"Flervalg":"flervalg","Beregning":"beregning","Case":"case"}
    qs = bank.get(tmap[test_type], [])

    if not qs:
        st.info("Ingen oppgaver her ennå. Prøv AI-treneren!")
    elif test_type == "Flervalg":
        # Filtrer på vanskelighetsgrad
        suitable = [q for q in qs if abs(q.get("difficulty",1)-diff)<=1]
        if not suitable: suitable = qs
        if "fv_order" not in st.session_state or len(st.session_state.fv_order) != len(suitable):
            st.session_state.fv_order = list(range(len(suitable))); random.shuffle(st.session_state.fv_order)
        if st.session_state.fv_total > 0:
            st.markdown(f"Score: **{st.session_state.fv_score}/{st.session_state.fv_total}**")
        if st.session_state.fv_idx < len(suitable):
            qi = st.session_state.fv_order[st.session_state.fv_idx % len(suitable)]
            q = suitable[qi]
            st.markdown(f"##### Spørsmål {st.session_state.fv_idx+1} <span class='micro-badge' style='background:#3b82f622;color:#3b82f6;'>{'⭐'*q.get('difficulty',1)}</span>", unsafe_allow_html=True)
            st.markdown(f"**{q['q']}**")
            for ci, ch in enumerate(q["choices"]):
                if st.button(ch, key=f"fvc_{ci}", use_container_width=True):
                    st.session_state.fv_total += 1
                    if ci == q["answer"]: st.session_state.fv_score += 1; st.session_state.points += 15
                    st.session_state["_fv"] = {"ci":ci,"ans":q["answer"],"exp":q["explanation"],"mis":q.get("misconception",""),"int":q.get("intuition",""),"f":q["formula"],"calc":q.get("calc_steps","")}
                    st.rerun()
            if "_fv" in st.session_state:
                fv = st.session_state["_fv"]
                if fv["ci"] == fv["ans"]:
                    st.markdown(f'<div class="feedback-correct">✅ {fv["exp"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="feedback-wrong">❌ {fv["mis"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="feedback-insight">💡 {fv["int"]}</div>', unsafe_allow_html=True)
                if fv["calc"]:
                    st.markdown(f'<div class="calc-step">HP 10bII+: {fv["calc"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="formula-block"><div class="formula-text">{fv["f"]}</div></div>', unsafe_allow_html=True)
                if st.button("➡️ Neste", use_container_width=True):
                    st.session_state.fv_idx += 1; st.session_state.pop("_fv",None); st.rerun()
        else:
            pct = round(st.session_state.fv_score/max(1,st.session_state.fv_total)*100)
            record_history(test_tid, st.session_state.fv_score, st.session_state.fv_total)
            st.success(f"Ferdig! {st.session_state.fv_score}/{st.session_state.fv_total} ({pct}%)")
            if pct >= 80: st.balloons()
            if st.button("🔄 Igjen"):
                st.session_state.fv_idx=0; st.session_state.fv_score=0; st.session_state.fv_total=0; st.rerun()

    elif test_type == "Beregning":
        if st.session_state.calc_idx < len(qs):
            q = qs[st.session_state.calc_idx]
            st.markdown(f"##### Oppgave {st.session_state.calc_idx+1}")
            st.markdown(q["q"])
            st.markdown(f'<div class="formula-block"><div class="formula-label">Formel</div><div class="formula-text">{q["formula"]}</div></div>', unsafe_allow_html=True)
            ua = st.number_input("Ditt svar:", key=f"ci_{st.session_state.calc_idx}", value=None, placeholder="Skriv inn...")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ Sjekk", use_container_width=True) and ua is not None:
                    st.session_state[f"_cr{st.session_state.calc_idx}"] = "ok" if abs(ua-q["answer"])<=q["tolerance"] else "no"
                    if abs(ua-q["answer"])<=q["tolerance"]: st.session_state.points+=15
                    st.rerun()
            with b2:
                if st.button("💡 Løsning", use_container_width=True):
                    st.session_state[f"_cr{st.session_state.calc_idx}"] = "show"; st.rerun()
            rk = f"_cr{st.session_state.calc_idx}"
            if rk in st.session_state:
                if st.session_state[rk] == "ok":
                    st.markdown(f'<div class="feedback-correct">✅ Riktig! {q["answer"]:,.0f}</div>', unsafe_allow_html=True)
                elif st.session_state[rk] == "no":
                    st.markdown(f'<div class="feedback-wrong">❌ Riktig svar: {q["answer"]:,.0f}</div>', unsafe_allow_html=True)
                    if q.get("common_mistake"):
                        st.markdown(f'<div class="feedback-insight">⚠️ {q["common_mistake"]}</div>', unsafe_allow_html=True)
                for s in q["steps"]:
                    st.markdown(f'<div class="solve-step">{s}</div>', unsafe_allow_html=True)
                if q.get("calc_steps"):
                    st.markdown("**HP 10bII+ tastetrykk:**")
                    for cs in q["calc_steps"]:
                        st.markdown(f'<div class="calc-step">{cs}</div>', unsafe_allow_html=True)
                if st.button("➡️ Neste", key="cn"):
                    st.session_state.calc_idx += 1; st.rerun()
        else:
            st.success("Alle oppgaver fullført!")
            if st.button("🔄 Igjen", key="cr"): st.session_state.calc_idx=0; st.rerun()

    elif test_type == "Case":
        if not qs:
            st.info("Ingen case-oppgaver.")
        else:
            case = qs[st.session_state.case_idx % len(qs)]
            st.markdown("##### Case — Eksamensformat")
            st.markdown(case["scenario"])
            st.markdown("---")
            for qi, cq in enumerate(case["questions"]):
                st.markdown(f"**{cq['q']}**")
                st.text_area("Ditt svar:", key=f"ca_{st.session_state.case_idx}_{qi}", height=80)
                rk = f"_cs{st.session_state.case_idx}_{qi}"
                if st.button(f"💡 Fasit {qi+1}", key=f"cb_{qi}"):
                    st.session_state[rk] = True; st.rerun()
                if st.session_state.get(rk):
                    st.markdown(f'<div class="feedback-correct">{cq["answer"]}</div>', unsafe_allow_html=True)
                st.markdown("")
            if st.button("➡️ Neste case", key="cnc"):
                st.session_state.case_idx += 1; st.rerun()

# ─── SMART ØKT (Interleaving + Adaptiv) ─────────────────────────────────────

with tabs[3]:
    st.markdown("### 🧠 Smart økt — Interleaved trening")
    st.caption("Blander temaer bevisst for bedre langtidshukommelse. Tilpasser seg ditt nivå.")

    phase_id, _, _ = study_phase()
    if phase_id == "build":
        st.info("📖 Fokus nå: Forstå konseptene først (Lær-fanen). Smart økt er mest effektiv etter du har sett temaene.")

    if not st.session_state.smart_queue:
        est = "~5 min" if phase_id in ["repeat","intense"] else "~8 min"
        st.markdown(f"**10 spørsmål, blandet fra alle temaer.** Estimert tid: {est}")
        if st.button("▶ Start smart økt", type="primary", use_container_width=True):
            st.session_state.smart_queue = build_smart_queue()
            st.session_state.smart_idx = 0; st.session_state.smart_score = 0; st.session_state.smart_total = 0
            st.rerun()
    else:
        queue = st.session_state.smart_queue
        idx = st.session_state.smart_idx
        if idx < len(queue):
            _, tid, tname, q = queue[idx]
            st.markdown(f"**{idx+1}/{len(queue)}** — <span style='color:#94a3b8'>{tname}</span>", unsafe_allow_html=True)
            st.progress((idx)/len(queue))
            st.markdown(f"**{q['q']}**")
            for ci, ch in enumerate(q["choices"]):
                if st.button(ch, key=f"sq_{ci}", use_container_width=True):
                    st.session_state.smart_total += 1
                    correct = ci == q["answer"]
                    if correct: st.session_state.smart_score += 1; st.session_state.points += 15
                    # Registrer i sub_stats
                    first_sub = topic_by_id(tid)["subs"][0]
                    if correct: record_correct(tid, first_sub)
                    else: record_attempt(tid, first_sub)
                    st.session_state["_sq"] = {"ci":ci,"ans":q["answer"],"exp":q["explanation"],"mis":q.get("misconception",""),"int":q.get("intuition",""),"calc":q.get("calc_steps",""),"f":q["formula"],"tid":tid,"tname":tname}
                    st.rerun()
            if "_sq" in st.session_state:
                sq = st.session_state["_sq"]
                if sq["ci"] == sq["ans"]:
                    st.markdown(f'<div class="feedback-correct">✅ {sq["exp"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="feedback-wrong">❌ {sq["mis"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="feedback-insight">💡 {sq["int"]}</div>', unsafe_allow_html=True)
                if sq["calc"]:
                    st.markdown(f'<div class="calc-step">HP 10bII+: {sq["calc"]}</div>', unsafe_allow_html=True)
                if st.button("➡️ Neste", key="sqn", use_container_width=True):
                    st.session_state.smart_idx += 1; st.session_state.pop("_sq",None); st.rerun()
        else:
            pct = round(st.session_state.smart_score/max(1,st.session_state.smart_total)*100)
            st.markdown(f'<div class="result-display">{st.session_state.smart_score}/{st.session_state.smart_total} — {pct}%</div>', unsafe_allow_html=True)
            # Vis svake temaer
            topic_results = {}
            for _, tid, tname, q in queue:
                if tid not in topic_results: topic_results[tid] = {"name":tname,"c":0,"t":0}
                topic_results[tid]["t"] += 1
            st.markdown("**Per tema:**")
            for tid, r in topic_results.items():
                acc = get_topic_accuracy(tid)
                ac = "#22c55e" if acc and acc>=70 else "#ef4444" if acc and acc<50 else "#eab308"
                st.markdown(f'<span style="color:{ac}">{"●"}</span> {r["name"]} — {acc or "?"}%', unsafe_allow_html=True)
            if st.button("🔄 Ny smart økt", use_container_width=True):
                st.session_state.smart_queue = []; st.session_state.pop("_sq",None); st.rerun()

# ─── AI-TRENER ───────────────────────────────────────────────────────────────

with tabs[4]:
    st.markdown("## AI-trener")

    # Tema, undertema og modus som dropdowns
    ai_c1, ai_c2 = st.columns(2)
    with ai_c1:
        ai_topic_sel = st.selectbox("Tema", [t["name"] for t in TOPICS], key="ai_tema_sel")
    ai_tid = next(t["id"] for t in TOPICS if t["name"] == ai_topic_sel)
    ai_topic_obj = topic_by_id(ai_tid)
    st.session_state.sel_topic = ai_tid

    with ai_c2:
        ai_sub_opts = ["Velges av AI"] + ai_topic_obj["subs"]
        ai_sub_sel = st.selectbox("Undertema", ai_sub_opts, key="ai_sub_sel")
    st.session_state.sel_sub = ai_sub_sel if ai_sub_sel != "Velges av AI" else None

    mode_labels = [f"{m['icon']} {m['name']} ({m['time']})" for m in MODES]
    mode_sel = st.selectbox("Modus", mode_labels, key="ai_mode_sel")
    sel_mode_idx = mode_labels.index(mode_sel)
    st.session_state.sel_mode = MODES[sel_mode_idx]["id"]
    if st.session_state.sel_topic:
        topic = topic_by_id(st.session_state.sel_topic)
        mode = next(m for m in MODES if m["id"]==st.session_state.sel_mode)
        diff = get_difficulty(topic["id"])
        diff_label = ["Grunnleggende","Middels","Avansert"][diff-1]
        st.caption(f"Adaptiv vanskelighetsgrad: {diff_label} ({'⭐'*diff})")
        if st.button(f"▶ Start {mode['name']} — {topic['name']}", type="primary", use_container_width=True):
            client = get_client()
            if not client:
                st.warning("Legg inn API-nøkkel på Hjem-fanen.")
            else:
                st.session_state.sessions += 1; st.session_state.points += 10
                if topic["id"] not in st.session_state.studied: st.session_state.studied.append(topic["id"])
                sub = f", undertema: {st.session_state.sel_sub}" if st.session_state.sel_sub else ""
                diff_instr = f"Studentens nivå: {diff_label}. " + ("Bruk enkle tall og ett steg om gangen." if diff==1 else "Bruk realistiske eksamenstall." if diff==2 else "Bruk komplekse oppgaver med flere steg og tidspress.")
                user_msg = f"{mode['instr']} {diff_instr} Tema: {topic['name']}{sub}. Start nå."
                st.session_state.study_msgs = [{"role":"user","content":user_msg}]
                system = f"""Du er eksamenstutor for BØK 3423 Finans ved BI. Svar ALLTID på norsk.

PEDAGOGISKE REGLER:
1. Gi ALDRI fasit før studenten har prøvd — still spørsmål, vent, evaluer.
2. Forklar ALLTID intuisjonen (HVORFOR) før formelen (HVORDAN).
3. Ved feil: forklar nøyaktig hva studenten misforsto, ikke bare si "feil".
4. Vis HP 10bII+ tastetrykk for alle beregninger.
5. Bruk eksamensformat: tabeller, realistiske tall, BI-språk.
6. Avslutt alltid med ett konkret spørsmål til studenten.
7. Riktig svar: «Riktig — og dette er akkurat det eksamen tester. [kort forklaring av hvorfor]»
8. Feil svar: «Nesten — de fleste gjør denne feilen fordi [konkret årsak]. Prøv igjen med dette hintet: [hint]»"""
                with st.spinner("Henter oppgave..."):
                    try:
                        reply = call_ai(client, st.session_state.study_msgs, system)
                        st.session_state.study_msgs.append({"role":"assistant","content":reply})
                    except Exception as e: st.error(f"API-feil: {e}")
                st.rerun()
    if st.session_state.study_msgs:
        for msg in st.session_state.study_msgs[1:]:
            cls = "msg-ai" if msg["role"]=="assistant" else "msg-user"
            st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

        sys = """Du er eksamenstutor for BØK 3423 Finans ved BI. Svar ALLTID på norsk. Gi aldri fasit direkte. Forklar intuisjon først. Vis HP 10bII+ tastetrykk. Behandle feil som læringsmomenter. Avslutt med neste spørsmål."""
        def ai_send(msg, bonus=0):
            st.session_state.points += bonus
            st.session_state.study_msgs.append({"role":"user","content":msg})
            client = get_client()
            if client:
                try:
                    reply = call_ai(client, st.session_state.study_msgs, sys)
                    st.session_state.study_msgs.append({"role":"assistant","content":reply})
                except Exception as e: st.error(f"API-feil: {e}")
            st.rerun()

        # Svarknapper A/B/C/D — klikk i stedet for å skrive
        st.markdown('<p class="meta">Velg svar:</p>', unsafe_allow_html=True)
        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            if st.button("A", key="ai_a", use_container_width=True): ai_send("A", 3)
        with ac2:
            if st.button("B", key="ai_b", use_container_width=True): ai_send("B", 3)
        with ac3:
            if st.button("C", key="ai_c", use_container_width=True): ai_send("C", 3)
        with ac4:
            if st.button("D", key="ai_d", use_container_width=True): ai_send("D", 3)

        # Verktøyknapper
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            if st.button("✅ Riktig +15", use_container_width=True): record_correct(); ai_send("Jeg svarte riktig.", 15)
        with q2:
            if st.button("❓ Hint", use_container_width=True): ai_send("Gi meg et hint — men ikke svaret.")
        with q3:
            if st.button("⏭ Ny oppgave", use_container_width=True): record_attempt(); ai_send("Ny oppgave, gjerne annet undertema.", 5)
        with q4:
            if st.button("💡 Forklar", use_container_width=True): ai_send("Forklar løsningen grundig med intuisjon og kalkulatorsteg.")

        # Fritekst for beregningsoppgaver og lengre svar
        ui = st.chat_input("Skriv svar eller tall...")
        if ui: ai_send(ui, 3)
        if st.button("🔄 Nullstill"): st.session_state.study_msgs = []; st.rerun()

# ─── FORMLER ─────────────────────────────────────────────────────────────────

with tabs[5]:
    st.markdown("### 📐 Formelsamling")
    search = st.text_input("Søk...", placeholder="NPV, CAPM, annuitet")
    for g in ALL_FORMULAS:
        sl = search.lower() if search else ""
        ms = [(f,e,n) for f,e,n in g["formulas"] if not search or any(sl in x.lower() for x in [f,e,n,g["group"]])]
        if ms:
            st.markdown(f'<h4 style="color:{g["color"]};margin-top:1.5rem;">{g["group"]}</h4>', unsafe_allow_html=True)
            for f,e,n in ms:
                st.markdown(f'<div class="formula-block" style="border-left:3px solid {g["color"]};"><div class="formula-label">{f}</div><div class="formula-text">{e}</div><div class="formula-note">{n}</div></div>', unsafe_allow_html=True)

# ─── CHAT ────────────────────────────────────────────────────────────────────

with tabs[6]:
    st.markdown("### 💬 Fri chat")
    CS = "Du er finanstutor for BØK 3423 Finans (BI). Norsk. Direkte. Bruk formler, eksempler og HP 10bII+ tastetrykk."
    if not st.session_state.chat_msgs:
        for idx, sug in enumerate(["Forklar CAPM","IRR vs NPV?","WACC steg for steg","Gordon Growth?","MM med/uten skatt","Sharpe vs beta"]):
            if idx%3==0: sc = st.columns(3)
            with sc[idx%3]:
                if st.button(sug, key=f"sg_{idx}", use_container_width=True):
                    st.session_state.chat_msgs.append({"role":"user","content":sug})
                    c = get_client()
                    if c:
                        try: st.session_state.chat_msgs.append({"role":"assistant","content":call_ai(c, st.session_state.chat_msgs, CS)})
                        except Exception as e: st.error(str(e))
                    st.rerun()
    for msg in st.session_state.chat_msgs:
        with st.chat_message("human" if msg["role"]=="user" else "ai"): st.markdown(msg["content"])
    ci = st.chat_input("Spør...")
    if ci:
        st.session_state.chat_msgs.append({"role":"user","content":ci})
        c = get_client()
        if c:
            try: st.session_state.chat_msgs.append({"role":"assistant","content":call_ai(c, st.session_state.chat_msgs, CS)})
            except Exception as e: st.error(str(e))
        st.rerun()
    if st.session_state.chat_msgs and st.button("🗑 Tøm"): st.session_state.chat_msgs=[]; st.rerun()

# ─── FREMGANG (Motiverende, viser forbedring) ───────────────────────────────

with tabs[7]:
    st.markdown("### 📊 Fremgang")
    m1,m2,m3 = st.columns(3)
    dl = days_left()
    with m1: st.metric("Poeng ⚡", st.session_state.points)
    with m2: st.metric("��kter 📚", st.session_state.sessions)
    with m3: st.metric("Dager 📅", dl, delta=f"-{dl}" if dl<=14 else None, delta_color="inverse")

    st.markdown("---")
    st.markdown("### Temaer — din utvikling")
    for t in TOPICS:
        acc = get_topic_accuracy(t["id"])
        subs = t["subs"]
        done = [s for s in subs if f"{t['id']}::{s}" in st.session_state.sub_stats]
        ca, cb = st.columns([4, 1])
        with ca:
            st.progress(len(done)/len(subs), text=f"{t['name']} ({len(done)}/{len(subs)})")
        with cb:
            if acc is not None:
                ac = "#22c55e" if acc>=70 else "#eab308" if acc>=40 else "#ef4444"
                st.markdown(f'<span style="color:{ac};font-weight:bold;">{acc}%</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#94a3b8">—</span>', unsafe_allow_html=True)

    # Historisk forbedring
    hist = st.session_state.history
    if hist:
        st.markdown("---")
        st.markdown("### 📈 Forbedring over tid")
        for tid, entries in hist.items():
            tname = topic_by_id(tid)["name"] if topic_by_id(tid) else tid
            if len(entries) >= 2:
                first_acc = round(entries[0]["correct"]/max(1,entries[0]["total"])*100)
                last_acc = round(entries[-1]["correct"]/max(1,entries[-1]["total"])*100)
                diff = last_acc - first_acc
                if diff > 0:
                    st.markdown(f'<div class="feedback-correct">📈 <strong>{tname}:</strong> {first_acc}% → {last_acc}% (+{diff}pp)</div>', unsafe_allow_html=True)
                elif diff < 0:
                    st.markdown(f'<div class="feedback-wrong">📉 <strong>{tname}:</strong> {first_acc}% → {last_acc}% ({diff}pp) — øv mer!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="topic-item">{tname}: Stabilt {last_acc}%</div>', unsafe_allow_html=True)

# ─── KALKULATOR ──────────────────────────────────────────────────────────────

with tabs[8]:
    st.markdown("### 🔢 HP 10bII+ Kalkulator")
    st.caption("La feltet stå tomt for ukjent.")
    with st.form("tvm"):
        f1,f2,f3,f4,f5 = st.columns(5)
        with f1: nv=st.text_input("N",placeholder="?")
        with f2: iv=st.text_input("I/YR%",placeholder="?")
        with f3: pvv=st.text_input("PV",placeholder="?")
        with f4: pmtv=st.text_input("PMT",placeholder="?")
        with f5: fvv=st.text_input("FV",placeholder="?")
        sub = st.form_submit_button("▶ Beregn", use_container_width=True)
    if sub:
        def pv(v):
            v=v.strip().replace(",",".").replace(" ","")
            return float(v) if v else None
        try: result = solve_tvm(pv(nv),pv(iv),pv(pvv),pv(pmtv),pv(fvv))
        except ValueError: result = {"error":"Ugyldig tall."}
        if "error" in result: st.error(result["error"])
        else:
            fmt = f"{result['value']:,.2f}".replace(","," ").replace(".",",")
            st.markdown(f'<div class="result-display">{result["var"]} = {fmt}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Eksempler:**")
    st.code("Annuitet: N=3, I/YR=6, PV=300000, FV=0 → PMT = −112 297")
    st.code("YTM: N=4, PV=−932255, PMT=50000, FV=1000000 → I/YR = ?")
    st.info("Negativ = utbetaling fra deg. Positiv = innbetaling.")
