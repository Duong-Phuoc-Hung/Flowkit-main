import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { slug, updatedData } = body;

    if (!slug) {
      return NextResponse.json({ error: 'Missing slug' }, { status: 400 });
    }

    const filename = `${slug}.json`;
    const dir2 = path.join(process.cwd(), '..', '2_cho_duyet');
    const dir3 = path.join(process.cwd(), '..', '3_dang_render_anh');
    
    const sourcePath = path.join(dir2, filename);
    const destPath = path.join(dir3, filename);

    if (!fs.existsSync(sourcePath)) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    if (!fs.existsSync(dir3)) {
      fs.mkdirSync(dir3, { recursive: true });
    }

    // Write the updated data to the source file before moving
    if (updatedData) {
      fs.writeFileSync(sourcePath, JSON.stringify(updatedData, null, 2), 'utf-8');
    }

    // Move file
    fs.renameSync(sourcePath, destPath);

    return NextResponse.json({ success: true, message: 'Project approved successfully' });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
