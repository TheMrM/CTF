#!/usr/bin/env python3
import sys, re, os, csv, random
from datetime import datetime

# ===== geometry (exactly like server) =====
POINTS = [(x, y) for x in range(3) for y in range(3)]

def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

def valid_segment(a, b):
    if a == b: return False
    dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
    return gcd(dx, dy) == 1 and 0 <= a[0] <= 2 and 0 <= a[1] <= 2 and 0 <= b[0] <= 2 and 0 <= b[1] <= 2

SEGMENTS = []
for i in range(len(POINTS)):
    for j in range(i+1, len(POINTS)):
        a, b = POINTS[i], POINTS[j]
        if valid_segment(a, b):
            SEGMENTS.append(tuple(sorted([a, b])))
assert len(SEGMENTS) == 28
SEG_INDEX = {SEGMENTS[i]: i for i in range(28)}

def rot_point(p, k):
    x, y = p; cx = cy = 1
    x0, y0 = x - cx, y - cy
    for _ in range(k % 4):
        x0, y0 = -y0, x0
    return (x0 + cx, y0 + cy)

def rot_segment(seg, k):
    a, b = seg
    A, B = tuple(sorted([rot_point(a, k), rot_point(b, k)]))
    return (A, B)

def canon_bits(segs):
    best = None
    for k in (0,1,2,3):
        bits = 0
        for (a, b) in segs:
            A, B = tuple(sorted([a, b]))
            rs = rot_segment((A, B), k)
            bits |= (1 << SEG_INDEX[rs])
        if best is None or bits < best:
            best = bits
    return best

# ===== logging (toggle with LOG=1) =====
LOG = os.getenv("LOG") == "1"
ts = datetime.now().strftime("%Y%m%d_%H%M%S") if LOG else ""
transcript = open(f"transcript_{ts}.txt","w",buffering=1,encoding="utf-8") if LOG else None
p1csv = open(f"phase1_map_{ts}.csv","w",newline="",encoding="utf-8") if LOG else None
p2csv = open(f"phase2_answers_{ts}.csv","w",newline="",encoding="utf-8") if LOG else None
p1w = csv.writer(p1csv) if LOG else None
p2w = csv.writer(p2csv) if LOG else None
if LOG:
    p1w.writerow(["canon_bits_decimal","N"])
    p2w.writerow(["query_idx","m","canon_bits_decimal","answered_N","server_reply"])

def _log_in(s):  # from server
    if transcript: transcript.write(f"< {s}\n")
def _log_out(s): # to server
    if transcript: transcript.write(f"> {s}\n")

# ===== I/O helpers =====
INTS = re.compile(r"-?\d+")

def rl():
    s = sys.stdin.readline()
    if not s:
        raise EOFError("server closed")
    s = s.rstrip("\r\n")
    _log_in(s)
    return s

def sendln(s):
    msg = str(s)
    _log_out(msg)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

# ===== Phase 1 pattern generator (unique signatures) =====
def gen_unique_pattern(used, min_sz=9, max_sz=14):
    while True:
        m = random.randint(min_sz, max_sz)
        segs = sorted(random.sample(SEGMENTS, m))
        c = canon_bits(segs)
        if c not in used:
            used.add(c)
            return segs, c

# ===== main solver =====
def main():
    random.seed(0xC0FFEE)  # our determinism only
    canon2N = {}
    used_sigs = set()

    # Banner
    rl()

    # Phase 1
    while True:
        line = rl()
        if "=== Phase 2 ===" in line:
            break
        if "N_" in line and ":" in line:
            nums = INTS.findall(line)
            if not nums:
                continue
            N = int(nums[-1])

            segs, c = gen_unique_pattern(used_sigs)
            canon2N[c] = N
            if LOG: p1w.writerow([str(c), str(N)])

            sendln(len(segs))
            for (a, b) in segs:
                sendln(f"{a[0]} {a[1]} {b[0]} {b[1]}")
            _ = rl()  # "OK"

    # Phase 2
    qidx = 0
    while True:
        try:
            line = rl()
        except EOFError:
            break

        if "MutatedPattern:" in line:
            qidx += 1
            m = int(rl())
            segs = []
            for _ in range(m):
                x1, y1, x2, y2 = map(int, INTS.findall(rl()))
                A, B = tuple(sorted([(x1, y1), (x2, y2)]))
                segs.append((A, B))
            c = canon_bits(segs)
            N = canon2N.get(c, 0)
            sendln(N)
            reply = rl()  # "OK" or "Wrong ..."
            if LOG: p2w.writerow([qidx, m, str(c), str(N), reply])

        elif "All correct! Here is your flag:" in line:
            flag = rl()
            # also echo to stderr so it shows even if stdout is piped
            print(flag, file=sys.stderr)
            try:
                with open("flag.txt","w",encoding="utf-8") as f: f.write(flag+"\n")
            except: pass
            break

        elif "You solved" in line:  # partial score
            break

if __name__ == "__main__":
    try:
        main()
    finally:
        if transcript: transcript.close()
        if p1csv: p1csv.close()
        if p2csv: p2csv.close()

