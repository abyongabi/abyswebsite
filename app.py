import requests
import urllib.parse
import random
import os

from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session, render_template
from dotenv import load_dotenv
import os


app = Flask(__name__, static_url_path='/static')

load_dotenv()
app.secret_key = os.getenv("app.secret_key")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


REDIRECT_URL = "http://localhost:5000/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

counter = 1
marks = 0
artists_quiz = None
keycode = ['0526', '0923']
positive_movie_quotes = [
    "Just keep swimming. - Dory, Finding Nemo",
    "You have within you right now, everything you need to deal with whatever the world can throw at you. - The Martian",
    "To see the world, things dangerous to come to, to see behind walls, to draw closer, to find each other and to feel. That is the purpose of life. - The Secret Life of Walter Mitty",
    "Life is not the amount of breaths you take, it’s the moments that take your breath away. - Hitch",
    "Don't let anyone ever make you feel like you don't deserve what you want. - 10 Things I Hate About You",
    "The only way to achieve the impossible is to believe it is possible. - Alice in Wonderland",
    "Life moves pretty fast. If you don’t stop and look around once in a while, you could miss it. - Ferris Bueller's Day Off",
    "The flower that blooms in adversity is the most rare and beautiful of all. - Mulan",
    "Happiness can be found even in the darkest of times if one only remembers to turn on the light. - Harry Potter and the Prisoner of Azkaban",
    "Oh yes, the past can hurt. But the way I see it, you can either run from it or learn from it. - The Lion King"
]

negative_movie_quotes = [
    "The greatest trick the Devil ever pulled was convincing the world he didn't exist. - The Usual Suspects",
    "Life's not a song. Life isn't bliss, life is just this. It's living. - Rent",
    "So it's not gonna be easy. It's going to be really hard; we're gonna have to work at this every day, but I want to do that because I want you. I want all of you, forever, every day. - The Notebook",
    "The things you own end up owning you. - Fight Club",
    "We accept the love we think we deserve. - The Perks of Being a Wallflower",
    "I wish I knew how to quit you. - Brokeback Mountain",
    "All those moments will be lost in time, like tears in rain. - Blade Runner",
    "People die at the fair. - Something Wicked This Way Comes",
    "I've seen things you people wouldn't believe. Attack ships on fire off the shoulder of Orion. - Blade Runner",
    "The horror... the horror. - Apocalypse Now"
]



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-read-recently-played user-top-read user-read-playback-position'

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URL,
        "show_dialog": True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URL,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        print(token_info)
        session['access_token'] = token_info['access_token']
        session['refresh_token'] =  token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        print('c')
        return redirect('/spotify')
    
    
@app.route('/spotify/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/playlists?limit=20", headers=headers)
    playlists = response.json()

    return render_template('playlists.html', playlists=playlists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    
    return redirect('/spotify')

@app.route('/spotify/tracks')
def get_top_tracks():
    return render_template('tracks.html')

@app.route('/spotify/tracks/long')
def get_top_tracks_long():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/top/tracks?time_range=long_term&limit=50", headers=headers)
    tracks = response.json()
    
    return render_template('tracks_disp.html', tracks=tracks, cat_tracks='All Time Favourites')   

@app.route('/spotify/tracks/medium')
def get_top_tracks_medium():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/top/tracks?time_range=medium_term&limit=50", headers=headers)
    tracks = response.json()
    return render_template('tracks_disp.html', tracks=tracks, cat_tracks='Memories From Before')    

@app.route('/spotify/tracks/short')
def get_top_tracks_short():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/top/tracks?time_range=short_term&limit=50", headers=headers)
    tracks = response.json()
    return render_template('tracks_disp.html', tracks=tracks, cat_tracks='Recent Tracks')  
  
@app.route('/spotify/artists')
def get_top_artists():
    return render_template('artists.html')

@app.route('/spotify/artists/long')
def get_top_artists_long():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/top/artists?time_range=long_term&limit=50", headers=headers)
    artists = response.json()
    return render_template('artists_disp.html', artists=artists, cat_artists="All Time Favourite")

@app.route('/spotify/artists/medium')
def get_top_artists_medium():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/top/artists?time_range=medium_term&limit=50", headers=headers)
    artists = response.json()
    return render_template('artists_disp.html', artists=artists, cat_artists="Memories From Before")

@app.route('/spotify/artists/short')
def get_top_artists_short():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/top/artists?time_range=short_term&limit=50", headers=headers)
    artists = response.json()
    return render_template('artists_disp.html', artists=artists, cat_artists="Recent Artists")

def quiz_generator(ls, x, y):
    x = random.randint(x, y)
    y = random.randint(x, y)
    while x == y:
        y = random.randint(x, y)
    if random.randint(0,1) == 1:
        z = x
        x = y 
        y = z
    return x, y, ls['items'][x], ls['items'][y]

@app.route('/spotify/artists/quiz', methods=['GET', 'POST'])
def artist_quiz():
    global counter
    global marks
    global artists_quiz
    artists = artists_quiz
    x, y, artist1, artist2 = quiz_generator(artists, 0, 49)
    if request.method == 'POST':
        user_choice = int(request.form['choice'])
        if user_choice == 1 and x < y:
            marks += 20
        if user_choice == 2 and x>y:
            marks += 20           
        counter += 1
        if counter > 5:
            counter = 1
            cur_mark = marks
            marks = 0
            return render_template('result.html', marks=cur_mark)
        else:
            x, y, artist1, artist2 = quiz_generator(artists, 0, 49)

    return render_template('quiz.html', artist1=artist1, artist2=artist2, counter=counter)


@app.route('/spotify/playback')
def get_playback():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/player/recently-played?limit=50", headers=headers)
    playback = response.json()
    #return jsonify(playback)
    return render_template('playback.html', playback=playback)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/spotify')
def spotify():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    return render_template('spotify.html')

@app.route('/spotify/quiz')
def quiz_menu():
    global artists_quiz
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + "me/top/artists?time_range=short_term&limit=50", headers=headers)
    artists_quiz = response.json()
    return render_template('quiz_menu.html')
    

@app.route('/spotify/overview')
def overview():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + "me/top/tracks?time_range=medium_term&limit=50", headers=headers)
    tracks = response.json()
    response = requests.get(API_BASE_URL + "me/top/artists?time_range=medium_term&limit=50", headers=headers)
    artists = response.json()
    return render_template('overview.html', artists=artists, tracks=tracks)

@app.route('/memoir')
def memoir():
    return render_template('memoir.html')

@app.route('/quote')
def quote():
    key = ['0526', '0923']
    return render_template('quote.html', key = key)

@app.route('/quote/process_form', methods=['POST'])
def process_form():
    if request.form['bfr'] == 'true':
        return redirect('/quote/verify')
    return redirect('/quote/society')

@app.route('/quote/verify')
def quote_verify():
    return render_template('quote_verify.html')

@app.route('/quote/verify/bestfried', methods = ['POST'])
def process_verify_form():
    if request.form['code'] in keycode:
        return redirect('/quote/bestfriend')
    return render_template('quote_fail.html')

@app.route('/quote/bestfriend')
def quote_bestfriend():
    line = positive_movie_quotes[random.randint(0,9)]
    return render_template('quote_bestfriend.html', line = line)

@app.route('/quote/stranger')
def quote_stranger():
    line = negative_movie_quotes[random.randint(0,9)]
    return render_template('quote_stranger.html', line = line)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)