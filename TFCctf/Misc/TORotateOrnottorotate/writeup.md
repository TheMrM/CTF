# TFCCTF — „To rotate, or not to rotate” (Write-up, RO)

> **Rezumat scurt:** Serverul lucrează cu **modele de segmente** pe o grilă 3×3.  
> **Faza 1:** pentru fiecare `N_i` trimiți un model (listă de segmente).  
> **Faza 2:** serverul îți trimite modele **rotite aleator** (0°, 90°, 180°, 270°), cu capete posibil inversate și ordine amestecată, și cere „**Your answer for N?**”.  
> **Cheia:** calculezi o **semnătură canonică** invariantă la rotație (`canon_bits`). În Faza 1 mapezi `semnătură → N`, în Faza 2 recalculezi semnătura și răspunzi cu `N`.

---

## Cuprins
- [Analiza](#analiza)
  - [Grila, segmentele și regula `gcd`](#grila-segmentele-și-regula-gcd)
  - [Rotațiile (90° CW/CCW)](#rotațiile-90-cwccw)
  - [Semnătura canonică (`canon_bits`)](#semnătura-canonică-canon_bits)
- [Strategia de rezolvare](#strategia-de-rezolvare)
- [Solver (Python)](#solver-python)
- [Rulare](#rulare)
  - [Remote cu `socat` (recomandat)](#remote-cu-socat-recomandat)
  - [Alternativ: `ncat` + FIFO](#alternativ-ncat--fifo)
- [Capcane & Debugging](#capcane--debugging)
- [Lessons learned](#lessons-learned)

---

## Analiza

### Grila, segmentele și regula `gcd`
Punctele sunt cele 9 coordonate ale grilei `(x,y)` cu `x,y ∈ {0,1,2}`.  
Un **segment** între două puncte distincte `(a,b)` este **valid** dacă:
- ambele capete sunt în grilă;
- `gcd(|dx|, |dy|) = 1`, adică nu „sare peste” un punct intermediar.

Totalul segmentelor valide este **28**. Serverul le indexează în `SEGMENTS` și construiește `SEG_INDEX[segment] = index`.

### Rotațiile (90° CW/CCW)
Rotația în jurul centrului `(1,1)`:

(x, y) -> (x-1, y-1) -> rotiri de 90° succesive -> + (1,1)

Aplici rotația capetelor și sortezi `(A,B)` astfel încât `A ≤ B` ⇒ `rot_segment(seg, k)`.

### Semnătura canonică (`canon_bits`)
Pentru o listă `segs`:
1. Pentru fiecare `k ∈ {0,1,2,3}`, rotești toate segmentele și setezi bitul corespondent (într-o mască pe 28 biți).
2. Alegi **minimul** dintre cele 4 măști. Acesta este **`canon_bits`** – invariant la rotație, inversare de capete și ordine.

**Concluzie:** două modele identice până la rotație au același `canon_bits`.

---

## Strategia de rezolvare

- **Faza 1 (training, Q=120):**
  - Serverul afișează `N_1: <N>`, `N_2: <N>`, …
  - Tu trimiți pentru fiecare `N` **un model** (subset de segmente valide).
  - Calculezi `canon_bits(model)` și salvezi `map[canon_bits] = N`.
  - ⚠️ Modelele trebuie să aibă **semnături unice** (altfel serverul refuză dacă aceeași semnătură apare la un alt `N`).

- **Faza 2 (quiz):**
  - Pentru fiecare „**MutatedPattern**”, citești `m` segmente.
  - Calculezi `canon_bits` al modelului **mutat** și cauți în `map`.
  - Răspunzi cu `N` ⇒ primești `OK`.  
  - După toate, primești **flag-ul** dacă scorul e complet.

---

## Solver (Python)

> Copiază logică identică serverului (grilă, rotații, `canon_bits`) și comunică linie-cu-linie pe `stdin/stdout`.

```python
#!/usr/bin/env python3
import sys, re, random

# --- Geometrie identică serverului ---
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
    x, y = p; x -= 1; y -= 1
    for _ in range(k & 3):
        x, y = -y, x
    return (x+1, y+1)

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

# --- IO helpers ---
INTS = re.compile(r"-?\d+")

def rl():
    s = sys.stdin.readline()
    if not s: raise EOFError("server closed")
    return s.rstrip("\r\n")

def sendln(x):
    sys.stdout.write(str(x) + "\n"); sys.stdout.flush()

# --- Generează modele cu semnături unice ---
def gen_unique(used, min_sz=9, max_sz=14):
    while True:
        m = random.randint(min_sz, max_sz)
        segs = sorted(random.sample(SEGMENTS, m))
        c = canon_bits(segs)
        if c not in used:
            used.add(c)
            return segs, c

def main():
    random.seed(0xC0FFEE)
    canon2N = {}
    used = set()

    rl()  # banner

    # Faza 1
    while True:
        line = rl()
        if "=== Phase 2 ===" in line:
            break
        if "N_" in line and ":" in line:
            N = int(INTS.findall(line)[-1])
            segs, c = gen_unique(used)
            canon2N[c] = N
            sendln(len(segs))
            for (a, b) in segs:
                sendln(f"{a[0]} {a[1]} {b[0]} {b[1]}")
            rl()  # "OK"

    # Faza 2
    while True:
        try:
            line = rl()
        except EOFError:
            break

        if "MutatedPattern:" in line:
            m = int(rl())
            segs = []
            for _ in range(m):
                x1, y1, x2, y2 = map(int, INTS.findall(rl()))
                A, B = tuple(sorted([(x1, y1), (x2, y2)]))
                segs.append((A, B))
            c = canon_bits(segs)
            sendln(canon2N.get(c, 0))
            rl()  # "OK" sau "Wrong ..."
        elif "All correct!" in line:
            flag = rl()
            print(flag, file=sys.stderr)  # ca să apară chiar dacă stdout e pipat
            break

if __name__ == "__main__":
    main()
```
Rulare
Remote cu socat (recomandat)

# în directorul cu solve.py
```
socat -v -T60 \
  EXEC:"python3 -u ./solve.py",pty,raw,echo=0,setsid,ctty \
  OPENSSL:to-rotate-<HASH>.challs.tfcctf.com:1337,verify=0 \
| tee solver_out.txt
```

- pty,raw,echo=0 previne eco-loop-uri.

- verify=0 e ok pentru endpoint-urile CTF.

- solver_out.txt va conține ieșirea solverului (inclusiv flag-ul).
