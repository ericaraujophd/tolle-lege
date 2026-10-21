"""draw_art.py: generates art.svg (run: python3 draw_art.py).

The drawing is written as code so it can be adjusted precisely and rebuilt.
All coordinates are in SVG units; the figure faces right, feet on y=229.
"""
from pathlib import Path
# First Snow silhouette, v3 (the version on the cover). A small girl, head tipped back to the sky, hair
# falling behind her, one hand raised and open to catch the snow.
# Solid ink shapes only; neighbouring shapes overlap so no paper shows at
# the joins.
import random, sys
INK = "#1a1a1a"
W, H = 200, 260
parts = []
def P(d): parts.append(f'<path d="{d}" fill="{INK}"/>')

# legs and boots (feet on y=229)
P("M96 194 L102 194 L101.5 221 Q102 226 100 228 Q96 230 91.5 229 Q90 227.5 92 226 Q95 224 96 221 Z")
P("M105 194 L111 194 L110.5 221 Q111 224 114 226 Q116 227.5 114.5 229 Q110 230 106 228 Q104.5 226 105 221 Z")
# coat
P("M93 133 Q96 124 103 123 Q111 123 114 130 Q116 140 116 150 "
  "Q118 175 121 196 Q103 200 86 196 Q90 173 91 150 Q91 139 93 133 Z")
# far arm, hanging behind
P("M93 134 Q88 152 88 170 Q89 174 92 173 Q94 162 96 145 Z")
# near arm raised up and forward; open hand, thumb apart from the fingers
P("M107 129 Q113 124 118 129 Q123 121 128 113 L132 116 Q127 126 120 136 Q112 141 107 135 Z")
P("M127 117 Q127 110 130 104 Q131.5 101 133 102.5 L133.5 104 "      # fingers
  "Q135 101 136.5 102.5 Q136 108 134.5 113 Q137 111 139 109.5 "      # thumb
  "Q140.5 109.5 140 111.5 Q137 116 132 119 Z")
# neck, short and overlapping head and coat
P("M98 111 L108 109 L109 127 L98 127 Z")
# hair: falls with gravity from the back of the head over the shoulders
P("M86 104 Q83 115 86 128 Q90 132 96 128 Q99 120 100 110 Q95 103 86 104 Z")
# scarf, wrapped over the neck and the hair
P("M93 123 Q103 116 112 121 Q114 127 111 129 Q103 125 95 129 Q91 127 93 123 Z")
# head, tipped back about 50 degrees, larger for a child's proportions
head = ("M-10 0 A10 10 0 0 1 6 -8 Q10 -6 10.5 -2 Q13 0 13 1.5 Q13 3 10.5 3.2 "
        "Q11.6 4.6 10.3 5.4 Q11 6.8 9.5 7.6 Q9.3 10.6 5.5 11 L-2 11.5 Q-9 9.5 -10 0 Z")
parts.append(f'<g transform="translate(96 101) rotate(-50) scale(1.3)">'
             f'<path d="{head}" fill="{INK}"/></g>')

# snow: sparse, mostly above her
rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
flakes = []
while len(flakes) < 30:
    x, y = rnd.uniform(25, 175), rnd.uniform(15, 215)
    if 74 < x < 148 and 80 < y < 232: continue
    if any((x-a)**2 + (y-b)**2 < 220 for a, b, _ in flakes): continue
    flakes.append((x, y, rnd.choice([0.8, 1.0, 1.2, 1.5, 1.8])))
for x, y, r in flakes:
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>')

(Path(__file__).parent / "art.svg").open("w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 10 160 225">' + "".join(parts) + "</svg>")
