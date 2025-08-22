# Premier League Betting Predictor - React Frontend

## Application Structure

```
src/
├── components/
│   ├── Header.js
│   ├── FixtureCard.js
│   ├── PredictionDashboard.js
│   ├── TeamSelector.js
│   ├── ResultsHistory.js
│   └── BettingCalculator.js
├── pages/
│   ├── Home.js
│   ├── Predictions.js
│   └── Statistics.js
├── services/
│   └── api.js
├── utils/
│   └── calculations.js
├── styles/
│   └── components.css
└── App.js
```

## Main App Component (App.js)

```jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Predictions from './pages/Predictions';
import Statistics from './pages/Statistics';
import { fetchFixtures } from './services/api';
import './App.css';

function App() {
  const [fixtures, setFixtures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    loadFixtures();
  }, []);

  const loadFixtures = async () => {
    try {
      const data = await fetchFixtures();
      setFixtures(data.fixtures);
    } catch (error) {
      console.error('Error loading fixtures:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <Router>
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home fixtures={fixtures} loading={loading} />} />
            <Route path="/predictions" element={<Predictions fixtures={fixtures} />} />
            <Route path="/statistics" element={<Statistics />} />
          </Routes>
        </main>
      </Router>
    </div>
  );
}

export default App;
```

## Header Component (components/Header.js)

```jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = ({ darkMode, toggleDarkMode }) => {
  const location = useLocation();

  return (
    <header className="header">
      <div className="container">
        <div className="logo">
          <h1>⚽ PL Predictor</h1>
          <span>Professional Premier League Betting Intelligence</span>
        </div>
        
        <nav className="navigation">
          <Link 
            to="/" 
            className={location.pathname === '/' ? 'active' : ''}
          >
            Home
          </Link>
          <Link 
            to="/predictions" 
            className={location.pathname === '/predictions' ? 'active' : ''}
          >
            Predictions
          </Link>
          <Link 
            to="/statistics" 
            className={location.pathname === '/statistics' ? 'active' : ''}
          >
            Statistics
          </Link>
        </nav>

        <div className="header-controls">
          <button 
            className="theme-toggle"
            onClick={toggleDarkMode}
            aria-label="Toggle dark mode"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
```

## Prediction Dashboard (components/PredictionDashboard.js)

