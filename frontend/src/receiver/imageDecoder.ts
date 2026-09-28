import jsQR from 'jsqr';

// Image decoding is independent of collection and recovery; a camera adapter can
// later pass its decoded text directly to collectFragment.
export async function decodeQRImage(file: File): Promise<string> {
  if (file.size > 20 * 1024 * 1024) throw new Error('Image exceeds the 20 MB limit.');
  if (!file.type.startsWith('image/')) throw new Error('Choose a QR image file.');
  let bitmap: ImageBitmap;
  try { bitmap = await createImageBitmap(file); }
  catch { throw new Error('Cannot open this image. Try a PNG or JPEG QR image.'); }
  try {
    if (bitmap.width * bitmap.height > 24_000_000) throw new Error('Image is too large. Crop it to the QR code first.');
    const canvas = document.createElement('canvas');
    canvas.width = bitmap.width;
    canvas.height = bitmap.height;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    if (!context) throw new Error('Image decoding is unavailable in this browser.');
    context.fillStyle = '#fff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(bitmap, 0, 0);
    const pixels = context.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(pixels.data, pixels.width, pixels.height, { inversionAttempts: 'attemptBoth' });
    if (!code) throw new Error('No readable QR code found. Use a clear image with one complete QR code.');
    return code.data;
  } finally { bitmap.close(); }
}
