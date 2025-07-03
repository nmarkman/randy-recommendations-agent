"""
Movie recommendation tool using TMDB API with robust error handling.
"""
import requests
import random
import logging
from datetime import datetime
from agents import function_tool
from config.settings import settings
from src.utils.retry import tmdb_retry, circuit_breaker, RetryError, APIHealthError
from src.utils.fallbacks import get_fallback_movie

logger = logging.getLogger('Randy.MovieTool')

@circuit_breaker(failure_threshold=3, recovery_timeout=300)  # 5 minute recovery
@tmdb_retry
def _fetch_movie_data():
    """
    Fetch movie data from TMDB API with retry logic.
    
    Returns:
        API response data
        
    Raises:
        Various exceptions for retry handling
    """
    # TMDB API - Get popular movies
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': random.randint(1, 5)  # Get from first 5 pages for variety
    }
    
    logger.info("Fetching popular movie data from TMDB")
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('results'):
        raise ValueError("No movies found in TMDB popular list")
    
    return data

@tmdb_retry  
def _fetch_movie_details(movie_id: int):
    """
    Fetch detailed movie information with retry logic.
    
    Args:
        movie_id: TMDB movie ID
        
    Returns:
        Detailed movie information or None if failed
    """
    try:
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        details_params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'append_to_response': 'external_ids,videos'  # Get IMDb ID and trailers
        }
        
        logger.debug(f"Fetching details for movie_id: {movie_id}")
        details_response = requests.get(details_url, params=details_params, timeout=10)
        
        if details_response.status_code == 200:
            return details_response.json()
        else:
            logger.warning(f"Failed to fetch details for movie_id {movie_id}: HTTP {details_response.status_code}")
            return None
    
    except Exception as e:
        logger.warning(f"Error fetching movie details for {movie_id}: {e}")
        return None

def _determine_season_and_time():
    """Determine current season and time period for context."""
    now = datetime.now()
    month = now.month
    hour = now.hour
    
    # Determine season
    if 3 <= month <= 5:
        season = "spring"
    elif 6 <= month <= 8:
        season = "summer"
    elif 9 <= month <= 11:
        season = "fall"
    else:
        season = "winter"
    
    # Determine time period
    if 6 <= hour < 11:
        time_period = "morning"
    elif 11 <= hour < 17:
        time_period = "afternoon"
    elif 17 <= hour < 23:
        time_period = "evening"
    else:
        time_period = "late night"
    
    return season, time_period

@function_tool
def get_movie_recommendation() -> str:
    """
    Get a random movie recommendation with robust error handling and fallbacks.
    
    Returns:
        Formatted movie recommendation string
    """
    season, time_period = _determine_season_and_time()
    
    try:
        logger.info(f"Starting movie recommendation at {time_period} in {season}")
        
        # Try to fetch movie data with retries
        data = _fetch_movie_data()
        
        # Get a random movie from the results
        movies = data['results']
        movie = random.choice(movies)
        
        # Get additional movie details including external IDs (with fallback to basic data)
        movie_id = movie['id']
        details = None
        
        if movie_id:
            details = _fetch_movie_details(movie_id)
        
        # Use details if available, otherwise fall back to search results
        info = details if details else movie
        
        # Extract movie information
        title = movie.get('title', 'Unknown Movie')
        release_date = movie.get('release_date', '')
        year = release_date.split('-')[0] if release_date else 'Unknown'
        rating = movie.get('vote_average', 0)
        overview = movie.get('overview', 'No description available.')
        poster_path = movie.get('poster_path')
        
        # Get genres
        genres = info.get('genres', [])
        genre_names = [g['name'] for g in genres[:3]]  # Limit to 3 genres
        genre_text = ', '.join(genre_names) if genre_names else 'Unknown'
        
        # Get runtime if available
        runtime = info.get('runtime')
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
        external_ids = info.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id')
        
        # Get poster URL if available
        poster_url = None
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        
        # Get trailer URL if available
        trailer_url = None
        videos = info.get('videos', {}).get('results', [])
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
        
        result = "\n".join(recommendation_parts)
        logger.info(f"Successfully generated movie recommendation: {title}")
        return result
        
    except (RetryError, APIHealthError) as e:
        # All retries exhausted or circuit breaker open - use fallback
        logger.error(f"API completely unavailable for movie recommendations: {e}")
        logger.info("Using fallback movie recommendation")
        return get_fallback_movie(season, time_period)
    
    except Exception as e:
        # Unexpected error - log and use fallback
        logger.error(f"Unexpected error in movie recommendation: {e}")
        logger.info("Using fallback movie recommendation due to unexpected error")
        return get_fallback_movie(season, time_period) 