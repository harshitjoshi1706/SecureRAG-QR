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
    <div>
      <h2>Upload Document</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={(event) => {
          const selectedFile =
            event.target.files?.[0] || null;

          setFile(selectedFile);
        }}
      />

      <button
        onClick={handleUpload}
        disabled={loading}
      >
        {loading ? "Uploading..." : "Upload"}
      </button>

      {result && (
        <div>
          <p>File: {result.filename}</p>
          <p>Pages: {result.page_count}</p>
          <p>Chunks: {result.chunk_count}</p>
          <p>Document ID: {result.document_id}</p>
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;