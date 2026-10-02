import { useState } from "react";
import api from "../services/api";

type UploadResponse = {
  document_id: string;
  filename: string;
  page_count: number;
  character_count: number;
  chunk_count: number;
};

type Props = {
  onUploadSuccess: (documentId: string) => void;
};

function DocumentUpload({ onUploadSuccess }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await api.post(
        "/api/documents/upload",
        formData
      );

      setResult(response.data);

      onUploadSuccess(response.data.document_id);
    } catch (error) {
      console.error(error);
      alert("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel upload-panel" aria-labelledby="upload-title">
      <div className="section-heading"><span className="step">1</span><div><h2 id="upload-title">Upload Document</h2><p>Select a PDF document to process</p></div></div>
      <label className="upload-zone">
        <span className="upload-icon" aria-hidden="true">↥</span>
        <strong>Select your PDF document</strong>
        <span>Click to browse your files</span>
        <input type="file" accept=".pdf" aria-label="Select PDF document"
          onChange={(event) => {
            const selectedFile = event.target.files?.[0] || null;
            setFile(selectedFile);
          }} />
        <small>PDF documents only</small>
      </label>
      {file && <p className="selected-file">Selected: <strong>{file.name}</strong></p>}
      <button className="primary upload-button" onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload Document"}
      </button>
      {result ? (
        <div className="document-card">
          <div className="document-name"><span className="pdf-icon" aria-hidden="true">PDF</span><div><strong>{result.filename}</strong><span className="badge success">Processed</span></div></div>
          <dl className="document-stats"><div><dt>Pages</dt><dd>{result.page_count}</dd></div><div><dt>Chunks</dt><dd>{result.chunk_count}</dd></div><div><dt>Characters</dt><dd>{result.character_count.toLocaleString()}</dd></div></dl>
          <p className="transfer-id">Document ID: {result.document_id}</p>
        </div>
      ) : <p className="upload-note">Document details will appear here after processing.</p>}
    </section>
  );
}

export default DocumentUpload;
