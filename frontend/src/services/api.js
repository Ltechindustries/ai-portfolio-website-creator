const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

/**
 * Upload a PDF file to extract resume text.
 * @param {File} file - PDF resume file
 * @returns {Promise<{text: string}>}
 */
export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('resume', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to upload and extract text from resume.');
  }

  return response.json();
}

/**
 * Generate HTML/CSS portfolio using Gemini.
 * @param {string} text - Extracted resume text
 * @param {string} theme - Style theme name
 * @returns {Promise<{html: string, css: string}>}
 */
export async function generatePortfolio(text, theme) {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, theme }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to generate portfolio. Please try again.');
  }

  return response.json();
}

/**
 * Request packaged ZIP file from the backend.
 * @param {string} html - Generated HTML
 * @param {string} css - Generated CSS
 * @returns {Promise<Blob>}
 */
export async function downloadProjectZip(html, css) {
  const response = await fetch(`${API_BASE_URL}/download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ html, css }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to generate download package.');
  }

  return response.blob();
}
