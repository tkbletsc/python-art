#!/usr/bin/perl

import os,sys,re
import Image,ImageDraw
from colorsys import hsv_to_rgb
import math

def linmap (v,oa,ob,na,nb):
	return float(v-oa)/(ob-oa)*(nb-na) + na

def color_linmap(v,c1,c2):
	return tuple(linmap(v,0,1,c1v,c2v) for c1v,c2v in zip (c1,c2))

def channel_ramp(v,order): 
	r = [0,0,0]
	r[order[0]] = linmap(v,0.000000,0.333333,0,1)
	r[order[1]] = linmap(v,0.333333,0.666666,0,1)
	r[order[2]] = linmap(v,0.666666,1.000000,0,1)
	return tuple(r)

def map_fire(v):     return channel_ramp(v,(0, 1, 2))
def map_rose(v):     return channel_ramp(v,(0, 2, 1))
def map_spring(v):   return channel_ramp(v,(1, 0, 2))
def map_emerald(v):  return channel_ramp(v,(1, 2, 0))
def map_amethyst(v): return channel_ramp(v,(2, 0, 1))
def map_ice(v):      return channel_ramp(v,(2, 1, 0))
def map_grey(v):     return (v,)*3
def map_hue(v):      return hsv_to_rgb(v,1,1)
def map_on(v):       return (1,1,1)

def make_map_interp(c1,c2): return lambda v: color_linmap(v,c1,c2)

def xform_gen_cos(n): return lambda v: math.cos(v*math.pi*n)/2+0.5
def xform_middle(v): return linmap(v,0,1,0.25,0.75)

def hilbert(x, y, xi, xj, yi, yj, n):
	#/* x and y are the coordinates of the bottom left corner */
	#/* xi & xj are the i & j components of the unit x vector of the frame */
	#/* similarly yi and yj */
	if n <= 0:
		yield (x + (xi + yi)/2, y + (xj + yj)/2)
	else:
		for q in hilbert(x,           y,           yi/2, yj/2,  xi/2,  xj/2, n-1): yield q
		for q in hilbert(x+xi/2,      y+xj/2 ,     xi/2, xj/2,  yi/2,  yj/2, n-1): yield q
		for q in hilbert(x+xi/2+yi/2, y+xj/2+yj/2, xi/2, xj/2,  yi/2,  yj/2, n-1): yield q
		for q in hilbert(x+xi/2+yi,   y+xj/2+yj,  -yi/2,-yj/2, -xi/2, -xj/2, n-1): yield q

def gen_hilbert_image(filename, n, xform=None, colormap=map_grey, s_factor=1, sx=None, sy=None, bg=(0,0,0), verbose=True):
	s = int(2**n * s_factor)
	if not sx: sx=s
	if not sy: sy=s
	num_points = 4**n

	img = Image.new("RGB", (sx, sy), bg)
	draw = ImageDraw.Draw(img)
	
	if verbose:
		print "Rendering to %s (%dx%d), %d hilbert points..." % (filename,sx,sy,num_points)
	
	x0,y0=None,None
	p = 0
	for x,y in hilbert(0,0, sx,0 ,0,sy, n):
		f = float(p)/num_points
		if xform: f = xform(f)
		color = colormap(f)
		color = tuple(int(max(min(c*255,255),0)) for c in color) # integer-ify and bound the color map
		
		if verbose and p%(max(1,num_points/20))==0: # print status at least every 5%
			print "%.0f%%" % (100.0*p/num_points)
		
		if x0 is not None:
			draw.line((x0,y0,x,y), fill = color)
		
		(x0,y0) = (x,y)
		p += 1

	if verbose: 
		print "Saving to %s..." % filename
	img.save(filename,"PNG")
		
#gen_hilbert_image("x1.png",8,colormap=map_fire,xform=lambda v: xform_middle(xform_gen_cos(8)(v)),s_factor=3)
#gen_hilbert_image("x1.png",8,colormap=make_map_interp((16./256,3./256,56./256),(22./256,6./256,91./256)), s_factor=3)
gen_hilbert_image("x1.png",4,colormap=map_grey, s_factor=4)