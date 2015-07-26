import sys,os,re
import random
from PIL import Image
import colorsys
import itertools
from math import sin
from math import pow
import math

file=open

def clamp(v,a,b):
    return max(a,min(v,b))

def plex(v,n): return v*n-int(v*n)
    
def linmap (v,oa,ob,na,nb):
    return float(v-oa)/(ob-oa)*(nb-na) + na

def clinmap(v,oa,ob,na,nb):
    return clamp(linmap(v,oa,ob,na,nb),na,nb)
    
def color_linmap(v,a,b,c1,c2):
    return tuple(int(linmap(v,a,b,c1v,c2v)) for c1v,c2v in zip (c1,c2))

def color_linmap_hsv(v,a,b,c1,c2):
    c1hsv = colorsys.rgb_to_hsv(*tuple(float(x)/255 for x in c1))
    c2hsv = colorsys.rgb_to_hsv(*tuple(float(x)/255 for x in c2))
    hsv = tuple(linmap(v,a,b,c1v,c2v) for c1v,c2v in zip (c1hsv,c2hsv))
    return tuple(int(255*x) for x in colorsys.hsv_to_rgb(*hsv))

def color_linmap_hsv2(v,a,b,c1,c2):
    hsv = tuple(linmap(v,a,b,c1v,c2v) for c1v,c2v in zip (c1,c2))
    return tuple(int(255*x) for x in colorsys.hsv_to_rgb(*hsv))

def color_2map(v,c1,c2,c3):
    return tern(v<0.5,color_linmap(v,0,0.5,c1,c2),color_linmap(v,0.5,1.0,c2,c3))

def channel_ramp(v,order): 
    r = [0,0,0]
    r[order[0]] = int(linmap(v,0.000000,0.333333,0,255))
    r[order[1]] = int(linmap(v,0.333333,0.666666,0,255))
    r[order[2]] = int(linmap(v,0.666666,1.000000,0,255))
    return tuple(r)

def map_fire(v):     return channel_ramp(v,(0, 1, 2))
def map_rose(v):     return channel_ramp(v,(0, 2, 1))
def map_spring(v):   return channel_ramp(v,(1, 0, 2))
def map_emerald(v):  return channel_ramp(v,(1, 2, 0))
def map_amethyst(v): return channel_ramp(v,(2, 0, 1))
def map_ice(v):      return channel_ramp(v,(2, 1, 0))
def map_grey(v):     return (int(v*255),)*3
def map_hue(v):      return tuple(int(x*255) for x in colorsys.hsv_to_rgb(v,1,1))

def make_map_const(r,g,b): return lambda v:(r,g,b)
    
def map_colorpatchy(v): return (int(255*plex(v,3)),int(255*plex(v,11)),int(255*plex(v,5)))

#def map_cyan(v): return color_2map(v,(0,0,0),(0,0,255),(0,255,255))
def map_cyan(v): return (0,int(clinmap(v,0.5,1,0,255)),int(clinmap(v,0,0.5,0,255)))

def map_cyan3(v): return (0,int(linmap(plex(v,3),0.5,1.0,0,255)),int(linmap(plex(v,3),0,0.5,0,255)))
    
def map_blux(v): 
    vv = (plex(v,3) + plex(v,11) + plex(v,5))/3
    return color_2map(vv,(0,0,0),(0,0,255),(255,255,255))
    
def map_blue2white(v): return color_2map(plex(v,21),(0,0,0),(0,0,255),(255,255,255))

def xform_sin(v): return sin(v*2*3.14159+1.5*3.14159)/2+0.5
def xform_triangle(v): return tern(v<0.5, v*2, 2-2*v)
def xform_triplex(v,n,g=1): math.pow(xform_triangle(plex(v,n)),g)

def map_grey_40sin(v): return map_grey(xform_sin(40*v))
def map_fire_sin(v): return map_fire(xform_sin(v))

