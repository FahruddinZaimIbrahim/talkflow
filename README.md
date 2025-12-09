![GitHub stars](https://img.shields.io/github/stars/FahruddinZaimIbrahim/talkflow)
![GitHub forks](https://img.shields.io/github/forks/FahruddinZaimIbrahim/talkflow)
![GitHub issues](https://img.shields.io/github/issues/FahruddinZaimIbrahim/talkflow)
![GitHub last commit](https://img.shields.io/github/last-commit/FahruddinZaimIbrahim/talkflow)

# 🤖 TalkFlow - AI Chat Platform

**Your AI Conversation Flow**

Modern, intelligent conversation platform powered by AI. Built with Django REST Framework and React.

---

## ✨ Features

- 🔐 **Secure Authentication** - JWT-based user authentication
- 💬 **Multi-turn Conversations** - Full conversation history support
- 🤖 **Multiple LLM Support** - Easy integration with free LLM providers
- 📊 **Usage Analytics** - Track messages and token consumption
- ⚡ **High Performance** - Optimized queries, caching, and indexing
- 🛡️ **Security First** - User-based access control, input validation
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Modern UI/UX** - Clean interface with Tailwind CSS and smooth animations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Groq API Key (free at https://console.groq.com)

### Backend Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add GROQ_API_KEY

# Run migrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd talkflow-frontend
npm install
npm start
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000/api
- Admin Panel: http://127.0.0.1:8000/admin

---

## 📚 API Endpoints

### Authentication
```
POST   /api/auth/register/        - Register new user
POST   /api/auth/login/           - Login (get JWT tokens)
POST   /api/auth/token/refresh/   - Refresh access token
GET    /api/auth/profile/         - Get user profile
```

### Chat
```
POST   /api/chat/                 - Send message to AI
GET    /api/chat/conversations/   - List all conversations
GET    /api/chat/conversations/:id/ - Get conversation details
DELETE /api/chat/conversations/:id/ - Delete conversation
GET    /api/chat/history/         - Get chat history
GET    /api/chat/stats/           - Get usage statistics
```

---

## 🏗️ Architecture

```
TalkFlow
├── Backend (Django + DRF)
│   ├── Authentication (JWT)
│   ├── Chat API
│   ├── LLM Service Layer
│   └── Database (PostgreSQL/SQLite)
│
└── Frontend (React + Tailwind)
    ├── Authentication Flow
    ├── Chat Interface
    ├── Conversation Management
    └── Responsive Design
```

---

## 🛠️ Tech Stack

**Backend:**
- Django 5.0.1
- Django REST Framework 3.14.0
- SimpleJWT (Authentication)
- Groq API (LLM)
- SQLite

**Frontend:**
- React 18.2.0
- React Router 6.20.0
- Tailwind CSS 3.4.1
- Axios
- Lucide Icons

---

## 🔐 Security Features

- JWT token authentication
- Password validation
- CORS protection
- SQL injection prevention
- XSS protection
- User-based data isolation
- Rate limiting ready

---

## ⚡ Performance

- Database query optimization
- Indexes on frequently queried fields
- Redis caching support
- Message history pagination
- Efficient conversation loading

**Benchmarks:**
- Chat response: 1-3s (Groq API)
- Conversation list: <100ms (cached)
- Concurrent users: 100+ (Gunicorn)

---

## 📝 License

MIT License - feel free to use in your projects!

---

## 🙏 Acknowledgments

- Django & Django REST Framework
- React & Tailwind CSS
- Groq for free LLM API access

---

## 📸 Screenshots

### Login Page
![Login](docs/screenshots/login.png)

### Chat Interface
![Chat](docs/screenshots/chat.png)

### Conversation List
![Conversations](docs/screenshots/conversations.png)

---

## 📧 Contact

Built with ❤️ by DINZ

**TalkFlow - Your AI Conversation Flow**