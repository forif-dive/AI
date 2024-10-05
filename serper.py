import requests
import json

def find_image(spot):
    url = "https://google.serper.dev/images"

    payload = json.dumps({
    "q": f"{spot}",
    "location": "Busan, Busan, South Korea",
    "gl": "kr"
    })
    headers = {
    'X-API-KEY': '9a82b78c00524acd2b4f166eb77c72d12525a604',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # JSON 문자열을 파이썬 딕셔너리로 파싱
    data = json.loads(response.text)
    # 첫 번째 이미지의 URL 추출
    first_image_url = data['images'][0]['imageUrl']
    return first_image_url

