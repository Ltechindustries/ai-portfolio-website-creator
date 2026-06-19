import React, { useState } from 'react';
import PreviewFrame from '../components/PreviewFrame';
import { downloadProjectZip } from '../services/api';
import './ResultsPage.css';

export default function ResultsPage({ generatedCode, theme, onGenerateAgain }) {
  const { html, css } = generatedCode;
  const [activeTab, setActiveTab] = useState('preview'); // 'preview', 'html', 'css'
  const [downloadingZip, setDownloadingZip] = useState(false);
  const [copied, setCopied] = useState(false);

  // Download files locally via browser blobs
  const downloadFile = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDownloadHtml = () => {
    downloadFile(html, 'index.html', 'text/html');
  };

  const handleDownloadCss = () => {
    downloadFile(css, 'style.css', 'text/css');
  };

  const handleDownloadZip = async () => {
    setDownloadingZip(true);
    try {
      const blob = await downloadProjectZip(html, css);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'portfolio.zip';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message || 'Failed to download project zip.');
    } finally {
      setDownloadingZip(false);
    }
  };

  const handleCopyCode = () => {
    const codeToCopy = activeTab === 'html' ? html : css;
    navigator.clipboard.writeText(codeToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="results-container animate-fade-in">
      {/* Top Bar / Actions */}
      <div className="results-header">
        <div className="header-details">
          <button className="back-btn" onClick={onGenerateAgain}>← Generate New Portfolio</button>
          <h2 className="results-title">Your Generated Portfolio</h2>
          <p className="results-subtitle">
            Theme: <span className="theme-highlight">{theme}</span>
          </p>
        </div>
        
        <div className="action-buttons-group">
          <button className="btn-secondary" onClick={handleDownloadHtml}>
            📥 Download HTML
          </button>
          <button className="btn-secondary" onClick={handleDownloadCss}>
            🎨 Download CSS
          </button>
          <button className="btn-primary" onClick={handleDownloadZip} disabled={downloadingZip}>
            {downloadingZip ? '📦 Packaging...' : '📦 Download ZIP'}
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="results-grid">
        {/* Controls Sidebar */}
        <div className="results-sidebar glass-panel">
          <h3 className="sidebar-title">View Options</h3>
          
          <div className="tabs-list">
            <button 
              className={`tab-item ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              👁️ Live Preview
            </button>
            <button 
              className={`tab-item ${activeTab === 'html' ? 'active' : ''}`}
              onClick={() => setActiveTab('html')}
            >
              📄 index.html Code
            </button>
            <button 
              className={`tab-item ${activeTab === 'css' ? 'active' : ''}`}
              onClick={() => setActiveTab('css')}
            >
              🎨 style.css Code
            </button>
          </div>

          <div className="sidebar-instructions">
            <h4>Instructions</h4>
            <ol>
              <li>Verify the content looks correct in the **Live Preview**.</li>
              <li>You can download the **index.html** and **style.css** separately.</li>
              <li>To run the portfolio locally, place both downloaded files in the **same folder**, and double-click `index.html`.</li>
              <li>Or download the **ZIP** file which contains both files pre-packaged.</li>
            </ol>
          </div>

          <div className="sidebar-footer">
            <button className="btn-secondary generate-again-btn" onClick={onGenerateAgain}>
              🔄 Try Another Theme / Edit Info
            </button>
          </div>
        </div>

        {/* Content Display Area */}
        <div className="results-content">
          {activeTab === 'preview' ? (
            <PreviewFrame html={html} css={css} />
          ) : (
            <div className="code-editor-container glass-panel">
              <div className="code-editor-header">
                <span className="file-name">{activeTab === 'html' ? 'index.html' : 'style.css'}</span>
                <button className="copy-btn btn-secondary" onClick={handleCopyCode}>
                  {copied ? '✓ Copied' : '📋 Copy Code'}
                </button>
              </div>
              <pre className="code-block">
                <code>{activeTab === 'html' ? html : css}</code>
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
