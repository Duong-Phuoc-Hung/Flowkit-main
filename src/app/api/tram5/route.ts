import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execAsync = util.promisify(exec);

export async function GET() {
  try {
    const exportsDir = path.join(process.cwd(), '..', 'output');
    let projects: string[] = [];
    if (fs.existsSync(exportsDir)) {
      projects = fs.readdirSync(exportsDir).filter(f => {
        const p = path.join(exportsDir, f);
        return fs.statSync(p).isDirectory() && fs.existsSync(path.join(p, `${f}_HOAN_CHINH.mp4`));
      });
    }
    return NextResponse.json({ projects });
  } catch (e) {
    return NextResponse.json({ projects: [] });
  }
}

export async function POST(request: Request) {
  try {
    const { slug, action } = await request.json();
    const scriptPath = action === 'seo' ? 'scripts/youtube_seo.py' : 'scripts/thumbnail_generator.py';
    
    // Call Python script
    const pyScript = path.join(process.cwd(), '..', scriptPath);
    const { stdout } = await execAsync(`python "${pyScript}" "${slug}"`);
    
    return NextResponse.json({ success: true, message: stdout });
  } catch (e) {
    return NextResponse.json({ success: false, message: (e as Error).message });
  }
}
