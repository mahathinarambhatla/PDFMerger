"""Flask routes for the PDF Merger backend API.

This module defines the HTTP interface (Blueprint `main`) for:
- GET `/` (welcome)
- GET `/health` (liveness)
- POST `/merge` (merge uploaded PDFs)

See individual function docstrings for request/response details.
"""


from flask import Blueprint, jsonify, request, send_file

from app.services.pdf_service import merge_pdfs
from app.utils.file_validator import validate_files
from app.utils.logger import logger

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def home():
    """GET `/`.

    Simple entrypoint endpoint used to confirm the service is reachable.

    Returns:
        flask.Response: JSON greeting.
    """
    return jsonify({"message": "Welcome to PDF Merger API"})


@main.route("/health", methods=["GET"])
def health():
    """GET `/health`.

    Liveness probe endpoint.

    Returns:
        tuple[flask.Response, int]: JSON status payload and HTTP 200.
    """
    return (
        jsonify(
            {
                "status": "UP",
                "application": "PDF Merger Backend",
                "version": "1.0.0",
            }
        ),
        200,
    )


@main.route("/merge", methods=["POST"])
def merge_pdf():
    """POST `/merge`.

    Merges uploaded PDF files into a single PDF document.

    Request:
        Content-Type: multipart/form-data
        Field name: `files` (repeatable)
            - Each part must be a PDF file.

    Validation (see `validate_files`):
        - Minimum: 2 PDFs
        - Maximum: 5 PDFs
        - Each file <= 10 MB

    Responses:
        - 200: merged PDF (attachment `merged.pdf`, `application/pdf`)
        - 400: validation error as JSON: {"error": "..."}
        - 500: unexpected error as JSON
          {"error": "Internal Server Error", "details": "..."}
    """
    try:
        logger.info("Merge request received")

        # Reject text values sent using the same key
        # (e.g., if someone posts form fields named `files` that aren't uploaded files)
        if request.form.getlist("files"):
            return (
                jsonify(
                    {
                        "error": "Only PDF files are allowed. Text values are not accepted.",
                    }
                ),
                400,
            )

        files = request.files.getlist("files")
        logger.info(f"Number of uploaded files: {len(files)}")

        validate_files(files)
        logger.info("File validation successful")

        merged_pdf = merge_pdfs(files)
        logger.info("PDF merge completed successfully")

        return send_file(
            merged_pdf,
            as_attachment=True,
            download_name="merged.pdf",
            mimetype="application/pdf",
        )

    except ValueError as e:
        logger.error(f"Validation Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.exception("Unexpected error occurred while merging PDFs")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "details": str(e),
                }
            ),
            500,
        )

