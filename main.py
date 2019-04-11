from utils import *
import pandas as pd
import numpy as np



def get_points(smartphone, basemap, threshold):
	
	# convert to cartesian coordinates distance
	dist_item = kmToDIST(threshold)
	
	dist = [dist_item] * len(smartphone)
	#dist = kmToDIST(threshold)
	lats_1d = basemap[:,1]
	lons_1d = basemap[:,2]
	x, y, z = zip(*map(to_Cartesian, lats_1d, lons_1d))
	# create the KD-tree using the 3D cartesian coordinates
	coordinates = list(zip(x, y, z))
	tree = spatial.cKDTree(coordinates)

	
	#x_ref, y_ref, z_ref = [to_Cartesian(lat, lng) for lat, lng in zip(smartphone[:, 2], smartphone[:, 1])]
	xyz_ref = np.array([to_Cartesian(lat, lng) for lat, lng in zip(smartphone[:, 1], smartphone[:, 0])])
	# get all the points within 30 km from the reference point
	ix = [tree.query_ball_point((x_ref, y_ref, z_ref), dist) for x_ref, y_ref, z_ref, dist in zip(xyz_ref[:,0],xyz_ref[:,1],xyz_ref[:,2], dist)]
	
	return ix

def get_distance(smartphone, basemap_numpy, basemap, ix):
	min_distance = []
	for i in range(len(smartphone)):
		all_distance = []
		all_delta_direction = []
		indice_map = []

		lat_phone = smartphone[i, 1]
		lon_phone = smartphone[i, 0]
		
		direction_phone = smartphone[i, 2]
		indice = ix[i]
		#lat_map = basemap_numpy[j, 1]
		#lon_map = basemap_numpy[j, 2]
		
		if indice != []:
			for j in range(len(indice)):
				item = indice[j]
				lat_map = basemap_numpy[item, 1]
				lon_map = basemap_numpy[item, 2]
				direction_map = basemap_numpy[item, 3]
				distance = haversine(lon_phone, lat_phone, lon_map, lat_map)
				delta_direction = np.abs(direction_phone - direction_map)

				all_distance.append(distance)
				all_delta_direction.append(delta_direction)
				indice_map.append(item)
				df = np.array([indice_map, all_distance, all_delta_direction])
				df = df[:, np.where(df[2, ] <= 90)]
				df = df.reshape(3,df.shape[2])
				if df !=[]:
					#df = np.array([indice_map, all_distance])
					min_indice = int(df[0, ][np.argmin(df[1, ])])
				else:
					min_indice = len(basemap_numpy)
		else:
			df = []
			min_indice = len(basemap_numpy)
		min_distance.append(min_indice)
	return min_distance

def approach_local(smartphone, basemap_numpy, basemap, ix):
	
	min_distance = get_distance(smartphone, basemap_numpy, basemap, ix)
	trajectory_raw = [x for x in basemap['approach_id'][min_distance]]
	trajectory_raw = pd.Series(trajectory_raw).fillna(0).tolist()
	trajectory = [x for x in trajectory_raw if str(x) != 'nan']

	#print('the vechilce trajectory is:', [int(x) for x in trajectory])

	result =  [int(x) for x in trajectory]
	
	return result


if __name__ == '__main__':
	path = r'G:\Project\Smart Phone\GPS\map matching\data\iphone1.csv'
	raw_data, approach_matrix, movement_matrix = dataprepossessing(path)
	basemap = pd.read_csv(r'G:\Project\Smart Phone\GPS\map\template\point_along_road.csv')
	basemap_matrix = basemap.as_matrix()
	ix = get_points(approach_matrix, basemap_matrix, 0.006)
	appoach_result = approach_local(approach_matrix, basemap_matrix, basemap, ix)