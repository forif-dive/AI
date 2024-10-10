import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from find_path import calculate_distance

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 관광지 정보 가져오기
def get_attraction_info(preferences, attractions, user_lat, user_lon):
    relevant_attractions = []
    for attr in attractions:
        if any(pref in attr['activities'] for pref in preferences):
            distance = calculate_distance(user_lat, user_lon, attr['latitude'], attr['longitude'])
            relevant_attractions.append({
                "name": attr['name'],
                "distance": distance,
                "activities": attr['activities'],
                "description": attr['description'][:100] + "..."  # 설명 요약
            })
    
    # 거리순으로 정렬
    relevant_attractions.sort(key=lambda x: x['distance'])
    return json.dumps(relevant_attractions[:5], ensure_ascii=False)  # 상위 5개로 증가


# GPT 모델에 프롬프트 보내기
def chat_with_gpt(previous_chat, preferences, latitude, longitude, attractions):
    attraction_info = get_attraction_info(preferences, attractions, latitude, longitude)
    
    context = f"""
    사용자 위치: 위도 {latitude}, 경도 {longitude}
    선호 활동들: {', '.join(preferences)}
    관련 명소 정보 (거리순): {attraction_info}
    기존 대화 : {previous_chat}
    """
    
    messages = [
        {"role": "system", "content": "당신은 부산의 여행 및 활동 전문가입니다. 사용자의 위치, 다양한 선호도, 그리고 주변 명소 정보를 바탕으로 맞춤형 조언을 제공해주세요. 거리 정보를 활용하여 접근성을 고려하고, 여러 선호 활동을 균형있게 반영한 추천을 해주세요."},
        {"role": "user", "content": context}
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=messages
    )
    
    return completion.choices[0].message.content


# 메인 함수
def process_chat(previous_chat, preferences, latitude, longitude, attractions):
    response = chat_with_gpt(previous_chat, preferences, latitude, longitude, attractions)
    return response
