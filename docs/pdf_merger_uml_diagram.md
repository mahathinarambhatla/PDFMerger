flowchart TB
  U[User (Browser)] -->|Select up to 5 PDFs| FE[React Frontend SPA]

  %% Client-side validation
  FE -->|Validate: max=5, extension=.pdf, size<=20MB| V1[Client Validation]
  V1 -->|Valid -> enable Merge button| FEmerge[Merge button enabled]
  V1 -->|Invalid -> show error banner| ErrUI[UI error message]

  %% Submit merge request
  FEmerge -->|POST /api/merge (multipart/form-data)<br/>files in UI order| API[Flask Backend API]

  %% Server-side validation
  API --> Val[schemas/validators.py: validate multipart]
  Val -->|Empty upload| E1[400 EMPTY_UPLOAD]
  Val -->|Too many files (>5)| E2[400 TOO_MANY_FILES]
  Val -->|Non-PDF/invalid type| E3[400 INVALID_FILE_TYPE]
  Val -->|Too large| E4[400 FILE_SIZE_LIMIT]
  Val -->|Valid| MS[services/merge_service.py: MergeService]

  %% Merge behavior
  MS --> Engine[PDF Merge Engine: pypdf.PdfMerger]
  Engine --> Append[Append PDFs in request order]
  Append -->|Write output/merged-<jobId>.pdf| Save[Persist merged PDF]
  Engine -->|Failure: pypdf parse/merge error| E5[MERGE_FAILURE or CORRUPTED_PDF]

  %% Response + preview
  Save --> Resp[200 JSON:<br/>jobId, mergedFileName, previewUrl, downloadUrl]
  Resp --> UIprev[UI: render preview]
  UIprev --> PrevPanel[Preview panel:<br/><iframe src=previewUrl />]

  %% Download
  UIprev -->|Download click| DL[GET /api/download/<jobId>]
  DL --> File[Serve output/merged-<jobId>.pdf<br/>Content-Type: application/pdf]
  File --> U

  %% Optional: upload endpoint
  API -.optional-> UploadAPI[POST /api/upload]<br/>uploads/ temp
  UploadAPI -->|jobId, status uploaded| Resp

  %% Styling
  classDef ui fill:#fff5e6,stroke:#c97a00,color:#3b2200;
  classDef api fill:#e6f2ff,stroke:#1f5fbf,color:#0b2a4a;
  classDef svc fill:#eef8ee,stroke:#2e7d32,color:#0b2a0b;
  classDef err fill:#ffe6e6,stroke:#b00020,color:#5a0014;

  class U,FE,V1,FEmerge,UIprev,PrevPanel ui;
  class API,Val,DL,Resp,File,UploadAPI api;
  class MS,Engine,Append,Save svc;
  class E1,E2,E3,E4,E5 err;


Data Flow Summary
The User uploads up to five PDF files using the Upload Component.
The React frontend sends the files to the Flask Upload API using Axios.
The Validation Service verifies:
File type (.pdf)
Maximum number of files (5)
Valid files are stored in a temporary upload folder.
When the user clicks Merge, the frontend invokes the Merge API.
The PDF Merge Service uses the pypdf library to merge the PDFs while preserving the upload order.
The merged document is written to the Merged PDF Output directory.
The merged PDF is returned to the frontend for preview.
The user downloads the merged PDF through the Download API.
After the download (or after processing, depending on implementation), the Cleanup Service removes temporary files.