import io
import zipfile
from flask import Blueprint, request, jsonify, send_file
from utils.pdf_extractor import extract_text_from_pdf
from services.gemini_service import generate_portfolio

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_resume():
    """
    Endpoint to receive resume PDF file, extract text, and return it.
    """
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded. Please upload a file with the key 'resume'."}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported."}), 400

    try:
        text = extract_text_from_pdf(file)
        return jsonify({"text": text}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to extract text from PDF: {str(e)}"}), 500

@api_bp.route('/generate', methods=['POST'])
def generate_code():
    """
    Endpoint to receive resume text and theme, call Gemini, and return HTML and CSS.
    """
    data = request.get_json() or {}
    resume_text = data.get("text", "")
    theme = data.get("theme", "Modern Developer")

    if not resume_text:
        return jsonify({"error": "Resume text is required."}), 400

    try:
        portfolio_data = generate_portfolio(resume_text, theme)
        return jsonify(portfolio_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate portfolio: {str(e)}"}), 500

@api_bp.route('/download', methods=['POST'])
def download_package():
    """
    Endpoint to receive HTML and CSS code, package them in a ZIP file, and return the ZIP file.
    """
    data = request.get_json() or {}
    html = data.get("html", "")
    css = data.get("css", "")

    if not html or not css:
        return jsonify({"error": "Both 'html' and 'css' fields are required to package files."}), 400

    try:
        # Create an in-memory ZIP file
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", html)
            zip_file.writestr("style.css", css)
            
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name="portfolio.zip"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to package files for download: {str(e)}"}), 500
