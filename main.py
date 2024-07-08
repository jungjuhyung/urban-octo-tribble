import os
import uvicorn
<<<<<<< HEAD
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from actor_face_movie_util import update_actors, load_embeddings, process_video
from emotion_music_movie_util import process_emotion_music_movie
from datetime import datetime
import json
from kobert import kobert_eval
app = FastAPI()

class VideoURL(BaseModel):
    url: str
    actors: dict

class VideoURLWithoutActors(BaseModel):
    url: str

embeddings = load_embeddings()

def get_timestamped_filename(base_name: str, extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

@app.get("/")
async def root():
    return {"message": "안녕하세요, 세계"}

@app.post("/actor_face_movie/")
async def actor_face_movie(video_url: VideoURL):
    print("배우 얼굴 인식 요청을 받았습니다.")
    try:
        update_actors(video_url.actors, embeddings)
        print("배우 정보를 성공적으로 업데이트했습니다.")

        final_results = process_video(video_url.url, embeddings)

        # 결과를 results 폴더에 저장
        os.makedirs('results', exist_ok=True)
        filename = get_timestamped_filename('actor_face_results', 'json')
        with open(os.path.join('results', filename), 'w', encoding='utf-8') as f:
            json.dump({"actor_timestamps": final_results}, f, ensure_ascii=False, indent=4)

        return JSONResponse(content={"actor_timestamps": final_results})

    except Exception as e:
        print(f"예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emotion_music_movie/")
async def emotion_music_movie(video_url: VideoURLWithoutActors):
    print("음악 감정 분석 요청을 받았습니다.")
    try:
        final_results, emotion_counts = process_emotion_music_movie(video_url.url)

        # 결과를 results 폴더에 저장
        os.makedirs('results', exist_ok=True)
        filename = get_timestamped_filename('emotion_music_results', 'json')
        with open(os.path.join('results', filename), 'w', encoding='utf-8') as f:
            json.dump({"mood_results": final_results, "emotion_counts": emotion_counts}, f, ensure_ascii=False, indent=4)

        return JSONResponse(content={"mood_results": final_results, "emotion_counts": emotion_counts})

    except Exception as e:
        print(f"Exception: {str(e)}")  # 예외 발생 시 로그 출력
        raise HTTPException(status_code=500, detail=str(e))  # 예외 응답 반환
    
@app.post("/kobert/")
async def kobert(subtitle_url: str):
    try:
        print("Request received for music emotion analysis.")  # 요청 수신 로그 출력 
        print("KoBert 작동중...")  # 요청 수신 로그 출력
        subtitle_url = "https://storage.googleapis.com/pretzel-movie/"+subtitle_url
        response = requests.get(subtitle_url, stream=True)
        response.encoding = 'utf-8'
        subtitle_text = response.text
        subtitle_text = subtitle_text.replace('\r\n', '\n').replace('\r', '\n')
        kobert_eval(subtitle_text)
        return 1

    except Exception as e:
        print(f"Exception: {str(e)}")  # 예외 발생 시 로그 출력
        raise HTTPException(status_code=500, detail=str(e))  # 예외 응답 반환
=======
from fastapi import FastAPI
from actor_face_movie_util import router as actor_face_movie_router
from emotion_music_movie_util import router as emotion_music_movie_router
from worlds_subtitle_movie import router as worlds_subtitle_movie_router

app = FastAPI()

# Include routers from other modules
app.include_router(actor_face_movie_router, prefix="/actor_face_movie")
app.include_router(emotion_music_movie_router, prefix="/emotion_music_movie")
app.include_router(worlds_subtitle_movie_router, prefix="/worlds_subtitle_movie")
>>>>>>> origin/lee

if __name__ == "__main__":
    print("서버를 시작합니다...")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\ICT05_04\\Desktop\\finalproject\\movie\\translate-movie-427703-adec2ac5235a.json"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