def map_purple_heat_rgb(v): return color_linmap(v,0,1,(0x5e,0x00,0x63),(0xff,0xeb,0xaa))
def map_purple_heat_hsv(v): return color_linmap_hsv(v,0,1,(0x5e,0x00,0x63),(0xff,0xeb,0xaa))

def map_contra(v): return color_linmap_hsv(v,0,1,(0,255,0),(255,0,255))
def map_contra2(v): return color_linmap(v,0,1,(0,255,0),(255,0,255))

def make_map_sinplex(colormap, n, g=1):
    return lambda v: colormap(xform_sin(n*math.pow(v,g)))
def make_map_triplex(colormap, n, g=1):
    return lambda v: colormap(math.pow(xform_triangle(plex(v,n)),g))

def map_blue(v): return (0,0,int(255*v))
def map_bluesin(v): return (0,0,int(255*xform_sin(v)))
def map_bluetri(v): return (0,0,int(255*xform_triangle(v)))
    
def map_cool2hot(v): return color_linmap_hsv2(v, 0,1,(0.6,0.8,0.5), (0.0,1,1))
    
def map_icecool(v): return map_ice(pow(linmap(v,0,1,0.2,0.74),1.5))
def map_icecool_rev(v): return map_icecool(1-v)

map_fire_sin2 = make_map_sinplex(map_fire,2)

map_blu_test = make_map_triplex(map_blue,1,1)

bp=81
mp=9
def map_plexhard(v): return (int(255*plex(v,bp*mp)),int(255*plex(v,bp*mp*mp)), int(255*plex(v,bp)))
    
def tern(t,a,b):
    if t: return a
    else: return b
    
def squamp(x):
    return (1-(1-x)**0.5)*0.7
    
def antisquamp(x):
    return (1-x**0.5)*0.7
    
#map_on = 'pixel_count' # q variable
map_on = 'tree_depth'  # d variable
 
w=1920
h=1200
dist=1
color_map_func = lambda x:map_ice(antisquamp(x))

w=int(w) ; h=int(h)

#color_map_func_orig = color_map_func
#color_map_func = lambda v: tuple(int(x) for x in color_map_func_orig(v))

def make_map_test_image(maps):
    h_bar=10
    h_margin=4
    h_skip=h_margin+h_bar
    w=1600
    h=h_skip*len(maps)
    img = Image.new( 'RGB', (w,h), "black") # create a new black image
    pixels = img.load() # create the pixel map
    ybase=h_margin//2
    for colormap in maps:
        for x in range(w):
            for dy in range(h_bar):
                y = ybase+dy
                pixels[x,y] = colormap(float(x)/w)
        ybase += h_skip
    img.save("maps.png")

def make_all_map_test_image():
    all_maps = list(v for (k,v) in sorted(globals().items(),key=lambda p:p[0]) if isinstance(v,type(lambda:0)) and k.startswith('map_'))
    all_maps.append(color_map_func)
    print("Writing color maps for map functions:")
    print("\n".join("  %s"%x.__name__ for x in all_maps))
    make_map_test_image(all_maps)

def make_one_map_test_image(color_map_func):
    w=1600
    h=20
    img = Image.new( 'RGB', (w,h), "black") # create a new black image
    pixels = img.load() # create the pixel map
    for x in range(w):
        for y in range(h):
            pixels[x,y] = color_map_func(float(x)/w)
    img.save("map.png")

if len(sys.argv)>=2 and sys.argv[1]=='c':
    print("Side-thing: making test image of all color ramps")
    make_all_map_test_image()
    sys.exit(1)

