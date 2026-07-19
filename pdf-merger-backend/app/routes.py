from flask import Blueprint, jsonify, request, send_file
from app.services.pdf_service import merge_pdfs

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to PDF Merger API"
    })

@main.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP",
        "application": "PDF Merger Backend",
        "version": "1.0.0"
    }), 200
@main.route("/merge", methods=["POST"])
def merge_pdf():
    files = request.files.getlist("files")

    if not files:
        return jsonify({
            "error": "No PDF files uploaded"
        }), 400
    merged_pdf = merge_pdfs(files)
    return send_file(
        merged_pdf,
        as_attachment=True,
        download_name="merged.pdf",
        mimetype="application/pdf"
    )