import { useState } from "react";

import DocumentUpload from "../components/DocumentUpload";
import QueryDocument from "../components/QueryDocument";
import QRReceiver from "./components/QRReceiver";

function App() {
  const [documentId, setDocumentId] = useState("");
  const [mode, setMode] = useState<"sender" | "receiver">("sender");

  return (
    <div>
      <h1>SecureRAG-QR</h1>

      <nav className="app-modes" aria-label="Transfer mode">
        <button type="button" aria-pressed={mode === "sender"} onClick={() => setMode("sender")}>Sender</button>
        <button type="button" aria-pressed={mode === "receiver"} onClick={() => setMode("receiver")}>Receiver</button>
      </nav>

      <div hidden={mode !== "sender"}>
        <DocumentUpload
          onUploadSuccess={setDocumentId}
        />

        {documentId && (
          <QueryDocument
            documentId={documentId}
          />
        )}
      </div>
      <div hidden={mode !== "receiver"}>
        <QRReceiver />
      </div>
    </div>
  );
}

export default App;
