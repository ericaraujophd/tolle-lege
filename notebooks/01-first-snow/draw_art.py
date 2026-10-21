"""
draw_art.py  --  draws art.svg, the silhouette for Notebook 01, First Snow
=========================================================================

Run:  python3 notebooks/01-first-snow/draw_art.py   (writes art.svg beside it)

THE DRAWING (version 8, 2026-10-20). An original silhouette of a little girl
of about five, in profile facing right, face tipped up to the falling snow,
one hand raised with the fingers open to catch a flake. Shoulder-length hair
with a small bow, a coat-dress with a full bell skirt, short legs, small
round shoes.

Style cues taken from example silhouettes Eric liked (a young child, a round
head, a short body, a full skirt, a tiny upturned nose, a reaching hand).
Those examples were watermarked stock and were NOT traced or copied; every
point below was placed by hand.

HOW IT IS BUILT
  * Each part is a list of points around its outline; spline() draws a smooth
    closed Catmull-Rom curve through them (organic, not geometric). To change
    a part, move its points and re-run this script.
  * The HEAD is written upright (facing right, centred near 0,0) and place()
    scales nothing but tips it back by TILT degrees and moves it so the NAPE
    point (-9, 20) lands at NAPE. The hair cap and the bow are written in the
    same upright coordinates, so they tip with the head; the loose hair is
    hung from the back of the head straight DOWN, because hair falls with
    gravity whatever the head does.
  * One ink colour, solid, no outlines: it prints crisply on kraft or stone.
    Touching parts overlap slightly so no paper shows at the joins.
  * SVG coordinates: y grows DOWNWARD. Feet stand on y = 258.
  * Snow: random dots from a FIXED seed (identical every build), kept out of
    a box around the figure.
"""
from pathlib import Path
import math, random
INK="#1a1a1a"; parts=[]
def spline(pts, t=0.5):
    n=len(pts); d=f"M{pts[0][0]:.2f} {pts[0][1]:.2f} "
    for i in range(n):
        p0=pts[(i-1)%n]; p1=pts[i]; p2=pts[(i+1)%n]; p3=pts[(i+2)%n]
        c1=(p1[0]+(p2[0]-p0[0])*t/3, p1[1]+(p2[1]-p0[1])*t/3)
        c2=(p2[0]-(p3[0]-p1[0])*t/3, p2[1]-(p3[1]-p1[1])*t/3)
        d+=f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f} "
    return d+"Z"
def P(pts): parts.append(f'<path d="{spline(pts)}" fill="{INK}"/>')
TILT, NAPE = -30, (101, 118)
def place(pts):
    a=math.radians(TILT); c,s=math.cos(a),math.sin(a)
    tf=lambda x,y:(x*c-y*s, x*s+y*c); nx,ny=tf(-9,20)
    return [(tf(x,y)[0]+NAPE[0]-nx, tf(x,y)[1]+NAPE[1]-ny) for x,y in pts]
# head (upright coords: round cranium, tiny upturned nose, soft chin)
head=place([(-9,20),(-18,8),(-20,-6),(-14,-18),(-1,-23),(11,-20),(17.5,-11),(19.5,-3),
            (19.2,1.5),(21.6,5.6),(22.4,7.4),(19.8,8.8),(20.5,11.2),(19.6,12.8),(20.2,14.4),
            (18.6,16.6),(19.2,19.2),(15.4,23),(8,25)])
P(head)
# neck, short
th=head[-1]
P([(NAPE[0]+2,NAPE[1]-2),(th[0],th[1]),(th[0]+2,th[1]+7),(116,130),(100,132),(98,126)])
# hair: cap over the back of the head (head coords) ...
P(place([(13,-20.5),(0,-24.5),(-15,-19.5),(-21.5,-6),(-20,8),(-12,14),(-6,8),(-2,-6),(6,-12)]))
# ... and loose hair falling with gravity to the shoulders, curling at the ends
b=place([(-20,-4)])[0]
P([(b[0]+5,b[1]-8),(b[0]-2,b[1]-5),(b[0]-4.5,b[1]+6),(b[0]-4,b[1]+18),(b[0]-5.5,b[1]+27),
   (b[0]-2.5,b[1]+32),(b[0]+2.5,b[1]+31),(b[0]+5,b[1]+27.5),(b[0]+8,b[1]+29),(b[0]+10.5,b[1]+24),
   (b[0]+10,b[1]+12),(b[0]+11,b[1]+2)])
# a small bow at the top of the head
bw=place([(-8,-22)])[0]
P([(bw[0],bw[1]),(bw[0]-7,bw[1]-6),(bw[0]-8,bw[1]+1),(bw[0]-1,bw[1]+2)])
P([(bw[0],bw[1]),(bw[0]+3,bw[1]-8),(bw[0]+8,bw[1]-6),(bw[0]+2,bw[1]+1)])
# coat-dress: fitted bodice, full bell skirt
P([(100,124),(95,132),(93,150),(91,166),(84,186),(78,204),(82,209),(100,212),(122,211),
   (137,207),(139,202),(130,184),(122,166),(120,150),(121,136),(116,127)])
# far arm hanging behind (only the hand shows)
# near arm: raised forward and up toward the snow, hand open, fingers spread
P([(104,130),(112,128),(120,124),(127,116),(132,106),(135.5,96),(139,98.5),(136,110),
   (130,122),(122,132),(112,140),(104,140)])
P([(133.5,98),(133,92),(131.5,86),(131,82.5),(133,82),(135,86.5),(135.4,80.5),(137,78.6),
   (138.4,80.6),(138.4,85.6),(139.8,80.8),(141.4,80),(142,82),(140.8,87),(142.8,84),(144.4,84.4),
   (143.8,87),(141.2,92.4),(143.6,92),(145,93.4),(142.6,96.6),(139,100)])
# legs: short and soft, slightly apart; small round shoes; ground y=258
P([(97.5,206),(106.5,206),(106,222),(105.5,238),(105.5,247),(106.5,251),(103,252),(98.6,251.5),(98.4,240),(98,224)])
P([(107.5,206),(116.5,206),(116,222),(115.4,237),(115.2,246),(114,251),(109,251.5),(108.4,240),(108,224)])
P([(97.2,248),(106,248),(108.6,252),(110,256),(107.4,258.2),(96.8,258.2),(95.4,255),(95.8,251)])
P([(107.6,248),(115.8,248),(119.4,252),(122,255.4),(120,258.2),(107.6,258.2),(106.6,255),(107,251)])
rnd=random.Random(4); fl=[]
while len(fl)<28:
    x,y=rnd.uniform(48,180),rnd.uniform(18,240)
    if 72<x<150 and 62<y<262: continue
    if any((x-a)**2+(y-b)**2<260 for a,b,_ in fl): continue
    fl.append((x,y,rnd.choice([1.0,1.3,1.6,2.0,2.3])))
for x,y,r in fl: parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>')
(Path(__file__).parent / "art.svg").open("w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="44 12 140 250">'+"".join(parts)+"</svg>")