```jsx
import React, { useState, useEffect } from 'react';
import { predictMatch } from '../services/api';
import TeamSelector from './TeamSelector';
import BettingCalculator from './BettingCalculator';

const PredictionDashboard = () => {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam) {
      setError('Please select both teams');
      return;
    }

    if (homeTeam === awayTeam) {
      setError('Please select different teams');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await predictMatch(homeTeam, awayTeam);
      setPrediction(result);
    } catch (err) {
      setError('Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getPredictionRecommendation = () => {
    if (!prediction) return null;

    const { home_win_probability, draw_probability, away_win_probability } = prediction;
    const maxProb = Math.max(home_win_probability, draw_probability, away_win_probability);
    
    let recommendation = '';
    let confidence = '';

    if (maxProb === home_win_probability) {
      recommendation = 'Home Win';
    } else if (maxProb === draw_probability) {
      recommendation = 'Draw';
    } else {
      recommendation = 'Away Win';
    }

    if (maxProb > 60) confidence = 'High';
    else if (maxProb > 45) confidence = 'Medium';
    else confidence = 'Low';

    return { recommendation, confidence };
  };

  return (
    <div className="prediction-dashboard">
      <div className="prediction-form">
        <h2>Match Predictor</h2>
        
        <div className="team-selection">
          <div className="team-selector-container">
            <label>Home Team</label>
            <TeamSelector 
              value={homeTeam} 
              onChange={setHomeTeam}
              placeholder="Select home team"
            />
          </div>
          
          <div className="vs-divider">VS</div>
          
          <div className="team-selector-container">
            <label>Away Team</label>
            <TeamSelector 
              value={awayTeam} 
              onChange={setAwayTeam}
              placeholder="Select away team"
            />
          </div>
        </div>

        <button 
          className="predict-button"
          onClick={handlePredict}
          disabled={loading || !homeTeam || !awayTeam}
        >
          {loading ? 'Analyzing...' : 'Get Prediction'}
        </button>

        {error && <div className="error-message">{error}</div>}
      </div>

      {prediction && (
        <div className="prediction-results">
          <div className="match-header">
            <h3>{prediction.home_team} vs {prediction.away_team}</h3>
            <div className="confidence-badge">
              Confidence: {prediction.confidence_score}%
            </div>
          </div>

          <div className="probability-bars">
            <div className="prob-bar">
              <label>Home Win</label>
              <div className="bar-container">
                <div 
                  className="bar home-bar" 
                  style={{width: `${prediction.home_win_probability}%`}}
                />
                <span>{prediction.home_win_probability}%</span>
              </div>
            </div>

            <div className="prob-bar">
              <label>Draw</label>
              <div className="bar-container">
                <div 
                  className="bar draw-bar" 
                  style={{width: `${prediction.draw_probability}%`}}
                />
                <span>{prediction.draw_probability}%</span>
              </div>
            </div>

            <div className="prob-bar">
              <label>Away Win</label>
              <div className="bar-container">
                <div 
                  className="bar away-bar" 
                  style={{width: `${prediction.away_win_probability}%`}}
                />
                <span>{prediction.away_win_probability}%</span>
              </div>
            </div>
          </div>

          <div className="expected-goals">
            <div className="expected-goal-item">
              <span className="team">{prediction.home_team}</span>
              <span className="goals">{prediction.expected_home_goals}</span>
              <span className="label">Expected Goals</span>
            </div>
            <div className="expected-goal-item">
              <span className="team">{prediction.away_team}</span>
              <span className="goals">{prediction.expected_away_goals}</span>
              <span className="label">Expected Goals</span>
            </div>
          </div>

          <div className="likely-scorelines">
            <h4>Most Likely Scorelines</h4>
            <div className="scorelines-grid">
              {prediction.most_likely_scorelines.map(([score, prob], index) => (
                <div key={index} className="scoreline-item">
                  <span className="score">{score}</span>
                  <span className="probability">{prob}%</span>
                </div>
              ))}
            </div>
          </div>

          {getPredictionRecommendation() && (
            <div className="recommendation">
              <h4>Betting Recommendation</h4>
              <div className={`recommendation-badge ${getPredictionRecommendation().confidence.toLowerCase()}`}>
                <strong>{getPredictionRecommendation().recommendation}</strong>
                <span>({getPredictionRecommendation().confidence} Confidence)</span>
              </div>
            </div>
          )}

          <BettingCalculator prediction={prediction} />
        </div>
      )}
    </div>
  );
};

export default PredictionDashboard;
```

## Betting Calculator (components/BettingCalculator.js)

