import { useState } from "react";
import api from "../services/api";

type Props = {
  documentId: string;
};

type TransferResponse = {
  transfer_id: string;
  fragment_count: number;
  qr_count: number;
  qr_urls: string[];
  answer: {
    answer: string;
    facts: string[];
    source_chunks: number[];
  };
  size_metrics: {
    retrieved_context_bytes: number;
    compact_payload_bytes: number;
    compressed_payload_bytes: number;
    encrypted_payload_bytes: number;
  };
};

function QueryDocument({ documentId }: Props) {
  const [query, setQuery] = useState("");
  const [password, setPassword] = useState("");

  const [answer, setAnswer] = useState<any>(null);
  const [transfer, setTransfer] = useState<TransferResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [qrLoading, setQrLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) {
      alert("Enter a question.");
      return;
    }

    if (!password.trim()) {
      alert("Enter an encryption password.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post(
        "/api/query/answer",
        {
          query,
          document_id: documentId,
          password,
          top_k: 3,
        }
      );

      setAnswer(response.data);
      setTransfer(null);
    } catch (error) {
      console.error(error);
      alert("Query failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQR = async () => {
    if (!query.trim()) {
      alert("Enter a question first.");
      return;
    }

    if (!password.trim()) {
      alert("Enter an encryption password.");
      return;
    }

    try {
      setQrLoading(true);

      const response = await api.post(
        "/api/transfer/generate",
        {
          query,
          document_id: documentId,
          password,
          top_k: 3,
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

      <input
        type="password"
        value={password}
        onChange={(event) => {
          setPassword(event.target.value);
        }}
        placeholder="Encryption password"
      />

      <br />

      <button
        onClick={handleQuery}
        disabled={loading}
      >
        {loading ? "Generating..." : "Ask"}
      </button>

      {answer && (
        <div>
          <h3>Answer</h3>

          <p>{answer.answer.answer}</p>

          <h4>Facts</h4>

          <ul>
            {answer.answer.facts.map(
              (fact: string, index: number) => (
                <li key={index}>{fact}</li>
              )
            )}
          </ul>

          <h4>Source Chunks</h4>

          <p>
            {answer.answer.source_chunks.join(", ")}
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

          <p>
            Encrypted:{" "}
            {answer.size_metrics.encrypted_payload_bytes} bytes
          </p>

          <button
            onClick={handleGenerateQR}
            disabled={qrLoading}
          >
            {qrLoading
              ? "Generating QR..."
              : "Generate Secure QR"}
          </button>
        </div>
      )}

      {transfer && (
        <div>
          <h3>Secure QR Transfer</h3>

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