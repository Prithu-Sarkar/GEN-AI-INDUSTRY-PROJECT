# 🎓 Smart Attendance Portal

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A secure, real-time, web-based attendance management system that eliminates manual roll calls, prevents proxy attendance, and delivers instant analytics.**

[🚀 Live Demo](#) · [📖 Documentation](#architecture) · [🐛 Report Bug](https://github.com/d-hackmt/attendence-portal/issues) · [✨ Request Feature](https://github.com/d-hackmt/attendence-portal/issues)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Deployment Versions](#-deployment-versions)
  - [Version 1 — Google Colab + ngrok](#version-1--google-colab--ngrok-lightweight)
  - [Version 2 — AWS EC2 Production](#version-2--aws-ec2-production-grade)
- [Quick Start](#-quick-start-colab-version)
- [Database Schema](#-database-schema)
- [Security Design](#-security-design)
- [Analytics & Reporting](#-analytics--reporting)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧭 Overview

Smart Attendance Portal is a full-stack attendance management system built for educational institutions. It replaces error-prone paper-based roll calls with a secure, code-gated digital system.

Teachers open a session with a time-limited code. Students submit attendance using their roll number, name, and the code. The system enforces roll-number/name locking to prevent impersonation, duplicate submission guards, and daily limits — all backed by a PostgreSQL database in the cloud.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔐 **Code-Gated Attendance** | Admin sets a session code; students must enter it to mark attendance |
| 🔒 **Roll-Number Locking** | Once a roll number is registered to a name, it cannot be changed — prevents impersonation |
| 🚫 **Duplicate Prevention** | One submission per student per day, enforced at both app and database level |
| 📊 **Daily Limit Control** | Admin sets a maximum headcount per session |
| 📈 **Analytics Dashboard** | Pivot-table matrix, bar charts, and CSV export for any date range |
| 🗑️ **Admin Corrections** | Delete erroneous records by ID |
| 📝 **Centralised Logging** | Every action logged to rotating file with filename and line number |
| ☁️ **Cloud Database** | All data persisted in Supabase (PostgreSQL) — survives session restarts |

---

## 🛠 Tech Stack

```
Frontend    →  Streamlit
Backend     →  Python 3.10+
Database    →  Supabase (PostgreSQL)
Analytics   →  Pandas · Matplotlib
Utilities   →  PyTZ · Logging
Deployment  →  Google Colab + ngrok  /  AWS EC2 + systemd
Version Control → GitHub
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                         │
│                       Streamlit                         │
│              UI Layer    ←→    Functionality             │
└───────────────────┬─────────────────────────────────────┘
                    │  HTTP Request / Response
┌───────────────────▼─────────────────────────────────────┐
│                        BACKEND                          │
│                    Pipeline Layer                       │
│         ┌──────────────┬──────────────────┐             │
│         │  DB Pipelines │   Core Logic     │             │
│         │  (CRUD ops)   │   (Python)       │             │
│         └──────┬────────┴──────────────────┘             │
└────────────────┼────────────────────────────────────────┘
                 │  Supabase Python Client
┌────────────────▼────────────────────────────────────────┐
│                      DATABASE                           │
│              Supabase (PostgreSQL)                      │
│    attendance · roll_map · classroom_settings           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
smart_attendance_portal/
│
├── admin_main.py              # Streamlit entry point — Admin portal
├── student_main.py            # Streamlit entry point — Student portal
├── versions.py                # Version metadata
├── requirements.txt           # Pinned dependencies
│
├── .streamlit/
│   └── secrets.toml           # Supabase credentials (never commit this)
│
└── Attendence/                # Core package
    ├── __init__.py
    ├── config.py              # Central constants & env vars
    ├── logger.py              # Rotating file + console logger
    ├── clients.py             # Supabase singleton client
    ├── supabase_client.py     # CRUD wrappers (all DB calls)
    ├── admin.py               # Admin business logic
    ├── student.py             # Student attendance pipeline
    ├── analytics.py           # Pivot tables, charts, CSV export
    └── utils.py               # Timezone, validation, sanitisation
```

---

## 🚀 Deployment Versions

### Version 1 — Google Colab + ngrok *(Lightweight)*

> **Best for:** Classroom demos, hackathons, quick testing, educational use.
> No server setup required — runs entirely in a browser.

#### Prerequisites
- Google account (for Colab)
- Supabase account (free tier)
- ngrok account (free tier)

#### Required Colab Secrets
Add these in **Colab → 🔑 Secrets panel** with Notebook Access ON:

| Secret Key | Where to get it |
|---|---|
| `SUPABASE_URL` | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_KEY` | Supabase Dashboard → Settings → API → Publishable key |
| `NGROK_AUTHTOKEN` | dashboard.ngrok.com → Your Authtoken |
| `MONGO_DB_URL` | MongoDB Atlas (optional, for future use) |
| `MLFLOW_TRACKING_URI` | DagsHub or local path |
| `MLFLOW_TRACKING_USERNAME` | DagsHub credentials |
| `MLFLOW_TRACKING_PASSWORD` | DagsHub credentials |

#### Run Order

```
1. Run Step 1  → Load secrets
2. Run Step 2  → Install dependencies
3. Run Step 3  → Create folder structure
4. Run Step 4  → Write all source files
5. Run Step 5  → Set up Supabase tables (SQL Editor)
6. Run Admin cell → Open a class session
7. Run Student cell → Share URL with students
```

#### Limitations of Colab Version
- Session dies after ~12 hours of inactivity
- URL changes every session restart
- Not suitable for concurrent large-scale use

---

### Version 2 — AWS EC2 Production-Grade

> **Best for:** Institutional deployment, persistent 24/7 availability, large student batches.

#### Infrastructure

```
Internet → Route 53 (DNS) → CloudFront (CDN/SSL)
        → ALB (Load Balancer)
        → EC2 t3.medium (Ubuntu 22.04)
           ├── Streamlit Admin  (port 8501, internal only)
           ├── Streamlit Student (port 8502, public)
           └── Nginx (reverse proxy, ports 80/443)
        → Supabase (managed PostgreSQL, external)
```

#### EC2 Setup

```bash
# 1. Launch EC2 — Ubuntu 22.04 LTS, t3.medium, 20GB gp3
# 2. Security Group: allow 22 (SSH), 80 (HTTP), 443 (HTTPS)

# 3. Connect and provision
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# 4. Install dependencies
sudo apt update && sudo apt install -y python3-pip python3-venv nginx git

# 5. Clone the repo
git clone https://github.com/d-hackmt/attendence-portal.git
cd attendence-portal

# 6. Create virtual environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 7. Set environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-publishable-key"
```

#### systemd Services

```bash
# /etc/systemd/system/attendance-student.service
[Unit]
Description=Smart Attendance Student Portal
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/attendence-portal
Environment="SUPABASE_URL=https://your-project.supabase.co"
Environment="SUPABASE_KEY=your-key"
ExecStart=/home/ubuntu/attendence-portal/venv/bin/streamlit run student_main.py --server.port 8502 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable attendance-student
sudo systemctl start attendance-student
sudo systemctl status attendance-student
```

#### Nginx Config

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Student portal — public
    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Admin portal — restricted to your IP
    location /admin {
        allow YOUR_ADMIN_IP;
        deny all;
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Version Comparison

| | Colab + ngrok | AWS EC2 |
|---|---|---|
| **Setup time** | 10 minutes | 45–60 minutes |
| **Cost** | Free | ~$15–30/month |
| **Uptime** | Session-based | 24/7 |
| **URL stability** | Changes each run | Fixed domain |
| **Concurrent users** | ~30 | 200+ |
| **SSL/HTTPS** | ngrok provides | ACM + CloudFront |
| **Best for** | Testing / demos | Production |

---

## ⚡ Quick Start (Colab Version)

```python
# Open the notebook in Colab
# https://github.com/d-hackmt/attendence-portal

# Step 1 — Add secrets in Colab (🔑 sidebar)
# SUPABASE_URL, SUPABASE_KEY, NGROK_AUTHTOKEN

# Step 2 — Run all cells top to bottom

# Step 3 — Launch Admin portal, open a class

# Step 4 — Launch Student portal, share URL
```

---

## 🗃 Database Schema

```sql
-- Classroom configuration
CREATE TABLE classroom_settings (
    id               SERIAL PRIMARY KEY,
    class_name       TEXT UNIQUE NOT NULL,
    attendance_code  TEXT NOT NULL DEFAULT '',
    daily_limit      INTEGER NOT NULL DEFAULT 60,
    attendance_open  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Roll number → name binding (immutable once set)
CREATE TABLE roll_map (
    id           SERIAL PRIMARY KEY,
    class_name   TEXT NOT NULL,
    roll_number  TEXT NOT NULL,
    name         TEXT NOT NULL,
    UNIQUE(class_name, roll_number)
);

-- Daily attendance records
CREATE TABLE attendance (
    id           SERIAL PRIMARY KEY,
    class_name   TEXT NOT NULL,
    roll_number  TEXT NOT NULL,
    name         TEXT NOT NULL,
    date         DATE NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(class_name, roll_number, date)  -- DB-level duplicate guard
);
```

---

## 🔐 Security Design

The system uses a **multi-layer validation pipeline** for every student submission:

```
Input received
     │
     ▼
[1] Sanitise & validate format
     │
     ▼
[2] Class exists & attendance is open?
     │
     ▼
[3] Daily limit not exceeded?
     │
     ▼
[4] Attendance code matches?
     │
     ▼
[5] Roll number / name consistent? (locking check)
     │
     ▼
[6] Already marked today? (duplicate check)
     │
     ▼
[7] Insert record ✅
```

Additionally, enable **Row Level Security (RLS)** on Supabase for production:

```sql
ALTER TABLE attendance         ENABLE ROW LEVEL SECURITY;
ALTER TABLE roll_map           ENABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_insert" ON attendance FOR INSERT WITH CHECK (true);
CREATE POLICY "allow_select" ON attendance FOR SELECT USING (true);
CREATE POLICY "allow_select" ON classroom_settings FOR SELECT USING (true);
```

---

## 📊 Analytics & Reporting

The Admin Analytics tab generates:

- **Attendance Matrix** — pivot table (students × dates, 1=present, 0=absent)
- **Daily Bar Chart** — student count per day via Matplotlib
- **CSV Export** — downloadable spreadsheet for any date range

Sample matrix output:

```
name          2024-01-15  2024-01-16  2024-01-17  Total
John Doe               1           1           0      2
Jane Smith             1           0           1      2
Ravi Kumar             0           1           1      2
```

---

## 🔮 Future Roadmap

- [ ] OTP-based student verification
- [ ] Auto-generation of daily attendance codes on schedule
- [ ] Teacher login system with role-based access
- [ ] Face recognition integration
- [ ] Mobile-friendly PWA
- [ ] Email alerts for low attendance percentage
- [ ] Schedule-based auto open/close
- [ ] Multi-institution support

---

## 🤝 Contributing

```bash
# Fork the repo, then:
git clone https://github.com/your-username/attendence-portal.git
cd attendence-portal
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes, then
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
# Open a Pull Request
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using Python · Streamlit · Supabase

⭐ Star this repo if it helped you!

</div>
