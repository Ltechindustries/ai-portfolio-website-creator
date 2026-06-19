import React, { useMemo } from 'react';
import './PreviewFrame.css';

export default function PreviewFrame({ html, css, title = "Portfolio Preview" }) {
  // Inject the CSS styles into the HTML <head> for iframe srcDoc rendering
  const combinedSrcDoc = useMemo(() => {
    if (!html) return '';
    
    const styleBlock = `<style>\n${css || ''}\n</style>`;
    
    // Check where to inject the styles. Head is best.
    if (html.includes('</head>')) {
      return html.replace('</head>', `${styleBlock}\n</head>`);
    } else if (html.includes('<head>')) {
      return html.replace('<head>', `<head>\n${styleBlock}`);
    } else {
      return `${styleBlock}\n${html}`;
    }
  }, [html, css]);

  if (!html) {
    return (
      <div className="preview-empty glass-panel">
        <p>No preview available. Generate a portfolio to see it live.</p>
      </div>
    );
  }

  return (
    <div className="browser-mockup glass-panel">
      {/* Browser Bar */}
      <div className="browser-bar">
        <div className="browser-dots">
          <span className="dot red" />
          <span className="dot yellow" />
          <span className="dot green" />
        </div>
        <div className="browser-address">
          <span className="lock-icon">🔒</span>
          <span className="address-text">localhost:3000/portfolio.html</span>
        </div>
        <div className="browser-actions">
          <span className="action-btn">🔄</span>
        </div>
      </div>
      
      {/* Iframe Content */}
      <div className="iframe-container">
        <iframe
          title={title}
          srcDoc={combinedSrcDoc}
          className="preview-frame"
          sandbox="allow-scripts"
        />
      </div>
    </div>
  );
}
