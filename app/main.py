from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import near_activity_recommend
import json
import find_path
import greetings_recommendation
import gpt_details
import gpt_chat
import os
import fetch_file
app = FastAPI()
file_path = os.path.join(os.path.dirname(__file__), 'data/attractions_with_activities.json')


class UserInput(BaseModel):
    latitude: float
    longitude: float
    preferences: list[str]


class LocationInput(BaseModel):
    latitude: float
    longitude: float


# 근처 역 가져오기
@app.post("/stations/nearest")
async def find_nearest_station(location: LocationInput):
    try:
        nearest_station, distance = find_path.find_nearest_station(
            location.latitude,
            location.longitude
        )
        return {
            "station_name": nearest_station['name'],
            "distance": distance,
            "latitude": nearest_station['latitude'],
            "longitude": nearest_station['longitude']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StationRequest(BaseModel):
    station_name: str


# 근처 관광지 가져오기
@app.post("/activities/nearby")
async def find_near_activity(user_input: UserInput):
    try:
        result_json = near_activity_recommend.find_activity(
            user_input.latitude,
            user_input.longitude,
            user_input.preferences
        )
        # JSON 문자열을 Python 딕셔너리로 파싱
        result_dict = json.loads(result_json)
        
        # 오류 확인
        if "error" in result_dict:
            raise HTTPException(status_code=400, detail=result_dict["error"])
        
        return result_dict
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON response from recommendation service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

with open(file_path, 'r', encoding='utf-8') as f:
    attractions_data = json.load(f)


# 해당 역의 관광지들 가져오기
@app.post("/stations/attractions")
async def get_attractions_by_station(request: StationRequest):
    station_name = request.station_name
    matching_attractions = []

    for attraction in attractions_data['attractions']:
        for near_station in attraction['near_stations']:
            if near_station['station'] == station_name:
                matching_attractions.append({
                    "name": attraction['name'],
                    "description": attraction['description'],
                    "latitude": attraction['latitude'],
                    "longitude": attraction['longitude'],
                    "distance": near_station['distance'],
                    "image_url": attraction.get('image_url', None)
                })
                break  # 이미 매칭되었으므로 다음 명소로 넘어감

    if not matching_attractions:
        raise HTTPException(status_code=404, detail="No attractions found for the given station")

    return {"attractions": matching_attractions}


# 관광지 카테고리 가져오기
@app.get("/categories")
async def get_categories():
    category_data_path = os.path.join(os.path.dirname(__file__), 'data/activity_category.json')

    with open(category_data_path, "r", encoding="utf-8") as file:
        categories = json.load(file)
    return categories


class UserGreetingInput(BaseModel):
    latitude: float
    longitude: float
    preferences: list[str]


# 사용자의 위치에 따른 추천 관광지 가져오기
@app.post("/greetings")
async def greetings(user_input: UserGreetingInput):
    try:
        result = greetings_recommendation.get_greeting_and_recommendations(
            user_input.latitude,
            user_input.longitude,
            user_input.preferences
        )
        return {
            "greeting": result["greeting"],
            "recommendations": result["recommendations"],
            "suggested_questions": result["suggested_questions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DetailsRequest(BaseModel):
    name: str


# 관광지 세부 정보 가져오기
@app.post("/attractions/details")
async def get_details(request: DetailsRequest):
    details = gpt_details.get_gpt_details(request.name)
    if not details:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return details


class ChatInput(BaseModel):
    previous_chat: list
    preferences: list[str]
    latitude: float
    longitude: float


@app.post("/chat")
async def chat_endpoint(chat_input: ChatInput):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            attractions_chat_data = json.load(f)['attractions']
        
        response = gpt_chat.process_chat(
            chat_input.previous_chat,
            chat_input.preferences,
            chat_input.latitude,
            chat_input.longitude,
            attractions_chat_data
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 요청 바디 모델
class SearchRequest(BaseModel):
    query: str  # 검색할 쿼리 (예: 부산 동해선 일광역 주요 관광지)
    location: str  # 위치 (예: 부산 동해선 일광역)


# POST 요청을 처리하는 엔드포인트
@app.post("/search")
async def search_data(request: SearchRequest):
    try:
        # Google Custom Search API에서 데이터 가져오기
        google_data = fetch_file.fetch_google_custom_search(request.query)
        if 'error' in google_data:
            raise HTTPException(status_code=500, detail=google_data['error'])

        # Google Maps API에서 데이터 가져오기
        map_data = fetch_file.fetch_map_data(request.location)
        if 'error' in map_data:
            raise HTTPException(status_code=500, detail=map_data['error'])

        # 결과 반환
        return {
            "google_search_results": google_data,
            "map_results": map_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
