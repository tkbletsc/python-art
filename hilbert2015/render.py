#!/usr/bin/perl

import os,sys,re
#import Image,ImageDraw
#from colorsys import hsv_to_rgb
import colorsys
import math
from struct import pack,unpack,calcsize
from array import array

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

def read_point_list(filename, nD):
    fp = open(filename)
    fmt = "i" * nD
    while True:
        buf = fp.read(calcsize(fmt))
        if not buf: break
        yield unpack(fmt,buf)

n = 256
#^ must be power of 4 for image dims to come out integer
image_size = int(n**(3.0/2.0))
max_i = n**3

fn2d = "cache-hilbert-2-%d.dat" % max_i
fn3d = "cache-hilbert-3-%d.dat" % max_i
if not os.path.exists(fn2d) or not os.path.exists(fn3d):
    print "Generating hilberts from scratch..."
    with open(fn2d,"wb") as fp2d:
        with open(fn3d,"wb") as fp3d:
            for i in range(max_i):
                if i%100==0: sys.stdout.write("\r%10d / %10d : %.1f%%            " % (i,max_i, float(i)/max_i*100))
                h2d = int_to_Hilbert( i, 2 )
                h3d = int_to_Hilbert( i, 3 )
                fp2d.write(pack("ii", h2d[0], h2d[1]))
                fp3d.write(pack("iii", h3d[0], h3d[1], h3d[2]))
    print ""

print "Initializing..."

def rgb(i,r,g,b): return r,g,b
def far(i,x,y,z): return (int(255.0*i/max_i),) * 3
def yiq(j,y,i,q): return yiq2rgb(y,linmap(i,0,255,-255,255),linmap(q,0,255,-255,255))
def hls(i,h,l,s): return hls2rgb(h,l,s)
#def hsv(i,h,s,v): return hsv2rgb(h,s,v)


def hsv(i,h,s,v):
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

                