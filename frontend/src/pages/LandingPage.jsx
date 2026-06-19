import React from 'react';
import './LandingPage.css';

export default function LandingPage({ onStart }) {
  return (
    <div className="landing-container animate-fade-in">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-glow animate-float"></div>
        <h1 className="hero-title">
          Convert Your Resume Into a <span className="gradient-text">Stunning Portfolio</span> Instantly
        </h1>
        <p className="hero-description">
          AuraPort uses advanced AI to analyze your PDF resume, extract your professional profile, write copy, and generate a fully responsive, custom-themed personal portfolio website with live preview.
        </p>
        <div className="hero-cta">
          <button className="btn-primary" onClick={onStart}>
            Get Started Free <span>→</span>
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <h2 className="section-title">How It Works</h2>
        <div className="features-grid">
          <div className="feature-card glass-panel">
            <div className="feature-num">01</div>
            <h3 className="feature-title">Upload PDF</h3>
            <p className="feature-desc">
              Upload your existing PDF resume. Our backend extracts all details accurately, including experience, skills, and projects.
            </p>
          </div>
          
          <div className="feature-card glass-panel">
            <div className="feature-num">02</div>
            <h3 className="feature-title">Select Style Theme</h3>
            <p className="feature-desc">
              Choose from 4 beautifully designed CSS themes including Modern Developer, Glassmorphism, Corporate, or Minimalist.
            </p>
          </div>

          <div className="feature-card glass-panel">
            <div className="feature-num">03</div>
            <h3 className="feature-title">AI Content Generation</h3>
            <p className="feature-desc">
              Gemini AI restructures your resume details, refines the professional copy, and builds clean semantic HTML and custom CSS.
            </p>
          </div>

          <div className="feature-card glass-panel">
            <div className="feature-num">04</div>
            <h3 className="feature-title">Preview & Download</h3>
            <p className="feature-desc">
              Interact with your portfolio instantly in the live mockup browser, tweak the theme, and download the raw HTML/CSS or ZIP package.
            </p>
          </div>
        </div>
      </section>

      {/* Tech Badges */}
      <section className="tech-section">
        <p className="tech-label">Powered by cutting-edge technology</p>
        <div className="tech-badges">
          <span className="tech-badge">React & Vite</span>
          <span className="tech-badge">Python Flask</span>
          <span className="tech-badge">Google Gemini API</span>
          <span className="tech-badge">PDFPlumber</span>
          <span className="tech-badge">Modern CSS</span>
        </div>
      </section>
    </div>
  );
}
