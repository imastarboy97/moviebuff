# 🎬 MovieBufff

**MovieBufff** is a real-time sentiment analysis dashboard that collects tweets about movies, analyzes public opinion using NLP, and displays results in a clean, private one-page dashboard.

🌐 Live at: [moviebufff.vercel.app](https://moviebufff.vercel.app/)

---

## 🚀 Features

- 🐦 Scrapes live tweets related to a movie
- 🤖 Analyzes tweet sentiment using NLP (VADER)
- 📊 Displays total tweets, sentiment breakdown, and a sample of tweets
- 📄 Static dashboard built with HTML/CSS, hosted via Vercel
- 🔁 Auto-updatable every 3 hours (via cron/automation setup)

---

## 🛠️ Tech Stack

- **Python**: Web scraping with Playwright
- **NLP**: Sentiment analysis using VADER (NLTK)
- **Frontend**: Static HTML, CSS, and JavaScript
- **Hosting**: [Vercel](https://vercel.com/)
- **Automation**: GitHub Actions / CRON (for periodic scraping)

---

## 📁 Project Structure
├── moviebuff.py           # Main scraper & analyzer script
├── sentiment.py           # Sentiment classifier (VADER)
├── constants.py           # Configurable keywords, time ranges, etc.
├── data.json              # Latest tweet analysis output
├── data.html              # Dashboard interface
├── vercel.json            # Vercel config
└── README.md              # You’re here
