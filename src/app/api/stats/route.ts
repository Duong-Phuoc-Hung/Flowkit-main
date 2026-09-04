import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import sqlite3 from 'sqlite3';

export async function GET() {
  try {
    const statusFile = path.join(process.cwd(), '..', 'config', 'status.json');
    let phase = '';
    let progress = 0;
    let log = '';
    
    if (fs.existsSync(statusFile)) {
      try {
        const statusData = JSON.parse(fs.readFileSync(statusFile, 'utf-8'));
        phase = statusData.phase || '';
        progress = statusData.progress || 0;
        log = statusData.log || '';
      } catch (e) {}
    }

    const dbPath = path.join(process.cwd(), '..', 'flow_agent.db');
    let stats = { PENDING: 0, PROCESSING: 0, COMPLETED: 0, FAILED: 0 };

    if (fs.existsSync(dbPath)) {
      stats = await new Promise((resolve, reject) => {
        const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
          if (err) resolve(stats);
        });
        db.all("SELECT status, COUNT(*) as count FROM request GROUP BY status", [], (err, rows) => {
          db.close();
          if (err) resolve(stats);
          else {
            const res = { PENDING: 0, PROCESSING: 0, COMPLETED: 0, FAILED: 0 };
            (rows as Array<{ status: string; count: number }>).forEach((row) => {
              if (row.status in res) (res as Record<string, number>)[row.status] = row.count;
            });
            resolve(res);
          }
        });
      });
    }

    return NextResponse.json({ phase, progress, log, queue: stats });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
