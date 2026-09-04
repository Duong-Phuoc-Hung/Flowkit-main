import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const dir2 = path.join(process.cwd(), '..', '2_cho_duyet');
    if (!fs.existsSync(dir2)) {
      return NextResponse.json({ pending: [] });
    }

    const files = fs.readdirSync(dir2).filter(f => f.endsWith('.json'));
    const pending = files.map(file => {
      const content = fs.readFileSync(path.join(dir2, file), 'utf-8');
      return {
        filename: file,
        slug: file.replace('.json', ''),
        data: JSON.parse(content)
      };
    });

    return NextResponse.json({ pending });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { slug } = await request.json();
    if (!slug) {
      return NextResponse.json({ error: "Slug is required" }, { status: 400 });
    }

    const dir2 = path.join(process.cwd(), '..', '2_cho_duyet');
    const filePath = path.join(dir2, `${slug}.json`);

    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      return NextResponse.json({ message: `Đã xóa kịch bản ${slug}` });
    }

    return NextResponse.json({ error: "File not found" }, { status: 404 });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
