const ALPHABET =
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

const BASE = 62n;

/**
 * Encode a non-negative BigInt into Base62.
 *
 * Examples:
 * 0n  -> "0"
 * 61n -> "z"
 * 62n -> "10"
 */
function encode(num) {
  if (typeof num !== 'bigint' || num < 0n) {
    throw new Error(
      'encode() expects a non-negative BigInt (e.g., 123n)'
    );
  }

  if (num === 0n) {
    return ALPHABET[0];
  }

  let result = '';
  let n = num;

  while (n > 0n) {
    const remainder = Number(n % BASE);
    result = ALPHABET[remainder] + result;
    n = n / BASE;
  }

  return result;
}

/**
 * Decode a Base62 string into BigInt.
 *
 * Example:
 * "10" -> 62n
 */
function decode(str) {
  if (typeof str !== 'string' || str.length === 0) {
    throw new Error('decode() expects a non-empty string');
  }

  let result = 0n;

  for (const char of str) {
    const value = ALPHABET.indexOf(char);

    if (value === -1) {
      throw new Error(`Invalid Base62 character: "${char}"`);
    }

    result = result * BASE + BigInt(value);
  }

  return result;
}

module.exports = {
  encode,
  decode,
  ALPHABET,
  BASE
};