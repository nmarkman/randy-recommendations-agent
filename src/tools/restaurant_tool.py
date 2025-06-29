"""
Restaurant recommendation tool using Google Places API.
"""
import requests
import random
from agents import function_tool
from config.settings import settings

@function_tool
def get_restaurant_recommendation(location: str = None) -> str:
    """
    Get a random restaurant recommendation with rich media (photos, website, phone).
    
    Args:
        location: Location to search for restaurants (defaults to configured region)
    
    Returns:
        Formatted restaurant recommendation string with rich content
    """
    if not location:
        location = settings.REGION
    
    try:
        # Google Places API - Text Search
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': f'restaurants in {location}',
            'key': settings.GOOGLE_PLACES_API_KEY,
            'type': 'restaurant',
            'language': 'en'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            return f"Sorry, I couldn't find any restaurants in {location}. Maybe try a different area?"
        
        # Get a random restaurant from the results
        restaurants = data['results']
        restaurant = random.choice(restaurants)
        
        # Get detailed information using Place Details API
        place_id = restaurant.get('place_id')
        details = None
        
        if place_id:
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'key': settings.GOOGLE_PLACES_API_KEY,
                'fields': 'name,formatted_address,rating,price_level,types,website,international_phone_number,photos,opening_hours,url'
            }
            
            details_response = requests.get(details_url, params=details_params)
            if details_response.status_code == 200:
                details_data = details_response.json()
                if details_data.get('result'):
                    details = details_data['result']
        
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
        
        return "\n".join(recommendation_parts)
        
    except requests.RequestException as e:
        return f"Sorry, I had trouble connecting to find restaurants. Error: {str(e)}"
    except Exception as e:
        return f"Oops! Something went wrong while finding restaurants: {str(e)}" 