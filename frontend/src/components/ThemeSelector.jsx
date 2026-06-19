import React from 'react';
import './ThemeSelector.css';

const THEMES = [
  {
    id: 'Modern Developer',
    name: 'Modern Developer',
    description: 'Dark terminal vibe with glowing neon cyan/purple accents, monospace typography, and sleek tech badges.',
    previewColors: ['#0f172a', '#06b6d4', '#8b5cf6'],
    icon: '⚡',
  },
  {
    id: 'Glassmorphism',
    name: 'Glassmorphism',
    description: 'Frosted transparent panels over rich gradient backdrops. Highly visual with backdrop filters and pastel glows.',
    previewColors: ['#2e1065', '#ec4899', '#3b82f6'],
    icon: '🔮',
  },
  {
    id: 'Professional Corporate',
    name: 'Professional Corporate',
    description: 'Clean, trust-focused layout with slate blue, white, and gray tones. Features elegant structured grids and timelines.',
    previewColors: ['#f8fafc', '#1e3a8a', '#475569'],
    icon: '💼',
  },
  {
    id: 'Minimal Clean',
    name: 'Minimal Clean',
    description: 'Timeless, monochromatic layout focusing on generous spacing, extreme text contrast, and stark minimalism.',
    previewColors: ['#ffffff', '#000000', '#64748b'],
    icon: '✏️',
  },
];

export default function ThemeSelector({ selectedTheme, onChange }) {
  return (
    <div className="theme-selector-container">
      <h3 className="theme-selector-title">Select a Design Theme</h3>
      <p className="theme-selector-subtitle">Choose the visual style for your generated portfolio website.</p>
      
      <div className="themes-grid">
        {THEMES.map((theme) => {
          const isSelected = selectedTheme === theme.id;
          return (
            <div
              key={theme.id}
              className={`theme-card glass-panel ${isSelected ? 'selected' : ''}`}
              onClick={() => onChange(theme.id)}
            >
              <div className="theme-card-header">
                <span className="theme-icon">{theme.icon}</span>
                <h4 className="theme-name">{theme.name}</h4>
              </div>
              <p className="theme-desc">{theme.description}</p>
              
              <div className="theme-preview-palette">
                {theme.previewColors.map((color, idx) => (
                  <span
                    key={idx}
                    className="color-dot"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
              {isSelected && <div className="selected-indicator">Active</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
