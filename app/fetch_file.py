import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from requests.exceptions import RequestException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


# def crawl_korean_page(url):
#     try:
#         response = requests.get(url)
#         response.encoding = 'utf-8'  # 명시적으로 인코딩 설정
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         # 메타 설명 추출
#         description = soup.find('meta', attrs={'name': 'description'})
#         meta_description = description['content'] if description else ""
#
#         # 본문 내용 추출 (예: 첫 번째 <p> 태그)
#         body_content = soup.find('p')
#         body_text = body_content.text if body_content else ""
#
#         return {
#             "meta_description": meta_description,
#             "body_text": body_text
#         }
#     except Exception as e:
#         print(f"Error crawling {url}: {str(e)}")
#         return {"meta_description": "", "body_text": ""}
#

def crawl_korean_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 메타 설명 추출
        meta_description = extract_meta_description(soup)

        # 본문 내용 추출
        body_text = extract_body_text(soup)

        return {
            "meta_description": meta_description[:500],
            "body_text": body_text[:1000],
        }
    except RequestException as e:
        logger.error(f"Request failed for {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")

    return {"meta_description": "", "body_text": "", "image_url": ""}


def extract_meta_description(soup):
    meta_tags = [
        soup.find('meta', attrs={'name': 'description'}),
        soup.find('meta', attrs={'property': 'og:description'}),
        soup.find('meta', attrs={'name': 'twitter:description'})
    ]
    for tag in meta_tags:
        if tag and tag.get('content'):
            return tag['content']
    return ""


def extract_body_text(soup):
    # 불필요한 요소 제거
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe', 'noscript']):
        tag.decompose()

    # 본문 추출 시도: 다양한 주요 섹션을 탐색
    content_sections = ['main', 'article', 'section', 'div', 'p']

    text = ""
    for section in content_sections:
        main_content = soup.find(section, class_=re.compile('(content|article|post|entry|main|body)'))
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            break

    if not text:
        # 마지막으로 전체 텍스트에서 불필요한 공백 제거 후 반환
        text = soup.get_text(separator=' ', strip=True)

    # 텍스트 정제: 너무 긴 공백 제거
    text = re.sub(r'\s+', ' ', text)

    return text

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
