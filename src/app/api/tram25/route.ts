import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const dir35 = path.join(process.cwd(), '..', '3.5_cho_duyet_anh');
    if (!fs.existsSync(dir35)) return NextResponse.json({ pending: [] });
    
    const files = fs.readdirSync(dir35).filter(f => f.endsWith('.json'));
    const pending = [];
    
    for (const file of files) {
      const content = fs.readFileSync(path.join(dir35, file), 'utf-8');
      const data = JSON.parse(content);
      const vid = data.video_id;
      
      let scenes = [];
      if (vid) {
        try {
          const res = await fetch(`http://127.0.0.1:8100/api/videos/${vid}/scenes`);
          if (res.ok) scenes = await res.json();
        } catch(e) {}
      }
      
      pending.push({
        filename: file,
        slug: file.replace('.json', ''),
        data: data,
        scenes: scenes
      });
    }
    
    return NextResponse.json({ pending });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { action, scene_id, video_id, slug } = await request.json();
    
    if (action === 'REGENERATE') {
      await fetch('http://127.0.0.1:8100/api/requests/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requests: [{ type: "REGENERATE_IMAGE", scene_id, video_id }] })
      });
      return NextResponse.json({ success: true });
    }
    
    if (action === 'APPROVE') {
      const filename = `${slug}.json`;
      const src = path.join(process.cwd(), '..', '3.5_cho_duyet_anh', filename);
      const dest = path.join(process.cwd(), '..', '3.8_dang_dung_video', filename);
      if (!fs.existsSync(path.dirname(dest))) fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.renameSync(src, dest);
      return NextResponse.json({ success: true });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
