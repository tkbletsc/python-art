import sys,os,re,math
import random
import colorsys

class ImageRGB(object):
    def __init__(self,w,h):
        self.w = w
        self.h = h
        self.img = [[(0,0,0)]*w for i in range(h)]

    def save_ppm(self, filename):
        with open(filename,"w") as fp:
            fp.write("P3\n")
            fp.write("%d %d\n" % (len(self.img[0]),len(self.img)))
            fp.write("255\n")
            for row in self.img:
                fp.write("  ".join("%3d %3d %3d"%v for v in row) + "\n")
        
    def set_pixel(self, x, y, color):
        self.img[y][x] = color

def dir_to_delta(dir):
    if   dir==0: return ( 0,-1)
    elif dir==1: return ( 1, 0)
    elif dir==2: return ( 0, 1)
    elif dir==3: return (-1, 0)
    
def all_colors(skip=1):
    for r in range(0,256,skip):
        for g in range(0,256,skip):
            for b in range(0,256,skip):
                yield (r,g,b)

def all_colors_hsv(h_bound=(0,256),s_bound=(0,256),v_bound=(0,256), skip=1):
    for h in range(h_bound[0], h_bound[1], skip):
        for s in range(s_bound[0], s_bound[1], skip):
            for v in range(v_bound[0], v_bound[1], skip):
                yield hsv2rgb((h,s,v))

def rgb2hsv(rgb): return tuple(int(255*v) for v in colorsys.rgb_to_hsv(*[v/255.0 for v in rgb]))
def hsv2rgb(hsv): return tuple(int(255*v) for v in colorsys.hsv_to_rgb(*[v/255.0 for v in hsv]))

def color_dist_rgb(c1,c2):
    return tuple_delta(c1,c2)
    
def color_dist_rgb2(c1,c2):
    return tuple_delta_sq(c1,c2)
    
def tuple_delta(c1,c2):
    return sum(abs(v1-v2) for v1,v2 in zip(c1,c2))
    
def tuple_delta_sq(c1,c2):
    return sum(abs(v1-v2)**2 for v1,v2 in zip(c1,c2))
    
def color_dist_hsv(c1,c2):
    return tuple_delta(rgb2hsv(c1),rgb2hsv(c2))
    
def color_dist_hsv2(c1,c2):
    return tuple_delta_sq(rgb2hsv(c1),rgb2hsv(c2))
    
    
# whatevs, its ugly but works
def spiral(img, origin_x, origin_y, colors):
    x = origin_x
    y = origin_y
    dir = 0
    leg_pos = 0
    leg_dist = -1
    for color in colors:
        img.set_pixel(x,y, color)
        
        if leg_pos >= leg_dist:
            if dir==0 or dir==2:
                leg_dist += 1
            dir = (dir+1) % 4
            leg_pos = 0
        else:
            leg_pos += 1
            
        delta = dir_to_delta(dir)
        x += delta[0]
        y += delta[1]

def allow_color(c):
    hsv = rgb2hsv(c)
    if hsv[0] > 50: return False
    if hsv[1] < 100: return False
    if hsv[2] < 150: return False
    return True
    
print "Generating color list..."
#colors = list(c for c in all_colors(3) if allow_color(c))
#colors = list(all_colors(4))
colors = all_colors_hsv((0,256),(150,250),(250,256))
colors = list(colors)
n = len(colors)
w = int(1.0 * math.sqrt(n))+3
h = w
    
print "Initializing image..."
img = ImageRGB(w,h)

print "Sorting color list..."
base_color = (0,0,0)
#random.shuffle(colors)
colors.sort(key=lambda c: rgb2hsv(c)[0])
#colors.sort(key=lambda c: c[0])
#colors.sort(key=lambda c: color_dist_hsv2(c, base_color))

print "Generating spiral..."
spiral(img,w/2,h/2,colors)

print rgb2hsv((255,0,0))

print "Writing image..."
img.save_ppm("x3.ppm")