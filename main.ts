import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

function validatePostJson(botDir: string): void {
  const postPath = join(botDir, 'POST.json');
  let raw: string;
  try {
    raw = readFileSync(postPath, 'utf8');
  } catch (err) {
    process.stderr.write(`Error: unable to read POST.json at ${postPath}: ${(err as Error).message}\n`);
    process.exit(1);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    process.stderr.write(`Error: invalid JSON in POST.json: ${(err as Error).message}\n`);
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

function run(): void {
  validatePostJson(BOT_DIR);

  try {
    mkdirSync(OUTPUT_DIR, { recursive: true });
    copyFileSync(join(BOT_DIR, 'POST.json'), join(OUTPUT_DIR, 'POST.json'));
  } catch (err) {
    process.stderr.write(`Error copying POST.json: ${(err as Error).message}\n`);
    process.exit(1);
  }
}

run();
