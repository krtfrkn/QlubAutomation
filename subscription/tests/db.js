import { Client } from 'pg';
import 'dotenv/config';

// Reuses the same db-customer tunnel/credentials already documented in this
// skill's DB Helpers section (tsh tunnel on 127.0.0.1:5433, SELECT-only).
// Credentials come from .env (see .env.example) — never hardcode them here.
//
// connectionTimeoutMillis/query_timeout are REQUIRED here — confirmed live
// on 2026-08-07: without them, a stalled tsh tunnel/handshake made
// client.connect() hang indefinitely, which not only stalled the test past
// its own test.setTimeout but kept the whole `npx playwright test` process
// alive afterward (a dangling open socket keeps Node's event loop alive).
// Every DB call here is already non-blocking (callers wrap it in
// `.catch(() => [])`), so failing fast is strictly better than hanging.
const DB_CONFIG = {
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: false,
  connectionTimeoutMillis: 5000,
  query_timeout: 5000,
};

export async function getCustomerMappingByPhone(phone) {
  const client = new Client(DB_CONFIG);
  await client.connect();
  try {
    const res = await client.query(
      `SELECT * FROM "public"."cust_customer_mapping"
       WHERE cust_id IN (
         SELECT cust_id FROM "public"."cust_customer_mapping"
         WHERE extra_info ->> 'phone' = $1
       )
       ORDER BY id DESC LIMIT 50`,
      [phone],
    );
    return res.rows;
  } finally {
    await client.end();
  }
}

export function findSubscriptionRow(rows) {
  return rows.find((r) => r.module_cat === 'subscription');
}
