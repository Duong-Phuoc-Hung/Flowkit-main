import { NextResponse } from 'next/server';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execAsync = util.promisify(exec);

export async function POST(request: Request) {
  try {
    const { url, topic } = await request.json();
    
    if (!url || !topic) {
      return NextResponse.json({ error: 'Missing url or topic' }, { status: 400 });
    }

    const scriptPath = path.join(process.cwd(), '..', 'scripts', 'spy_clone.py');
    const { stdout, stderr } = await execAsync(`python "${scriptPath}" "${url}" "${topic}"`);

    if (stdout.includes('SUCCESS')) {
      const parts = stdout.split('SUCCESS');
      const details = parts[1].trim().split('\n');
      return NextResponse.json({ success: true, project: details[0], rules: details[1] });
    } else {
      return NextResponse.json({ error: stderr || stdout }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
