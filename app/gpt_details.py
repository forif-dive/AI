import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 주요 관광지 정보 불러오기
def load_attractions():
    file_path = os.path.join(os.path.dirname(__file__), 'data/attractions_with_activities.json')

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)['attractions']


def get_attraction_details(name):
    attractions = load_attractions()
    attraction = next((a for a in attractions if a['name'] == name), None)
    if not attraction:
        return None
    return attraction


# 주요 관광지 설명 생성하기
def generate_detailed_description(attraction):
    prompt = f"""
    제공된 장소에 대한 상세한 설명을 생성해주세요. 다음 정보를 바탕으로 흥미롭고 유익한 내용을 작성해주세요:

    장소 이름: {attraction['name']}
    기본 설명: {attraction['description']}
    위치: 위도 {attraction['latitude']}, 경도 {attraction['longitude']}
    가능한 활동: {', '.join(attraction['activities'])}
    주변 역: {', '.join([f"{station['station']}역 (거리: {station['distance']}m)" for station in attraction['near_stations']])}

    다음 사항을 포함해주세요:
    1. 장소의 역사나 문화적 의미
    2. 추천 방문 시기나 시간
    3. 주변 명소나 연계 가능한 장소
    4. 방문객들을 위한 팁이나 주의사항
    5. 이 장소만의 특별한 매력이나 특징

    응답은 JSON 형식으로 제공해주세요:
    {{
        "detailed_description": "상세 설명",
        "highlights": ["주요 포인트 1", "주요 포인트 2", "주요 포인트 3"],
        "best_for": ["이런 사람에게 추천 1", "이런 사람에게 추천 2"]
    }}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "당신은 여행 전문가이자 로컬 가이드입니다. 방문객들에게 유용하고 흥미로운 정보를 제공해주세요."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(completion.choices[0].message.content)


# 주요 관광지 정보 json 형식으로 반환
def get_gpt_details(name):
    attraction = get_attraction_details(name)
    if not attraction:
        return None

    gpt_details = generate_detailed_description(attraction)

    return {
        "name": attraction['name'],
        "basic_info": {
            "description": attraction['description'],
            "latitude": attraction['latitude'],
            "longitude": attraction['longitude'],
            "image_url": attraction.get('image_url'),
            "activities": attraction['activities'],
            "near_stations": attraction['near_stations']
        },
        "gpt_details": gpt_details
    }


def get_gpt_response_from_search_data(google_search_results, map_results):
    prompt = f"""
구글 검색 결과와 지도 정보를 받았습니다. 다음과 같은 내용이 들어가도록 정리해주세요:
1. 역 이름
2. 관광지 이름
3. 위도
4. 경도
5. 주요 관광지 설명


다음은 검색 결과와 지도 데이터입니다:

구글 검색 결과:
{google_search_results}

지도 결과:
{map_results}

    {{
        "station_name": str,
        "attraction_name": str,
        "latitude": float,
        "longitude": float,
        "description": str
    }}
    한 역마다 이런 형식이면 되고, 응답은 한글로 되어있어야 합니다. 위 형태처럼 Json으로 반환해야합니다.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "당신은 여행 전문가이자 로컬 가이드입니다. 방문객들에게 유용하고 흥미로운 정보를 제공해주세요."},
            {"role": "user", "content": prompt}
        ]
    )
    response_content = completion.choices[0].message.content
    try:
        parsed_json = json.loads(response_content)
        pretty_response = json.dumps(parsed_json, indent=4, ensure_ascii=False)
    except json.JSONDecodeError:
        # JSON이 아닌 경우 원본 텍스트 그대로 반환
        pretty_response = response_content

    return pretty_response

