// App.js
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

  // Load upcoming fixtures on mount
  useEffect(() => {
    const loadFixtures = async () => {
      try {
        const data = await fetchFixtures();
        setFixtures(data.fixtures);
      } catch (err) {
        console.error('Error loading fixtures:', err);
      } finally {
        setLoading(false);
      }
    };
    loadFixtures();
  }, []);

  // Toggle dark/light theme
  const toggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <Router>
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={<Home fixtures={fixtures} loading={loading} />}
            />
            <Route
              path="/predictions"
              element={<Predictions fixtures={fixtures} />}
            />
            <Route path="/statistics" element={<Statistics />} />
          </Routes>
        </main>
      </Router>
    </div>
  );
}

export default App;
