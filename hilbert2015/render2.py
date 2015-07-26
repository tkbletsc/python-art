#!/usr/bin/perl

import os,sys,re
#import Image,ImageDraw
#from colorsys import hsv_to_rgb
import colorsys
import math
from struct import pack,unpack,calcsize
from array import array
import itertools

from hilbert import *

def linmap (v,oa,ob,na,nb):
	return float(v-oa)/(ob-oa)*(nb-na) + na

# use the colorsys function with values in [0..255] instead of [0..1]
def colorsys_wrap(func, a,b,c):
    a,b,c = (v/255.0 for v in (a,b,c))
    x,y,z = func(a,b,c)
    return tuple(int(v*255) for v in (x,y,z))

def rgb2yiq(a,b,c): return colorsys_wrap(colorsys.rgb_to_yiq, a,b,c)
def yiq2rgb(a,b,c): return colorsys_wrap(colorsys.yiq_to_rgb, a,b,c)
def rgb2hls(a,b,c): return colorsys_wrap(colorsys.rgb_to_hls, a,b,c)
def hls2rgb(a,b,c): return colorsys_wrap(colorsys.hls_to_rgb, a,b,c)
def rgb2hsv(a,b,c): return colorsys_wrap(colorsys.rgb_to_hsv, a,b,c)
def hsv2rgb(a,b,c): return colorsys_wrap(colorsys.hsv_to_rgb, a,b,c)



class ImageRGB(object):
    def __init__(self,w,h):
        self.w = w
        self.h = h
        #self.img = [[(0,0,0)]*w for i in range(h)]
        #self.img = array("B", (0 for i in range(3*w*h)))
        self.img = array("B", [0]*(3*w*h))

    def save_ppm(self, filename, binary=True):
        if binary:
            with open(filename,"wb") as fp:
                fp.write("P6\n")
                fp.write("%d %d\n" % (self.w,self.h))
                fp.write("255\n")
                self.img.tofile(fp)
        else:
            with open(filename,"w") as fp:
                fp.write("P3\n")
                fp.write("%d %d\n" % (self.w,self.h))
                fp.write("255\n")
                #TODO - make this print the color components on one line if you care
                fp.write("\n".join(str(v) for v in self.img))
        
    def set_pixel(self, x, y, color):
        self.set_pixel_i(y*self.w + x, color)
        
    def set_pixel_i(self, i, color):
        self.img[3*i : 3*i+3] = array("B",color)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

def cached_hilbert_sequence(max_i, nD):
    fmt = "i" * nD
    filename = "cache-hilbert-%d-%d.dat" % (nD,max_i)
    if not os.path.exists(filename):
        print ""
        with open(filename,"wb") as fp:
            for i in range(max_i):
                if i%100==0: sys.stdout.write("\rGenerating hilbert cache: %10d / %10d : %.1f%%            " % (i,max_i, float(i)/max_i*100))
                point = int_to_Hilbert( i, nD )
                fp.write(pack(fmt, *point))
        print ""
    with open(filename) as fp:
        while True:
            buf = fp.read(calcsize(fmt))
            if not buf: break
            yield unpack(fmt,buf)

print "Initializing..."

def hsv_to_rgb_integer(h,s,v):
    # HSV to RGB conversion function with only integer math - from http://web.mit.edu/storborg/Public/hsvtorgb.c
    if s == 0:
        # color is grayscale
        return (v,v,v)
    
    # /* make hue 0-5 */
    region = h / 43
    # /* find remainder part, make it from 0-255 */
    fpart = (h - (region * 43)) * 6;
    
    # /* calculate temp vars, doing integer multiplication */
    p = (v * (255 - s)) >> 8
    q = (v * (255 - ((s * fpart) >> 8))) >> 8
    t = (v * (255 - ((s * (255 - fpart)) >> 8))) >> 8
        
    # /* assign temp vars based on color cone region */
    if   region==0: return (v,t,p)
    elif region==1: return (q,v,p)
    elif region==2: return (p,v,t)
    elif region==3: return (p,q,v)
    elif region==4: return (t,p,v)
    else:           return (v,p,q)



