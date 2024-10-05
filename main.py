from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import near_activity_recommend
import json, find_path
import greetings_recommendation
import gpt_details, gpt_chat
app = FastAPI()
with open('attractions_with_activities.json', 'r', encoding='utf-8') as f:
    attractions_data = json.load(f)
    
class UserInput(BaseModel):
    latitude: float
    longitude: float
    preferences: list[str]

class LocationInput(BaseModel):
    latitude: float
    longitude: float

@app.post("/find_nearest_station")
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

@app.post("/find_near_activity")
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

with open('attractions_with_activities.json', 'r', encoding='utf-8') as f:
    attractions_data = json.load(f)

@app.post("/get_attractions_by_station")
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

@app.get("/categories")
async def get_categories():
    with open("activity_category.json", "r", encoding="utf-8") as file:
        categories = json.load(file)
    return categories

class UserGreetingInput(BaseModel):
    latitude: float
    longitude: float
    preferences: list[str]
    
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
    
@app.post("/details")
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
        with open('attractions_with_activities.json', 'r', encoding='utf-8') as f:
            attractions_data = json.load(f)['attractions']
        
        response = gpt_chat.process_chat(
            chat_input.previous_chat,
            chat_input.preferences,
            chat_input.latitude,
            chat_input.longitude,
            attractions_data
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)