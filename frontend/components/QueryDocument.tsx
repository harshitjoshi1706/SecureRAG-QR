import { useState } from "react";
import api from "../services/api";
import type { RecoveredInformation } from "../src/receiver/protocol";

type Props = {
  documentId: string;
};

type TransferResponse = {
  transfer_id: string;
  is_encrypted: boolean;
  fragment_count: number;
  qr_count: number;
  qr_urls: string[];
  answer: RecoveredInformation;
  size_metrics: {
    retrieved_context_bytes: number;
    compact_payload_bytes: number;
    compressed_payload_bytes: number;
    encrypted_payload_bytes: number | null;
  };
};

type QueryResponse = Pick<TransferResponse, "transfer_id" | "is_encrypted" | "answer" | "size_metrics">;

function QueryDocument({ documentId }: Props) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"fast" | "ai">("fast");
  const [encrypt, setEncrypt] = useState(true);
  const [password, setPassword] = useState("");

  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [transfer, setTransfer] = useState<TransferResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [qrLoading, setQrLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) {
      alert("Enter a question.");
      return;
    }

    if (encrypt && !password.trim()) {
      alert("Enter an encryption password.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post<QueryResponse>(
        "/api/query/answer",
        {
          query,
          document_id: documentId,
          encrypt,
          password: encrypt ? password : null,
          top_k: 3,
          mode,
        }
      );

      setAnswer(response.data);

      localStorage.setItem(
        "secureRagTransferId",
        response.data.transfer_id
      );

      setTransfer(null);
    } catch (error) {
      console.error(error);
      alert("Query failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQR = async () => {
    const transferId =
      answer?.transfer_id ||
      localStorage.getItem("secureRagTransferId");

    if (!transferId) {
      alert("No transfer ID found. Ask a question first.");
      return;
    }

    try {
      setQrLoading(true);

      const response = await api.post(
        "/api/transfer/generate",
        {
          transfer_id: transferId,
        }
      );

      setTransfer(response.data);
    } catch (error) {
      console.error(error);
      alert("QR generation failed.");
    } finally {
      setQrLoading(false);
    }
  };

  return (
    <div className="query-workspace">
      <section className="panel ask-panel" aria-labelledby="ask-title">
        <div className="section-heading"><span className="step">2</span><div><h2 id="ask-title">Ask Document</h2><p>Ask a question about your document</p></div></div>
        <label className="sr-only" htmlFor="document-question">Your question</label>
        <div className="question-field"><textarea id="document-question" value={query} onChange={(event) => { setQuery(event.target.value); }} placeholder="What would you like to know about this document?" /><span className="character-count">{query.length} characters</span></div>
        <div className="query-options">
          <fieldset disabled={loading || qrLoading}>
            <legend>Processing Mode</legend>
            <label className="choice-card"><input type="radio" name="processing-mode" value="fast" checked={mode === "fast"} onChange={() => setMode("fast")} /><span className="choice-icon" aria-hidden="true">ϟ</span><span><strong>Fast Retrieval</strong><small>Faster, skips the LLM</small></span></label>
            <label className="choice-card"><input type="radio" name="processing-mode" value="ai" checked={mode === "ai"} onChange={() => setMode("ai")} /><span className="choice-icon" aria-hidden="true">✧</span><span><strong>AI Summary</strong><small>Uses a local LLM for a concise answer</small></span></label>
          </fieldset>
          <div>
            <fieldset><legend>Transfer Type</legend>
              <label className="choice-card"><input type="radio" name="transfer-type" checked={!encrypt} onChange={() => { setEncrypt(false); setPassword(""); }} /><span className="choice-icon" aria-hidden="true">▦</span><span><strong>Standard QR</strong><small>Direct transfer, no encryption</small></span></label>
              <label className="choice-card"><input type="radio" name="transfer-type" checked={encrypt} onChange={() => { setEncrypt(true); }} /><span className="choice-icon" aria-hidden="true">◇</span><span><strong>Encrypted QR</strong><small>Secured with a password</small></span></label>
            </fieldset>
            {encrypt && <label className="password-label" htmlFor="sender-password">Password<input id="sender-password" type="password" value={password} onChange={(event) => { setPassword(event.target.value); }} placeholder="Encryption password" /></label>}
          </div>
        </div>
        <div className="query-actions">
          <button className="primary" onClick={handleQuery} disabled={loading || qrLoading}>{loading ? (mode === "fast" ? "Retrieving..." : "Generating...") : "Generate Response"}</button>
          {answer && <button className="secondary" onClick={handleGenerateQR} disabled={qrLoading || loading}>{qrLoading ? "Generating QR..." : "Generate QR Codes"}</button>}
        </div>
      </section>
      {answer && <section className="panel response-panel" aria-labelledby="response-title">
        <div className="response-header"><div className="section-heading"><span className="step">3</span><div><h2 id="response-title">Response</h2><p>Information from your document</p></div></div><div className="response-badges"><span className="badge">{answer.answer.mode === "fast" ? "ϟ Fast Retrieval" : "✧ AI Summary"}</span><span className="badge neutral">{answer.is_encrypted ? "Encrypted" : "Standard"}</span></div></div>
        {answer.answer.mode === "fast" ? <>
          {answer.answer.query !== undefined && <p className="query-summary"><strong>Query</strong><span>{answer.answer.query}</span></p>}
          <div className="chunk-list">{answer.answer.retrieved_information.length ? answer.answer.retrieved_information.map((chunk, index) => <section className="chunk-card" key={index}><h4>Chunk {chunk.chunk_number}</h4><p>{chunk.text}</p></section>) : <p>No relevant chunks were retrieved.</p>}</div>
        </> : <div className="ai-answer"><h3>Answer</h3><p>{answer.answer.answer}</p><h4>Facts</h4><ul>{answer.answer.facts.map((fact, index) => <li key={index}>{fact}</li>)}</ul></div>}
        <p className="source-chunks"><strong>Source chunks:</strong> {answer.answer.source_chunks.join(", ") || "None provided."}</p>
      </section>}
      {transfer && <section className="panel qr-output" aria-labelledby="qr-output-title">
        <div className="section-heading"><span className="section-icon" aria-hidden="true">▦</span><div><h2 id="qr-output-title">Generated QR Codes</h2><p>Upload these codes in the receiver to recover information</p></div></div>
        <div className="qr-output-meta"><span className="badge">{transfer.is_encrypted ? "Encrypted transfer" : "Standard transfer"}</span><p className="transfer-id">Transfer ID: {transfer.transfer_id}</p></div>
        <div className="qr-grid">{transfer.qr_urls.map((url, index) => <figure className="qr-card" key={url}><figcaption>QR {index + 1} of {transfer.qr_count}</figcaption><img src={url} alt={`QR ${index + 1} of ${transfer.qr_count}`} width="300" /></figure>)}</div>
      </section>}
      {answer && <section className="panel metrics-panel" aria-label="Transfer metrics"><div className="metrics-heading"><span className="section-icon teal" aria-hidden="true">▥</span><div><h3>Transfer Metrics</h3><p>Payload sizes and QR information</p></div></div><dl className="metrics-grid">
        <div><dt>Retrieved Context</dt><dd>{answer.size_metrics.retrieved_context_bytes.toLocaleString()} <small>B</small></dd><span>Original context</span></div>
        <div><dt>Compact Payload</dt><dd>{answer.size_metrics.compact_payload_bytes.toLocaleString()} <small>B</small></dd><span>After tokenization</span></div>
        <div><dt>Compressed Payload</dt><dd>{answer.size_metrics.compressed_payload_bytes.toLocaleString()} <small>B</small></dd><span>After compression</span></div>
        {answer.size_metrics.encrypted_payload_bytes !== null && <div><dt>Encrypted Payload</dt><dd>{answer.size_metrics.encrypted_payload_bytes.toLocaleString()} <small>B</small></dd><span>After encryption</span></div>}
        {transfer && <div><dt>QR Count</dt><dd>{transfer.qr_count}</dd><span>Total QR codes</span></div>}
      </dl></section>}
    </div>
  );
}

export default QueryDocument;
