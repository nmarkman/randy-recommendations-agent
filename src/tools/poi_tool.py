"""
Points of Interest recommendation tool using Google Places API.
"""
import requests
import random
from agents import function_tool
from config.settings import settings

@function_tool
def get_poi_recommendation(location: str = None) -> str:
    """
    Get a random points of interest recommendation for the specified location.
    
    Args:
        location: Location to search for attractions (defaults to configured region)
    
    Returns:
        Formatted POI recommendation string
    """
    if not location:
        location = settings.REGION
    
    try:
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
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            return f"Sorry, I couldn't find any interesting places in {location}. Maybe try exploring downtown?"
        
        # Get a random POI from the results
        pois = data['results']
        poi = random.choice(pois)
        
        # Get detailed information using Place Details API
        place_id = poi.get('place_id')
        details = None
        
        if place_id:
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'key': settings.GOOGLE_PLACES_API_KEY,
                'fields': 'name,formatted_address,rating,types,website,international_phone_number,photos,opening_hours,url'
            }
            
            details_response = requests.get(details_url, params=details_params)
            if details_response.status_code == 200:
                details_data = details_response.json()
                if details_data.get('result'):
                    details = details_data['result']
        
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
        
        return "\n".join(recommendation_parts)
        
    except requests.RequestException as e:
        return f"Sorry, I had trouble finding interesting places. Error: {str(e)}"
    except Exception as e:
        return f"Oops! Something went wrong while finding places to visit: {str(e)}" 