DIR_PERMUTATIONS = list(itertools.permutations("lrud"))
#for i in range(100): DIR_PERMUTATIONS.extend(["uldr","drul"]) # WOW!
#for i in range(100): DIR_PERMUTATIONS.extend(["udlr","durl"]) # meh
#for i in range(100): DIR_PERMUTATIONS.extend(["lurd","rdlu"]) # WOW-rot
#DIR_PERMUTATIONS=['lrud']
#DIR_PERMUTATIONS=["uldr","drul"]
#DIR_PERMUTATIONS=["udlr","durl"]
#DIR_PERMUTATIONS=["lurd","ulrd","rdul","drul"]
for i in range(8): DIR_PERMUTATIONS.extend(["lurd","rdlu"]) # WOW-rot
def shuffled_dirs():
    return random.choice(DIR_PERMUTATIONS)

def rotate(l,n):
    return l[n:] + l[:n]
    
def reclin(w,h):
    img = Image.new('RGB',(w,h),"black")
    pixels = img.load()
    
    primline(img,(0,h//2),0,1,1)
    
    return img

def zeroish(x):
    try:
        return sum(x)==0
    except TypeError:
        return x==0

def randint(a,b):
    if a>b: a,b=b,a
    return random.randint(a,b)
    
das_color = 1
# dim is 0 or 1
# step is -1 or 1
def primline(img,pos_start,dim,step,color, min_dist=1, num_forks=30):
    global das_color
    px = img.load()
    (w,h) = img.size
    if not (0<=pos_start[0]<w and 0<=pos_start[1]<h): return
    if not zeroish(px[pos_start[0],pos_start[1]]): return
    pos = list(pos_start)
    print("PL p0=%12s d=%d s=%2d c=%3d wh=%s px[pos]=%s" % (pos_start, dim, step, color, (w,h), px[pos[0],pos[1]]))
    while 0<=pos[0]<w and 0<=pos[1]<h and zeroish(px[pos[0],pos[1]]):
        #print("  pos=%s" % (pos,))
        px[pos[0],pos[1]] = color
        pos[dim] += step
    pos_end=pos
    dist = abs(pos_end[dim] - pos_start[dim])
    if dist < min_dist: return
    
    for i in range(num_forks):
        new_pos_start = [randint(pos_start[0],pos_end[0]), randint(pos_start[1],pos_end[1])]
        new_step = random.choice((-1,1))
        new_dim = 1 - dim
        new_color = color + 1
        #new_color = das_color
        #das_color = das_color + 1
        new_pos_start[new_dim] += new_step
        new_pos_start = tuple(new_pos_start)
        primline(img, new_pos_start, new_dim, new_step, new_color, min_dist=min_dist, num_forks=num_forks)
    

"""def do_walk(w, h, dir_func, dist=1, start_x=None, start_y=None, map_on='tree_depth', inline_colormap=None, print_progress=True):
    img = Image.new( 'RGB', (w,h), "white") # create a new black image
    pixels = img.load() # create the pixel map

    if start_x is None: x=w//2
    else:               x=start_x
    if start_y is None: y=h//2
    else:               y=start_y

    dirs={
        'u':( 0,-1),
        'd':( 0, 1),
        'r':( 1, 0),
        'l':(-1, 0)
    }

    backtrack={}

    q=0
    pixels[x,y]=1
    x0=x
    y0=y
    open_branches_from_origin=0
    d=0
    Q=int(w/dist)*int(h/dist)
    while True:
        moved=False
        for dir in dir_func(x,y,q,d,w,h):
            dx = dirs[dir][0]
            dy = dirs[dir][1]
            xn = x + dx*dist
            yn = y + dy*dist
            if (0<=xn<w) and (0<=yn<h) and (xn,yn) not in backtrack:
                if x==x0 and y==y0: 
                    open_branches_from_origin += 1
                d += 1
                moved = True
                q += 1
                f = float(q)/Q
                if print_progress and q%(max(1,Q//1000))==0:
                    sys.stdout.write("\r%d %.1f%%"%(q,100*f))
                    sys.stdout.flush()
                backtrack[xn,yn] = (x,y)
                for i in range(dist):
                    x += dx
                    y += dy
                    
                    if inline_colormap:
                        if   map_on == 'pixel_count': pixels[x,y] = inline_colormap(f)
                        elif map_on == 'tree_depth':  pixels[x,y] = inline_colormap(d/Q*2)
                    else:
                        # we cheat and cram the distance into the color field; later we retrieve it, normalize it, and apply the color map
                        if   map_on == 'pixel_count': pixels[x,y] = q
                        elif map_on == 'tree_depth':  pixels[x,y] = d
                break
        if not moved: # backtrack
            x,y = backtrack[x,y]
            d -= 1
            #print("BT (%d,%d)" % (x,y))
            if x==x0 and y==y0: open_branches_from_origin -= 1
            if open_branches_from_origin==0: break
    
    if print_progress:
        sys.stdout.write("\r                                      \n")
        sys.stdout.flush()
    return img
"""


def apply_colormap(img, colormap, max_v_filename=None, image_filename=None, print_progress=False):
    (w,h) = img.size
    pixels = img.load() # create the pixel map
    
    # find max v
    max_v = None
    if max_v_filename and os.path.isfile(max_v_filename):
        try:
            max_v = int(file(max_v_filename,"r").read())
            print("Read max_v from %s (%d)." % (max_v_filename,max_v))
        except Exception: 
            print("Unable to read max_v from %s." % (max_v_filename))
            pass
    
    print("Scanning for max_v...")
    if max_v is None:
        max_v=-1
        q=0
        Q=w*h
        for x in range(w):
            for y in range(h):
                q+=1
                f = float(q)/Q
                if q%(max(1,Q//1000))==0:
                    sys.stdout.write("\r%d %.1f%%"%(q,100*f))
                    sys.stdout.flush()
                p = pixels[x,y]
                if p == (255,255,255):
                    continue
                v = p[0] + 256*p[1] + 256*256*p[2]
                if v>max_v: max_v=v
        if max_v_filename:
            print("\nSaving max_v to %s (%d)..." % (max_v_filename,max_v))
            file(max_v_filename,"w").write(str(max_v))

    #if print_progress: print("\nmax_v=%d"%max_v)
    # apply color map to to all pixels
    q=0
    Q=w*h
    for x in range(w):
        for y in range(h):
            q+=1
            f = float(q)/Q
            if q%(max(1,Q//1000))==0:
                sys.stdout.write("\r%d %.1f%%"%(q,100*f))
                sys.stdout.flush()
            p = pixels[x,y]
            v = p[0] + 256*p[1] + 256*256*p[2]
            #if v == 255*256*255+256*256*255:
            if p == (255,255,255):
                pixels[x,y] = (0,0,0)
            else:
                pixels[x,y] = colormap(float(v)/max_v)
            
    if print_progress:
        sys.stdout.write("\n")
        sys.stdout.flush()

input_filename = None
output_unmapped_filename = "out-unmapped.png"
max_v_filename = "%s.maxv" % output_unmapped_filename
output_filename = "out.png"
if len(sys.argv)>=2:
    input_filename = sys.argv[1]
    max_v_filename = "%s.maxv" % input_filename
if len(sys.argv)>=3:
    output_filename = sys.argv[2]
    output_unmapped_filename = output_filename.replace(".png","-unmapped.png")
    if output_unmapped_filename==output_filename: output_unmapped_filename="out-unmapped.png" # ugh whatever im lazy
    
if input_filename:
    print("Reading %s..." % input_filename)
    img = Image.open(input_filename)
else:
    print("Rendering walk...")
    img = reclin(w,h)
    print("Saving %s..." % output_filename)
    img.save(output_unmapped_filename)
    try: os.remove(max_v_filename)
    except: pass
print("Applying color map...")
apply_colormap(img, color_map_func, max_v_filename=max_v_filename, print_progress=True)
print("Saving %s..." % output_filename)
img.save(output_filename)
print("Done.")
#img.show()
