# 🎧 Automated YouTube Mixtape Creation

> An end-to-end multimedia automation pipeline that blends audio tracks into a smooth DJ-style mixtape, generates a YouTube-ready video, and produces a fully formatted description — all tracked with MLflow and persisted to MongoDB.

---

## 📌 Overview

This project automates the full workflow of creating and publishing a YouTube mixtape. Users provide raw audio tracks and a cover image; the system handles everything else — crossfade blending, video rendering, timestamped descriptions, experiment tracking, and artifact packaging.

It is built using a clean, modular architecture that mirrors real-world production systems, making it both educational and industry-relevant.

---

## 🗂️ Project Structure

```
Automated YouTube Mixtape Creation/
│
├── mixtape/
│   ├── __init__.py          # Package initializer
│   ├── config.py            # Path and format configuration
│   ├── audio.py             # Audio mixing with crossfade transitions
│   ├── video.py             # FFmpeg-based video generation
│   ├── description.py       # YouTube description with timestamps
│   ├── utils.py             # Job store and utility functions
│   └── main.py              # FastAPI backend (REST API)
│
├── streamlit_app.py         # Streamlit frontend UI
├── youtube_description.txt  # Sample generated description output
├── youtube_mixtape_automation_Final.ipynb  # Main project notebook
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Audio Processing | Pydub |
| Video Rendering | FFmpeg + Pillow |
| Experiment Tracking | MLflow + DagsHub |
| Database | MongoDB (via PyMongo) |
| Notebook Environment | Jupyter |

---

## 🔁 Pipeline Flow

```
Audio Tracks (.mp3 / .wav / .flac)
        │
        ▼
┌─────────────────────┐
│   Audio Mixing      │  ← Crossfade + Low-pass filter transitions
│   (audio.py)        │
└────────┬────────────┘
         │  mixtape.mp3
         ▼
┌─────────────────────┐
│  Description Gen    │  ← Timestamped tracklist + hashtags
│  (description.py)   │
└────────┬────────────┘
         │  youtube_description.txt
         ▼
┌─────────────────────┐
│   Video Creation    │  ← Still image looped over audio via FFmpeg
│   (video.py)        │
└────────┬────────────┘
         │  mixtape_vid.mp4
         ▼
┌─────────────────────┐
│  MLflow Tracking    │  ← Params, metrics, and all artifacts logged
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  MongoDB Persist    │  ← Full run metadata saved to DB
└────────┬────────────┘
         │
         ▼
    📦 ZIP Export
```

---

## 🧩 Module Breakdown

### `config.py`
Defines all base paths and allowed audio formats. Single source of truth for directory configuration across the project.

### `audio.py` — `smooth_fade_mixtape_from_files()`
Blends multiple audio files into a single MP3 using:
- Stereo normalization at 44.1 kHz
- Configurable crossfade duration (default 6000ms)
- Low-pass filter on transition segments for a smooth DJ-style blend

### `description.py` — `generate_youtube_description_with_timestamps()`
Generates a complete YouTube description including:
- Mixtape title and genre header
- Auto-calculated timestamps per track
- Download links section
- Relevant hashtags

### `video.py` — `make_video_from_audio()`
Creates a YouTube-ready MP4 by:
- Resizing the cover image to 1280×720
- Looping it as a still frame over the full audio duration
- Encoding with H.264 video and AAC 192kbps audio via FFmpeg

### `utils.py`
Thread-safe in-memory job store for async task tracking (`new_job`, `set_job_status`, `get_job`).

### `main.py`
FastAPI REST backend exposing endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-track/` | Upload a single audio track |
| `POST` | `/create-mixtape/` | Kick off async mixtape creation |
| `GET` | `/job/{job_id}` | Poll job status |
| `POST` | `/make-video/` | Generate video from audio + image |
| `POST` | `/generate-description/` | Generate YouTube description |
| `GET` | `/download/` | Download any output file |

### `streamlit_app.py`
Lightweight frontend for non-technical users. Supports track uploads, mixtape creation, description generation, video rendering, and job status polling — all through a simple UI.

---

## 📊 MLflow Tracking

Every pipeline run logs the following to DagsHub:

**Parameters**
- `mixtape_name`, `genre`, `transition_ms`, `track_count`, `output_mp3`, `output_mp4`, `cover_image`

**Metrics**
- `audio_elapsed_sec` — time taken to blend the mixtape
- `video_elapsed_sec` — time taken to render the video

**Artifacts**
- `audio/mixtape.mp3`
- `video/mixtape_vid.mp4`
- `description/youtube_description.txt`
- `checkpoints/checkpoint_1_audio.json`
- `checkpoints/checkpoint_2_description.json`
- `checkpoints/checkpoint_3_video.json`

---

## 🗄️ MongoDB Schema

Each pipeline run inserts one document into the `mixtape_automation.runs` collection:

```json
{
  "run_id": "<mlflow_run_id>",
  "mixtape_name": "Afro House Summer Mix",
  "genre": "Afro House",
  "transition_ms": 6000,
  "track_count": 3,
  "tracks": ["track1.mp3", "track2.mp3", "track3.mp3"],
  "mixtape_path": "/content/output/mixtape.mp3",
  "video_path": "/content/output/mixtape_vid.mp4",
  "desc_path": "/content/output/youtube_description.txt",
  "audio_elapsed": 42.3,
  "video_elapsed": 18.7,
  "created_at": "2025-07-14T10:32:00"
}
```

---

## 📦 Output Artifacts

After a successful run, the following files are produced and zipped for download:

| File | Description |
|------|-------------|
| `mixtape.mp3` | Blended mixtape with smooth transitions |
| `mixtape_vid.mp4` | YouTube-ready video (1280×720) |
| `youtube_description.txt` | Full description with tracklist timestamps |
| `checkpoint_1_audio.json` | Audio job metadata |
| `checkpoint_2_description.json` | Description generation metadata |
| `checkpoint_3_video.json` | Video job metadata |

---

## 🚀 Future Scope

- AI-based genre detection and auto-tagging
- Auto-upload to YouTube via the YouTube Data API
- User-selectable transition styles (hard cut, echo fade, filter sweep)
- Waveform visualizer overlay rendered into the video
- User accounts with saved project history
- Dockerized deployment for production use

---

## 📄 Sample Output — YouTube Description

```
🔥 Afro House Summer Mix 🔥
Genre: Afro House

🎵 Tracklist:
00:00 - Awen (Caiiro - Your Voice - Adam Port Remix)
04:20 - Waves

💽 Download/Listen links:
You can find these tracks online.

🎧 Follow for more mixes!

#Mixtape #DJMix #HouseMusic #MusicMix #AfroHouse #ElectronicMusic
```

---

## 👤 Author

**Prithu Sarkar**  
MLOps & Generative AI Industry Project  
IIT Guwahati Certification Program
