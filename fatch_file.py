import os
import requests
from serper import Serper
from googleapiclient.discovery import build
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 가져오기
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
CUSTOM_SEARCH_ENGINE_ID = os.getenv('CUSTOM_SEARCH_ENGINE_ID')
MAP_API_KEY = os.getenv('MAP_API_KEY')


def fetch_serper_data(query):
    serper = Serper(SERPER_API_KEY)
    results = serper.get_search_results(query)
    return results


def fetch_public_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def fetch_google_custom_search(query):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=CUSTOM_SEARCH_ENGINE_ID).execute()
    return res


def fetch_map_data(location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={location}&key={MAP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def main():
    # 예시 쿼리
    query = "부산 맛집"
    location = "부산"
    public_api_url = "http://apis.data.go.kr/B551011/KorService/areaCode?serviceKey=serviceKey&numOfRows=10&pageNo=1&MobileOS=ETC&MobileApp=TestApp&_type=json"

    # Serper API 데이터 가져오기
    serper_data = fetch_serper_data(query)
    print("Serper Data:", serper_data)

    # 공공기관 데이터 가져오기
    public_data = fetch_public_data(public_api_url)
    print("Public Data:", public_data)

    # Google Custom Search 데이터 가져오기
    google_data = fetch_google_custom_search(query)
    print("Google Search Data:", google_data)

    # 지도 API 데이터 가져오기
    map_data = fetch_map_data(location)
    print("Map Data:", map_data)

    # 데이터 저장 또는 처리 로직 추가


if __name__ == "__main__":
    main()
