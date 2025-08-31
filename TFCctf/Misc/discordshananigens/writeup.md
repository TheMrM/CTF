# Discord Shenanigans V5 — Writeup

**Category:** Misc  
**Points:** 50  
**Solves:** 337  

---

## Challenge Description
We were given a Discord announcement message that claimed:

> *"The Discord flag is right here in this message, that I replied to, hidden away.  
> You will NOT be able to see it with your eyes, as the flag is hidden."*

A small hint also said:

> *"Bulking up on the nothingness was the best way to hide it. Go get your shovels ready!"*

---

## Initial Analysis
- The message states the flag is “right here” but invisible to the human eye.
- The hint about *“nothingness”* strongly suggests **zero-width Unicode characters** or **trailing whitespace** steganography.
- Copy–pasting into normal editors shows nothing suspicious (Discord strips invisibles in some contexts).

So the flag is not in the visible ASCII text, but hidden in **Unicode control characters**.

---

## Approach
1. **Inspecting the raw message:**  
   Copying the message into a hex dump (`xxd`) only revealed normal ASCII. That confirmed the invisibles were stripped during copy.

2. **Using Discord Web + DevTools:**  
   To preserve the hidden characters, the message was inspected directly in the browser’s DOM.

   ```js
   // Example snippet in the console to collect invisibles
   const s = document.querySelector('[id^="message-content"]').textContent;
   [...s].forEach(ch => {
     if (ch.codePointAt(0) > 126) console.log(ch, ch.codePointAt(0).toString(16));
   });```

This revealed the presence of zero-width characters (U+200B, U+200C, U+200D, etc.).

3. **Decoding the scheme:**
The characters followed a common stego pattern:

U+200B (Zero Width Space) → 0

U+200C (Zero Width Non-Joiner) → 1

U+200D (Zero Width Joiner) → separator

After mapping bits and grouping them into bytes, the hidden binary string decoded cleanly into ASCII.

Solution

Running a custom decoder on the invisibles extracted from the reply preview text revealed the flag.

```
(() => {
  // === 1) Collect ALL invisible-ish code points we care about ===
  const INVIS_CP = new Set([
    // zero-width spaces/joiners
    0x200B,0x200C,0x200D,0xFEFF,
    // direction/format controls (often used to hide)
    0x200E,0x200F,0x202A,0x202B,0x202C,0x202D,0x202E,
    0x061C,0x034F,0x180E,0x2060,0x2061,0x2062,0x2063,0x2064,
    // keep regular controls too (just in case)
    0x0009,0x000A,0x000D
  ]);

  const cp = c => c.codePointAt(0);
  const bitsToStr = bits => {
    let out = "";
    for (let i = 0; i + 7 < bits.length; i += 8) {
      out += String.fromCharCode(parseInt(bits.slice(i, i+8), 2));
    }
    return out;
  };

  // === 2) Walk all text nodes on the page ===
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const carriers = []; // { node, text, invis, cps }
  while (walker.nextNode()) {
    const n = walker.currentNode;
    const s = n.nodeValue || "";
    if (!s) continue;
    const invisChars = [...s].filter(ch => INVIS_CP.has(cp(ch)));
    if (invisChars.length) {
      carriers.push({
        node: n,
        text: s,
        invis: invisChars.join(""),
        cps: [...new Set(invisChars.map(ch => cp(ch)))],
      });
    }
  }

  if (!carriers.length) {
    console.log("No invisible characters found on the page. Make sure the message and its reply preview are on screen.");
    return;
  }

  // === 3) Try to decode each carrier ===
  const SEP_CANDIDATES = new Set([0x200D, 0x2060]); // ZWJ, WORD JOINER as chunk separators (common)
  const preferredPairs = [
    [0x200B, 0x200C],     // ZWSP = 0, ZWNJ = 1
    [0x200E, 0x200F],     // LRM = 0, RLM = 1
    [0x200B, 0xFEFF],     // ZWSP = 0, ZWNBSP = 1
  ];

  function tryDecode(invis, cps) {
    const uniq = [...new Set([...invis])];
    const codepoints = uniq.map(cp);

    // Build candidate (zero, one) pairs to try
    const pairs = [];
    // 1) preferred pairs if present
    preferredPairs.forEach(([z,o]) => {
      if (codepoints.includes(z) && codepoints.includes(o)) pairs.push([z,o]);
    });
    // 2) otherwise: try any 2 distinct invisibles as 0/1
    for (let i=0;i<codepoints.length;i++){
      for (let j=i+1;j<codepoints.length;j++){
        pairs.push([codepoints[i], codepoints[j]]);
        pairs.push([codepoints[j], codepoints[i]]);
      }
    }

    // Identify separators in stream (optional)
    const seps = codepoints.filter(c => SEP_CANDIDATES.has(c));

    const outputs = new Set();

    for (const [zero, one] of pairs) {
      const mapBit = ch => {
        const c = cp(ch);
        if (c === zero) return '0';
        if (c === one)  return '1';
        return ''; // ignore others here (may be seps/garbage)
      };

      if (seps.length) {
        // split by any of the known seps and decode parts
        const parts = [...invis].join('').split(new RegExp(`[${seps.map(x=>`\\u${x.toString(16).padStart(4,'0')}` ).join('')}]`,'u'));
        for (const p of parts) {
          const bits = [...p].map(mapBit).join('');
          if (/^[01]{8,}$/.test(bits)) outputs.add(bitsToStr(bits));
        }
      } else {
        const bits = [...invis].map(mapBit).join('');
        if (/^[01]{8,}$/.test(bits)) outputs.add(bitsToStr(bits));
      }
    }
    return [...outputs];
  }

  // === 4) Print candidates that look promising ===
  let foundAny = false;
  carriers.forEach((car, idx) => {
    const outs = tryDecode(car.invis, car.cps);
    if (outs.length) {
      const hits = outs.filter(t => /{.*}|flag|ctf/i.test(t));
      if (hits.length) {
        foundAny = true;
        console.log(`\n[#${idx}] POSSIBLE FLAG in`, car.node.parentElement?.outerHTML?.slice(0,120)+'...');
        console.log("→", hits);
        car.node.parentElement?.scrollIntoView({behavior:'smooth', block:'center'});
      } else if (outs.some(t => /^[\x20-\x7E]+$/.test(t))) {
        // Show readable ASCII candidates too
        foundAny = true;
        console.log(`\n[#${idx}] Readable decode in`, car.node.parentElement?.outerHTML?.slice(0,120)+'...');
        console.log(outs);
      }
    }
  });

  if (!foundAny) {
    console.log("Invisible chars found, but no obvious decode. Scroll so the REPLY PREVIEW is visible and run again.");
  } else {
    console.log("\nDone. If you saw candidates above, one should contain the flag like CTF{...} / FLAG{...}.");
  }
})();
```