def rgb2i(r,g,b):
    return r<<16 | g<<8 | b
def i2rgb(i):
    return ((i&0xff0000)>>16, (i&0xff00)>>8, i&0xff)
    
#all_colors = [i2rgb(i) for i in range(n**3)]
#all_colors = [i2rgb(i) for i in range(n**3)]
#all_colors = array("I", rgb2i(rgb) for rgb in itertools.product(range(n),repeat(3)))
#for q in itertools.product(range(n),repeat=3): print q
#all_colors = array("I", (rgb2i(*rgb) for rgb in itertools.product(range(n),repeat=3)))
#all_colors = [rgb2i(*rgb) for rgb in itertools.product(range(n),repeat=3)]

def my_rgb_to_yiq(colorsystem_scale_factor, r,g,b): 
    y,i,q = colorsys.rgb_to_yiq(r/255.0,g/255.0,b/255.0)
    return (
        int(y*colorsystem_scale_factor),
        int(linmap(i,-1,1,0,colorsystem_scale_factor)),
        int(linmap(q,-1,1,0,colorsystem_scale_factor))
    )
def my_rgb_to_hls(colorsystem_scale_factor, r,g,b): return tuple(int(v*colorsystem_scale_factor) for v in colorsys.rgb_to_hls(r/255.0,g/255.0,b/255.0))
def my_rgb_to_hsv(colorsystem_scale_factor, r,g,b): return tuple(int(v*colorsystem_scale_factor) for v in colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0))

colorsystems = {
    'rgb': lambda F, r,g,b: (r,g,b),
    'yiq': my_rgb_to_yiq,
    'hls': my_rgb_to_hls,
    'hsv': my_rgb_to_hsv,
}


all_colors = None

def make_map(n, colorsystem_name, colorsystem_scale_factor):
    global all_colors

    colorsystem_func = colorsystems[colorsystem_name]
    img_filename = "colors-%d-%s-%04d.ppm" % (n,colorsystem_name,colorsystem_scale_factor)
    
    if os.path.exists(img_filename):
        print "Skipping %s" % img_filename
        print ""
        return

    print "Making %s..." % img_filename
    
    image_size = int(n**(3.0/2.0))
    max_i = n**3
    

    # re-use the color array if possible
    if all_colors and len(all_colors)==n**3:
        print "Re-using color list."
    else:
        print "Generating color list..."
        all_colors = [rgb2i(*rgb) for rgb in itertools.product((256/n*v for v in range(n)),repeat=3)]

    print "Sorting color list..."
    all_colors.sort(key=lambda c: Hilbert_to_int(colorsystem_func(colorsystem_scale_factor, *i2rgb(c))))

    hilberts2d = cached_hilbert_sequence(n**3, 2)

    img = ImageRGB(image_size,image_size)

    for i,color in enumerate(all_colors):
        if i%1000==0: sys.stdout.write("\rRendering: %10d / %10d : %.1f%%            " % (i,max_i, float(i)/max_i*100))
        x,y = hilberts2d.next()
        img.set_pixel(x,y,i2rgb(color))
    print ""    

    print "Saving %s..." % img_filename

    img.save_ppm(img_filename)
    
    print "Done with %s." % img_filename

def make_strip(n, colorsystem_name, colorsystem_scale_factor, h=1):
    global all_colors

    colorsystem_func = colorsystems[colorsystem_name]
    img_filename = "strip-%d-%s-%04d.ppm" % (n,colorsystem_name,colorsystem_scale_factor)
    
    if os.path.exists(img_filename):
        print "Skipping %s" % img_filename
        print ""
        return

    print "Making %s..." % img_filename
    
    #image_size = int(n**(3.0/2.0))
    max_i = n**3
    

    # re-use the color array if possible
    if all_colors and len(all_colors)==n**3:
        print "Re-using color list."
    else:
        print "Generating color list..."
        all_colors = [rgb2i(*rgb) for rgb in itertools.product((256/n*v for v in range(n)),repeat=3)]

    print "Sorting color list..."
    all_colors.sort(key=lambda c: Hilbert_to_int(colorsystem_func(colorsystem_scale_factor, *i2rgb(c))))

    #hilberts2d = cached_hilbert_sequence(n**3, 2)

    img = ImageRGB(len(all_colors),h)

    for i,color in enumerate(all_colors):
        if i%1000==0: sys.stdout.write("\rRendering: %10d / %10d : %.1f%%            " % (i,max_i, float(i)/max_i*100))
        for y in range(h):
            img.set_pixel(i,y,i2rgb(color))
    print ""    

    print "Saving %s..." % img_filename

    img.save_ppm(img_filename)
    
    print "Done with %s." % img_filename


