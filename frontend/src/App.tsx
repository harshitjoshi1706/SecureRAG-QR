import { useState } from "react";

import DocumentUpload from "../components/DocumentUpload";
import QueryDocument from "../components/QueryDocument";

function App() {
  const [documentId, setDocumentId] = useState("");

  return (
    <div>
      <h1>SecureRAG-QR</h1>

      <DocumentUpload
        onUploadSuccess={setDocumentId}
      />

      {documentId && (
        <QueryDocument
          documentId={documentId}
        />
      )}
    </div>
  );
}

export default App;