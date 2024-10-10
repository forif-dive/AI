import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
X_API_KEY = os.getenv('X_API_KEY')


def find_image(spot):
    url = "https://google.serper.dev/images"

    payload = json.dumps({
        "q": f"{spot}",
        "location": "Busan, Busan, South Korea",
        "gl": "kr"
    })
    headers = {
        'X-API-KEY': X_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # JSON 문자열을 파이썬 딕셔너리로 파싱
    data = json.loads(response.text)
    # 첫 번째 이미지의 URL 추출
    first_image_url = data['images'][0]['imageUrl']
    return first_image_url
