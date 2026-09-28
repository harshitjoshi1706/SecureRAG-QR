import axios from 'axios';
import api from '../../services/api';
import type { RecoveredInformation, Transfer } from './protocol';

// Swap this adapter for browser-local Argon2id/AES-GCM/Zstandard recovery later.
// This adapter only contacts the receiver endpoint; no query or RAG calls.
export async function recoverTransfer(
  transfer: Transfer,
  password?: string,
  signal?: AbortSignal,
): Promise<RecoveredInformation> {
  try {
    const { data } = await api.post<{ payload: RecoveredInformation }>(
      '/api/receiver/decode',
      {
        transfer_id: transfer.id,
        fragments: Object.values(transfer.fragments).map(fragment => JSON.stringify(fragment)),
        password,
      },
      { signal, timeout: 60000 },
    );
    return data.payload;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail: unknown = error.response?.data?.detail;
      if (typeof detail === 'string') throw new Error(detail);
      if (!error.response) throw new Error('Cannot reach the receiver backend. Check that it is available, then retry recovery.');
      throw new Error('The receiver could not process this transfer. Check the QR images and retry.');
    }
    throw error;
  }
}
