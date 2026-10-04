const {
  encode,
  decode
} = require('./services/base62.service');

const testValues = [
  0n,
  1n,
  9n,
  10n,
  61n,
  62n,
  63n,
  123n,
  1000n,
  999999n
];

console.log('--- Base62 Test ---');

for (const value of testValues) {
  try {
    const encoded = encode(value);
    const decoded = decode(encoded);

    const passed = value === decoded;

    console.log(
      `${value.toString()} -> ${encoded} -> ${decoded.toString()} | ${
        passed ? 'PASS' : 'FAIL'
      }`
    );
  } catch (error) {
    console.log(
      `${value.toString()} | FAIL | ${error.message}`
    );
  }
}

// Test invalid character
console.log('\n--- Invalid Character Test ---');

try {
  decode('abc@123');
  console.log('FAIL - Invalid character was accepted');
} catch (error) {
  console.log('PASS - Invalid character rejected');
}