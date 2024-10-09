import json
import math
import os


# 거리 계산
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # 지구의 반경 (미터)
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return round(distance)


# 거리가 가장 가까운 역 찾기
def find_nearest_station(lat, lon):
    file_path = os.path.join(os.path.dirname(__file__), 'data/station_activity.json')

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f) 

    stations = data['stations']
    nearest_station = None
    min_distance = float('inf')
    
    for station in stations:
        distance = calculate_distance(lat, lon, station['latitude'], station['longitude'])
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    
    return nearest_station, min_distance



