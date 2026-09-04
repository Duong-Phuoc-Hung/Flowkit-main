import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execAsync = util.promisify(exec);

export async function GET() {
  try {
    const exportsDir = path.join(process.cwd(), '..', 'exports');
    const musicDir = path.join(process.cwd(), '..', 'config', 'music');
    
    let projects: string[] = [];
    if (fs.existsSync(exportsDir)) {
      projects = fs.readdirSync(exportsDir).filter(f => {
        const p = path.join(exportsDir, f);
        return fs.statSync(p).isDirectory() && fs.existsSync(path.join(p, 'raw_concat.mp4'));
      });
    }

    let musicFiles: string[] = [];
    if (fs.existsSync(musicDir)) {
      musicFiles = fs.readdirSync(musicDir).filter(f => f.endsWith('.mp3') || f.endsWith('.wav'));
    }

    return NextResponse.json({ projects, musicFiles });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { action, project, musicFile } = await request.json();
    const exportsDir = path.join(process.cwd(), '..', 'exports');
    const configDir = path.join(process.cwd(), '..', 'config');

    if (action === 'mix') {
      if (!project || !musicFile) return NextResponse.json({ error: 'Missing params' }, { status: 400 });
      
      const rawVid = path.join(exportsDir, project, 'raw_concat.mp4');
      const bgmPath = path.join(configDir, 'music', musicFile);
      const finalOut = path.join(exportsDir, project, `${project}_HOAN_CHINH.mp4`);
      const logoPath = path.join(configDir, 'brand_logo.png');
      
      let cmd = '';
      if (fs.existsSync(logoPath)) {
        cmd = `ffmpeg -y -i "${rawVid}" -stream_loop -1 -i "${bgmPath}" -i "${logoPath}" -filter_complex "[2:v]scale=150:-1[logo];[0:v][logo]overlay=main_w-overlay_w-20:20[vout];[0:a]volume=1.0[orig];[1:a]volume=0.25[bgm];[orig][bgm]amix=inputs=2:duration=first[aout]" -map "[vout]" -map "[aout]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -shortest "${finalOut}"`;
      } else {
        cmd = `ffmpeg -y -i "${rawVid}" -stream_loop -1 -i "${bgmPath}" -filter_complex "[0:a]volume=1.0[orig];[1:a]volume=0.25[bgm];[orig][bgm]amix=inputs=2:duration=first[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest "${finalOut}"`;
      }

      await execAsync(cmd);
      return NextResponse.json({ success: true });
    }

    if (action === 'upload') {
      if (!project) return NextResponse.json({ error: 'Missing params' }, { status: 400 });
      const finalOut = path.join(exportsDir, project, `${project}_HOAN_CHINH.mp4`);
      if (!fs.existsSync(finalOut)) return NextResponse.json({ error: 'Chưa có file hoàn chỉnh' }, { status: 400 });
      
      const secretFile = path.join(configDir, 'client_secrets.json');
      if (!fs.existsSync(secretFile)) return NextResponse.json({ error: 'Chưa có file client_secrets.json' }, { status: 400 });

      const scriptPath = path.join(process.cwd(), '..', 'scripts', 'youtube_uploader.py');
      // Running it asynchronously without waiting since upload takes time
      exec(`python "${scriptPath}" "${finalOut}" "${project}"`);
      
      return NextResponse.json({ success: true, message: 'Đã gửi lệnh Upload lên Youtube!' });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
