import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const type = formData.get('type') as string;
    const file = formData.get('file') as File | null;
    
    if (!file || !type) {
      return NextResponse.json({ error: 'Missing file or type' }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const configDir = path.join(process.cwd(), '..', 'config');
    if (!fs.existsSync(configDir)) fs.mkdirSync(configDir, { recursive: true });

    if (type === 'logo') {
      const dest = path.join(configDir, 'brand_logo.png');
      fs.writeFileSync(dest, buffer);
      return NextResponse.json({ success: true, message: 'Đã lưu Logo bản quyền!' });
    }
    
    if (type === 'voice') {
      const dest = path.join(configDir, 'voice_clone.wav');
      fs.writeFileSync(dest, buffer);
      return NextResponse.json({ success: true, message: 'Đã trích xuất giọng nói!' });
    }

    if (type === 'kloning') {
      const c_name = formData.get('c_name') as string;
      if (!c_name) return NextResponse.json({ error: 'Missing character name' }, { status: 400 });
      
      const tempPath = path.join(configDir, file.name);
      fs.writeFileSync(tempPath, buffer);
      
      // Call Google Flow API
      try {
        const res = await fetch('http://127.0.0.1:8100/api/flow/upload-image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_path: tempPath, file_name: file.name })
        });
        
        const data = await res.json();
        if (data.media_id) {
          const charsFile = path.join(configDir, 'characters.json');
          let chars: Record<string, string> = {};
          if (fs.existsSync(charsFile)) chars = JSON.parse(fs.readFileSync(charsFile, 'utf-8'));
          chars[c_name] = data.media_id;
          fs.writeFileSync(charsFile, JSON.stringify(chars, null, 2), 'utf-8');
          
          return NextResponse.json({ success: true, message: `Đã Kloning mặt cho nhân vật ${c_name}!` });
        } else {
          return NextResponse.json({ error: 'Lỗi từ Google Flow API: ' + JSON.stringify(data) }, { status: 500 });
        }
      } catch (e) {
        return NextResponse.json({ error: 'Không thể kết nối đến Máy chủ Python (Cổng 8100)' }, { status: 500 });
      }
    }

    return NextResponse.json({ error: 'Invalid type' }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