```jsx
import React, { useState } from 'react';

const BettingCalculator = ({ prediction }) => {
  const [betAmount, setBetAmount] = useState(10);
  const [selectedBet, setSelectedBet] = useState('home');

  // Mock odds (in real app, fetch from odds API)
  const getOdds = () => {
    const homeProb = prediction.home_win_probability / 100;
    const drawProb = prediction.draw_probability / 100;
    const awayProb = prediction.away_win_probability / 100;

    return {
      home: (1 / homeProb).toFixed(2),
      draw: (1 / drawProb).toFixed(2),
      away: (1 / awayProb).toFixed(2)
    };
  };

  const calculatePayout = () => {
    const odds = getOdds();
    const selectedOdds = odds[selectedBet];
    return (betAmount * selectedOdds).toFixed(2);
  };

  const calculateProfit = () => {
    return (calculatePayout() - betAmount).toFixed(2);
  };

  const getExpectedValue = () => {
    const odds = getOdds();
    const selectedOdds = parseFloat(odds[selectedBet]);
    let winProbability;
    
    switch (selectedBet) {
      case 'home':
        winProbability = prediction.home_win_probability / 100;
        break;
      case 'draw':
        winProbability = prediction.draw_probability / 100;
        break;
      case 'away':
        winProbability = prediction.away_win_probability / 100;
        break;
      default:
        winProbability = 0;
    }

    const expectedReturn = (selectedOdds * winProbability) - 1;
    return (expectedReturn * 100).toFixed(1);
  };

  const odds = getOdds();

  return (
    <div className="betting-calculator">
      <h4>Betting Calculator</h4>
      
      <div className="bet-options">
        <div 
          className={`bet-option ${selectedBet === 'home' ? 'active' : ''}`}
          onClick={() => setSelectedBet('home')}
        >
          <div className="bet-label">{prediction.home_team} Win</div>
          <div className="bet-odds">{odds.home}</div>
          <div className="bet-prob">{prediction.home_win_probability}%</div>
        </div>

        <div 
          className={`bet-option ${selectedBet === 'draw' ? 'active' : ''}`}
          onClick={() => setSelectedBet('draw')}
        >
          <div className="bet-label">Draw</div>
          <div className="bet-odds">{odds.draw}</div>
          <div className="bet-prob">{prediction.draw_probability}%</div>
        </div>

        <div 
          className={`bet-option ${selectedBet === 'away' ? 'active' : ''}`}
          onClick={() => setSelectedBet('away')}
        >
          <div className="bet-label">{prediction.away_team} Win</div>
          <div className="bet-odds">{odds.away}</div>
          <div className="bet-prob">{prediction.away_win_probability}%</div>
        </div>
      </div>

      <div className="bet-amount-section">
        <label>Bet Amount (£)</label>
        <input
          type="number"
          value={betAmount}
          onChange={(e) => setBetAmount(parseFloat(e.target.value) || 0)}
          min="1"
          step="1"
        />
      </div>

      <div className="calculation-results">
        <div className="calc-row">
          <span>Total Payout:</span>
          <span className="value">£{calculatePayout()}</span>
        </div>
        <div className="calc-row">
          <span>Profit:</span>
          <span className="value profit">£{calculateProfit()}</span>
        </div>
        <div className="calc-row">
          <span>Expected Value:</span>
          <span className={`value ${parseFloat(getExpectedValue()) > 0 ? 'positive' : 'negative'}`}>
            {getExpectedValue()}%
          </span>
        </div>
      </div>

      {parseFloat(getExpectedValue()) > 0 && (
        <div className="value-bet-notice">
          ✅ This appears to be a value bet based on our prediction!
        </div>
      )}
    </div>
  );
};

export default BettingCalculator;
```

## API Service (services/api.js)

```js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Generic API call function
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};

// Predict match outcome
export const predictMatch = async (homeTeam, awayTeam) => {
  return apiCall('/predict', {
    method: 'POST',
    body: JSON.stringify({
      home_team: homeTeam,
      away_team: awayTeam,
    }),
  });
};

// Get upcoming fixtures
export const fetchFixtures = async () => {
  return apiCall('/fixtures');
};

// Get all teams
export const fetchTeams = async () => {
  return apiCall('/teams');
};

// Get team results
export const fetchTeamResults = async (teamName) => {
  return apiCall(`/results/${encodeURIComponent(teamName)}`);
};

// Batch predict multiple matches
export const batchPredict = async (matches) => {
  return apiCall('/batch-predict', {
    method: 'POST',
    body: JSON.stringify({
      matches: matches,
    }),
  });
};
```

## Package.json

```json
{
  "name": "premier-league-predictor-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.3.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

## Environment Variables (.env)

```
REACT_APP_API_URL=https://your-backend-api.herokuapp.com
REACT_APP_APP_NAME=Premier League Predictor
```

This React frontend provides:
- Interactive match prediction interface
- Real-time probability visualization
- Betting calculator with expected value analysis
- Responsive design for mobile betting
- Dark/light theme support
- Integration with Flask backend API