import { useState } from "react";

import DocumentUpload from "../components/DocumentUpload";
import QueryDocument from "../components/QueryDocument";
import QRReceiver from "./components/QRReceiver";
import "./App.css";

function App() {
  const [documentId, setDocumentId] = useState("");
  const [mode, setMode] = useState<"sender" | "receiver">("sender");

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">⬡</span>
          <div><h1>SecureRAG-QR</h1><p>Secure offline document intelligence via QR transfer</p></div>
        </div>
        <nav className="app-modes" aria-label="Transfer mode">
          <button type="button" aria-pressed={mode === "sender"} onClick={() => setMode("sender")}><span aria-hidden="true">↥</span> Sender</button>
          <button type="button" aria-pressed={mode === "receiver"} onClick={() => setMode("receiver")}><span aria-hidden="true">▦</span> Receiver</button>
        </nav>
        <span className="header-caption">Document transfer workspace</span>
      </header>
      <main className="workspace">
        <div hidden={mode !== "sender"}>
          <div className="workspace-heading"><div><p className="eyebrow">SENDER WORKSPACE</p><h2>From document to information.</h2></div><p>Upload. Ask. Transfer.</p></div>
          <div className="sender-grid">
            <DocumentUpload onUploadSuccess={setDocumentId} />
            {documentId ? <QueryDocument documentId={documentId} /> : (
              <section className="panel query-placeholder">
                <div className="section-heading"><span className="step">2</span><div><h2>Ask Document</h2><p>Ask a question about your document</p></div></div>
                <div className="empty-state"><span className="empty-icon" aria-hidden="true">✧</span><h3>Your document is the starting point</h3><p>Upload a PDF to retrieve relevant information or create an AI summary, then transfer it with QR codes.</p><span className="badge">Waiting for a document</span></div>
              </section>
            )}
          </div>
        </div>
        <div hidden={mode !== "receiver"}>
          <div className="workspace-heading"><div><p className="eyebrow">RECEIVER WORKSPACE</p><h2>Bring your information together.</h2></div><p>Collect. Recover. Read.</p></div>
          <QRReceiver />
        </div>
      </main>
    </div>
  );
}

export default App;
