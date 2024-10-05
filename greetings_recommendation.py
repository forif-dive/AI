import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from find_path import calculate_distance

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_attractions(file_path='attractions_with_activities.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)['attractions']

def get_greeting_and_recommendations(user_latitude, user_longitude, preferences: list[str]):
    attractions = load_attractions()
    
    matching_attractions = [
        attraction for attraction in attractions
        if any(pref in attraction['activities'] for pref in preferences)
    ]
    
    for attraction in matching_attractions:
        attraction['distance'] = calculate_distance(
            user_latitude, user_longitude,
            attraction['latitude'], attraction['longitude']
        )
    
    sorted_attractions = sorted(matching_attractions, key=lambda x: x['distance'])
    top_attractions = sorted_attractions[:3]  # 상위 3개로 제한
    
    context = {
        "user_latitude": user_latitude,
        "user_longitude": user_longitude,
        "preferences": preferences,
        "attractions": [
            {
                "name": attr['name'],
                "distance": attr['distance'],
                "activities": attr['activities']
            } for attr in top_attractions
        ]
    }
    
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "당신은 여행 추천을 제공하는 도우미입니다."},
            {"role": "user", "content": f"""
다음 정보를 바탕으로 친근한 인사말을 만들고, 추천 장소와 관련된 질문을 생성해주세요:
{json.dumps(context, ensure_ascii=False)}

응답은 다음 조건을 만족해야 합니다:
1. 인사말은 한국어로 작성할 것
2. 인사말은 한 문장으로 작성할 것
3. 인사말에서 사용자의 선호도 중 하나 이상을 언급할 것
4. 인사말에서 동해선을 언급할 것
5. 인사말에 계절감을 포함시킬 것 (현재 계절에 맞게)
6. 추천 질문은 각각 10자 내외의 길이로 작성할 것
7. 추천 질문은 추천된 장소나 활동과 관련이 있어야 함

출력 형식:
{{
    "greeting": "인사말을 여기에 작성",
    "recommendations": [
        {{
            "name": "장소 이름",
            "distance": 거리(미터 단위의 정수),
            "image_url": "이미지 URL",
            "description": "장소에 대한 간단한 설명"
        }},
        ...
    ],
    "suggested_questions": [
        "추천 질문 1",
        "추천 질문 2"
    ]
}}

위의 형식에 맞춰 JSON 형태로 응답해주세요.
"""
            }
        ],
        response_format={"type": "json_object"}
    )
    
    response = json.loads(completion.choices[0].message.content)
    
    # API 응답의 recommendations를 실제 데이터로 교체
    response['recommendations'] = [
        {
            "name": attr['name'],
            "distance": attr['distance'],
            "image_url": attr['image_url'],
            "description": attr['description'][:100] + "..."  # 첫 100자만 사용
        } for attr in top_attractions
    ]
    
    return response

# 테스트 용도의 메인 실행 부분
if __name__ == "__main__":
    result = get_greeting_and_recommendations(35.1640413, 129.0604598, ["산책", "사진 촬영"])
    print(json.dumps(result, ensure_ascii=False, indent=2))