print ""

def make_map_helper(lst): return make_map(*lst)
def make_strip_helper(lst): return make_strip(*lst,h=64)

def iff(c,a,b):
    if c: return a
    else: return b
    
#colorsystem_scale_factors = [512,256,1024]
colorsystem_scale_factors = [2**i for i in range(8,14)]
n_values = [16]
param_lists = []
for colorsystem_scale_factor in colorsystem_scale_factors:
    for n in n_values:
        for colorsystem_name in colorsystems.keys():
            param_list = (n, colorsystem_name, iff(colorsystem_name!='rgb',colorsystem_scale_factor,0))
            if param_list not in param_lists:
                param_lists.append(param_list) 

parallelism = 4

target_func = make_strip_helper

print "\033[32mParam lists:\033[m"
for param_list in param_lists:
    print "\033[32m  %s\033[m" % str(param_list)
if parallelism>1:
    print "\033[32mStarting multiprocessing (p=%d)...\033[m" % parallelism
    import multiprocessing as mp
    pool = mp.Pool(parallelism)
    pool.map(target_func, param_lists)
else:
    print "\033[32mSingle-process mode proceeding...\033[m"
    for param_list in param_lists:
        target_func(param_list)
print "\033[32mDone.\033[m"
    
#pool.close()
#pool.join()

"""

for color_xform in (far, rgb, yiq, hls, hsv):
    print ""
    
    color_xform_name = color_xform.__name__
    img_filename = "colors-%d-%s.ppm" % (n,color_xform_name)
    
    if os.path.exists(img_filename):
        print "Skipping %s" % img_filename
        continue
    
    #done_rgb = set()
    done_rgb = array("B", [0]*(256**3))

    print "Making %s..." % img_filename
    
    hilberts2d = read_point_list(fn2d, 2)
    hilberts3d = read_point_list(fn3d, 3)

    img = ImageRGB(image_size,image_size)
    
    dupes = 0

    for i in range(max_i):
        if i%1000==0: sys.stdout.write("\r%10d / %10d : %.1f%%            " % (i,max_i, float(i)/max_i*100))
        a,b,c = tuple(hilberts3d.next())
        color = color_xform(i,a,b,c)
        x,y = hilberts2d.next()
        if done_rgb[rgb2i(*color)]:
            dupes+=1
            #print "Dup: %s" % str(color)
        done_rgb[rgb2i(*color)] = 1
        #done_rgb.add(color)
        img.set_pixel(x,y,color)
    print ""    
    
    if dupes: print "Did %d duplicate RGBs" % dupes

    print "Saving %s..." % img_filename

    img.save_ppm(img_filename)
    
    print "Identifying missing colors..."
    #list_missing = []
    num_missing = 256**3 - sum(done_rgb)
    print "Missing colors: %d" % num_missing
    if num_missing:
        img_missing_filename = "missing-%d-%s.ppm" % (n,color_xform_name)
        print "Saving missing colors to %s..." % img_missing_filename
        sz = int(num_missing ** 0.5 + 1)
        img_missing = ImageRGB(sz,sz)
        j=0
        for i in range(256**3):
            if i%1000==0: sys.stdout.write("\r%10d / %10d : %.1f%%            " % (i,256**3, float(i)/256**3*100))
            if not done_rgb[i]:
                img_missing.set_pixel_i(j, i2rgb(i))
                j+=1
        print ""
        img_missing.save_ppm(img_missing_filename)
        print "Saved."

"""