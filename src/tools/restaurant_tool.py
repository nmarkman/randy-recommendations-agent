"""
Restaurant recommendation tool using Google Places API with robust error handling.
"""
import requests
import random
import logging
from datetime import datetime
from agents import function_tool
from config.settings import settings
from src.utils.retry import google_places_retry, circuit_breaker, RetryError, APIHealthError
from src.utils.fallbacks import get_fallback_restaurant

logger = logging.getLogger('Randy.RestaurantTool')

@circuit_breaker(failure_threshold=3, recovery_timeout=300)  # 5 minute recovery
@google_places_retry
def _fetch_restaurant_data(location: str):
    """
    Fetch restaurant data from Google Places API with retry logic.
    
    Args:
        location: Location to search for restaurants
        
    Returns:
        API response data
        
    Raises:
        Various exceptions for retry handling
    """
    # Google Places API - Text Search
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': f'restaurants in {location}',
        'key': settings.GOOGLE_PLACES_API_KEY,
        'type': 'restaurant',
        'language': 'en'
    }
    
    logger.info(f"Fetching restaurant data for location: {location}")
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('results'):
        raise ValueError(f"No restaurants found in {location}")
    
    return data

@google_places_retry  
def _fetch_restaurant_details(place_id: str):
    """
    Fetch detailed restaurant information with retry logic.
    
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
            'fields': 'name,formatted_address,rating,price_level,types,website,international_phone_number,photos,opening_hours,url'
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
        logger.warning(f"Error fetching restaurant details for {place_id}: {e}")
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
def get_restaurant_recommendation(location: str = None) -> str:
    """
    Get a random restaurant recommendation with robust error handling and fallbacks.
    
    Args:
        location: Location to search for restaurants (defaults to configured region)
    
    Returns:
        Formatted restaurant recommendation string with rich content
    """
    if not location:
        location = settings.REGION
    
    season, time_period = _determine_season_and_time()
    
    try:
        logger.info(f"Starting restaurant recommendation for {location} at {time_period} in {season}")
        
        # Try to fetch restaurant data with retries
        data = _fetch_restaurant_data(location)
        
        # Get a random restaurant from the results
        restaurants = data['results']
        restaurant = random.choice(restaurants)
        
        # Get detailed information using Place Details API (with fallback to basic data)
        place_id = restaurant.get('place_id')
        details = None
        
        if place_id:
            details = _fetch_restaurant_details(place_id)
        
        # Use details if available, otherwise fall back to search results
        info = details if details else restaurant
        
        # Extract basic information
        name = info.get('name', 'Unknown Restaurant')
        rating = info.get('rating', 'No rating')
        address = info.get('formatted_address', 'Address not available')
        price_level = info.get('price_level')
        website = info.get('website')
        phone = info.get('international_phone_number')
        google_url = info.get('url')  # Google Maps link
        
        # Convert price level to $ symbols
        price_display = ''
        if price_level:
            price_display = f" ({'$' * price_level})"
        
        # Get cuisine type from types if available
        types = info.get('types', [])
        cuisine_types = [t.replace('_', ' ').title() for t in types 
                        if t not in ['establishment', 'point_of_interest', 'food']]
        cuisine = ', '.join(cuisine_types[:2]) if cuisine_types else 'Restaurant'
        
        # Get photo URL if available
        photo_url = None
        photos = info.get('photos', [])
        if photos:
            photo_reference = photos[0].get('photo_reference')
            if photo_reference:
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={settings.GOOGLE_PLACES_API_KEY}"
        
        # Build the recommendation with rich content
        recommendation_parts = [f"🍽️ **{name}**"]
        recommendation_parts.append(f"📍 {address}")
        recommendation_parts.append(f"⭐ {rating}/5{price_display}")
        recommendation_parts.append(f"🍜 {cuisine}")
        
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
        recommendation_parts.append("This looks like a great spot for you two to try something new together!")
        
        result = "\n".join(recommendation_parts)
        logger.info(f"Successfully generated restaurant recommendation: {name}")
        return result
        
    except (RetryError, APIHealthError) as e:
        # All retries exhausted or circuit breaker open - use fallback
        logger.error(f"API completely unavailable for restaurant recommendations: {e}")
        logger.info("Using fallback restaurant recommendation")
        return get_fallback_restaurant(season, time_period)
    
    except Exception as e:
        # Unexpected error - log and use fallback
        logger.error(f"Unexpected error in restaurant recommendation: {e}")
        logger.info("Using fallback restaurant recommendation due to unexpected error")
        return get_fallback_restaurant(season, time_period) 