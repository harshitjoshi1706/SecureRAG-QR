import { useEffect, useRef, useState } from 'react';
import { decodeQRImage } from '../receiver/imageDecoder';
import { collectFragment, reconstructPacket } from '../receiver/protocol';
import type { Packet, RecoveredInformation, Transfer } from '../receiver/protocol';
import { recoverTransfer } from '../receiver/recovery';
import './QRReceiver.css';

const message = (error: unknown) => error instanceof Error ? error.message : 'Unable to process this transfer.';

export default function QRReceiver() {
  const [transfer, setTransfer] = useState<Transfer | null>(null);
  const [packet, setPacket] = useState<Packet | null>(null);
  const [password, setPassword] = useState('');
  const [result, setResult] = useState<RecoveredInformation | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);
  const locked = useRef(false);
  const request = useRef<AbortController | null>(null);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => () => {
    generation.current += 1;
    request.current?.abort();
  }, []);

  function reset() {
    generation.current += 1;
    request.current?.abort();
    locked.current = false;
    setBusy(false);
    setTransfer(null);
    setPacket(null);
    setPassword('');
    setResult(null);
    setErrors([]);
    setNotice('');
    if (input.current) input.current.value = '';
  }

  async function recover(current: Transfer, secret: string | undefined, token: number) {
    request.current = new AbortController();
    const recovered = await recoverTransfer(current, secret, request.current.signal);
    if (token !== generation.current) return;
    setResult(recovered);
    setPassword('');
    setNotice('Information recovered successfully.');
  }

  async function upload(files: File[]) {
    if (locked.current || !files.length) return;
    locked.current = true;
    setBusy(true);
    setErrors([]);
    setNotice('Reading QR images…');
    const token = generation.current;
    const failures: string[] = [];
    let current = transfer;
    let duplicates = 0;
    try {
      for (const file of files) {
        try {
          const text = await decodeQRImage(file);
          if (token !== generation.current) return;
          const collected = collectFragment(current, text);
          current = collected.transfer;
          if (collected.duplicate) duplicates += 1;
          setTransfer(current);
        } catch (error) {
          if (token !== generation.current) return;
          failures.push(`${file.name}: ${message(error)}`);
        }
      }
      setNotice(duplicates ? `${duplicates} duplicate fragment(s) ignored.` : 'QR images processed.');
      if (current && Object.keys(current.fragments).length === current.total) {
        const assembled = reconstructPacket(current);
        setPacket(assembled);
        if (!assembled.encrypted && !result) await recover(current, undefined, token);
      }
    } catch (error) {
      failures.push(message(error));
    } finally {
      if (token === generation.current) {
        setErrors(failures);
        setBusy(false);
        locked.current = false;
      }
    }
  }

  async function retryRecovery() {
    if (!transfer || !packet || locked.current) return;
    locked.current = true;
    setBusy(true);
    setErrors([]);
    const token = generation.current;
    try { await recover(transfer, packet.encrypted ? password : undefined, token); }
    catch (error) { if (token === generation.current) setErrors([message(error)]); }
    finally {
      if (token === generation.current) {
        setBusy(false);
        locked.current = false;
      }
    }
  }

  const received = transfer ? Object.keys(transfer.fragments).length : 0;
  const complete = transfer !== null && received === transfer.total;
  const missing = transfer
    ? Array.from({ length: transfer.total }, (_, i) => i + 1).filter(i => !transfer.fragments[i])
    : [];

  return (
    <section className="qr-receiver" aria-labelledby="receiver-title">
      <header>
        <h2 id="receiver-title">SecureRAG-QR Receiver</h2>
        <p>Upload the QR images from one transfer, in any order.</p>
      </header>
      <div className="qr-upload">
        <label htmlFor="qr-images">Upload QR Image</label>
        <input ref={input} id="qr-images" type="file" accept="image/*" multiple disabled={busy}
          aria-describedby="qr-image-help"
          onChange={event => {
            const files = Array.from(event.currentTarget.files ?? []);
            event.currentTarget.value = '';
            void upload(files);
          }} />
        <p id="qr-image-help">Select one or more images, with one QR code per image. PNG or JPEG works best.</p>
      </div>
      <div className="qr-progress" aria-live="polite">
        <p><strong>Transfer ID:</strong> <span className="qr-transfer-id">{transfer?.id ?? '—'}</span></p>
        <p><strong>Fragments received:</strong> {received} / {transfer?.total ?? '—'}</p>
        <progress value={received} max={transfer?.total ?? 1} aria-label="Fragments received" />
        <p><strong>Status:</strong> {complete ? 'All fragments received' : 'Waiting for fragments'}</p>
        {missing.length > 0 && <p>Missing fragments: {missing.slice(0, 30).join(', ')}{missing.length > 30 ? '…' : ''}</p>}
        {packet && <p className="qr-mode">{packet.encrypted ? 'Encrypted transfer' : 'Standard transfer'}</p>}
      </div>
      {packet && !result && (
        <form onSubmit={event => { event.preventDefault(); void retryRecovery(); }}>
          {packet.encrypted && <>
            <label htmlFor="qr-password">Transfer password</label>
            <input id="qr-password" type="password" autoComplete="off" value={password}
              disabled={busy} onChange={event => setPassword(event.target.value)} required />
          </>}
          <button type="submit" disabled={busy || (packet.encrypted && !password)}>
            {busy ? 'Recovering…' : packet.encrypted ? 'Decrypt' : 'Recover information'}
          </button>
        </form>
      )}
      <p role="status">{busy ? 'Processing transfer…' : notice}</p>
      {errors.length > 0 && <div className="qr-errors" role="alert"><ul>
        {errors.map((error, index) => <li key={index}>{error}</li>)}
      </ul></div>}
      {result && <article className="qr-result">
        <h2>Recovered Information</h2>
        <h3>Answer</h3><p className="qr-answer">{result.answer}</p>
        <h3>Facts</h3>
        {result.facts.length ? <ul>{result.facts.map((fact, i) => <li key={i}>{fact}</li>)}</ul> : <p>No facts provided.</p>}
        <h3>Source Chunks</h3><p>{result.source_chunks.join(', ') || 'None provided.'}</p>
      </article>}
      <button type="button" className="qr-reset" onClick={reset}>Clear / Reset Transfer</button>
    </section>
  );
}
