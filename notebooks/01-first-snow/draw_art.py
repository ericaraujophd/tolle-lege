"""
draw_art.py  --  draws art.svg, the silhouette for Notebook 01, First Snow
=========================================================================

Run:  python3 notebooks/01-first-snow/draw_art.py   (writes art.svg beside it)

THE DRAWING (version 5, 2026-10-20). A girl of about nine or ten, in true
profile facing right, her head tipped back to look up at the falling snow.
Long hair hangs straight down her back; she wears a knee-length coat, tights
and ankle boots, arms relaxed at her sides. Realistic proportions (about six
heads tall) and a real facial profile: brow, small nose, lips, chin, throat.
(Earlier versions were geometric or cartoon figures; Eric asked for the
silhouette of a real girl.)

HOW IT IS BUILT
  * Each part (head, hair, neck, coat, sleeve, two legs) is a list of points
    around its outline. spline() draws a smooth closed Catmull-Rom curve
    through them, which is what makes the shapes look organic rather than
    geometric. To reshape something, move its points and re-run.
  * Everything is ONE ink colour, solid, no outlines, so it prints crisply
    on kraft or stone with any printer. Parts overlap a little where they
    meet, so no paper shows through at the joins.
  * Coordinates are SVG units; y grows DOWNWARD. The crown is near y = 41,
    the feet on y = 281.
  * The snow is random dots from a FIXED seed (every build is identical),
    kept out of a box around the figure so no dot touches her.
  * The viewBox at the end crops tightly to figure plus snow; the cover
    template sizes the picture by its height.
"""
from pathlib import Path
import math, random
INK="#1a1a1a"; parts=[]
def spline(pts, closed=True, t=0.5):
    """Closed Catmull-Rom spline through pts -> SVG cubic path."""
    n=len(pts); d=f"M{pts[0][0]:.2f} {pts[0][1]:.2f} "
    rng=range(n) if closed else range(n-1)
    for i in rng:
        p0=pts[(i-1)%n]; p1=pts[i]; p2=pts[(i+1)%n]; p3=pts[(i+2)%n]
        c1=(p1[0]+(p2[0]-p0[0])*t/3, p1[1]+(p2[1]-p0[1])*t/3)
        c2=(p2[0]-(p3[0]-p1[0])*t/3, p2[1]-(p3[1]-p1[1])*t/3)
        d+=f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f} "
    return d+"Z"
def P(d, tr=""): parts.append(f'<path d="{d}" fill="{INK}"{tr}/>')
def rot(pts, ang, cx, cy):
    a=math.radians(ang); c,s=math.cos(a),math.sin(a)
    return [(cx+x*c-y*s, cy+x*s+y*c) for x,y in pts]

# HEAD, in profile facing right and tipped back about 34 degrees so she
# looks up at the snow. Points go round the outline clockwise from the nape;
# a Catmull-Rom spline (spline()) draws a smooth curve through them.
head=[(100,92),(92.6,87.2),(82.9,74.8),(80.4,59.0),(87.7,45.9),(100.8,41.2),  # back, crown
      (112.9,45.1),(119.8,51.3),(122.6,55.6),                                  # forehead, brow
      (128.4,59.0),(131.6,60.3),(128.8,63.9),                                  # nose
      (131.0,66.1),(130.9,68.2),(132.9,69.6),                                  # lips
      (133.0,72.6),(135.4,75.6),(132.6,79.4),                                  # chin
      (124,86.5),(116.5,94),(112,102)]                                         # throat
P(spline(head))
# HAIR: from the crown it hugs the back of the head, then falls with
# gravity in a soft curtain to the shoulder blades
P(spline([(106.5,42),(91,42.4),(80.2,51.6),(77.2,64),(78.4,80),(80.8,96),(82.6,112),
          (84.4,124.5),(89,127.5),(94.6,122),(97.6,108),(99,94),(100,78),(104,58)]))
# NECK
P(spline([(98,88),(110,99),(112.5,104),(112,113),(99,114),(96,100)]))
# COAT (profile): soft shoulder, straight back, gentle flare to the knee
coat=[(98,104),(92,110),(89,124),(89.5,145),(88,170),(85,198),(85.5,211),(104,214.5),(123,211.5),
      (124.5,206),(120.5,184),(117,163),(119,147),(119.5,131),(116.5,116),(110,107)]
P(spline(coat))
# NEAR SLEEVE edge and hand at her side (the arm hangs relaxed)
P(spline([(101,112),(108,113),(111,130),(112,160),(113,174),(114,182),(111,186),(107,183),(104,170),(102,145)]))
# LEGS in tights, slightly staggered, ankle boots; feet on y=280
back_leg=[(94,206),(103,208),(102,226),(101,244),(100,257),(101,266),(104,270),(108,276),(112,279.5),
          (110,281),(92,281),(91,276),(92,266),(93,257),(93,244),(94,226)]
P(spline(back_leg))
front_leg=[(103,208),(112,208),(111,226),(110,244),(109,256),(110,265),(115,270),(122,274),(125,278),
           (122,281),(103,281),(102,276),(103,266),(103,256),(103,244),(103,226)]
P(spline(front_leg))

# SNOW: 30 dots, radius 1 to 2.4, at least ~17 units apart
rnd=random.Random(7); fl=[]
while len(fl)<30:
    x,y=rnd.uniform(40,180),rnd.uniform(5,240)
    if 72<x<146 and 22<y<290: continue
    if any((x-a)**2+(y-b)**2<300 for a,b,_ in fl): continue
    fl.append((x,y,rnd.choice([1.0,1.3,1.6,2.0,2.4])))
for x,y,r in fl: parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>')
(Path(__file__).parent / "art.svg").open("w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="38 0 146 284">'+"".join(parts)+"</svg>")
