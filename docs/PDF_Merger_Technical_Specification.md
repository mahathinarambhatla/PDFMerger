# PDF MErger — Technical Specification (Web UI + Backend)

**Version:** v1.1.0  
**Author(s):** BlackboxAI  
**Date:** 2026-07-18  

## Abstract
This document specifies the technical design, requirements, architecture, technology stack, implementation details, and testing strategy for **PDF Merger**. This specification covers a **single-page React UI** that allows users to upload up to **5 PDF files**, validates inputs, submits them to a **Flask** backend to merge them **in the user-selected order**, previews the merged result, and enables download. The system is designed for **local deployment**, **no login**, **no database**, and **local filesystem storage** with optional temporary upload/output directories.

---

## Table of Contents
1. [Overview](#1-overview)
2. [Requirements](#2-requirements)
   - 2.1 [Functional Requirements](#21-functional-requirements)
   - 2.2 [Non-Functional Requirements](#22-non-functional-requirements)
   - 2.3 [User Stories / Use Cases (Prioritized)](#23-user-stories--use-cases-prioritized)
   - 2.4 [Performance Benchmarks & Compliance](#24-performance-benchmarks--compliance)
   - 2.5 [Assumptions and Constraints](#25-assumptions-and-constraints)
3. [System Design](#3-system-design)
   - 3.1 [High-Level Architecture](#31-high-level-architecture)
   - 3.2 [System Flow](#32-system-flow)
   - 3.3 [Component Design](#33-component-design)
   - 3.4 [Deployment Considerations](#34-deployment-considerations)
4. [Technologies Used](#4-technologies-used)
5. [API Specifications (Backend)](#5-api-specifications-backend)
   - 5.1 [REST Endpoints](#51-rest-endpoints)
   - 5.2 [POST /upload](#post-upload)
   - 5.3 [POST /merge](#post-merge)
   - 5.4 [GET /download](#get-download)
   - 5.5 [Error Handling](#55-error-handling)
   - 5.6 [Security Measures](#56-security-measures)
6. [UI/UX Specification](#6-uiux-specification)
   - 6.1 [Single-Page Structure](#61-single-page-structure)
   - 6.2 [User Workflow](#62-user-workflow)
   - 6.3 [Validation Rules (Client-side)](#63-validation-rules-client-side)
   - 6.4 [Validation Rules (Server-side)](#64-validation-rules-server-side)
7. [Data Models and Storage](#7-data-models-and-storage)
8. [Implementation Details](#8-implementation-details)
   - 8.1 [Folder Structure](#81-folder-structure)
   - 8.2 [Backend Implementation](#82-backend-implementation)
   - 8.3 [Frontend Implementation](#83-frontend-implementation)
   - 8.4 [Merge Behavior & Ordering](#84-merge-behavior--ordering)
   - 8.5 [Edge Cases & Limitations](#85-edge-cases--limitations)
9. [Testing Strategy](#9-testing-strategy)
   - 9.1 [Unit Tests](#91-unit-tests)
   - 9.2 [Integration Tests](#92-integration-tests)
   - 9.3 [API Contract Tests](#93-api-contract-tests)
   - 9.4 [Performance Tests](#94-performance-tests)
   - 9.5 [Security / Robustness Tests](#95-security--robustness-tests)
10. [Appendix](#10-appendix)
    - A. [Glossary](#a-glossary)
    - B. [Future Scope](#b-future-scope)

---

## 1. Overview
### Purpose and Scope
**PDF MErger** provides a local web application for merging multiple PDF files into a single PDF. Users upload PDFs, the application validates file constraints, merges PDFs on the backend using **pypdf**, displays a **merged PDF preview in the browser**, and lets users download the merged output.

### Target Audience
- Users who need a simple UI to combine PDFs without CLI knowledge.
- Teams that standardize document packaging for submissions/reports.

### Use Case Scenarios
1. **Combine multiple PDFs** (e.g., front page + sections + appendices) into one output.
2. **Upload and merge quickly** in a local environment without authentication.
3. **Review merged output** using an embedded browser preview before downloading.

---

## 2. Requirements
### 2.1 Functional Requirements
**FR-1: Upload PDFs**  
The system shall allow uploading up to **5** PDF files.

**FR-2: Enforce Allowed Format**  
The system shall accept **only `.pdf`** files.

**FR-3: Enforce Max File Count**  
If more than **5** files are uploaded, the system shall return an error.

**FR-4: Validate Corruption / Parseability**  
If the server cannot read a PDF (corrupted/unreadable/encrypted unsupported), the system shall return an error.

**FR-5: Merge in User Order**  
The system shall merge PDFs in the order received from the UI.

**FR-6: Output Generation**  
The system shall generate a merged PDF file for download.

**FR-7: Preview and Download**  
The UI shall display the merged PDF preview and provide a way to download the merged output.

**FR-8: No Login / No Database**  
The system shall not require authentication and shall not use a database.

### 2.2 Non-Functional Requirements
**NFR-1: Response Time**  
For typical workloads, the system shall return merge results in **< 1 second** (configured target; actual time depends on PDF size/complexity).

**NFR-2: Concurrent Users**  
The system shall support **2 concurrent users**.

**NFR-3: Availability**  
Target availability: **99.9%** (local deployment caveat applies).

**NFR-4: Reliability & Clear Errors**  
The system shall provide user-friendly error messages for invalid input, corrupted PDFs, empty uploads, and merge failures.

**NFR-5: Maintainability**  
Code should be modular with clear separation between UI, API, and merge logic.

### 2.3 User Stories / Use Cases (Prioritized)
1. Upload up to 5 PDFs and click **Merge** to get a combined PDF.
2. If a user uploads invalid/non-PDF files or too many PDFs, show an immediate actionable error.
3. Preview merged output and download it.
4. Ensure deterministic merge ordering matches user selection/upload order.

### 2.4 Performance Benchmarks & Compliance
**Benchmarks (targets):**
- Response time: **< 1 second** for typical PDF sizes.
- Concurrency: handle **2** concurrent merges without crashing or producing corrupted outputs.

**Compliance / constraints:**
- Local processing only.
- No upload to third-party services.
- Uploaded files stored temporarily on local disk (no database).

### 2.5 Assumptions and Constraints
- Python version: **3.12**.
- React version and build tool are to be confirmed; defaulting in this spec to a modern Vite setup (see “Technologies Used”).
- Maximum PDF size per file is not provided; defaulting to **20 MB** (can be adjusted in config).

---

## 3. System Design
### 3.1 High-Level Architecture
**Architecture Type:** SPA (React) + REST API (Flask), single host deployment.

**Components:**
1. **React Frontend (single page)**
   - Handles file selection, client-side validation, merge request, and preview.
2. **Flask Backend**
   - Receives uploads (optional in this design), validates server-side constraints, merges using `pypdf`, and stores output.
3. **Local Filesystem Storage**
   - Temporary uploads directory (e.g., `uploads/`).
   - Output directory for merged PDFs (e.g., `output/`).

**Key design decisions:**
- No database: use deterministic filenames/job IDs (recommended).
- Preview uses browser PDF rendering via `<iframe>`/`<embed>`.

### 3.2 System Flow
1. **User opens application** (single page).
2. **User selects PDFs** (max 5, `.pdf` only).
3. UI validates client-side:
   - file count
   - file types
   - (optional) file size
4. UI sends merge request to backend.
5. Backend validates again:
   - file count, file types, non-empty
   - attempts to parse/merge using `pypdf`
6. Backend saves merged PDF into `output/`.
7. Backend returns a reference (e.g., `downloadUrl`) or `jobId`.
8. UI displays merged PDF preview.
9. User downloads merged PDF.

### 3.3 Component Design
#### 3.3.1 Frontend Component: `PdfMergerPage`
- Responsibilities:
  - file input handling
  - ordering (keep selection order)
  - preview
  - error display

#### 3.3.2 Backend Component: `MergeService`
- Responsibilities:
  - validate files
  - perform merge
  - write merged PDF to output

#### 3.3.3 PDF Merge Engine
- Technology: `pypdf.PdfMerger`
- Guarantees order by appending in request order.

### 3.4 Deployment Considerations
- Local Machine deployment by default.
- Recommended: run backend and frontend via dev server locally; build frontend for production if needed.
- Concurrency: ensure output filenames are unique per request to avoid collisions.
- Temporary storage cleanup: recommended TTL or delete on completion (future enhancement).

---

## 4. Technologies Used
### Frontend
- **React**: defaulting to **React 18** + **Vite** (recommended for modern tooling; confirm if different).
- TypeScript (optional; not specified—defaulting to JavaScript is acceptable).
- PDF preview: browser native renderer via `<iframe src="...">`.

### Backend
- **Language:** Python 3.12
- **Framework:** Flask
- **PDF library:** `pypdf` (`PdfMerger`)
- Request handling: `multipart/form-data` for uploads.

### Rationale & Trade-offs
- React + Flask is lightweight and suitable for a local, single-feature app.
- `pypdf` is pure Python and easy to integrate; may have limitations on malformed PDFs compared with CLI tools.

---

## 5. API Specifications (Backend)
> Backend APIs are optional per your questionnaire, but included here to support UI preview + download.

### 5.1 REST Endpoints
Base path: `/api`

### POST /api/upload
Uploads PDFs and returns a temporary job reference.

**Request:** `multipart/form-data`
- `files`: one or more files (`file1.pdf`, `file2.pdf`, ...)

**Response (200):**
```json
{
  "jobId": "<uuid>",
  "status": "uploaded"
}
```

> Note: If you prefer “merge directly return the PDF”, the system can skip this endpoint. This spec supports upload+merge for clearer workflow.

### POST /api/merge
Merges PDFs.

**Request:** `multipart/form-data` or `jobId` reference (choose one approach). Default:
- `files`: one or more PDFs (order must be preserved)

**Response (200):**
```json
{
  "jobId": "<uuid>",
  "mergedFileName": "merged-<uuid>.pdf",
  "previewUrl": "/api/download/<jobId>",
  "downloadUrl": "/api/download/<jobId>"
}
```

### GET /api/download/<jobId>
Returns merged PDF.

**Response (200):** `application/pdf` with `Content-Disposition: attachment; filename="..."`

### 5.5 Error Handling
**Error Response Format (example):**
```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only .pdf files are supported."
  }
}
```

**Recommended error codes:**
- `EMPTY_UPLOAD`
- `TOO_MANY_FILES` (more than 5)
- `INVALID_FILE_TYPE`
- `CORRUPTED_PDF`
- `MERGE_FAILURE`

**HTTP Status Codes:**
- `400` for validation errors
- `500` for merge failures/unhandled exceptions

### 5.6 Security Measures
- No authentication required.
- Use OS permissions to secure file system.
- Validate file extensions and MIME types.
- Enforce size limits.
- Ensure unique output filenames per job/request.

---

## 6. UI/UX Specification
### 6.1 Single-Page Structure
Single route: `/`

UI sections on the same page:
1. File selection area
2. Uploaded file list (show names and allow reordering optional)
3. Merge button
4. Error banner/toast area
5. Preview panel (shows merged PDF)
6. Download button

### 6.2 User Workflow
1. User opens application.
2. User uploads PDFs.
3. Application validates files.
4. User clicks **Merge**.
5. Backend merges PDFs.
6. Merged PDF preview displayed.
7. User downloads PDF.

> Per your questionnaire: workflow has **no changes**.

### 6.3 Validation Rules (Client-side)
- Max number of files: **5**.
- Allowed format: **only `.pdf`**.
- File size: default **20 MB** limit (update if you provide a different value).
- Disable **Merge** button until at least 1 file is selected.

### 6.4 Validation Rules (Server-side)
- Validate multipart content contains at least 1 file.
- Enforce max 5 files.
- Reject non-PDF files.
- Enforce file size limit.
- Attempt to parse/merge; if `pypdf` fails, return `CORRUPTED_PDF` or `MERGE_FAILURE`.

---

## 7. Data Models and Storage
### Data Models
- **Upload request model**
  - `files: ordered list of PDF binary blobs`
- **Merge response model**
  - `jobId`
  - `downloadUrl`
  - `previewUrl`

### Storage
- **Temporary uploads**: `uploads/`
- **Merged outputs**: `output/`
- **No database**.

> Recommended: clean up temporary uploads after merge completion.

---

## 8. Implementation Details
### 8.1 Folder Structure
Professional enterprise structure (as requested):
```
PDF-Merger/
  frontend/
  backend/
  docs/
  tests/
  uploads/
  output/
  logs/
```

### 8.2 Backend Implementation
Backend modules (recommended):
- `app.py` (Flask app + routes)
- `services/merge_service.py` (merge logic)
- `schemas/validators.py` (validation functions)
- `config.py` (size/count constraints)

Merge logic:
- Create `PdfMerger()`.
- Append PDFs in request order.
- Write merged PDF to `output/merged-<jobId>.pdf`.

### 8.3 Frontend Implementation
Frontend modules (recommended):
- `src/pages/PdfMergerPage.jsx`
- `src/components/FilePicker.jsx`
- `src/components/PreviewPanel.jsx`
- `src/api/client.js` (API calls)

Preview:
- Use `<iframe src={downloadUrl} />` or `<embed ... />`.
- Provide a fallback “Download” button.

### 8.4 Merge Behavior & Ordering
- The order of merged pages is determined by the order of files provided by the frontend.
- Server must maintain the same order when iterating received files.

### 8.5 Edge Cases & Limitations
- **Empty upload**: return `EMPTY_UPLOAD`.
- **More than five PDFs**: return `TOO_MANY_FILES`.
- **Corrupted PDFs**: return `CORRUPTED_PDF`.
- **Merge failure**: return `MERGE_FAILURE`.
- **Encrypted PDFs**: unspecified; backend may fail unless enhanced with password support (future scope).

---

## 9. Testing Strategy
### 9.1 Unit Tests
- File validation:
  - non-pdf rejection
  - file count enforcement
  - size limit enforcement
- Merge service:
  - order preservation using generated PDFs
  - single-file merge

### 9.2 Integration Tests
- Backend routes:
  - POST /merge returns previewUrl/downloadUrl
  - GET /download returns `application/pdf`
- End-to-end using temporary directories.

### 9.3 API Contract Tests
- Validate error response JSON schema and HTTP codes.

### 9.4 Performance Tests
- Simulate 2 concurrent merge requests (target concurrency).
- Test multiple sizes under the configured file size limit.

### 9.5 Security / Robustness Tests
- Attempt uploading invalid file types.
- Attempt corrupted PDFs.
- Ensure job-based output filenames do not collide.

---

## 10. Appendix
### A. Glossary
- **Job ID**: Unique identifier for a merge operation.
- **Preview URL**: API endpoint that serves merged PDF for rendering.

### B. Future Scope
Include future enhancements in planning backlog:
- PDF Split
- PDF Compress
- Password-protected PDFs
- Rotate Pages
- Reorder PDFs
- Cloud Storage Integration
- OCR Support

