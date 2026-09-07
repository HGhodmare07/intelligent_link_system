const ALPHABET =
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

const BASE = ALPHABET.length; // 62

function encode(num) {
  if (typeof num !== 'number' || num < 0 || !Number.isFinite(num)) {
    throw new Error('encode() expects a non-negative finite number');
  }

  if (num === 0) return ALPHABET[0];

  let result = '';
  let n = num;

  while (n > 0) {
    result = ALPHABET[n % BASE] + result;
    n = Math.floor(n / BASE);
  }

  return result;
}

function decode(str) {
  if (typeof str !== 'string' || str.length === 0) {
    throw new Error('decode() expects a non-empty string');
  }

  let result = 0;

  for (const char of str) {
    const value = ALPHABET.indexOf(char);

    if (value === -1) {
      throw new Error(`Invalid Base62 character: "${char}"`);
    }

    result = result * BASE + value;
  }

  return result;
}

module.exports = {
  encode,
  decode,
  ALPHABET,
  BASE
};