import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const EXPECTED_WIDTH = 1536;
const EXPECTED_HEIGHT = 960;

function validatePostJson(botDir: string): void {
  const postPath = join(botDir, 'POST.json');
  let raw: string;
  try {
    raw = readFileSync(postPath, 'utf8');
  } catch (err) {
    process.stderr.write(`Error reading POST.json at ${postPath}: ${(err as Error).message}\n`);
    process.exit(1);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    process.stderr.write(`Error parsing JSON in POST.json: ${(err as Error).message}\n`);
    process.exit(1);
  }

  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    process.stderr.write('Error: POST.json must contain a JSON object\n');
    process.exit(1);
  }

  const postUrl = (parsed as { url?: unknown }).url;
  if (typeof postUrl !== 'string') {
    process.stderr.write('Error: POST.json missing or invalid "url" field\n');
    process.exit(1);
  }

  const xPostRegex = /^https:\/\/x\.com\/[A-Za-z0-9_]+\/status\/\d+$/;
  if (!xPostRegex.test(postUrl)) {
    process.stderr.write(`Error: "url" field is not a valid X post URL: ${postUrl}\n`);
    process.exit(1);
  }
}

function validateMemePng(botDir: string): void {
  const memePath = join(botDir, 'meme.png');
  let buf: Buffer;
  try {
    buf = readFileSync(memePath);
  } catch (err) {
    process.stderr.write(`Error reading meme.png at ${memePath}: ${(err as Error).message}\n`);
    process.exit(1);
  }

  if (buf.length < 24) {
    process.stderr.write(`Error: meme.png is too small to be a valid PNG (${buf.length} bytes)\n`);
    process.exit(1);
  }

  if (!buf.subarray(0, 8).equals(PNG_SIGNATURE)) {
    process.stderr.write('Error: meme.png does not match standard 8-byte PNG signature\n');
    process.exit(1);
  }

  const chunkType = buf.toString('ascii', 12, 16);
  if (chunkType !== 'IHDR') {
    process.stderr.write(`Error: expected first PNG chunk to be IHDR, found "${chunkType}"\n`);
    process.exit(1);
  }

  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    process.stderr.write(
      `Error: meme.png dimensions must be exactly ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}, got ${width}x${height}\n`
    );
    process.exit(1);
  }
}

function run(): void {
  validatePostJson(BOT_DIR);
  validateMemePng(BOT_DIR);

  try {
    mkdirSync(OUTPUT_DIR, { recursive: true });
    copyFileSync(join(BOT_DIR, 'POST.json'), join(OUTPUT_DIR, 'POST.json'));
    copyFileSync(join(BOT_DIR, 'meme.png'), join(OUTPUT_DIR, 'meme.png'));
  } catch (err) {
    process.stderr.write(`Error writing output files: ${(err as Error).message}\n`);
    process.exit(1);
  }
}

run();
