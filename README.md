# 동해선 관광 추천 API

이 프로젝트는 부산의 관광 명소와 활동을 추천하는 FastAPI 기반의 API 서비스입니다. 사용자의 위치와 선호도를 바탕으로 맞춤형 관광 정보를 제공합니다.

## 목차

1. [기능](#기능)
2. [설치 방법](#설치-방법)
3. [환경 설정](#환경-설정)
4. [실행 방법](#실행-방법)
5. [API 엔드포인트](#api-엔드포인트)
6. [데이터 구조](#데이터-구조)
7. [의존성](#의존성)
8. [라이선스](#라이선스)

## 기능

- 사용자 위치 기반 가까운 역 찾기
- 사용자 선호도에 따른 주변 관광 활동 추천
- 역 주변 관광 명소 정보 제공
- 관광 활동 카테고리 목록 제공
- 맞춤형 인사말과 추천 생성
- 특정 관광 명소에 대한 상세 정보 제공

## 설치 방법

1. 이 저장소를 클론합니다:
   ```
   git clone https://github.com/your-username/busan-tourism-api.git
   cd busan-tourism-api
   ```

2. 가상 환경을 생성하고 활성화합니다:
   ```
   python -m venv venv
   source venv/bin/activate  # Windows의 경우: venv\Scripts\activate
   ```

3. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 환경 설정

1. `.env` 파일을 프로젝트 루트 디렉토리에 생성합니다.
2. 다음 환경 변수를 설정합니다:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## 실행 방법

서버를 실행하려면 다음 명령어를 사용합니다:

```
uvicorn main:app --reload
```

서버가 실행되면 `http://localhost:8000`에서 API에 액세스할 수 있습니다.

## API 엔드포인트

- POST `/find_nearest_station`: 가장 가까운 역 찾기
- POST `/find_near_activity`: 주변 관광 활동 추천
- POST `/get_attractions_by_station`: 특정 역 주변의 관광 명소 조회
- GET `/categories`: 관광 활동 카테고리 목록 조회
- POST `/greetings`: 맞춤형 인사말과 추천 생성
- POST `/details`: 특정 관광 명소의 상세 정보 조회

각 엔드포인트의 자세한 사용법은 FastAPI의 자동 생성 문서 (`/docs`)를 참조하세요.

## 데이터 구조

프로젝트는 다음과 같은 주요 데이터 파일을 사용합니다:

- `attractions_with_activities.json`: 관광 명소와 활동 정보
- `activity_category.json`: 활동 카테고리 정보
- `stations.json`: 역 정보

## 의존성

주요 의존성:

- FastAPI
- Uvicorn
- OpenAI
- Pydantic
- python-dotenv

전체 의존성 목록은 `requirements.txt` 파일을 참조하세요.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.
