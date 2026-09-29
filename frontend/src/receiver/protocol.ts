export type Fragment = {
  version: 'SRQ1';
  transfer_id: string;
  fragment_index: number;
  fragment_total: number;
  payload: string;
};

export type Transfer = {
  id: string;
  total: number;
  fragments: Record<number, Fragment>;
};

export type Packet = {
  version: 'SRQ1';
  transfer_id: string;
  encrypted: boolean;
  payload: string;
  salt?: string;
  nonce?: string;
};

export type AISummary = {
  mode?: 'ai';
  answer: string;
  facts: string[];
  source_chunks: number[];
};

export type FastRetrieval = {
  mode: 'fast';
  query?: string;
  retrieved_information: { chunk_number: number; text: string }[];
  source_chunks: number[];
};

export type RecoveredInformation = AISummary | FastRetrieval;

function objectFromJSON(text: string): Record<string, unknown> {
  let value: unknown;
  try { value = JSON.parse(text); }
  catch { throw new Error('QR data contains malformed JSON.'); }
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('QR data must contain a JSON object.');
  }
  return value as Record<string, unknown>;
}

// Both uploaded images and a future camera decoder feed this same collector.
export function collectFragment(current: Transfer | null, text: string) {
  if (text.length > 4096) throw new Error('QR fragment exceeds the size limit.');
  const value = objectFromJSON(text);
  if (value.version !== 'SRQ1') throw new Error('This QR is not a SecureRAG-QR SRQ1 fragment.');
  if (typeof value.transfer_id !== 'string' || !value.transfer_id || value.transfer_id.length > 128) {
    throw new Error('Fragment has an invalid transfer ID.');
  }
  const index = value.fragment_index;
  const total = value.fragment_total;
  if (typeof total !== 'number' || !Number.isInteger(total) || total < 1 || total > 4096 ||
      typeof index !== 'number' || !Number.isInteger(index) || index < 1 || index > total) {
    throw new Error('Fragment has an invalid index or total.');
  }
  if (typeof value.payload !== 'string' || !value.payload) throw new Error('Fragment payload is missing.');
  const fragment = value as Fragment;
  if (current && current.id !== fragment.transfer_id) {
    throw new Error('This QR belongs to another transfer. Clear the current transfer first.');
  }
  if (current && current.total !== total) throw new Error('Fragment total does not match this transfer.');
  const existing = current?.fragments[index];
  if (existing) {
    if (existing.payload !== fragment.payload) throw new Error('Conflicting duplicate fragment. Clear and upload the original QR images.');
    return { transfer: current!, duplicate: true };
  }
  const fragments = { ...current?.fragments, [index]: fragment };
  if (Object.values(fragments).reduce((sum, item) => sum + item.payload.length, 0) > 4 * 1024 * 1024) {
    throw new Error('Transfer exceeds the receiver size limit.');
  }
  return { transfer: { id: fragment.transfer_id, total, fragments }, duplicate: false };
}

export function reconstructPacket(transfer: Transfer): Packet {
  if (Object.keys(transfer.fragments).length !== transfer.total) {
    throw new Error('Missing fragments. Upload all QR images before recovery.');
  }
  const text = Array.from({ length: transfer.total }, (_, index) => transfer.fragments[index + 1].payload).join('');
  const value = objectFromJSON(text);
  if (value.version !== 'SRQ1' || value.transfer_id !== transfer.id || typeof value.encrypted !== 'boolean') {
    throw new Error('Reconstructed packet has an invalid version, transfer ID, or encryption flag.');
  }
  if (typeof value.payload !== 'string' || !value.payload) throw new Error('Packet payload is missing.');
  if (value.encrypted && (typeof value.salt !== 'string' || !value.salt || typeof value.nonce !== 'string' || !value.nonce)) {
    throw new Error('Encrypted packet is missing its salt or nonce.');
  }
  return value as Packet;
}
