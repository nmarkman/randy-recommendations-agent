"""
Points of Interest recommendation tool using Google Places API with robust error handling.
"""
import requests
import random
import logging
from datetime import datetime
from agents import function_tool
from config.settings import settings
from src.utils.retry import google_places_retry, circuit_breaker, RetryError, APIHealthError
from src.utils.fallbacks import get_fallback_poi

logger = logging.getLogger('Randy.POITool')

@circuit_breaker(failure_threshold=3, recovery_timeout=300)  # 5 minute recovery
@google_places_retry
def _fetch_poi_data(location: str):
    """
    Fetch POI data from Google Places API with retry logic.
    
    Args:
        location: Location to search for attractions
        
    Returns:
        API response data
        
    Raises:
        Various exceptions for retry handling
    """
    # Google Places API - Text Search for attractions
    attraction_queries = [
        f'tourist attractions in {location}',
        f'parks in {location}',
        f'museums in {location}',
        f'historic sites in {location}',
        f'art galleries in {location}',
        f'outdoor activities in {location}'
    ]
    
    # Try a random query type
    query = random.choice(attraction_queries)
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': query,
        'key': settings.GOOGLE_PLACES_API_KEY,
        'type': 'tourist_attraction',
        'language': 'en'
    }
    
    logger.info(f"Fetching POI data for location: {location} with query: {query}")
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('results'):
        raise ValueError(f"No interesting places found in {location}")
    
    return data

@google_places_retry  
def _fetch_poi_details(place_id: str):
    """
    Fetch detailed POI information with retry logic.
    
    Args:
        place_id: Google Places place ID
        
    Returns:
        Detailed place information or None if failed
    """
    try:
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            'place_id': place_id,
            'key': settings.GOOGLE_PLACES_API_KEY,
            'fields': 'name,formatted_address,rating,types,website,international_phone_number,photos,opening_hours,url'
        }
        
        logger.debug(f"Fetching details for place_id: {place_id}")
        details_response = requests.get(details_url, params=details_params, timeout=10)
        
        if details_response.status_code == 200:
            details_data = details_response.json()
            return details_data.get('result')
        else:
            logger.warning(f"Failed to fetch details for place_id {place_id}: HTTP {details_response.status_code}")
            return None
    
    except Exception as e:
        logger.warning(f"Error fetching POI details for {place_id}: {e}")
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
def get_poi_recommendation(location: str = None) -> str:
    """
    Get a random points of interest recommendation with robust error handling and fallbacks.
    
    Args:
        location: Location to search for attractions (defaults to configured region)
    
    Returns:
        Formatted POI recommendation string
    """
    if not location:
        location = settings.REGION
    
    season, time_period = _determine_season_and_time()
    
    try:
        logger.info(f"Starting POI recommendation for {location} at {time_period} in {season}")
        
        # Try to fetch POI data with retries
        data = _fetch_poi_data(location)
        
        # Get a random POI from the results
        pois = data['results']
        poi = random.choice(pois)
        
        # Get detailed information using Place Details API (with fallback to basic data)
        place_id = poi.get('place_id')
        details = None
        
        if place_id:
            details = _fetch_poi_details(place_id)
        
        # Use details if available, otherwise fall back to search results
        info = details if details else poi
        
        # Extract information
        name = info.get('name', 'Unknown Location')
        rating = info.get('rating', 'No rating')
        address = info.get('formatted_address', 'Address not available')
        website = info.get('website')
        phone = info.get('international_phone_number')
        google_url = info.get('url')  # Google Maps link
        
        # Get type of attraction
        types = info.get('types', [])
        poi_types = [t.replace('_', ' ').title() for t in types 
                    if t not in ['establishment', 'point_of_interest']]
        category = ', '.join(poi_types[:2]) if poi_types else 'Attraction'
        
        # Determine appropriate emoji based on type
        emoji = '🏛️'  # default
        if 'park' in category.lower():
            emoji = '🌳'
        elif 'museum' in category.lower():
            emoji = '🏛️'
        elif 'beach' in category.lower():
            emoji = '🏖️'
        elif 'historic' in category.lower() or 'monument' in category.lower():
            emoji = '🏛️'
        elif 'garden' in category.lower():
            emoji = '🌺'
        elif 'zoo' in category.lower() or 'aquarium' in category.lower():
            emoji = '🐾'
        
        # Get photo URL if available
        photo_url = None
        photos = info.get('photos', [])
        if photos:
            photo_reference = photos[0].get('photo_reference')
            if photo_reference:
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={settings.GOOGLE_PLACES_API_KEY}"
        
        # Build the recommendation with rich content
        recommendation_parts = [f"{emoji} **{name}**"]
        recommendation_parts.append(f"📍 {address}")
        recommendation_parts.append(f"⭐ {rating}/5")
        recommendation_parts.append(f"🎯 {category}")
        
        # Add rich media links
        links = []
        if website:
            links.append(f"🌐 [Website]({website})")
        if phone:
            links.append(f"📞 {phone}")
        if google_url:
            links.append(f"🗺️ [Directions]({google_url})")
        
        if links:
            recommendation_parts.append("")
            recommendation_parts.append(" • ".join(links))
        
        # Add photo if available
        if photo_url:
            recommendation_parts.append("")
            recommendation_parts.append(f"📸 [View Photo]({photo_url})")
        
        recommendation_parts.append("")
        recommendation_parts.append("Perfect for you two to explore and discover something new together!")
        
        result = "\n".join(recommendation_parts)
        logger.info(f"Successfully generated POI recommendation: {name}")
        return result
        
    except (RetryError, APIHealthError) as e:
        # All retries exhausted or circuit breaker open - use fallback
        logger.error(f"API completely unavailable for POI recommendations: {e}")
        logger.info("Using fallback POI recommendation")
        return get_fallback_poi(season, time_period)
    
    except Exception as e:
        # Unexpected error - log and use fallback
        logger.error(f"Unexpected error in POI recommendation: {e}")
        logger.info("Using fallback POI recommendation due to unexpected error")
        return get_fallback_poi(season, time_period) 