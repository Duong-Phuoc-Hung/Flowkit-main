import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { projName, idea, factCheck } = body;

    if (!projName || !idea) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // DEFENSE IN DEPTH: Chặn đứng Path Traversal và ký tự lạ ở tầng Server
    const safeProjName = String(projName).replace(/[^a-z0-9_-]/gi, '').toLowerCase();
    if (!safeProjName) {
      return NextResponse.json({ error: 'Invalid project name' }, { status: 400 });
    }

    const dir1 = path.join(process.cwd(), '..', '1_nhap_lieu');
    if (!fs.existsSync(dir1)) {
      fs.mkdirSync(dir1, { recursive: true });
    }

    let finalIdea = idea;
    if (factCheck) {
      finalIdea = "[FACT_CHECK_MODE]\n" + idea;
    }

    const filePath = path.join(dir1, `${safeProjName}.txt`);
    fs.writeFileSync(filePath, finalIdea, 'utf-8');

    return NextResponse.json({ success: true, message: 'Idea submitted successfully' });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
