# YT SEO Insights Generator

> AI-powered YouTube SEO analysis — tags, audience profiling, chapter timestamps, and flaw detection in a single pipeline.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.3--70b-orange)](https://groq.com/)
[![MLflow](https://img.shields.io/badge/Tracking-MLflow-blue?logo=mlflow)](https://mlflow.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)](https://streamlit.io/)
[![Colab](https://img.shields.io/badge/Run%20on-Google%20Colab-yellow?logo=googlecolab)](https://colab.research.google.com/)

---

## Overview

**YT SEO Insights Generator** takes any public YouTube URL and returns a structured set of SEO recommendations powered by **Groq's `llama-3.3-70b-versatile`** model. It scrapes video metadata directly from the YouTube page (no YouTube Data API key required), feeds it into an LLM, and produces:

| Output | Description |
|---|---|
| **Tags** | 35 SEO-optimised hashtags |
| **Audience** | Target audience analysis paragraph |
| **Timestamps** | AI-generated chapter markers scaled to video length |
| **Flaws** | 2–3 identified SEO issues with actionable fixes |

All runs are tracked with **MLflow** and the results are exportable as text files or a zip archive. An optional **Streamlit web UI** can be launched via localtunnel directly from within the Colab session.

---

## Architecture

```
YouTube URL
    │
    ▼
VideoExtractor          ← scrapes og:title, viewCount, lengthSeconds, author
    │
    ▼
SEOEngine               ← builds structured prompt, calls Groq API, parses JSON
    │
    ▼
MLflow Logger           ← logs params, metrics, and seo_results.json artifact
    │
    ▼
Output Files            ← seo_tags.txt | seo_timestamps.txt | seo_flaws.txt
    │
    ▼
Streamlit App (opt.)    ← full web UI exposed via localtunnel
```

---

## Tech Stack

| Component | Library / Service |
|---|---|
| LLM inference | [Groq](https://groq.com/) — `llama-3.3-70b-versatile` |
| Metadata scraping | `requests` + regex (no YouTube Data API) |
| Experiment tracking | [MLflow](https://mlflow.org/) |
| Web UI | [Streamlit](https://streamlit.io/) |
| Tunnel (Colab) | [localtunnel](https://theboroer.github.io/localtunnel-www/) |
| Logging | Python `logging` (file-based, timestamped sessions) |
| Runtime | Google Colab (Python 3.10) |

---

## Quick Start

### 1. Open in Google Colab

Upload `YT_SEO_Insights_Generator.ipynb` to [colab.research.google.com](https://colab.research.google.com) or open it directly from your repository.

### 2. Add Secrets

In the Colab left sidebar, click the **lock icon (Secrets)** and add:

| Secret Name | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key — get one free at [console.groq.com](https://console.groq.com) |
| `NGROK_AUTHTOKEN` | *(Optional)* Only needed if you prefer ngrok over localtunnel |

### 3. Run All Cells

Execute cells in order (1 → 12). Cell 9 runs the full pipeline; Cell 11 launches the Streamlit UI.

```
Runtime → Run all  (Ctrl + F9)
```

### 4. Provide a YouTube URL

In **Cell 9**, replace the placeholder with any public YouTube video URL:

```python
YOUTUBE_URL = 'https://www.youtube.com/watch?v=YOUR_VIDEO_ID'
```

---

## Supported URL Formats

```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID
```

---

## Project Structure

```
YT_SEO_Insights_Generator.ipynb   ← single-notebook project (all cells inline)
│
├── Cell 1   config.py            Project paths, audio/image settings, MLflow name
├── Cell 2   install              pip install of all runtime dependencies
├── Cell 3   secrets              GROQ_API_KEY loaded from Colab Secrets
├── Cell 4   logger.py            File-based logger → logs/<timestamp>.log
├── Cell 5   custom_exception.py  Enriches exceptions with file + line info
├── Cell 6   video_extractor.py   YouTube metadata scraper (no API key)
├── Cell 7   seo_engine.py        Groq LLM prompt builder, caller, and JSON parser
├── Cell 8   mlflow_tracker.py    Experiment logging — params, metrics, artifact
├── Cell 9   pipeline             End-to-end run: scrape → generate → log → display
├── Cell 10  save_outputs         Write tags / timestamps / flaws to OUTPUT_DIR
├── Cell 11  streamlit_app.py     Optional Streamlit UI via localtunnel
└── Cell 12  download             Zip OUTPUT_DIR and trigger browser download
```

---

## Output Files

All files are written to `/content/output/` and available for download via Cell 12.

| File | Contents |
|---|---|
| `seo_results.json` | Full structured JSON output (also logged to MLflow) |
| `seo_tags.txt` | 35 hashtags, space-separated, ready to paste into YouTube |
| `seo_timestamps.txt` | Chapter list formatted for a YouTube description |
| `seo_flaws.txt` | Flaw report — issue, impact, and fix for each identified problem |
| `yt_seo_outputs.zip` | Archive of all the above |

---

## MLflow Experiment Tracking

Each pipeline run logs the following to a local MLflow store at `OUTPUT_DIR/mlruns`:

**Parameters**
- `video_title`, `platform`, `duration_sec`, `author`

**Metrics**
- `tag_count`, `timestamp_count`, `flaw_count`

**Artifact**
- `seo_results.json`

The experiment name defaults to `youtube-mixtape-automation` and can be changed in Cell 1 via `MLFLOW_EXPERIMENT`.

---

## Streamlit Web UI (Cell 11)

Cell 11 writes `app.py` to disk, starts Streamlit on port `8501`, and exposes it publicly via **localtunnel** (no account required). After running the cell you will see output like:

```
Streamlit app live at: https://plain-dolls-make.loca.lt
If asked for a password, enter: 8.229.58.215
```

Open the URL in any browser. Enter your Groq API key in the sidebar, paste a YouTube URL, and click **Generate SEO Insights**.

---

## Configuration Reference

Key constants defined in **Cell 1**:

| Constant | Default | Description |
|---|---|---|
| `AUDIO_DIR` | `/content/audio` | Upload directory for audio tracks |
| `IMAGE_DIR` | `/content/images` | Upload directory for cover images |
| `OUTPUT_DIR` | `/content/output` | All generated output files |
| `TRANSITION_MS` | `6000` | Crossfade duration in milliseconds |
| `MIXTAPE_NAME` | `Afro House Summer Mix` | Display name for the mix |
| `GENRE` | `Afro House` | Genre tag used in prompts |
| `MLFLOW_EXPERIMENT` | `youtube-mixtape-automation` | MLflow experiment name |

---

## Error Handling

The project uses a project-wide `CustomException` class (Cell 5) that enriches every exception with the originating **file name** and **line number**, making deep call-stack failures easy to trace. All errors are also written to the session log file in `logs/`.

---

## Requirements

All dependencies are installed automatically by Cell 2. For reference:

```
streamlit
groq
python-dotenv
requests
mlflow
pyngrok        # (optional, if using ngrok instead of localtunnel)
```

---

## License

This project is released for personal and educational use. See `LICENSE` for details.

---

## Acknowledgements

- [Groq](https://groq.com/) for fast LLM inference
- [MLflow](https://mlflow.org/) for experiment tracking
- [Streamlit](https://streamlit.io/) for the web interface
- [localtunnel](https://theboroer.github.io/localtunnel-www/) for zero-config public tunnelling
