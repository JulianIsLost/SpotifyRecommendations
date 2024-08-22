import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up the Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="your_client_id_here",
    client_secret="your_client_secret_here",
    redirect_uri="http://localhost:8080/callback",
    scope="user-library-read user-top-read user-read-recently-played user-modify-playback-state user-read-playback-state",
    cache_path="[optional path]/.spotify_cache"
))

# Function to fetch top tracks
def get_top_tracks(sp, time_range='medium_term', limit=10):
    return sp.current_user_top_tracks(time_range=time_range, limit=limit)['items']

# Function to get recommendations
def get_recommendations(sp, seed_tracks, limit=10):
    return sp.recommendations(seed_tracks=seed_tracks, limit=limit)['tracks']

# Function to analyze audio features and determine a good timestamp
def get_best_timestamp(track_id):
    # Fetch audio features for the track
    features = sp.audio_features(track_id)[0]
    if not features:
        return 0
    
    # Audio feature extraction
    tempo = features['tempo']  # BPM
    energy = features['energy']  # Intensity, 0.0 to 1.0
    duration_ms = features['duration_ms']  # Duration of the track in milliseconds

    # Simple heuristic: start playback at a segment with high energy
    # Note: Actual timestamp determination logic can be more complex
    # Here we're just using a simplified approach
    return int(duration_ms * (1 - energy))  # Example: Start at a point proportional to energy

# Function to start playback at the given timestamp
def start_playback_at_timestamp(sp, device_id, track_uri, timestamp_ms):
    sp.start_playback(device_id=device_id, uris=[track_uri], position_ms=timestamp_ms)

# Function to display song recommendations
def display_song_recommendation(song):
    print(f"🎵 {song['name']} by {', '.join(artist['name'] for artist in song['artists'])}")
    print(f"Album: {song['album']['name']}")
    print(f"Preview: {song['preview_url']}")
    print("-" * 40)

def tiktok_like_display(sp, recommendations, device_id):
    for song in recommendations:
        display_song_recommendation(song)
        
        # Determine the best timestamp based on audio features
        best_timestamp = get_best_timestamp(song['id'])
        print(f"Starting playback at: {best_timestamp / 1000:.2f} seconds")
        
        # Start playback on Spotify at the best timestamp
        start_playback_at_timestamp(sp, device_id, song['uri'], best_timestamp)
        
        # Allow user to quit the program
        user_input = input("Press Enter to see the next song or 'q' to quit: ")
        if user_input.lower() == 'q':
            print("Exiting the program.")
            break

# Function to select a Spotify device
def select_device(sp):
    devices = sp.devices()
    if devices['devices']:
        print("Available Spotify Devices:")
        for i, device in enumerate(devices['devices']):
            print(f"{i+1}: {device['name']} - {device['type']}")
        
        selected_index = int(input("Select a device by number: ")) - 1
        return devices['devices'][selected_index]['id']
    else:
        print("No active Spotify devices found.")
        return None

# Fetch top tracks
top_tracks = get_top_tracks(sp)

# Generate recommendations based on top tracks
if top_tracks:  # Ensure there are top tracks to seed the recommendations
    seed_tracks = [track['id'] for track in top_tracks[:5]]
    recommendations = get_recommendations(sp, seed_tracks)
    
    # Select a Spotify device
    device_id = select_device(sp)
    
    if device_id:
        # Display recommendations
        if recommendations:
            tiktok_like_display(sp, recommendations, device_id)
        else:
            print("No recommendations found.")
    else:
        print("Playback cannot proceed without a selected device.")
else:
    print("No top tracks found.")
