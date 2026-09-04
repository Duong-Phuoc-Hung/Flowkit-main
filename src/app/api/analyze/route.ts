import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execAsync = util.promisify(exec);

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('image') as File | null;
    
    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    
    const uploadDir = path.join(process.cwd(), '..', 'config');
    const filePath = path.join(uploadDir, 'temp_chart.jpg');
    fs.writeFileSync(filePath, buffer);

    const scriptPath = path.join(process.cwd(), '..', 'scripts', 'ai_analyze.py');
    const { stdout, stderr } = await execAsync(`python "${scriptPath}" "${filePath}"`);
    
    // Clean up
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);

    if (stdout.includes('SUCCESS')) {
      const parts = stdout.split('SUCCESS');
      const rules = parts[1].trim();
      return NextResponse.json({ success: true, rules });
    } else {
      return NextResponse.json({ error: stderr || stdout }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function GET() {
  try {
    const learningFile = path.join(process.cwd(), '..', 'config', 'learning.json');
    if (fs.existsSync(learningFile)) {
      const data = JSON.parse(fs.readFileSync(learningFile, 'utf-8'));
      return NextResponse.json(data);
    }
    return NextResponse.json({ rules: "Chưa có quy luật nào." });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
