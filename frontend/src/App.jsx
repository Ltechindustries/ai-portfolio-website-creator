import React, { useState } from 'react';
import LandingPage from './pages/LandingPage';
import GeneratorPage from './pages/GeneratorPage';
import ResultsPage from './pages/ResultsPage';
import './App.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('landing'); // 'landing', 'generator', 'results'
  const [generatedCode, setGeneratedCode] = useState(null);
  const [selectedTheme, setSelectedTheme] = useState('Modern Developer');

  const handleGenerationComplete = (code, theme) => {
    setGeneratedCode(code);
    setSelectedTheme(theme);
    setCurrentPage('results');
  };

  const handleReset = () => {
    setGeneratedCode(null);
    setCurrentPage('generator');
  };

  return (
    <div className="app-container">
      {/* Global Navbar */}
      <header className="app-header glass-panel">
        <div className="nav-brand" onClick={() => setCurrentPage('landing')}>
          <span className="brand-logo">⚡</span>
          <span className="brand-name">AuraPort</span>
        </div>
        <div className="nav-tagline">AI Resume-to-Portfolio Website Generator</div>
        <nav className="nav-links">
          <button className="nav-btn" onClick={() => setCurrentPage('landing')}>Home</button>
          <button className="nav-btn" onClick={() => setCurrentPage('generator')}>Create</button>
        </nav>
      </header>

      {/* Main App Page Routing */}
      <main className="app-content">
        {currentPage === 'landing' && (
          <LandingPage onStart={() => setCurrentPage('generator')} />
        )}
        {currentPage === 'generator' && (
          <GeneratorPage 
            onGenerationComplete={handleGenerationComplete} 
            onBack={() => setCurrentPage('landing')}
          />
        )}
        {currentPage === 'results' && (
          <ResultsPage 
            generatedCode={generatedCode} 
            theme={selectedTheme} 
            onGenerateAgain={handleReset} 
          />
        )}
      </main>

      {/* Global Footer */}
      <footer className="app-footer">
        <p>© 2026 AuraPort. Powered by Google Gemini AI. Professional resume analysis & code generation.</p>
      </footer>
    </div>
  );
}
