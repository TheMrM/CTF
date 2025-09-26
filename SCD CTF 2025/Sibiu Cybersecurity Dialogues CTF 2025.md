# Extracted Linux Commands & Exercises

This document collects **all Linux exercises and commands** that appeared in the session — commands you ran, commands I suggested, helper one‑liners, and short descriptions so you can reproduce or study them. Organized by category.

> **Note:** This file was generated from the session transcript and contains commands that were executed, suggested, or discussed.

---

## 1) System & environment information

- `help` — list Bash builtins.
- `env` — print environment variables.
- `echo "Hello world"` — simple output test.
- `whoami` — show current user.
- `pwd` — print working directory (appeared in prompts).
- `uname -a` — kernel and build string.
- `cat /etc/os-release` — OS distribution information.
- `wc /etc/passwd` — word/line/byte counts for `/etc/passwd`.
- `cat /etc/passwd` — show local user accounts (mentioned).
- `date` / `uptime` — show date and system uptime (requested).

---

## 2) Files & listing tricks (builtins-only environment)

- `echo *` — glob expansion of non-hidden files.
- `echo .*` — glob expansion for hidden files.
- `for f in $(compgen -f); do echo "$f"; done` — enumerate files using builtin `compgen` when `ls` is not available.
- `compgen -d` — list directories.
- `compgen -f` — list files.
- `compgen -d /` and `compgen -f /` — list root subdirs/files.
- `compgen -d /var/lib/*` — list subdirectories under `/var/lib`.

---

## 3) Recursive search & find

- `find / -type d -name "*sql*" 2>/dev/null` — find directories with "sql" in name (MySQL/Postgres evidence).
- `find / -type f -name "*sql*" 2>/dev/null` — find files matching pattern.
- `find / -type f -name "*.db" 2>/dev/null` — find `.db` files (SQLite).
- `find / -type f -name "*.sqlite*" 2>/dev/null` — find SQLite files.

---

## 4) Directory listings & inspections

- `ls -l /var/lib/mysql` — inspect MySQL data directory contents.
- `ls -lR /var/lib/postgresql | head -50` — partial recursive listing for PostgreSQL dir.
- `ls -l /etc/mysql` — inspect MySQL config directory.
- `ls -l /etc/mysql/conf.d` — list MySQL conf.d files.
- `ls -l /etc/mysql/conf.d/*.cnf` — show details of conf files.
- `cat /etc/mysql/conf.d/mysql.cnf` — view the `mysql` client config (example).
- `cat /etc/mysql/conf.d/mysqldump.cnf` — view mysqldump config (example).

---

## 5) Reading files & permissions

- `cat /etc/mysql/debian.cnf` — attempted (permission denied; file usually owned by root).
- `cat decoded_C.txt` / `cat decoded_B.txt` / `cat output.txt` — examples of viewing locally generated files.
- `cat spectrogram.png` — image was uploaded (not appropriate for `cat`, but referenced).

---

## 6) Audio, spectrogram & steganography commands

- `ffmpeg -i audio.wav -lavfi showspectrumpic=s=1920x1080:legend=disabled:scale=log spectrogram.png` — create spectrogram (common invocation).
- `ffmpeg -i audio.wav -lavfi showspectrumpic=s=4096x1080:legend=disabled:scale=log spectrogram_wide.png` — wide spectrogram for long/horiz text.
- Note: When generating single-image outputs with FFmpeg, use `-frames:v 1` or `-update 1` to avoid sequence pattern warnings.
- (Suggested) `sox` alternatives: `sox audio.wav -n spectrogram -o spectrogram.png`.

---

## 7) Python environment & packaging

- `python3 -m venv enigma_env` — create virtualenv.
- `source enigma_env/bin/activate` — activate virtualenv.
- `pip install py-enigma` / `pip3 install py-enigma` — install Enigma support (attempts shown).
- `python3 decode_enigma.py` / `python decode.py` / `python3 something.py` — example scripts executed during challenge.
- `python3 -m pip install py-enigma` — alternative pip invocation.

