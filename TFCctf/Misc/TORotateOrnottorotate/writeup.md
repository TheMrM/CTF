Write-up (RO) — „To rotate, or not to rotate” (TFCCTF)
🧩 Rezumat

Challenge-ul expune un server care lucrează cu modele de segmente pe o grilă 3×3. În Faza 1 îți arată pe rând câte un N_i și te roagă să trimiți un model (o listă de segmente). În Faza 2, serverul ia modelele trimise de tine, le rotește aleator (0°, 90°, 180°, 270°), poate inversa capetele fiecărui segment și amestecă ordinea segmentelor, apoi îți cere: „Your answer for N?”.
Cheia este să calculezi o semnătură canonică a modelului invariantă la rotație. În Faza 1, mapăm semnătură → N; în Faza 2, recalculezi semnătura pentru modelul „beat” și răspunzi cu N corespondent.

🔎 Analiza
Grila, segmentele și restricția gcd

Punctele sunt cele 9 coordonate ale grilei: (x,y) cu x,y ∈ {0,1,2}. Un segment dintre două puncte distincte (a,b) este valid dacă:

se află în grilă,

gcd(|dx|, |dy|) = 1, adică segmentul nu sare „peste” un punct intermediar pe grilă.

Totalul segmentelor valide este 28. Serverul indexează aceste 28 de segmente într-o listă SEGMENTS și construiește un dicționar SEG_INDEX[segment] = index.

Rotațiile

Rotația cu k ∈ {0,1,2,3} pași de 90° în jurul centrului (1,1) se face prin:

'''
(x, y) -> (x-1, y-1) -> rotiri de 90° succesive -> + (1,1)
'''

Aplicând rotația asupra capetelor unui segment și sortând (A,B) astfel încât A ≤ B, obținem segmentul rotit rot_segment(seg, k).

Semnătura canonică (canon_bits)

Pentru o listă de segmente segs, serverul:

Pentru fiecare k ∈ {0,1,2,3}, rotește toate segmentele și pune bitul corespunzător fiecărui segment rotit în masca de 28 de biți.

Alege minimul dintre cele 4 măști — acesta e „canonical bits”: invariant la rotație, la inversarea capetelor și la ordinea segmentelor.

Concluzie: două modele care sunt identice până la rotație vor avea același canon_bits.


🛠️ Strategia de rezolvare

Faza 1 (training):

Serverul afișează N_1: <N>, N_2: <N>, … de Q=120 ori.

Tu trimiți, pentru fiecare N, un model ales de tine (un subset de segmente valide).

Calculezi canon_bits(model) și salvezi în dicționar: map[canon_bits] = N.

Ai grijă ca modelele trimise să aibă semnături unice (altfel serverul refuză un duplicat cu alt N).

Faza 2 (quiz):

Pentru fiecare „MutatedPattern” de la server, citești m linii cu segmente.

Calculezi canon_bits al modelului mutat și cauți în map.

Răspunzi cu N corespunzător → primești OK.

Dacă răspunzi corect la toate, primești flag-ul.

💻 Solver (Python, compact)

Acest solver copiază logica serverului (grilă, rotații, canon_bits) și implementează protocolul.
Intrare/Ieșire: linia cu linie pe stdin/stdout.

'''
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
'''

▶️ Rulare
Varianta — Remote cu socat (recomandat)

'''
# în directorul cu solve.py
socat -v -T60 \
  EXEC:"python3 -u ./solve.py",pty,raw,echo=0,setsid,ctty \
  OPENSSL:to-rotate-<HASH>.challs.tfcctf.com:1337,verify=0 \
| tee solver_out.txt
'''

- pty,raw,echo=0 previne „eco-loop-uri”.

- verify=0 e ok pentru endpoint-urile CTF.

- În solver_out.txt vei avea și flag-ul.

💡 „Lessons learned”

Invarianții (semnături canonice) sunt arma supremă împotriva rotațiilor, permutărilor și schimbării ordinii.

Reproducerea exactă a logicii serverului (grilă, rotații, gcd, canon_bits) elimină orice ambiguitate.

Pentru integrare remote, socat cu pty,raw,echo=0 e prietenul tău.
