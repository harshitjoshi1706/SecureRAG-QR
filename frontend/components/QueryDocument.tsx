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
    <div>
      <h2>Ask Document</h2>

      <textarea
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
        }}
        placeholder="Ask a question about the document"
      />

      <br />

      <fieldset disabled={loading || qrLoading}>
        <legend>Processing Mode</legend>
        <label>
          <input type="radio" name="processing-mode" value="fast"
            checked={mode === "fast"} onChange={() => setMode("fast")} />
          Fast Retrieval
          <span style={{ display: "block" }}>Retrieve relevant document information directly.</span>
          <span style={{ display: "block" }}>Fast — no LLM required.</span>
        </label>
        <label>
          <input type="radio" name="processing-mode" value="ai"
            checked={mode === "ai"} onChange={() => setMode("ai")} />
          AI Summary
          <span style={{ display: "block" }}>Generate a concise answer using Qwen3:4B.</span>
          <span style={{ display: "block" }}>Slower — local LLM required.</span>
        </label>
      </fieldset>

      <h3>Transfer Type</h3>

      <label>
        <input
          type="radio"
          checked={!encrypt}
          onChange={() => {
            setEncrypt(false);
            setPassword("");
          }}
        />
        Standard QR
      </label>

      <br />

      <label>
        <input
          type="radio"
          checked={encrypt}
          onChange={() => {
            setEncrypt(true);
          }}
        />
        Encrypted QR
      </label>

      <br />

      {encrypt && (
        <>
          <input
            type="password"
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
            }}
            placeholder="Encryption password"
          />

          <br />
        </>
      )}

      <button
        onClick={handleQuery}
        disabled={loading || qrLoading}
      >
        {loading ? (mode === "fast" ? "Retrieving..." : "Generating...") : "Ask"}
      </button>

      {answer && (
        <div>
          {answer.answer.mode === "fast" ? (
            <>
              <h3>Retrieved Information</h3>
              <p>Query: {answer.answer.query}</p>
              {answer.answer.retrieved_information.length ? answer.answer.retrieved_information.map((chunk, index) => (
                <section key={index}>
                  <h4>Chunk {chunk.chunk_number}</h4>
                  <p style={{ whiteSpace: "pre-wrap" }}>{chunk.text}</p>
                </section>
              )) : <p>No relevant chunks were retrieved.</p>}
            </>
          ) : (
            <>
              <h3>Answer</h3>
              <p>{answer.answer.answer}</p>
              <h4>Facts</h4>
              <ul>
                {answer.answer.facts.map((fact, index) => (
                  <li key={index}>{fact}</li>
                ))}
              </ul>
            </>
          )}

          <h4>Source Chunks</h4>

          <p>
            {answer.answer.source_chunks.join(", ")}
          </p>

          <h4>Transfer Mode</h4>

          <p>Processing: {answer.answer.mode === "fast" ? "Fast Retrieval" : "AI Summary"}</p>

          <p>
            {answer.is_encrypted
              ? "Encrypted"
              : "Standard"}
          </p>

          <h4>Payload Sizes</h4>

          <p>
            Context:{" "}
            {answer.size_metrics.retrieved_context_bytes} bytes
          </p>

          <p>
            Compact:{" "}
            {answer.size_metrics.compact_payload_bytes} bytes
          </p>

          <p>
            Compressed:{" "}
            {answer.size_metrics.compressed_payload_bytes} bytes
          </p>

          {answer.size_metrics.encrypted_payload_bytes !== null && (
            <p>
              Encrypted:{" "}
              {answer.size_metrics.encrypted_payload_bytes} bytes
            </p>
          )}

          <button
            onClick={handleGenerateQR}
            disabled={qrLoading || loading}
          >
            {qrLoading
              ? "Generating QR..."
              : "Generate QR"}
          </button>
        </div>
      )}

      {transfer && (
        <div>
          <h3>QR Transfer</h3>

          <p>
            Mode:{" "}
            {transfer.is_encrypted
              ? "Encrypted"
              : "Standard"}
          </p>

          <p>
            Transfer ID: {transfer.transfer_id}
          </p>

          <p>
            QR Count: {transfer.qr_count}
          </p>

          {transfer.qr_urls.map(
            (url, index) => (
              <div key={url}>
                <p>
                  QR {index + 1} of {transfer.qr_count}
                </p>

                <img
                  src={url}
                  alt={`QR ${index + 1}`}
                  width="300"
                />
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}

export default QueryDocument;
