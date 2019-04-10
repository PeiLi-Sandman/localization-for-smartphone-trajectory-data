from utils import *
import pandas as pd
import numpy as np

def get_points(smartphone, base, threshold):
    
    # convert the threshold value(km) to cartesian coordinates distance
    dist_item = kmToDIST(threshold)
    
    dist = [dist_item] * len(smartphone)
    #dist = kmToDIST(threshold)
    lats_1d = base[:,1]
    lons_1d = base[:,2]
    x, y, z = zip(*map(to_Cartesian, lats_1d, lons_1d))
    # create the KD-tree using the 3D cartesian coordinates
    coordinates = list(zip(x, y, z))
    tree = spatial.cKDTree(coordinates)

    

    xyz_ref = np.array([to_Cartesian(lat, lng) for lat, lng in zip(smartphone[:, 2], smartphone[:, 1])])
    # get all the points within the threshold
    ix = [tree.query_ball_point((x_ref, y_ref, z_ref), dist) for x_ref, y_ref, z_ref, dist in zip(xyz_ref[:,0],xyz_ref[:,1],xyz_ref[:,2], dist)]
    
    return ix

def get_trajectory(smartphone, ix):
    
    min_distance = []
    for i in range(len(smartphone)):
        all_distance = []
        all_delta_direction = []
        indice_map = []

        lat_phone = smartphone[i, 2]
        lon_phone = smartphone[i, 1]
        
        direction_phone = smartphone[i, 3]
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

    trajectory_raw = [x for x in basemap['approach_id'][min_distance]]
    trajectory = [x for x in trajectory_raw if str(x) != 'nan']

    return trajectory

if __name__ == '__main__':
    import time
    start_time = time.time()
    # here you need to define your own data
    basemap = pd.read_csv(r'G:\Project\Smart Phone\GPS\map\template\point_along_road.csv')
    android = pd.read_csv(r'G:\Project\Smart Phone\GPS\Experiment\3_13\android\20_13_new.csv')
    iphone = pd.read_csv(r'G:\Project\Smart Phone\GPS\Experiment\3_13\iphone\20_13_new.csv')

    iphone = iphone.sort_values(by='Date')
    iphone = iphone.loc[:,['Date','lon','lan']]
    iphone = iphone.drop_duplicates(subset=['lon','lan'])
    iphone = iphone.reset_index(drop=True)

    #get the direction of android
    android = android.sort_values(by='Date')
    android = android.loc[:,['Date','lon','lat']]
    android = android.drop_duplicates(subset=['lon','lat'])
    android = android.reset_index(drop=True)
    android['direction'] = 0
    android['lon_1'] = android['lon'].shift(-1)
    android['lat_1'] = android['lat'].shift(-1)

    for i in range(len(android['Date'])):
        pointA = (android['lat'][i], android['lon'][i])
        pointB = (android['lat_1'][i], android['lon_1'][i])
        android['direction'][i] = calculate_initial_compass_bearing(pointA, pointB)
    
    android = android.drop(columns=['lon_1','lat_1'])
    android = android.drop((len(android)-1))
    
    #get the direction of iphone
    iphone = iphone.sort_values(by='Date')
    iphone = iphone.loc[:,['Date','lon','lan']]
    iphone = iphone.drop_duplicates(subset=['lon','lan'])
    iphone = iphone.reset_index(drop=True)
    iphone['direction'] = 0
    iphone['lon_1'] = iphone['lon'].shift(-1)
    iphone['lan_1'] = iphone['lan'].shift(-1)

    for i in range(len(iphone['Date'])):
        pointA = (iphone['lan'][i], iphone['lon'][i])
        pointB = (iphone['lan_1'][i], iphone['lon_1'][i])
        iphone['direction'][i] = calculate_initial_compass_bearing(pointA, pointB)
    
    iphone = iphone.drop(columns=['lon_1','lan_1'])
    iphone = iphone.drop((len(iphone)-1))

    android_numpy = android.as_matrix()
    basemap_numpy = basemap.as_matrix()
    iphone_numpy = iphone.as_matrix()

    ix_iphone = get_points(iphone_numpy, basemap_numpy, 0.03)
    ix_android = get_points(android_numpy, basemap_numpy, 0.05)
    trajectory_iphone = get_trajectory(iphone_numpy, ix_iphone)
    trajectory_android = get_trajectory(android_numpy, ix_android)

    print('the trajectory of iphone is:', [int(x) for x in trajectory_iphone])
    print('the trajectory of android is:', [int(x) for x in trajectory_android])
    print("--- %s seconds ---" % (time.time() - start_time))
