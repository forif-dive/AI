import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import find_path, serper
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_station_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def get_station_info(station_name, stations):
    for station in stations:
        if station['name'] == station_name:
            return station
    return None


def get_station_info_json(station_name, preference, attractions):
    attractions_info = json.dumps(attractions, ensure_ascii=False)
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "당신은 철도역과 주변 명소에 대한 정보를 제공하는 도우미입니다. 사용자의 선호도를 고려하여 적절한 장소를 추천해주세요."},
            {"role": "user", "content": f"""
{station_name}역 주변의 명소들 중에서 다음 선호도를 고려하여 최소 1곳, 최대 3곳을 추천해주세요: {preference}. 
추천 장소는 JSON 형식으로 출력해주세요. 각 장소에는 이름, 위도, 경도, 그리고 짧은 한 줄 평이 포함되어야 합니다. 

다음은 {station_name}역 주변 명소들의 정보입니다: {attractions_info}

출력 형식 예시:
{{
    "recommendations": [
        {{
            "name": "올림픽동산",
            "latitude": 35.1648505,
            "longitude": 129.1333409,
            "description": "다양한 레크리에이션 활동과 조깅, 산책에 최적화된 공원입니다."
        }},
        {{
            "name": "벡스코",
            "latitude": 35.1689766,
            "longitude": 129.1360411,
            "description": "다양한 박람회와 문화 행사가 열리는 부산의 대표 컨벤션 센터로 활동적인 체험이 가능합니다."
        }}
    ]
}}

이 형식을 참고하여 주어진 정보를 바탕으로 추천 장소를 JSON 형식으로 제공해주세요.
            """}
        ],
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content


def process_recommendations(data, user_lat, user_lon):
    if isinstance(data, str):
        data = json.loads(data)
    
    for recommendation in data.get('recommendations', []):
        distance = find_path.calculate_distance(user_lat, user_lon, recommendation.get('latitude', 0), recommendation.get('longitude', 0))
        recommendation['image'] = serper.find_image(recommendation.get('name', ''))
        recommendation['distance'] = distance
        recommendation['time'] = distance // 115
        recommendation.pop('latitude', None)
        recommendation.pop('longitude', None)
    return data


def find_activity(user_latitude, user_longitude, preferences):
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'data/station_activity.json')

        station_data = load_station_data(file_path)
        stations = station_data['stations']

        nearest_station, distance = find_path.find_nearest_station(user_latitude, user_longitude)
        station_name = nearest_station['name']
        station_info = get_station_info(station_name, stations)
        
        if not station_info:
            return json.dumps({"error": "Station information not found"}, ensure_ascii=False)

        station_info_json = get_station_info_json(station_name, preferences, station_info)
        processed_data = process_recommendations(station_info_json, user_latitude, user_longitude)
        
        return json.dumps(processed_data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# 테스트 실행
# if __name__ == "__main__":
#     result = find_activity(35.1640413, 129.0604598, ['쇼핑', '먹거리', '놀이공원'])
#     print(result)