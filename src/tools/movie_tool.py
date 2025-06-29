"""
Movie recommendation tool using TMDB API.
"""
import requests
import random
from agents import function_tool
from config.settings import settings

@function_tool
def get_movie_recommendation() -> str:
    """
    Get a random movie recommendation from TMDB.
    
    Returns:
        Formatted movie recommendation string
    """
    try:
        # TMDB API - Get popular movies
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'page': random.randint(1, 5)  # Get from first 5 pages for variety
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            return "Sorry, I couldn't find any movie recommendations right now. Maybe try again later?"
        
        # Get a random movie from the results
        movies = data['results']
        movie = random.choice(movies)
        
        # Get additional movie details including external IDs
        movie_id = movie['id']
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        details_params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'append_to_response': 'external_ids,videos'  # Get IMDb ID and trailers
        }
        
        details_response = requests.get(details_url, params=details_params)
        if details_response.status_code == 200:
            details = details_response.json()
        else:
            details = movie
        
        # Extract movie information
        title = movie.get('title', 'Unknown Movie')
        release_date = movie.get('release_date', '')
        year = release_date.split('-')[0] if release_date else 'Unknown'
        rating = movie.get('vote_average', 0)
        overview = movie.get('overview', 'No description available.')
        poster_path = movie.get('poster_path')
        
        # Get genres
        genres = details.get('genres', [])
        genre_names = [g['name'] for g in genres[:3]]  # Limit to 3 genres
        genre_text = ', '.join(genre_names) if genre_names else 'Unknown'
        
        # Get runtime if available
        runtime = details.get('runtime')
        runtime_text = f" • {runtime} min" if runtime else ""
        
        # Choose emoji based on genre
        emoji = '🎬'  # default
        if any('horror' in g.lower() for g in genre_names):
            emoji = '👻'
        elif any(g.lower() in ['comedy'] for g in genre_names):
            emoji = '😂'
        elif any(g.lower() in ['romance'] for g in genre_names):
            emoji = '💕'
        elif any(g.lower() in ['action', 'adventure'] for g in genre_names):
            emoji = '💥'
        elif any(g.lower() in ['animation'] for g in genre_names):
            emoji = '🎨'
        elif any(g.lower() in ['documentary'] for g in genre_names):
            emoji = '📚'
        
        # Get external links
        external_ids = details.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id')
        
        # Get poster URL if available
        poster_url = None
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        
        # Get trailer URL if available
        trailer_url = None
        videos = details.get('videos', {}).get('results', [])
        for video in videos:
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                trailer_url = f"https://www.youtube.com/watch?v={video.get('key')}"
                break
        
        # Truncate overview if too long
        if len(overview) > 200:
            overview = overview[:197] + "..."
        
        # Build the recommendation with rich content
        recommendation_parts = [f"{emoji} **{title}** ({year})"]
        recommendation_parts.append(f"⭐ {rating}/10")
        recommendation_parts.append(f"🎭 {genre_text}{runtime_text}")
        recommendation_parts.append("")
        recommendation_parts.append(overview)
        
        # Add rich media links
        links = []
        if imdb_id:
            links.append(f"🎬 [IMDb](https://www.imdb.com/title/{imdb_id}/)")
        if trailer_url:
            links.append(f"🎥 [Watch Trailer]({trailer_url})")
        
        if links:
            recommendation_parts.append("")
            recommendation_parts.append(" • ".join(links))
        
        # Add poster if available
        if poster_url:
            recommendation_parts.append("")
            recommendation_parts.append(f"🖼️ [View Poster]({poster_url})")
        
        recommendation_parts.append("")
        recommendation_parts.append("Perfect for a cozy movie night together!")
        
        return "\n".join(recommendation_parts)
        
    except requests.RequestException as e:
        return f"Sorry, I had trouble connecting to get movie recommendations. Error: {str(e)}"
    except Exception as e:
        return f"Oops! Something went wrong while finding movies: {str(e)}" 