---

## 8) Enigma decoding (Python) — sample patterns used

Example actions and function calls seen in scripts (py-enigma API):

```python
from enigma.machine import EnigmaMachine

machine = EnigmaMachine.from_key_sheet(
    rotors='I II III',
    reflector='C',
    ring_settings=[12,8,4],
    plugboard_settings='SE CU RI TY'
)

machine.set_display('LHD')  # or 'EJT' etc.
plaintext = machine.process_text(ciphertext)
```

Also common helper operations:
- `cleaned = plaintext.replace("X", "")` — strip Enigma padding
- grouping into 5s: `" ".join(cleaned[i:i+5] for i in range(0, len(cleaned), 5))`
- regex search for flags: `re.search(r'CSCTF\{.*?\}', cleaned, re.IGNORECASE)`

---

## 9) Binary / filesystem carving & YAFFS

- `binwalk` output references (YAFFS filesystem blocks found).
- External extractor attempt: `yaffshiv --auto --brute-force -f '%e' -d 'yaffs-root'` (failed: extractor missing).
- Advice noted: use `strings`, `grep`, or dedicated YAFFS tools for extracting embedded YAFFS images.

---

## 10) Database interaction attempts & tips

Commands suggested / tried to interact with DB servers:

- MySQL client attempts:
  - `mysql -u root`
  - `mysql -u root -p` (try empty password)
  - `mysql -u ctf`
  - `mysql -u debian-sys-maint` (credentials often stored in `/etc/mysql/debian.cnf`)

- PostgreSQL attempts:
  - `psql -U postgres`
  - `psql -U ctf`

- If authenticated, standard enumeration:
  - `SHOW DATABASES;` (MySQL)
  - `USE <db>; SHOW TABLES; SELECT * FROM <table>;`
  - `SELECT version();` (Postgres/MySQL variant)

---

## 11) Shell tricks & exploration

- `set` / `declare -p` / `export -p` — inspect shell variables and environment.
- `compgen -f` / `compgen -d` (used to enumerate files/dirs in restricted shells).
- `for f in $(compgen -f); do echo "$f"; done` — loop to print files when `ls` is disabled.
- When `cat` permission denied, inspect world-readable config directories (`/etc/mysql/conf.d`).

---

## 12) Decoding/crypto helper approaches used

- `base64.b32decode(...)` — Base32 decode in Python (with padding fixes).
- `binascii.hexlify(...)` — dump bytes to hex for magic header inspection.
- Single-byte XOR brute force (Python) example:

```python
for key in range(256):
    decoded = bytes(b ^ key for b in data)
    try:
        text = decoded.decode('utf-8')
        if 'CSCTF' in text.upper():
            print(key, text)
    except UnicodeDecodeError:
        pass
```

- Repeating-key XOR trial with key like `b"SECURITY"` (given challenge plugged `SE CU RI TY`).

---

## 13) Useful one-liners (portable)

- Read `code.txt`, decode with Enigma script pattern (example):
  - `python3 decode_enigma.py`
- Strip Xs and show grouped output:
  ```bash
  python3 - <<'PY'
  s = open('decoded_C.txt').read().replace('\n','').replace(' ','').replace('X','')
  print(' '.join(s[i:i+5] for i in range(0,len(s),5)))
  PY
  ```

- Quick `find` for databases:
  ```bash
  find / -type f -iname '*.db' -o -iname '*.sqlite*' 2>/dev/null
  ```

---

## 14) Reproduction options
Choose how you want this exported:

- (A) **Plain .md** (this document) — ready to copy/paste.
- (B) **commands_used.txt** — one command per line.
- (C) **run.sh** — wrapper that reproduces safe environment steps (non-destructive) and recreates output files.

Tell me which option you prefer (A/B/C) or if you want modifications — I can produce the requested artifact next.

