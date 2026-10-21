"""
draw_art.py  --  draws art.svg, the silhouette for Notebook 01, First Snow
=========================================================================

Run:  python3 notebooks/01-first-snow/draw_art.py   (writes art.svg beside it)

THE DRAWING (version 4, 2026-10-20). A small girl seen FROM BEHIND, standing
in falling snow with her arms open, in a knit hat with a pompom, a chin-length
bob, a short A-line coat, mittens and boots. Earlier versions showed her in
profile looking up; at pocket-cover size the face and hand never read well,
so this one avoids both: the back view, the open arms and the snow above say
"first snow" without any fine detail.

HOW IT IS BUILT. Simple solid shapes in one ink colour (no greys, no
outlines), so it prints crisply on kraft or stone with any printer:
  * every shape is a <path> or <circle>; shapes that touch OVERLAP a little,
    so no paper shows through at the joins;
  * the figure is symmetric about x = 100: the legs and arms are written once
    for her right side and mirror() makes the left side;
  * coordinates are SVG units; the head is at y = 64, the feet at y = 168;
  * the snow is random dots (a FIXED seed, so every build is identical) kept
    out of the area around her body so it never touches the silhouette.
The viewBox at the end crops the picture tightly to figure plus snow; the
cover template sizes it by height.
"""
from pathlib import Path
import random, re
INK="#1a1a1a"; parts=[]
def P(d): parts.append(f'<path d="{d}" fill="{INK}"/>')
def mirror(d):
    """Return path d reflected across the vertical line x = 100: every x
    coordinate becomes 200 - x; y coordinates and commands are unchanged."""
    toks=re.findall(r"[A-Za-z]|-?[\d.]+", d); out=[]; isx=True
    for t in toks:
        if t.isalpha(): out.append(t); isx=True
        else: out.append(f"{200-float(t):.2f}" if isx else t); isx=not isx
    return " ".join(out)
def C(x,y,r): parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>')
# legs + boots (feet on y=168)
leg="M93.8 136 L98.6 136 L98.2 162 Q98.8 166.5 96.6 168 L90.6 168 Q88.7 167 90.3 164.8 Q93.5 163.8 93.9 160.5 Z"
P(leg); P(mirror(leg))
# coat: soft shoulders, gentle A-line, slightly curved hem
P("M100 82 C108 82 114.5 84 116.5 90 C118.5 102 121 119 124.5 137 Q100 141.5 75.5 137 C79 119 81.5 102 83.5 90 C85.5 84 92 82 100 82 Z")
# arms open, a little below horizontal, as if to say "look!"; round mittens
arm="M113 87 C122 89.5 129.5 95.5 135 103 L131.6 106.4 C126.5 100.5 120 96 111.5 95 Z"
P(arm); P(mirror(arm)); C(134.6,106.4,3.6); C(65.4,106.4,3.6)
# short neck, mostly hidden by the hair
P("M96.5 74 L103.5 74 L104 84 L96 84 Z")
# head and a chin-length bob that flips out a little at the ends
C(100,64,11.8)
P("M88.2 62 C87.6 70 87.4 75.5 86.2 79.2 Q90.5 81.2 95 78.2 Q100 79.6 105 78.2 Q109.5 81.2 113.8 79.2 C112.6 75.5 112.4 70 111.8 62 Z")
# knit hat: dome, folded brim, small pompom
P("M88.2 61 C88.2 50.5 94 46 100 46 C106 46 111.8 50.5 111.8 61 Z")
P("M87.6 59.4 Q100 56 112.4 59.4 L112.4 63.2 Q100 60.4 87.6 63.2 Z")
C(100,44.6,3.0)
# snow: 24 dots, sizes 0.8 to 1.8, at least ~14 units apart, none near her
rnd=random.Random(5); fl=[]
while len(fl)<24:
    x,y=rnd.uniform(48,152),rnd.uniform(10,165)
    if 80<x<120 and 36<y<172: continue
    if 58<x<142 and 80<y<114: continue
    if any((x-a)**2+(y-b)**2<190 for a,b,_ in fl): continue
    fl.append((x,y,rnd.choice([0.8,1.0,1.2,1.5,1.8])))
for x,y,r in fl: C(round(x,1),round(y,1),r)
(Path(__file__).parent / "art.svg").open("w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="44 4 112 168">'+"".join(parts)+"</svg>")
