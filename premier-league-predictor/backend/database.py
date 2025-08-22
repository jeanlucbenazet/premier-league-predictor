# database.py - Database Setup and Management
import sqlite3
import os
from datetime import datetime, timedelta
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection for local or Heroku PostgreSQL."""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        try:
            return psycopg2.connect(database_url, sslmode='require')
        except:
            print("PostgreSQL connection failed. Falling back to SQLite.")
            return sqlite3.connect('premier_league.db')
    else:
        return sqlite3.connect('premier_league.db')

def init_db():
    """Initialize the database with tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        is_postgres = hasattr(conn, 'autocommit')
        if is_postgres:
            setup_postgres_tables(cursor)
        else:
            setup_sqlite_tables(cursor)
        insert_sample_data(cursor, is_postgres)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

def setup_postgres_tables(cursor):
    """Create tables in PostgreSQL."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            stadium VARCHAR(100),
            manager VARCHAR(100),
            founded INTEGER,
            website VARCHAR(200),
            goals_per_game REAL DEFAULT 0.0,
            goals_conceded_per_game REAL DEFAULT 0.0,
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
            gameweek INTEGER DEFAULT 1,
            season VARCHAR(10) DEFAULT '2025-26',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id),
            home_win_prob REAL NOT NULL,
            draw_prob REAL NOT NULL,
            away_win_prob REAL NOT NULL,
            expected_home_goals REAL,
            expected_away_goals REAL,
            confidence_score REAL,
            most_likely_score VARCHAR(10),
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accuracy_score REAL DEFAULT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_stats (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id),
            season VARCHAR(10) DEFAULT '2025-26',
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            position INTEGER DEFAULT NULL,
            form VARCHAR(20) DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def setup_sqlite_tables(cursor):
    """Create tables in SQLite."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stadium TEXT,
            manager TEXT,
            founded INTEGER,
            website TEXT,
            goals_per_game REAL DEFAULT 0.0,
            goals_conceded_per_game REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team_id INTEGER,
            away_team_id INTEGER,
            match_date DATE,
            match_time TIME,
            home_goals INTEGER,
            away_goals INTEGER,
            status TEXT DEFAULT 'scheduled',
            stadium TEXT,
            attendance INTEGER,
            gameweek INTEGER DEFAULT 1,
            season TEXT DEFAULT '2025-26',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(home_team_id) REFERENCES teams(id),
            FOREIGN KEY(away_team_id) REFERENCES teams(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            home_win_prob REAL NOT NULL,
            draw_prob REAL NOT NULL,
            away_win_prob REAL NOT NULL,
            expected_home_goals REAL,
            expected_away_goals REAL,
            confidence_score REAL,
            most_likely_score TEXT,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accuracy_score REAL DEFAULT NULL,
            FOREIGN KEY(match_id) REFERENCES matches(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            season TEXT DEFAULT '2025-26',
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            position INTEGER DEFAULT NULL,
            form TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(team_id) REFERENCES teams(id)
        )
    ''')

def insert_sample_data(cursor, is_postgres=False):
    """Insert latest 2025-26 season teams."""
    teams = [
        ('Arsenal', 'Emirates Stadium', 'Mikel Arteta', 1886, 'https://arsenal.com', 2.4, 1.1),
        ('Manchester City', 'Etihad Stadium', 'Pep Guardiola', 1880, 'https://mancity.com', 2.8, 0.9),
        ('Liverpool', 'Anfield', 'Arne Slot', 1892, 'https://liverpoolfc.com', 2.6, 1.0),
        ('Chelsea', 'Stamford Bridge', 'Mauricio Pochettino', 1905, 'https://chelseafc.com', 2.1, 1.2),
        ('Manchester United', 'Old Trafford', 'Erik ten Hag', 1878, 'https://manutd.com', 1.9, 1.4),
        ('Tottenham', 'Tottenham Hotspur Stadium', 'Ange Postecoglou', 1882, 'https://tottenhamhotspur.com', 2.3, 1.3),
        ('Newcastle United', 'St. James Park', 'Eddie Howe', 1892, 'https://nufc.co.uk', 2.0, 1.2),
        ('Brighton', 'Amex Stadium', 'Roberto De Zerbi', 1901, 'https://brightonandhovealbion.com', 1.8, 1.3),
        ('Aston Villa', 'Villa Park', 'Unai Emery', 1874, 'https://avfc.co.uk', 2.0, 1.1),
        ('West Ham United', 'London Stadium', 'David Moyes', 1895, 'https://whufc.com', 1.7, 1.5),
        ('Crystal Palace', 'Selhurst Park', 'Roy Hodgson', 1905, 'https://cpfc.co.uk', 1.5, 1.4),
        ('Fulham', 'Craven Cottage', 'Marco Silva', 1879, 'https://fulhamfc.com', 1.6, 1.3),
        ('Wolves', 'Molineux Stadium', 'GJ O’Neil', 1877, 'https://wolves.co.uk', 1.4, 1.6),
        ('Everton', 'Goodison Park', 'Sean Dyche', 1878, 'https://evertonfc.com', 1.3, 1.7),
        ('Brentford', 'Brentford Community Stadium', 'Thomas Frank', 1889, 'https://brentfordfc.com', 1.7, 1.4),
        ('Nottingham Forest', 'City Ground', 'Nuno Espirito Santo', 1865, 'https://nottinghamforest.co.uk', 1.4, 1.5),
        ('Sheffield United', 'Bramall Lane', 'J. J. O’Connell', 1889, 'https://sufc.co.uk', 1.2, 1.8),
        ('Burnley', 'Turf Moor', 'TBA', 1882, 'https://burnleyfc.com', 1.1, 1.9),
        ('Luton Town', 'Kenilworth Road', 'Rob Edwards', 1885, 'https://lutontown.co.uk', 1.3, 1.7),
        ('AFC Bournemouth', 'Vitality Stadium', 'Andoni Iraola', 1899, 'https://afcb.co.uk', 1.6, 1.5),
        ('Leeds United', 'Elland Road', 'Daniel Farke', 1919, 'https://leedsunited.com', 2.2, 1.3),
        ('Sunderland', 'Stadium of Light', 'Regis Le Bris', 1879, 'https://safc.com', 1.7, 1.5)
    ]
    if is_postgres:
        # Insert in PostgreSQL
        cursor.execute('SELECT COUNT(*) FROM teams')
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany('''
                INSERT INTO teams (name, stadium, manager, founded, website, goals_per_game, goals_conceded_per_game)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', teams)
    else:
        # Insert in SQLite
        cursor.execute('SELECT COUNT(*) FROM teams')
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.executemany('''
                INSERT INTO teams (name, stadium, manager, founded, website, goals_per_game, goals_conceded_per_game)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', teams)
