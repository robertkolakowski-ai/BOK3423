# BØK 3423 Finans — AI-drevet eksamenstrener

En AI-drevet eksamenstrener for faget **BØK 3423 Finans** ved BI Handelshøyskolen.
Bygget med Streamlit og Claude AI.

## Funksjoner

- **Øv** — 6 treningsmoduser (beregning, flervalg, feiljakten, forklar tilbake, lynquiz, eksamensimulering)
- **Lær** — Pensumoversikt med intuisjon, formler og eksamenstips for alle 7 temaer
- **Formler** — Søkbart formelark
- **Chat** — Fri chat med AI-tutor
- **Fremgang** — Spored repetisjon og statistikk
- **Kalkulator** — TVM-kalkulator (HP 10bII+ stil)

## Kjør lokalt

```bash
pip install -r requirements.txt
streamlit run app.py
```

Du trenger en Anthropic API-nøkkel. Legg den inn i appen under "API-nøkkel" på Hjem-fanen.

## Deploy til Streamlit Cloud

1. Push til GitHub
2. Gå til [share.streamlit.io](https://share.streamlit.io) → New app → velg repo og `app.py`
3. Under Settings → Secrets, legg inn:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Deploy — ferdig!

## Teknisk stack

- Python 3.11+
- Streamlit
- Anthropic Python SDK (Claude claude-sonnet-4-6)
