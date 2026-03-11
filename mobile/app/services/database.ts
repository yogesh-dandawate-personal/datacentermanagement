/**
 * SQLite Database Service
 *
 * Offline data storage using react-native-sqlite-storage
 */

import SQLite from 'react-native-sqlite-storage';

// Enable debugging
SQLite.DEBUG(true);
SQLite.enablePromise(true);

const DATABASE_NAME = 'inetzero.db';
const DATABASE_VERSION = '1.0';
const DATABASE_DISPLAY_NAME = 'iNetZero Offline Database';
const DATABASE_SIZE = 200000;

let db: SQLite.SQLiteDatabase | null = null;

/**
 * Initialize database
 */
export const initDatabase = async (): Promise<void> => {
  try {
    db = await SQLite.openDatabase({
      name: DATABASE_NAME,
      location: 'default',
    });

    console.log('Database opened successfully');

    // Create tables
    await createTables();
  } catch (error) {
    console.error('Failed to open database:', error);
    throw error;
  }
};

/**
 * Create tables
 */
const createTables = async (): Promise<void> => {
  if (!db) {
    throw new Error('Database not initialized');
  }

  const tables = [
    // Energy Metrics Table
    `CREATE TABLE IF NOT EXISTS energy_metrics (
      id TEXT PRIMARY KEY,
      facility_id TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      power_kw REAL NOT NULL,
      energy_kwh REAL NOT NULL,
      pue REAL,
      temperature_c REAL,
      synced INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,

    // Emissions Table
    `CREATE TABLE IF NOT EXISTS emissions (
      id TEXT PRIMARY KEY,
      facility_id TEXT NOT NULL,
      date TEXT NOT NULL,
      scope1_kg REAL NOT NULL,
      scope2_kg REAL NOT NULL,
      scope3_kg REAL NOT NULL,
      total_kg REAL NOT NULL,
      synced INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,

    // Alarms Table
    `CREATE TABLE IF NOT EXISTS alarms (
      id TEXT PRIMARY KEY,
      facility_id TEXT NOT NULL,
      type TEXT NOT NULL,
      severity TEXT NOT NULL,
      message TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      acknowledged INTEGER DEFAULT 0,
      synced INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,

    // Sync Queue Table
    `CREATE TABLE IF NOT EXISTS sync_queue (
      id TEXT PRIMARY KEY,
      action_type TEXT NOT NULL,
      endpoint TEXT NOT NULL,
      method TEXT NOT NULL,
      payload TEXT,
      retries INTEGER DEFAULT 0,
      last_error TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
  ];

  for (const sql of tables) {
    await db.executeSql(sql);
  }

  console.log('All tables created successfully');
};

/**
 * Energy Metrics Operations
 */

export const saveEnergyMetrics = async (metrics: any[]): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const insertSql = `
    INSERT OR REPLACE INTO energy_metrics
    (id, facility_id, timestamp, power_kw, energy_kwh, pue, temperature_c, synced)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
  `;

  for (const metric of metrics) {
    await db.executeSql(insertSql, [
      metric.id,
      metric.facility_id,
      metric.timestamp,
      metric.power_kw,
      metric.energy_kwh,
      metric.pue || null,
      metric.temperature_c || null,
    ]);
  }

  console.log(`Saved ${metrics.length} energy metrics`);
};

export const getEnergyMetrics = async (facilityId: string): Promise<any[]> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `
    SELECT * FROM energy_metrics
    WHERE facility_id = ?
    ORDER BY timestamp DESC
    LIMIT 100
  `;

  const [result] = await db.executeSql(sql, [facilityId]);
  return result.rows.raw();
};

/**
 * Emissions Operations
 */

export const saveEmissions = async (emissions: any[]): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const insertSql = `
    INSERT OR REPLACE INTO emissions
    (id, facility_id, date, scope1_kg, scope2_kg, scope3_kg, total_kg, synced)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
  `;

  for (const emission of emissions) {
    await db.executeSql(insertSql, [
      emission.id,
      emission.facility_id,
      emission.date,
      emission.scope1_kg,
      emission.scope2_kg,
      emission.scope3_kg,
      emission.total_kg,
    ]);
  }

  console.log(`Saved ${emissions.length} emissions records`);
};

export const getEmissions = async (facilityId: string): Promise<any[]> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `
    SELECT * FROM emissions
    WHERE facility_id = ?
    ORDER BY date DESC
    LIMIT 100
  `;

  const [result] = await db.executeSql(sql, [facilityId]);
  return result.rows.raw();
};

/**
 * Alarms Operations
 */

export const saveAlarms = async (alarms: any[]): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const insertSql = `
    INSERT OR REPLACE INTO alarms
    (id, facility_id, type, severity, message, timestamp, acknowledged, synced)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
  `;

  for (const alarm of alarms) {
    await db.executeSql(insertSql, [
      alarm.id,
      alarm.facility_id,
      alarm.type,
      alarm.severity,
      alarm.message,
      alarm.timestamp,
      alarm.acknowledged ? 1 : 0,
    ]);
  }

  console.log(`Saved ${alarms.length} alarms`);
};

export const getAlarms = async (facilityId: string): Promise<any[]> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `
    SELECT * FROM alarms
    WHERE facility_id = ? AND acknowledged = 0
    ORDER BY timestamp DESC
  `;

  const [result] = await db.executeSql(sql, [facilityId]);
  return result.rows.raw();
};

export const acknowledgeAlarm = async (alarmId: string): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `UPDATE alarms SET acknowledged = 1 WHERE id = ?`;
  await db.executeSql(sql, [alarmId]);
  console.log(`Acknowledged alarm: ${alarmId}`);
};

/**
 * Sync Queue Operations
 */

export const addToSyncQueue = async (
  actionType: string,
  endpoint: string,
  method: string,
  payload: any
): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const id = Date.now().toString();
  const sql = `
    INSERT INTO sync_queue (id, action_type, endpoint, method, payload)
    VALUES (?, ?, ?, ?, ?)
  `;

  await db.executeSql(sql, [
    id,
    actionType,
    endpoint,
    method,
    JSON.stringify(payload),
  ]);

  console.log(`Added to sync queue: ${actionType}`);
};

export const getSyncQueue = async (): Promise<any[]> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `SELECT * FROM sync_queue WHERE retries < 3 ORDER BY created_at ASC`;
  const [result] = await db.executeSql(sql);
  return result.rows.raw();
};

export const removeFromSyncQueue = async (id: string): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `DELETE FROM sync_queue WHERE id = ?`;
  await db.executeSql(sql, [id]);
  console.log(`Removed from sync queue: ${id}`);
};

export const incrementSyncRetries = async (
  id: string,
  error: string
): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const sql = `UPDATE sync_queue SET retries = retries + 1, last_error = ? WHERE id = ?`;
  await db.executeSql(sql, [error, id]);
};

/**
 * Clear all data
 */
export const clearAllData = async (): Promise<void> => {
  if (!db) throw new Error('Database not initialized');

  const tables = ['energy_metrics', 'emissions', 'alarms', 'sync_queue'];

  for (const table of tables) {
    await db.executeSql(`DELETE FROM ${table}`);
  }

  console.log('All data cleared');
};

/**
 * Close database
 */
export const closeDatabase = async (): Promise<void> => {
  if (db) {
    await db.close();
    db = null;
    console.log('Database closed');
  }
};
