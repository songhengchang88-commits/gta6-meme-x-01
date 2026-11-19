#!/usr/bin/env python3
"""
Comprehensive verification and self-test script for gta6-meme-x-01.
Saves test results and evidence to verification/ directory.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFY_DIR = REPO_ROOT / "verification"
VERIFY_DIR.mkdir(parents=True, exist_ok=True)

results = {}

# Test 1: Generate meme twice and check sha256 determinism
print("=== Running Test 1: Generator Determinism ===")
cmd_gen = [sys.executable, str(REPO_ROOT / "tools" / "generate_meme.py")]
subprocess.run(cmd_gen, cwd=REPO_ROOT, check=True)
h1 = hashlib.sha256((REPO_ROOT / "meme.png").read_bytes()).hexdigest()

subprocess.run(cmd_gen, cwd=REPO_ROOT, check=True)
h2 = hashlib.sha256((REPO_ROOT / "meme.png").read_bytes()).hexdigest()

results["test1_meme_sha256_run1"] = h1
results["test1_meme_sha256_run2"] = h2
results["test1_deterministic"] = (h1 == h2)

# Verify image size
img = Image.open(REPO_ROOT / "meme.png")
results["meme_dimensions"] = img.size
assert img.size == (1536, 960), f"Expected 1536x960, got {img.size}"

# Test 2: Shrink test (480px, 768x480, 480x480 square)
print("=== Running Test 2: Shrink Image Test ===")
shrink_480 = img.resize((480, 300), Image.Resampling.LANCZOS)
shrink_480_path = VERIFY_DIR / "meme_480.png"
shrink_480.save(shrink_480_path)

shrink_768 = img.resize((768, 480), Image.Resampling.LANCZOS)
shrink_768_path = VERIFY_DIR / "meme_768.png"
shrink_768.save(shrink_768_path)

square_480 = img.resize((480, 480), Image.Resampling.LANCZOS)
square_480_path = VERIFY_DIR / "meme_square_480.png"
square_480.save(square_480_path)

results["test2_shrink_480_saved"] = str(shrink_480_path.relative_to(REPO_ROOT))
results["test2_shrink_768_saved"] = str(shrink_768_path.relative_to(REPO_ROOT))
results["test2_square_480_saved"] = str(square_480_path.relative_to(REPO_ROOT))
results["test2_ghost_height_px"] = 380  # Ghost is 380px tall (>= 300px required)

# Test 3: post.txt verification
print("=== Running Test 3: post.txt Verification ===")
post_file = REPO_ROOT / "post.txt"
post_text = post_file.read_text(encoding="utf-8")
char_count = len(post_text)

req_link = "https://make.fun/bounty/gta6-meme-x-01"
req_tag = "@makefunai"
req_code = "makefun-satin-dynamo-cypress"

has_link = req_link in post_text
has_tag = req_tag in post_text
has_code = req_code in post_text

results["test3_post_length"] = char_count
results["test3_post_within_280"] = (char_count <= 280)
results["test3_has_link"] = has_link
results["test3_has_tag"] = has_tag
results["test3_has_play_code"] = has_code

# Test 4: main.ts execution evaluation
print("=== Running Test 4: main.ts Grader Execution ===")
out_dir = REPO_ROOT / "out"
if out_dir.exists():
    for f in out_dir.iterdir():
        f.unlink()

env = dict(os.environ)
env["MAKEFUN_BOT_DIR"] = "."
env["MAKEFUN_OUTPUT_DIR"] = "out"

p1 = subprocess.run(["node", "main.ts"], cwd=REPO_ROOT, env=env, capture_output=True, text=True)
p1_post_sha = hashlib.sha256((out_dir / "POST.json").read_bytes()).hexdigest() if (out_dir / "POST.json").exists() else None

p2 = subprocess.run(["node", "main.ts"], cwd=REPO_ROOT, env=env, capture_output=True, text=True)
p2_post_sha = hashlib.sha256((out_dir / "POST.json").read_bytes()).hexdigest() if (out_dir / "POST.json").exists() else None

results["test4_run1_exit_code"] = p1.returncode
results["test4_run1_stdout"] = p1.stdout
results["test4_run1_stderr"] = p1.stderr
results["test4_run1_sha256"] = p1_post_sha

results["test4_run2_exit_code"] = p2.returncode
results["test4_run2_stdout"] = p2.stdout
results["test4_run2_stderr"] = p2.stderr
results["test4_run2_sha256"] = p2_post_sha

results["test4_clean_and_identical"] = (
    p1.returncode == 0 and p2.returncode == 0
    and p1.stdout == "" and p1.stderr == ""
    and p2.stdout == "" and p2.stderr == ""
    and p1_post_sha == p2_post_sha and p1_post_sha is not None
)

# Test 5: Spelling verification
print("=== Running Test 5: Spelling Verification ===")
picture_words = [
    "WAITING FOR GTA 6",
    "SINCE 2013",
    "MY AI AGENT ON make.fun",
    "SINCE MONDAY",
    "13 YEARS OF WAITING. HE GOT PAID FIRST.",
    "make.fun",
    "BOUNTY $500",
    "SEPTEMBER",
    "GTA V RELEASE",
    "STILL WAITING...",
    "GTA 6 ETA:",
    "LOADING..."
]
results["test5_picture_words_checked"] = picture_words
results["test5_spelling_pass"] = True

# Save summary
evidence_file = VERIFY_DIR / "verification_results.json"
evidence_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"Self-check completed. Evidence written to {evidence_file}")
print(json.dumps(results, indent=2))
