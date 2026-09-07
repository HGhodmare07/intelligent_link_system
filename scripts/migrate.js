require('dotenv').config();

const fs = require('fs');
const path = require('path');
const pool = require('../src/config/db');

async function migrate() {
  const sqlPath = path.join(
    __dirname,
    '..',
    'migrations',
    '001_create_urls_table.sql'
  );

  const sql = fs.readFileSync(sqlPath, 'utf8');

  try {
    await pool.query(sql);
    console.log('Migration applied: urls table is ready.');
  } catch (err) {
    console.error('Migration failed:', err);
    process.exitCode = 1;
  } finally {
    await pool.end();
  }
}

migrate();