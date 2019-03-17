import pandas as pd
import numpy as np
from scipy import spatial
from math import *


def rad2deg(rad):
	'''
	function to convert radian to degree
	'''
	degree = rad/2/np.pi * 360
	return(degree)

def kmToDIST(x):
	'''
	function to convert real distance in km to cartesian distance 
	'''
	R = 6371 # earth radius
	gamma = 2*np.arcsin(x/2./R) 
	
	dist = 2*R*rad2deg(sin(gamma / 2.))
	return(dist)

def to_Cartesian(lat, lng):
	'''
	function to convert latitude and longitude to 3D cartesian coordinates
	'''
	R = 6371 # radius of the Earth in kilometers

	x = R * cos(lat) * cos(lng)
	y = R * cos(lat) * sin(lng)
	z = R * sin(lat)
	return x, y, z

def haversine(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees)
	"""
	# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

	# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	r = 6371 # Radius of earth in kilometers. Use 3956 for miles
	
	return c * r