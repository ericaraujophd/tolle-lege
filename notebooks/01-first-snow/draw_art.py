"""
draw_art.py  --  draws art.svg, the silhouette for Notebook 01, First Snow
=========================================================================

Run:  python3 notebooks/01-first-snow/draw_art.py   (writes art.svg beside it)

THE DRAWING (version 5, 2026-10-20). A girl of about nine or ten, in true
profile facing right, her head tipped back to look up at the falling snow.
Her hair is in a ponytail that hangs down her back; she wears a knee-length coat, tights
and ankle boots, arms relaxed at her sides. Realistic proportions (about seven
heads tall, head scaled by HEAD_SCALE) and a real facial profile: brow, small nose, lips, chin, throat.
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

# HEAD, NECK AND HAIR (version 7)
# The head is drawn upright (facing right, cranium centred on 0,0, about 50
# units tall), scaled, tipped back by TILT degrees and then moved so that its
# NAPE (the back of the neck, just under the skull) sits on the line of her
# back. When someone looks up, the neck bends with the head: the throat
# becomes a long diagonal from chin to collarbone and the nape gets short.
# The neck shape below joins those points to the shoulders, so the head
# never sits on a stalk.
TILT, SCALE, NAPE = -34, 0.78, (96, 97)   # 0.78: a slim, child-sized head
upright = [(-11,24),(-19,10),(-20,-4),(-14,-17),(-2,-23),(10,-20),(17,-11),(19,-3),  # nape..brow
           (18.7,1.5),(21,7.5),(21.6,9.6),(19.4,11.2),                               # nose
           (20.2,13.8),(19.2,15.4),(19.9,17.2),                                      # lips
           (18.2,19.8),(18.6,23),(15,26.8),(8,29)]                                   # chin, throat
def place(pts):
    """Scale, tilt and move upright head coordinates into the picture. The
    shift is fixed by where the NAPE point (-11, 24) must land, so any point
    of the head (the ponytail tie, say) can be placed the same way."""
    a = math.radians(TILT); c, s_ = math.cos(a), math.sin(a)
    tf = lambda x, y: (x*SCALE*c - y*SCALE*s_, x*SCALE*s_ + y*SCALE*c)
    nx, ny = tf(-11, 24)
    dx, dy = NAPE[0]-nx, NAPE[1]-ny
    return [(tf(x, y)[0]+dx, tf(x, y)[1]+dy) for x, y in pts]
head = place(upright)
P(spline(head))
# NECK: nape -> down the back; throat (last head points) -> down to the chest
throat = head[-1]
P(spline([NAPE, (head[-2][0]-2, head[-2][1]+1), throat, (throat[0]+1, throat[1]+8),
          (115, 114), (104, 118), (93, 114), (92.5, 104)]))
# PONYTAIL: tied at the back of the head, it hangs straight down with gravity,
# a little away from her neck, tapering to a soft point at the shoulder blade
tie = place([(-18, -9)])[0]          # high on the back of the head
P(spline([(tie[0]+2, tie[1]-4), (tie[0]-3, tie[1]-3), (tie[0]-6, tie[1]+6), (tie[0]-7, tie[1]+20),
          (tie[0]-5.5, tie[1]+34), (tie[0]-2.5, tie[1]+42), (tie[0]-1, tie[1]+36),
          (tie[0]-1.5, tie[1]+20), (tie[0]+1, tie[1]+8), (tie[0]+4, tie[1]+2)]))
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
