import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from datetime import datetime
import json
from actor_face_movie_util import update_actors, load_embeddings, process_video
from emotion_music_movie_util import process_emotion_music_movie
from worlds_subtitle_movie import translate_subtitle
from urllib.parse import unquote, urlparse
from kobert import kobert_eval

app = FastAPI()

class VideoURL(BaseModel):
    url: str
    actors: dict

class VideoURLWithoutActors(BaseModel):
    url: str

class SubtitleRequest(BaseModel):
    url: str

embeddings = load_embeddings()

def get_filename_from_url(url: str) -> str:
    parsed_url = unquote(urlparse(url).path)
    return os.path.splitext(os.path.basename(parsed_url))[0]

@app.post("/actor_face_movie/")
async def actor_face_movie(video_url: VideoURL):
    print("배우 얼굴 인식 요청을 받았습니다.")
    try:
        update_actors(video_url.actors, embeddings)
        print("배우 정보를 성공적으로 업데이트했습니다.")

        final_results = process_video(video_url.url, embeddings)

        # 결과를 results 폴더에 저장
        os.makedirs('results', exist_ok=True)
        original_filename = get_filename_from_url(video_url.url)
        filename = f"{original_filename}_actor_face_results.json"
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
        original_filename = get_filename_from_url(video_url.url)
        filename = f"{original_filename}_emotion_music_results.json"
        with open(os.path.join('results', filename), 'w', encoding='utf-8') as f:
            json.dump({"mood_results": final_results, "emotion_counts": emotion_counts}, f, ensure_ascii=False, indent=4)

        return JSONResponse(content={"mood_results": final_results, "emotion_counts": emotion_counts})

    except Exception as e:
        print(f"예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/worlds_subtitle_movie/")
async def worlds_subtitle_movie(subtitle_request: SubtitleRequest):
    print("자막 번역 요청을 받았습니다.")
    try:
        translations = translate_subtitle(subtitle_request)
        return JSONResponse(content=translations)
    except Exception as e:
        print(f"예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if not os.path.exists("images"):
    os.makedirs("images")

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

if __name__ == "__main__":
    print("서버를 시작합니다...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
