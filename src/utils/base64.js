/**
 * Base64 Encoding/Decoding Utilities
 */

import { logger } from '../config/audio-config';

/**
 * Convert ArrayBuffer to Base64 string
 * @param {ArrayBuffer} buffer
 * @returns {string}
 */
export function arrayBufferToBase64(buffer) {
  logger.audio('Converting ArrayBuffer to Base64', `size: ${buffer.byteLength} bytes`);

  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;

  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }

  const base64 = window.btoa(binary);
  logger.audio('Base64 conversion complete', `output length: ${base64.length}`);

  return base64;
}

/**
 * Convert Base64 string to ArrayBuffer
 * @param {string} base64
 * @returns {ArrayBuffer}
 */
export function base64ToArrayBuffer(base64) {
  logger.audio('Converting Base64 to ArrayBuffer', `input length: ${base64.length}`);

  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);

  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  logger.audio('ArrayBuffer conversion complete', `size: ${bytes.buffer.byteLength} bytes`);

  return bytes.buffer;
}

/**
 * Convert Float32Array to 16-bit PCM
 * @param {Float32Array} float32Array
 * @returns {ArrayBuffer}
 */
export function float32ToPCM16(float32Array) {
  logger.audio('Converting Float32 to PCM16', `samples: ${float32Array.length}`);

  const pcm16 = new Int16Array(float32Array.length);

  for (let i = 0; i < float32Array.length; i++) {
    // Clamp to [-1, 1] and scale to 16-bit range
    const s = Math.max(-1, Math.min(1, float32Array[i]));
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }

  logger.audio('PCM16 conversion complete', `bytes: ${pcm16.buffer.byteLength}`);

  return pcm16.buffer;
}

/**
 * Convert Int16Array to Float32Array
 * @param {Int16Array} int16Array
 * @returns {Float32Array}
 */
export function pcm16ToFloat32(int16Array) {
  logger.audio('Converting PCM16 to Float32', `samples: ${int16Array.length}`);

  const float32 = new Float32Array(int16Array.length);

  for (let i = 0; i < int16Array.length; i++) {
    float32[i] = int16Array[i] / 32768.0;
  }

  logger.audio('Float32 conversion complete');

  return float32;
}
