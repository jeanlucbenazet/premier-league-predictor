# app.py - Main Flask Application
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import sqlite3
import os
from scipy.stats import poisson
import joblib
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
API_KEYS = {
    'football_api': os.environ.get('FOOTBALL_API_KEY', 'your_api_key_here'),
    'sportmonks': os.environ.get('SPORTMONKS_API_KEY', 'your_api_key_here')
}

class PremierLeaguePredictor:
    def __init__(self):
        self.model_home = None
        self.model_away = None
        self.load_models()
        
    def load_models(self):
        """Load pre-trained ML models for home and away goal prediction"""
        try:
            self.model_home = joblib.load('models/home_goals_model.pkl')
            self.model_away = joblib.load('models/away_goals_model.pkl')
        except:
            print("Models not found, will train new ones")
            
    def fetch_team_stats(self, team_name, season='2024-25'):
        """Fetch team statistics from API"""
        # Using football-api.com or similar service
        url = f"https://api.football-api.com/v2/teams/{team_name}/stats"
        headers = {'Authorization': f"Bearer {API_KEYS['football_api']}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching team stats: {e}")
            
        # Return mock data if API fails
        return self.get_mock_team_stats(team_name)
    
    def get_mock_team_stats(self, team_name):
        """Provide mock data for development/testing"""
        mock_stats = {
            'Manchester City': {'goals_per_game': 2.8, 'goals_conceded_per_game': 0.9, 'form': [3, 3, 1, 3, 3]},
            'Arsenal': {'goals_per_game': 2.4, 'goals_conceded_per_game': 1.1, 'form': [3, 1, 3, 3, 0]},
            'Liverpool': {'goals_per_game': 2.6, 'goals_conceded_per_game': 1.0, 'form': [3, 3, 3, 1, 3]},
            'Chelsea': {'goals_per_game': 2.1, 'goals_conceded_per_game': 1.2, 'form': [3, 0, 1, 3, 1]},
            'Manchester United': {'goals_per_game': 1.9, 'goals_conceded_per_game': 1.4, 'form': [1, 3, 0, 1, 3]},
            'Tottenham': {'goals_per_game': 2.3, 'goals_conceded_per_game': 1.3, 'form': [3, 1, 3, 0, 1]},
            'Newcastle United': {'goals_per_game': 2.0, 'goals_conceded_per_game': 1.2, 'form': [3, 1, 1, 3, 3]},
            'Brighton': {'goals_per_game': 1.8, 'goals_conceded_per_game': 1.3, 'form': [1, 3, 1, 0, 3]},
            'Aston Villa': {'goals_per_game': 2.0, 'goals_conceded_per_game': 1.1, 'form': [3, 3, 1, 3, 1]},
            'West Ham United': {'goals_per_game': 1.7, 'goals_conceded_per_game': 1.5, 'form': [0, 1, 3, 1, 1]},
            'Crystal Palace': {'goals_per_game': 1.5, 'goals_conceded_per_game': 1.4, 'form': [1, 0, 1, 3, 0]},
            'Fulham': {'goals_per_game': 1.6, 'goals_conceded_per_game': 1.3, 'form': [1, 1, 3, 0, 1]},
            'Wolves': {'goals_per_game': 1.4, 'goals_conceded_per_game': 1.6, 'form': [0, 1, 1, 0, 3]},
            'Everton': {'goals_per_game': 1.3, 'goals_conceded_per_game': 1.7, 'form': [1, 0, 0, 1, 1]},
            'Brentford': {'goals_per_game': 1.7, 'goals_conceded_per_game': 1.4, 'form': [3, 1, 0, 3, 1]},
            'Nottingham Forest': {'goals_per_game': 1.4, 'goals_conceded_per_game': 1.5, 'form': [1, 1, 0, 1, 3]},
            'Sheffield United': {'goals_per_game': 1.2, 'goals_conceded_per_game': 1.8, 'form': [0, 0, 1, 0, 1]},
            'Burnley': {'goals_per_game': 1.1, 'goals_conceded_per_game': 1.9, 'form': [0, 1, 0, 0, 0]},
            'Luton Town': {'goals_per_game': 1.3, 'goals_conceded_per_game': 1.7, 'form': [1, 0, 1, 0, 1]},
            'AFC Bournemouth': {'goals_per_game': 1.6, 'goals_conceded_per_game': 1.5, 'form': [1, 3, 0, 1, 1]}
        }
        return mock_stats.get(team_name, {'goals_per_game': 1.5, 'goals_conceded_per_game': 1.5, 'form': [1, 1, 1, 1, 1]})
    
    def calculate_attack_defence_strength(self, team_stats, league_avg=1.4):
        """Calculate team attack and defence strength"""
        attack_strength = team_stats['goals_per_game'] / league_avg
        defence_strength = team_stats['goals_conceded_per_game'] / league_avg
        return attack_strength, defence_strength
    
    def calculate_form_factor(self, form_list):
        """Calculate team form factor from recent results"""
        if not form_list:
            return 1.0
        
        # Weight recent games more heavily
        weights = [0.4, 0.3, 0.2, 0.1]  # Most recent game has highest weight
        weighted_points = sum(points * weight for points, weight in zip(form_list[:4], weights))
        max_possible = sum(3 * weight for weight in weights)
        
        return weighted_points / max_possible
    
    def predict_match_outcome(self, home_team, away_team):
        """Predict match outcome using enhanced Poisson distribution"""
        # Get team statistics
        home_stats = self.fetch_team_stats(home_team)
        away_stats = self.fetch_team_stats(away_team)
        
        # Calculate strengths
        home_attack, home_defence = self.calculate_attack_defence_strength(home_stats)
        away_attack, away_defence = self.calculate_attack_defence_strength(away_stats)
        
        # Calculate form factors
        home_form = self.calculate_form_factor(home_stats.get('form', []))
        away_form = self.calculate_form_factor(away_stats.get('form', []))
        
        # Home advantage factor
        home_advantage = 1.3
        
        # Expected goals calculation with form adjustment
        expected_home_goals = home_attack * away_defence * home_advantage * 1.4 * (1 + home_form * 0.2)
        expected_away_goals = away_attack * home_defence * 1.4 * (1 + away_form * 0.1)
        
        # Ensure reasonable goal expectations
        expected_home_goals = max(0.5, min(4.0, expected_home_goals))
        expected_away_goals = max(0.5, min(4.0, expected_away_goals))
        
        # Generate probability matrix using Poisson distribution
        max_goals = 6
        probabilities = {}
        
        for home_goals in range(max_goals):
            for away_goals in range(max_goals):
                prob = (poisson.pmf(home_goals, expected_home_goals) * 
                       poisson.pmf(away_goals, expected_away_goals))
                probabilities[f"{home_goals}-{away_goals}"] = prob
        
        # Calculate match outcome probabilities
        home_win_prob = sum([prob for score, prob in probabilities.items() 
                           if int(score.split('-')[0]) > int(score.split('-')[1])])
        draw_prob = sum([prob for score, prob in probabilities.items() 
                        if int(score.split('-')[0]) == int(score.split('-')[1])])
        away_win_prob = sum([prob for score, prob in probabilities.items() 
                           if int(score.split('-')[0]) < int(score.split('-')[1])])
        
        # Most likely scorelines
        sorted_scores = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        top_scorelines = sorted_scores[:5]
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'expected_home_goals': round(expected_home_goals, 2),
            'expected_away_goals': round(expected_away_goals, 2),
            'home_win_probability': round(home_win_prob * 100, 1),
            'draw_probability': round(draw_prob * 100, 1),
            'away_win_probability': round(away_win_prob * 100, 1),
            'most_likely_scorelines': [(score, round(prob * 100, 2)) for score, prob in top_scorelines],
            'confidence_score': self.calculate_confidence(home_win_prob, draw_prob, away_win_prob),
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def calculate_confidence(self, home_prob, draw_prob, away_prob):
        """Calculate prediction confidence based on probability distribution"""
        max_prob = max(home_prob, draw_prob, away_prob)
        # Higher difference between max and others = higher confidence
        prob_spread = max_prob - min(home_prob, draw_prob, away_prob)
        confidence = min(95.0, max(10.0, prob_spread * 150))
        return round(confidence, 1)

