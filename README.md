# ML/AI Engineer Portfolio

> Professional portfolio for Machine Learning and AI Engineering with comprehensive analytics tracking

## Hi! Here is Jackie!

Full-stack portfolio showcasing ML/AI projects and technical blog posts, featuring:
- 📊 Real-time visitor analytics
- 📱 Device & browser tracking
- 📧 Contact form with backend integration
- ☁️ Multi-cloud deployment ready (AWS + AliCloud)

Reach me at jyang297@uottawa.ca

## Project Structure

```
myPortfolio/
├── astro_frontend/        # Astro frontend application
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── package.json      # Frontend dependencies
│
├── api_backend/          # FastAPI backend
│   ├── main.py          # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── README.md        # Backend documentation
│
└── README.md            # This file
```

## Getting Started

### Frontend (Astro)

```bash
cd astro_frontend
npm install
npm run dev
# Runs on http://localhost:4321
```

### Backend (FastAPI)

```bash
cd api_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# Runs on http://localhost:8000
```

## Tech Stack

**Frontend:**
- Astro 5.5.2
- React 19.0.0
- Tailwind CSS v4
- TypeScript

**Backend:**
- FastAPI
- Python 3.x
- Uvicorn

## 📚 Documentation

**Quick Links:**
- 🚀 **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- 📖 **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet
- 🧪 **[astro_frontend/TESTING_GUIDE.md](astro_frontend/TESTING_GUIDE.md)** - Complete testing guide
- 🎯 **[astro_frontend/TRACKING_EXAMPLES.md](astro_frontend/TRACKING_EXAMPLES.md)** - Add tracking to components
- 🚢 **[DEPLOYMENT.md](DEPLOYMENT.md)** - AWS & AliCloud deployment
- ✅ **[TODO_CHECKLIST.md](TODO_CHECKLIST.md)** - Deployment checklist

**Architecture:**
- 🏗️ **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Backend architecture
- 🔗 **[FRONTEND_INTEGRATION_SUMMARY.md](FRONTEND_INTEGRATION_SUMMARY.md)** - Frontend integration

## Features

### Analytics & Tracking
- ✅ Automatic page view tracking
- ✅ Device & browser detection (mobile, tablet, desktop)
- ✅ Geographic location tracking (country, city)
- ✅ User engagement metrics (time on page, scroll depth)
- ✅ Referrer tracking (LinkedIn, GitHub, Google, etc.)
- ✅ Custom event tracking (clicks, downloads, form submissions)
- ✅ Privacy-conscious (IP hashing, bot filtering, GDPR-ready)

### Backend (FastAPI)
- ✅ RESTful API with comprehensive endpoints
- ✅ Structured JSON logging (CloudWatch/SLS compatible)
- ✅ Prometheus metrics endpoint
- ✅ Supabase integration for data storage
- ✅ Contact form processing
- ✅ Health checks and monitoring

### Frontend (Astro)
- ✅ Static site generation with Astro
- ✅ React components for interactive features
- ✅ Tailwind CSS v4 styling
- ✅ TypeScript for type safety
- ✅ Automatic analytics integration

### DevOps
- ✅ Docker containerized (frontend + backend)
- ✅ Docker Compose for local development
- ✅ Multi-cloud ready (AWS ECS, AliCloud ACK)
- ✅ CI/CD templates (GitHub Actions)
- ✅ Health checks for orchestrators

## Acknowledgments

This project was initially based on https://github.com/coding-in-public/astro-course-files

Thank Chris a lot for his courses and code.
