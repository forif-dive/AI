import os
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 가져오기
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
CUSTOM_SEARCH_ENGINE_ID = os.getenv('CUSTOM_SEARCH_ENGINE_ID')
MAP_API_KEY = os.getenv('MAP_API_KEY')


def fetch_google_custom_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    try:
        res = requests.get(url, params={
            "key": GOOGLE_API_KEY,
            "cx": CUSTOM_SEARCH_ENGINE_ID,
            "q": query,
        })
        res.raise_for_status()  # 요청 실패 시 예외 발생
        content = res.json()

        if 'items' in content:
            # 제목과 링크만 추출
            results = []
            for item in content['items']:
                results.append({
                    "title": item['title'],   # 관광지 이름
                    "link": item['link']      # 장소 URL
                })
            return results
        else:
            return {"message": "No results found"}
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return {"error": str(e)}


def fetch_map_data(location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={location}&key={MAP_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청 실패 시 예외 발생
        data = response.json()

        if data['status'] == 'OK':
            # 이름, 주소, 위도, 경도 추출
            results = []
            for result in data['results']:
                results.append({
                    "name": result['name'],  # 관광지 이름
                    "address": result['formatted_address'],  # 주소
                    "latitude": result['geometry']['location']['lat'],  # 위도
                    "longitude": result['geometry']['location']['lng']  # 경도
                })
            return results
        else:
            return {"message": f"Error: {data['status']}"}
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return {"error": str(e)}

# 테스트 실행
# def main():
#     # 예시 쿼리
#     query = "부산 동해선 일광역 주요 관광지"
#     location = "부산 동해선 일광역"
#     # Google Custom Search 데이터 가져오기
#     google_data = fetch_google_custom_search(query)
#     print("\nGoogle Search Data (Name & Link):")
#     if google_data:
#         for item in google_data:
#             print(f"Name: {item['title']}")
#             print(f"Link: {item['link']}\n")
#
#     # 지도 API 데이터 가져오기 (위도, 경도 포함)
#     map_data = fetch_map_data(location)
#     print("\nMap Data (Name, Address, Latitude, Longitude):")
#     if map_data:
#         for result in map_data:
#             print(f"Name: {result['name']}")
#             print(f"Address: {result['address']}")
#             print(f"Latitude: {result['latitude']}")
#             print(f"Longitude: {result['longitude']}\n")


# if __name__ == "__main__":
#     main()
