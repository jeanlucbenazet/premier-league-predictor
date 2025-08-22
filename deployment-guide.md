# Premier League Betting Predictor - Deployment Guide

## Deployment Architecture

### Backend (Flask) - Deploy to Heroku
### Frontend (React) - Deploy to Vercel
### Database - Heroku PostgreSQL

---

## 1. Backend Deployment (Heroku)

### Prerequisites
- Heroku CLI installed
- Git repository initialized
- Heroku account created

### Step 1: Prepare Flask App for Heroku

Create **Procfile** in project root:
```
web: gunicorn app:app
```

Create **runtime.txt**:
```
python-3.11.4
```

Update **requirements.txt**:
```
Flask==2.3.3
Flask-CORS==4.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.7
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
scipy==1.11.1
requests==2.31.0
joblib==1.3.2
python-dotenv==1.0.0
```

### Step 2: Heroku Deployment Commands

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create pl-predictor-backend

# Add PostgreSQL database
heroku addons:create heroku-postgresql:mini -a pl-predictor-backend

# Set environment variables
heroku config:set FLASK_ENV=production -a pl-predictor-backend
heroku config:set SECRET_KEY=your_secret_key_here -a pl-predictor-backend
heroku config:set FOOTBALL_API_KEY=your_api_key -a pl-predictor-backend

# Deploy to Heroku
git add .
git commit -m "Deploy to Heroku"
heroku git:remote -a pl-predictor-backend
git push heroku main

# Initialize database (run once)
heroku run python database.py -a pl-predictor-backend
```

### Step 3: Update Flask App for Production

**app.py** production updates:
```python
import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Production CORS settings
if os.environ.get('FLASK_ENV') == 'production':
    CORS(app, origins=['https://your-frontend-domain.vercel.app'])
else:
    CORS(app)  # Allow all origins in development

# Database URL for production
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///premier_league.db')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

---

## 2. Frontend Deployment (Vercel)

### Prerequisites
- Vercel CLI installed (optional)
- GitHub account
- Vercel account connected to GitHub

### Method 1: GitHub Integration (Recommended)

1. **Push React code to GitHub repository**

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Select React framework preset
   - Configure environment variables

3. **Environment Variables in Vercel:**
   ```
   REACT_APP_API_URL=https://pl-predictor-backend.herokuapp.com
   REACT_APP_APP_NAME=Premier League Predictor
   ```

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Build the React app
npm run build

# Deploy to Vercel
vercel --prod

# Set environment variables
vercel env add REACT_APP_API_URL production
# Enter: https://pl-predictor-backend.herokuapp.com
```

### Step 3: Update React App for Production

**src/services/api.js** production updates:
```js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Add error handling for production
const apiCall = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // In production, you might want to send errors to a logging service
    if (process.env.NODE_ENV === 'production') {
      // Log to analytics/error tracking service
    }
    throw error;
  }
};
```

---

## 3. Database Setup (PostgreSQL)

### Heroku PostgreSQL Configuration

```python
# database.py - Updated for PostgreSQL
import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection for both local and production"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse Heroku DATABASE_URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        return psycopg2.connect(database_url, sslmode='require')
    else:
        # Local development
        return psycopg2.connect(
            host='localhost',
            database='premier_league',
            user='your_username',
            password='your_password'
        )

def init_db():
    """Initialize PostgreSQL database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables with PostgreSQL syntax
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            stadium VARCHAR(100),
            manager VARCHAR(100),
            founded INTEGER,
            website VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            home_team_id INTEGER REFERENCES teams(id),
            away_team_id INTEGER REFERENCES teams(id),
            match_date DATE,
            match_time TIME,
            home_goals INTEGER,
            away_goals INTEGER,
            status VARCHAR(20) DEFAULT 'scheduled',
            stadium VARCHAR(100),
            attendance INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            home_win_prob REAL,
            draw_prob REAL,
            away_win_prob REAL,
            expected_home_goals REAL,
            expected_away_goals REAL,
            confidence_score REAL,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
```

---

## 4. Domain Configuration & SSL

### Custom Domain (Optional)

**For Vercel Frontend:**
1. Go to Vercel dashboard → Project → Settings → Domains
2. Add your custom domain (e.g., `plpredictor.com`)
3. Update DNS records as instructed
4. SSL certificate is automatically provisioned

**For Heroku Backend:**
1. Add custom domain: `heroku domains:add api.plpredictor.com`
2. Update DNS CNAME record to point to Heroku
3. Add SSL: `heroku certs:auto:enable`

### CORS Configuration Update

```python
# app.py - Update CORS for custom domains
CORS(app, origins=[
    'https://plpredictor.com',
    'https://www.plpredictor.com', 
    'https://pl-predictor.vercel.app',  # Vercel default domain
    'http://localhost:3000'  # Local development
])
```

---

## 5. Monitoring & Analytics

### Backend Monitoring (Heroku)

```bash
# View logs
heroku logs --tail -a pl-predictor-backend

# Monitor performance
heroku addons:create newrelic:wayne -a pl-predictor-backend
```

### Frontend Analytics (Vercel)

Add to React app:
```jsx
// src/utils/analytics.js
export const trackPrediction = (homeTeam, awayTeam) => {
  if (process.env.NODE_ENV === 'production') {
    // Google Analytics, Mixpanel, etc.
    gtag('event', 'prediction_made', {
      home_team: homeTeam,
      away_team: awayTeam
    });
  }
};
```

---

## 6. Continuous Deployment

### GitHub Actions (Optional)

**.github/workflows/deploy.yml**:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "pl-predictor-backend"
        heroku_email: "your-email@example.com"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID}}
        vercel-project-id: ${{ secrets.PROJECT_ID}}
```

---

## 7. Testing Deployment

### Backend API Testing
```bash
# Test API endpoints
curl https://pl-predictor-backend.herokuapp.com/
curl -X POST https://pl-predictor-backend.herokuapp.com/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Arsenal", "away_team": "Chelsea"}'
```

### Frontend Testing
1. Visit deployed URL
2. Test team selection and predictions
3. Verify API connectivity
4. Test responsive design on mobile

---

## 8. Post-Deployment Checklist

- [ ] Backend API responding correctly
- [ ] Frontend loading and functional
- [ ] Database connections working
- [ ] CORS properly configured
- [ ] Environment variables set
- [ ] Error logging setup
- [ ] Performance monitoring enabled
- [ ] SSL certificates active
- [ ] Mobile responsiveness verified
- [ ] API rate limiting configured (if needed)

## Estimated Costs

**Heroku (Backend + Database):**
- Hobby plan: ~$7/month
- Database: ~$9/month
- **Total: ~$16/month**

**Vercel (Frontend):**
- Pro plan: ~$20/month (optional, free tier available)

**Domain (Optional):**
- ~$12/year

**Total Monthly Cost: ~$16-36/month**

The application is now ready for production use with automatic updates after every game!