from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import requests
import time
load_dotenv()

app = Flask(__name__)

 #   cache block, caps to make it a constant
GLOBAL_CACHE = {}
CACHE_TTL_SECONDS = 300 #   5mins

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/ping/')
def ping():
    return jsonify(ok = True), 200

@app.route('/echo')
def echo():
    q = request.args.get("q", "")
    return jsonify(q = q), 200

#   checks and sees if the API information is present, returns false if not.
@app.route('/debug/env')
def debug():
    current_device_time = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="milliseconds")
    list_of_req = {
        "api_key": bool(os.getenv("MOVIEGLU_API_KEY")),
        "client": bool(os.getenv("MOVIEGLU_CLIENT")),
        "auth": bool(os.getenv("MOVIEGLU_AUTH")),
        "territory": bool(os.getenv("MOVIEGLU_TERRITORY")),
        "api_base": bool(os.getenv("MOVIEGLU_API_BASE")),
        "api_version": bool(os.getenv("MOVIEGLU_API_VERSION")),
        "device-datetime": current_device_time
    }
    return jsonify(list_of_req), 200

#   ℹ️ headers information retreived from the .env document
def movieglu_headers():
    current_device_time = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="milliseconds")
    return {
        "x-api-key": os.getenv("MOVIEGLU_API_KEY","").strip(),
        "client": os.getenv("MOVIEGLU_CLIENT", "").strip(),
        "Authorization": os.getenv("MOVIEGLU_AUTH","").strip(),
        "territory": os.getenv("MOVIEGLU_TERRITORY", "").strip(),
        "api-version": os.getenv("MOVIEGLU_API_VERSION", "").strip(),
        "device-datetime": current_device_time
    }

#   ℹ️ route where user will be able to query film_id, and output individual film's name and stats
@app.route('/filmDetails', methods = ["GET"]) #type: ignore
def film_details(): 
    film_id = request.args.get("film_id")
    
     #   ❌ when film_id not given 
    if film_id == None:
        return {
            "error": "film_id is required"
        }, 400  
    
    #   cache block lookup
    time_now = time.time()
    cached = GLOBAL_CACHE.get(film_id)
    if cached and cached.get("expires_at", 0) > time_now:
        return jsonify({**cached["data"], "cached": True}), 200

    get_base = os.getenv("MOVIEGLU_API_BASE")
    build_url = str(get_base) + "/filmDetails"
    headers = movieglu_headers()
    params = {"film_id": film_id}
    response = requests.get(build_url, headers=headers, params=params)

    #   ❌ no content found
    if response.status_code == 204:
        return {
            "error": "no results",
            "film id": film_id
        }, response.status_code

    #   ❌ unsuccesful output  
    if response.status_code != 200:
        retry_after = response.headers.get("Retry-After")
        return {
            "response" :response.status_code,
            "MG Message": response.headers.get("MG-message"),
            "text preview": response.text[:200],
            "Retry After": retry_after
        }, response.status_code
    
    #   ✅ succesful output 
    if response.status_code == 200:
        # film's information -- IMBD style
        data = response.json()
        film_title = data.get("film_name")
        film_release_dates = data.get("release_dates", [])
        film_release_date = film_release_dates[0].get("release_date") if film_release_dates else None
        film_genres = data.get("genres", [])
        film_genre_names = [gen.get("genre_name") for gen in film_genres]
        film_duration = data.get("duration_mins")
        #   film_director = data.get("director_name", [])
        #   film_director_names = film_director[1].get("director_name")


        film_info = {
            "Title": film_title,
            "Release Date": film_release_date,
            "Genre": film_genre_names,
            "Duration": film_duration,
            #   "Director(s)": film_director
        }  

        #   cache store goes here ⬇️
        GLOBAL_CACHE[film_id] = {
            "expires_at": time_now + CACHE_TTL_SECONDS,
            "data": film_info
        }
    # return jsonify(film_info), 200    --- former return result before flag below
        return {**film_info, "cached":False}

#   ℹ️ allows you to to see the first five films that match the query ID typed in route. film_id + film_name
@app.route('/filmLiveSearch/', methods =["GET"])  # type: ignore
def film_live_search():
    query = request.args.get("query", "")
    if query == "":
        return {
            "error": "query required"
        }, 400
    
    get_base = os.getenv("MOVIEGLU_API_BASE") 
    build_url = str(get_base) + "/filmLiveSearch/"
    params = {"query": query}
    headers = movieglu_headers()
    response = requests.get(build_url, headers = headers, params=params)

    #   ❌ unsuccesful output 
    if response.status_code != 200:
        return {
            "response" :response.status_code, 
            "content type": response.headers.get("Content-Type"),
            "text preview": response.text[:200],
            "url": response.url,
            "raw body len": len(response.content),
            "MG Message": response.headers.get("MG-message"),
            "MG-error": response.headers.get("MG-error"),
            "has auth": bool(headers.get("Authorization"))
        }
    
    #   ✅ succesful output 
    if response.status_code == 200:
        film_data = response.json()
        films = film_data["films"]
        first_film = films[0] if films else{}

        #   variable that jsonify's and returns the first film only
        first_film_output =  jsonify(
            film_id = first_film.get("film_id"),
            film_name = first_film.get("film_name")
        ), 200    

        #   5️⃣-ℹ️ variales and jsonify that returns the first-five films
        first_five_films = []   # empty list of the first five films
        for film in films[:5]:
            film_id = film.get("film_id")
            film_name = film.get("film_name")

            if (film_name is None) or (film_id is None):
                continue

            first_five_films.append({
                "film_id": film_id,
                "film_name": film_name
            })
        return jsonify(first_five_films),200

if __name__ == '__main__':
    app.run(debug=True, port=5001)