# Initialize predictor
predictor = PremierLeaguePredictor()

# API Routes
@app.route('/')
def index():
    return jsonify({
        "message": "Premier League Betting Predictor API",
        "version": "1.0",
        "status": "active",
        "endpoints": {
            "/predict": "POST - Predict match outcome",
            "/fixtures": "GET - Get upcoming fixtures", 
            "/teams": "GET - Get all Premier League teams",
            "/results": "GET - Get recent results",
            "/batch-predict": "POST - Predict multiple matches"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict_match():
    """Predict match outcome between two teams"""
    data = request.get_json()
    
    if not data or 'home_team' not in data or 'away_team' not in data:
        return jsonify({'error': 'Missing home_team or away_team in request'}), 400
    
    home_team = data['home_team']
    away_team = data['away_team']
    
    if home_team == away_team:
        return jsonify({'error': 'Home and away teams cannot be the same'}), 400
    
    try:
        prediction = predictor.predict_match_outcome(home_team, away_team)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/fixtures', methods=['GET'])
def get_fixtures():
    """Get upcoming Premier League fixtures"""
    # This would fetch from Premier League API in production
    # For demo, return mock data with current dates
    today = datetime.now()
    
    fixtures = [
        {
            'id': 1,
            'home_team': 'Manchester City',
            'away_team': 'Arsenal', 
            'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            'time': '15:00',
            'stadium': 'Etihad Stadium',
            'gameweek': 3
        },
        {
            'id': 2,
            'home_team': 'Liverpool',
            'away_team': 'Chelsea',
            'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            'time': '17:30',
            'stadium': 'Anfield',
            'gameweek': 3
        },
        {
            'id': 3,
            'home_team': 'Manchester United',
            'away_team': 'Tottenham',
            'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            'time': '16:30', 
            'stadium': 'Old Trafford',
            'gameweek': 3
        },
        {
            'id': 4,
            'home_team': 'Newcastle United',
            'away_team': 'Brighton',
            'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'time': '14:00',
            'stadium': 'St. James Park',
            'gameweek': 4
        },
        {
            'id': 5,
            'home_team': 'Aston Villa',
            'away_team': 'West Ham United',
            'date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            'time': '15:00',
            'stadium': 'Villa Park',
            'gameweek': 4
        }
    ]
    
    return jsonify({'fixtures': fixtures, 'total': len(fixtures)})

@app.route('/teams', methods=['GET'])
def get_teams():
    """Get all Premier League teams"""
    teams = [
        'Arsenal', 'Aston Villa', 'Brighton', 'Brentford', 'Burnley',
        'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Liverpool',
        'Manchester City', 'Manchester United', 'Newcastle United',
        'Nottingham Forest', 'Sheffield United', 'Tottenham', 
        'West Ham United', 'Wolves', 'AFC Bournemouth', 'Luton Town'
    ]
    
    # Add team stats for each team
    teams_with_stats = []
    for team in teams:
        stats = predictor.get_mock_team_stats(team)
        teams_with_stats.append({
            'name': team,
            'goals_per_game': stats['goals_per_game'],
            'goals_conceded_per_game': stats['goals_conceded_per_game'],
            'form_points': sum(stats['form'][:5])
        })
    
    return jsonify({'teams': teams_with_stats, 'total': len(teams_with_stats)})

@app.route('/results/<team_name>', methods=['GET'])
def get_team_results(team_name):
    """Get recent results for a specific team"""
    # Mock recent results - in production, fetch from API
    mock_results = {
        'Manchester City': [
            {'opponent': 'Liverpool', 'result': 'W', 'score': '2-1', 'date': '2025-08-15', 'home': True},
            {'opponent': 'Chelsea', 'result': 'W', 'score': '3-1', 'date': '2025-08-08', 'home': False}, 
            {'opponent': 'Arsenal', 'result': 'D', 'score': '1-1', 'date': '2025-08-01', 'home': True},
            {'opponent': 'Tottenham', 'result': 'W', 'score': '2-0', 'date': '2025-07-25', 'home': False},
            {'opponent': 'Newcastle', 'result': 'W', 'score': '1-0', 'date': '2025-07-18', 'home': True}
        ],
        'Arsenal': [
            {'opponent': 'Chelsea', 'result': 'W', 'score': '2-1', 'date': '2025-08-15', 'home': True},
            {'opponent': 'Liverpool', 'result': 'D', 'score': '1-1', 'date': '2025-08-08', 'home': False}, 
            {'opponent': 'Manchester City', 'result': 'W', 'score': '3-0', 'date': '2025-08-01', 'home': True},
            {'opponent': 'Tottenham', 'result': 'W', 'score': '2-1', 'date': '2025-07-25', 'home': False},
            {'opponent': 'Brighton', 'result': 'L', 'score': '0-1', 'date': '2025-07-18', 'home': True}
        ]
    }
    
    results = mock_results.get(team_name, [
        {'opponent': 'Unknown', 'result': 'D', 'score': '1-1', 'date': '2025-08-15', 'home': True},
        {'opponent': 'Unknown', 'result': 'D', 'score': '1-1', 'date': '2025-08-08', 'home': False}
    ])
    
    return jsonify({'team': team_name, 'recent_results': results, 'total': len(results)})

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """Predict multiple matches at once"""
    data = request.get_json()
    
    if not data or 'matches' not in data:
        return jsonify({'error': 'Missing matches array in request'}), 400
    
    predictions = []
    for match in data['matches']:
        if 'home_team' in match and 'away_team' in match:
            try:
                prediction = predictor.predict_match_outcome(match['home_team'], match['away_team'])
                predictions.append(prediction)
            except Exception as e:
                predictions.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'], 
                    'error': str(e)
                })
    
    return jsonify({'predictions': predictions, 'total': len(predictions)})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
