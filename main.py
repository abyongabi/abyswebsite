import requests
import urllib.parse

from datetime import datetime, timedelta
from flask import Flask, redirect, request, jsonify, session, render_template

app = Flask(__name__, static_url_path='/static')
app.secret_key = "1231231231231"

CLIENT_ID = "8782189721584222a5fec8051ba70281"
CLIENT_SECRET = "33ba989f44994641a7c6673b752acb5b"
REDIRECT_URL = "http://localhost:5000/callback"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

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

        session['access_token'] = token_info['access_token']
        session['refresh_token'] =  token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        
        return redirect('/menu')
    
    
@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get(API_BASE_URL + "me/playlists", headers=headers)
    playlists = response.json()
    
    return jsonify(playlists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'request_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()
    
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
    
    return redirect('/playlists')

@app.route('/tracks')
def get_top_tracks():
    return render_template('tracks.html')

@app.route('/tracks/long')
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

@app.route('/tracks/medium')
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

@app.route('/tracks/short')
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
  
@app.route('/artists')
def get_top_artists():
    return render_template('artists.html')

@app.route('/artists/long')
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

@app.route('/artists/medium')
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

@app.route('/artists/short')
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



@app.route('/menu')
def menu():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    return render_template('menu.html')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)