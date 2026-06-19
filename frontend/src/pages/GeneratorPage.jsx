import React, { useState, useRef } from 'react';
import ThemeSelector from '../components/ThemeSelector';
import { uploadResume, generatePortfolio } from '../services/api';
import './GeneratorPage.css';

export default function GeneratorPage({ onGenerationComplete, onBack }) {
  const [file, setFile] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('Modern Developer');
  
  // Loading & Step States
  const [loading, setLoading] = useState(false);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [error, setError] = useState('');
  
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // Loading animation steps
  const steps = [
    "Uploading PDF and connecting to parser...",
    "Extracting text structures and details...",
    "Sending profile to Google Gemini API...",
    "Analyzing professional background and experience...",
    "Generating responsive semantic HTML layout...",
    "Injecting CSS variables and theme style guidelines...",
    "Assembling codebase and polishing layouts..."
  ];

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.pdf')) {
        handleFileSelection(droppedFile);
      } else {
        setError('Only PDF files are supported.');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = async (selectedFile) => {
    setFile(selectedFile);
    setError('');
    setLoading(true);
    setCurrentStepIdx(0);

    // Simulate/run extraction steps
    const stepInterval = setInterval(() => {
      setCurrentStepIdx((prev) => {
        if (prev < 1) return prev + 1;
        return prev;
      });
    }, 1200);

    try {
      const response = await uploadResume(selectedFile);
      setExtractedText(response.text);
      setLoading(false);
      clearInterval(stepInterval);
    } catch (err) {
      setError(err.message || 'Failed to extract text. Please check the PDF file.');
      setFile(null);
      setLoading(false);
      clearInterval(stepInterval);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  };

  const handleGenerate = async () => {
    if (!extractedText.strip) {
      if (!extractedText.trim()) return;
    }
    
    setLoading(true);
    setCurrentStepIdx(2); // Jump to Gemini API step
    setError('');

    // Animate through remaining steps during generation
    const generationTimer = setInterval(() => {
      setCurrentStepIdx((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2500);

    try {
      const result = await generatePortfolio(extractedText, selectedTheme);
      clearInterval(generationTimer);
      setLoading(false);
      onGenerationComplete(result, selectedTheme);
    } catch (err) {
      setError(err.message || 'Failed to generate portfolio. Please verify your Gemini API key in the backend.');
      setLoading(false);
      clearInterval(generationTimer);
    }
  };

  const handleReset = () => {
    setFile(null);
    setExtractedText('');
    setError('');
  };

  return (
    <div className="generator-container animate-fade-in">
      <div className="generator-header">
        <button className="back-btn" onClick={onBack}>← Back to Landing</button>
        <h2 className="generator-title">Generate Your Portfolio</h2>
        <p className="generator-subtitle">Follow the steps below to transform your resume into a personalized site.</p>
      </div>

      {error && <div className="error-alert glass-panel">{error}</div>}

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-card glass-panel">
            <div className="spinner">
              <div className="double-bounce1"></div>
              <div className="double-bounce2"></div>
            </div>
            <h3 className="loading-title">Generating Portfolio</h3>
            <p className="loading-step-desc">This may take a few seconds...</p>
            
            <div className="steps-progress-list">
              {steps.map((step, idx) => {
                let status = "pending";
                if (idx < currentStepIdx) status = "completed";
                else if (idx === currentStepIdx) status = "active";
                
                return (
                  <div key={idx} className={`progress-step ${status}`}>
                    <span className="step-check">
                      {status === "completed" ? "✓" : status === "active" ? "●" : "○"}
                    </span>
                    <span className="step-text">{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {!file ? (
        /* Step 1: Upload Resume */
        <div 
          className={`upload-zone glass-panel ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={triggerFileSelect}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            className="file-input-hidden"
          />
          <div className="upload-icon-container">
            <span className="upload-icon">📄</span>
          </div>
          <h3>Drag & Drop your Resume PDF here</h3>
          <p>or click to browse your computer</p>
          <span className="file-limit-badge">Supports PDF up to 10MB</span>
        </div>
      ) : (
        /* Step 2: Extracted Text & Theme Selection */
        <div className="editor-layout animate-fade-in">
          <div className="editor-left">
            <div className="text-preview-header">
              <h3>Extracted Resume Content</h3>
              <button className="reset-btn" onClick={handleReset}>Upload Different File</button>
            </div>
            <textarea
              className="text-editor glass-panel"
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              placeholder="Wait for extraction or paste resume text here..."
            />
          </div>

          <div className="editor-right glass-panel">
            <ThemeSelector selectedTheme={selectedTheme} onChange={setSelectedTheme} />
            
            <div className="generator-actions">
              <button 
                className="btn-primary generate-btn" 
                onClick={handleGenerate}
                disabled={!extractedText.trim()}
              >
                Generate Portfolio Website ⚡
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
