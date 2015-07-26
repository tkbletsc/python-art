import sys,os,re
import random
from PIL import Image

 
#print(sys.getrecursionlimit())
#sys.exit(1)
sys.setrecursionlimit(100000)
 
w=101
h=101
img = Image.new( 'RGB', (w,h), "black") # create a new black image
pixels = img.load() # create the pixel map

x=w/2*0
y=h/3*0

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
dist=2
pixels[x,y]=1
x0=x
y0=y
while True:
    moved=False
    print("(%d,%d)"%(x,y))
    q += 1
    if q>10000: break
    for dir in shuffled_dirs():
        dx = dirs[dir][0]
        dy = dirs[dir][1]
        xn = x + dx*dist
        yn = y + dy*dist
        print("(%d,%d) <%s>"%(x,y,dir))
        if (0<=xn<w) and (0<=yn<h) and (xn,yn) not in backtrack:
            print("(%d,%d) <%s> GO %d"%(x,y,dir,moved))
            moved = True
            backtrack[xn,yn] = (x,y)
            for i in range(dist):
                x += dx
                y += dy
                pixels[x,y] = 1        
            break
    if not moved: # backtrack
        print("BT")
        antidir = backtrack[x,y]
        dx = -dirs[antidir][0]
        dy = -dirs[antidir][1]
        x += dx*dist
        y += dy*dist
        print("BT <%s> (%d,%d)" % (antidir,x,y))
        if x==x0 and y==y0: break
    
img.show()