import sys,os,re
import random
from PIL import Image
import colorsys

def plex(v,n): return v*n-int(v*n)
    
def linmap (v,oa,ob,na,nb):
	return float(v-oa)/(ob-oa)*(nb-na) + na

def color_linmap(v,a,b,c1,c2):
	return tuple(int(linmap(v,a,b,c1v,c2v)) for c1v,c2v in zip (c1,c2))

def color_2map(v,c1,c2,c3):
	return tern(v<0.5,color_linmap(v,0,0.5,c1,c2),color_linmap(v,0.5,1.0,c2,c3))

def channel_ramp(v,order): 
	r = [0,0,0]
	r[order[0]] = linmap(v,0.000000,0.333333,0,255)
	r[order[1]] = linmap(v,0.333333,0.666666,0,255)
	r[order[2]] = linmap(v,0.666666,1.000000,0,255)
	return tuple(int(x) for x in r)

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

def map_cyan(v): return (0,int(linmap(plex(v,3),0.5,1.0,0,255)),int(linmap(plex(v,3),0,0.5,0,255)))
    
def map_blux(v): 
    vv = (plex(v,3) + plex(v,11) + plex(v,5))/3
    return color_2map(vv,(0,0,0),(0,0,255),(255,255,255))
    
def map_blue2white(v): return color_2map(plex(v,21),(0,0,0),(0,0,255),(255,255,255))
    
def tern(t,a,b):
    if t: return a
    else: return b
 
#print(sys.getrecursionlimit())
#sys.exit(1)
sys.setrecursionlimit(100000)
 
w=1920*0.5
h=1200*0.5
dist=1
color_map_func = map_colorpatchy

w=int(w) ; h=int(h)

#color_map_func_orig = color_map_func
#color_map_func = lambda v: tuple(int(x) for x in color_map_func_orig(v))

if 0:
    w=1600
    h=20
    img = Image.new( 'RGB', (w,h), "black") # create a new black image
    pixels = img.load() # create the pixel map
    for x in range(w):
        for y in range(h):
            pixels[x,y] = color_map_func(x/w)
    img.show()
    sys.exit(1)


img = Image.new( 'RGB', (w,h), "black") # create a new black image
pixels = img.load() # create the pixel map

x=w//2
y=h//3

dirs={
    'u':( 0,-1),
    'd':( 0, 1),
    'r':( 1, 0),
    'l':(-1, 0)
}

def shuffled_dirs():
    ops = list('lrud')
    random.shuffle(ops)
    return ops

backtrack={}

q=0
pixels[x,y]=1
x0=x
y0=y
open_branches_from_origin=0
Q=int(w/dist)*int(h/dist)
while True:
    moved=False
    #print("(%d,%d)"%(x,y))
    for dir in shuffled_dirs():
        dx = dirs[dir][0]
        dy = dirs[dir][1]
        xn = x + dx*dist
        yn = y + dy*dist
        #print("(%d,%d) <%s>"%(x,y,dir))
        if (0<=xn<w) and (0<=yn<h) and (xn,yn) not in backtrack:
            #print("(%d,%d) <%s> GO %d"%(x,y,dir,moved))
            if x==x0 and y==y0: open_branches_from_origin += 1
            moved = True
            q += 1
            f = float(q)/Q
            if q%(Q//1000)==0:
                sys.stdout.write("\r%d %.1f%%"%(q,100*f))
                sys.stdout.flush()
            backtrack[xn,yn] = (x,y)
            for i in range(dist):
                x += dx
                y += dy
                pixels[x,y] = color_map_func(f)
            break
    if not moved: # backtrack
        x,y = backtrack[x,y]
        #print("BT (%d,%d)" % (x,y))
        if x==x0 and y==y0: open_branches_from_origin -= 1
        if open_branches_from_origin==0: break
print("\nDone.                        ")
img.save("out.png")
img.show()