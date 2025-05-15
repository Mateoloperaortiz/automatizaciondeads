import crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 16; // For AES-GCM, the IV is typically 12 bytes, but 16 bytes (128 bits) is also common and secure.
// Node.js crypto.createCipheriv for GCM defaults to 12 bytes if not specified for the cipher.
// However, it's good practice to be explicit. Let's stick to 12 for GCM standard.
const GCM_IV_LENGTH = 12;
const AUTH_TAG_LENGTH = 16; // GCM auth tag is typically 16 bytes (128 bits)

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;

if (!ENCRYPTION_KEY || ENCRYPTION_KEY.length !== 64) { // 32 bytes = 64 hex characters
  throw new Error(
    'Invalid ENCRYPTION_KEY. Please set a 64-character hex string (32 bytes) in your .env file.'
  );
}

const key = Buffer.from(ENCRYPTION_KEY, 'hex');

/**
 * Encrypts a plain text string.
 * @param text The plain text to encrypt.
 * @returns A string containing the IV, auth tag, and ciphertext, concatenated and hex-encoded.
 *          Format: ivHex:authTagHex:ciphertextHex
 */
export function encrypt(text: string): string {
  if (!text) {
    return '';
  }
  try {
    const iv = crypto.randomBytes(GCM_IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
  } catch (error) {
    console.error('Encryption failed:', error);
    throw new Error('Encryption process failed.');
  }
}

/**
 * Decrypts a string that was encrypted with the encrypt function.
 * @param encryptedText The hex-encoded string (iv:authTag:ciphertext) to decrypt.
 * @returns The original plain text.
 */
export function decrypt(encryptedText: string): string {
  if (!encryptedText) {
    return '';
  }
  try {
    const parts = encryptedText.split(':');
    if (parts.length !== 3) {
      throw new Error('Invalid encrypted text format. Expected iv:authTag:ciphertext');
    }

    const iv = Buffer.from(parts[0], 'hex');
    const authTag = Buffer.from(parts[1], 'hex');
    const ciphertext = parts[2];

    if (iv.length !== GCM_IV_LENGTH) {
      throw new Error(`Invalid IV length. Expected ${GCM_IV_LENGTH} bytes.`);
    }
    if (authTag.length !== AUTH_TAG_LENGTH) {
      throw new Error(`Invalid authTag length. Expected ${AUTH_TAG_LENGTH} bytes.`);
    }

    const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(ciphertext, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  } catch (error) {
    console.error('Decryption failed:', error);
    // In a real app, be careful about exposing too much detail from decryption errors.
    // For now, rethrowing to indicate failure clearly.
    throw new Error('Decryption process failed. Invalid key, IV, auth tag, or ciphertext.');
  }
}
