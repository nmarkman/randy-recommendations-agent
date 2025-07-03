"""
Fallback system for when APIs fail completely.
Provides cached/static recommendations to ensure Randy always has something to suggest.
"""
import random
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger('Randy.Fallbacks')

# Static fallback recommendations for Charleston, SC
FALLBACK_RESTAURANTS = [
    {
        'name': 'Husk Restaurant',
        'address': '76 Queen St, Charleston, SC 29401',
        'rating': '4.4',
        'cuisine': 'New American, Southern',
        'description': 'Celebrated farm-to-table restaurant showcasing Southern ingredients in an elegant Queen Street setting.',
        'price_level': '$$$'
    },
    {
        'name': 'FIG Restaurant',
        'address': '232 Meeting St, Charleston, SC 29401',
        'rating': '4.5',
        'cuisine': 'Mediterranean, American',
        'description': 'Seasonal Mediterranean-inspired cuisine in a cozy downtown Charleston atmosphere.',
        'price_level': '$$$'
    },
    {
        'name': 'The Ordinary',
        'address': '544 King St, Charleston, SC 29403',
        'rating': '4.3',
        'cuisine': 'Seafood, Raw Bar',
        'description': 'Stunning oyster bar and seafood hall in a beautifully restored bank building.',
        'price_level': '$$$'
    },
    {
        'name': 'Hominy Grill',
        'address': '207 Rutledge Ave, Charleston, SC 29403',
        'rating': '4.2',
        'cuisine': 'Southern, Breakfast',
        'description': 'Beloved local spot serving authentic Lowcountry comfort food since 1996.',
        'price_level': '$$'
    },
    {
        'name': 'Xiao Bao Biscuit',
        'address': '224 Rutledge Ave, Charleston, SC 29403',
        'rating': '4.1',
        'cuisine': 'Asian Fusion, Bao',
        'description': 'Creative Asian-Southern fusion in a hip, casual atmosphere.',
        'price_level': '$$'
    }
]

FALLBACK_POIS = [
    {
        'name': 'Rainbow Row',
        'address': 'E Bay St, Charleston, SC 29401',
        'rating': '4.6',
        'category': 'Historic Site, Architecture',
        'description': 'Iconic series of 13 colorful historic houses along East Bay Street, perfect for photos and strolling.',
        'type': 'Historic'
    },
    {
        'name': 'Waterfront Park',
        'address': 'Vendue Range, Charleston, SC 29401',
        'rating': '4.5',
        'category': 'Park, Waterfront',
        'description': 'Beautiful waterfront park with harbor views, famous pineapple fountain, and romantic walking paths.',
        'type': 'Park'
    },
    {
        'name': 'Charleston City Market',
        'address': '188 Meeting St, Charleston, SC 29401',
        'rating': '4.2',
        'category': 'Market, Shopping',
        'description': 'Historic covered market with local artisans, sweetgrass baskets, and Charleston souvenirs.',
        'type': 'Market'
    },
    {
        'name': 'The Battery',
        'address': 'Murray Blvd, Charleston, SC 29401',
        'rating': '4.7',
        'category': 'Historic Park, Mansions',
        'description': 'Scenic waterfront promenade lined with antebellum mansions and harbor cannons.',
        'type': 'Historic'
    },
    {
        'name': 'Magnolia Plantation and Gardens',
        'address': '3550 Ashley River Rd, Charleston, SC 29414',
        'rating': '4.4',
        'category': 'Plantation, Gardens',
        'description': 'Americas oldest public gardens with stunning azaleas, oak trees, and historic plantation house.',
        'type': 'Garden'
    }
]

FALLBACK_MOVIES = [
    {
        'title': 'The Princess Bride',
        'year': '1987',
        'rating': '8.0',
        'genre': 'Adventure, Family, Fantasy',
        'runtime': '98',
        'description': 'A timeless fairy tale adventure perfect for couples, with romance, humor, and unforgettable quotes.',
        'reason': 'Perfect date night classic'
    },
    {
        'title': 'When Harry Met Sally',
        'year': '1989',
        'rating': '7.7',
        'genre': 'Comedy, Romance',
        'runtime': '96',
        'description': 'The ultimate romantic comedy about friendship, love, and whether men and women can just be friends.',
        'reason': 'Ideal couple movie night'
    },
    {
        'title': 'The Grand Budapest Hotel',
        'year': '2014',
        'rating': '8.1',
        'genre': 'Adventure, Comedy, Crime',
        'runtime': '99',
        'description': 'Wes Andersons whimsical tale of a legendary concierge and his protégé at a famous European hotel.',
        'reason': 'Visually stunning and charming'
    },
    {
        'title': 'Paddington',
        'year': '2014',
        'rating': '7.3',
        'genre': 'Adventure, Comedy, Family',
        'runtime': '95',
        'description': 'Heartwarming story of a polite bear finding his place in London, perfect for a cozy evening.',
        'reason': 'Feel-good and delightful'
    },
    {
        'title': 'Chef',
        'year': '2014',
        'rating': '7.3',
        'genre': 'Comedy, Drama',
        'runtime': '114',
        'description': 'A chef starts a food truck to rediscover his passion for cooking and reconnect with his family.',
        'reason': 'Inspiring and mouth-watering'
    }
]

def get_fallback_restaurant(season: str = None, time_period: str = None) -> str:
    """
    Generate a fallback restaurant recommendation.
    
    Args:
        season: Current season for context
        time_period: Current time period (morning, afternoon, evening)
    
    Returns:
        Formatted restaurant recommendation
    """
    restaurant = random.choice(FALLBACK_RESTAURANTS)
    
    # Add seasonal context
    seasonal_note = ""
    if season == "spring":
        seasonal_note = " The spring weather makes this a perfect time to explore Charleston's dining scene!"
    elif season == "summer":
        seasonal_note = " Their air-conditioned dining room is perfect for Charleston's summer heat!"
    elif season == "fall":
        seasonal_note = " Fall weather makes this an ideal time to try somewhere new!"
    elif season == "winter":
        seasonal_note = " Their warm atmosphere is perfect for a cozy winter evening!"
    
    # Add time context
    time_note = ""
    if time_period == "morning":
        time_note = " Great for a special brunch or late breakfast!"
    elif time_period == "afternoon":
        time_note = " Perfect for a leisurely lunch!"
    elif time_period == "evening":
        time_note = " Ideal for a romantic dinner out!"
    
    recommendation = f"""🍽️ **{restaurant['name']}** (Backup Recommendation)

📍 {restaurant['address']}
⭐ {restaurant['rating']}/5 {restaurant['price_level']}
🍜 {restaurant['cuisine']}

{restaurant['description']}{seasonal_note}{time_note}

🌐 [Search on Google](https://www.google.com/search?q={restaurant['name'].replace(' ', '+')}+Charleston+SC)

*Note: This is a curated backup recommendation. Randy's APIs are temporarily unavailable, but this is still a fantastic choice for you two!*"""

    logger.info(f"Generated fallback restaurant recommendation: {restaurant['name']}")
    return recommendation

def get_fallback_poi(season: str = None, time_period: str = None) -> str:
    """
    Generate a fallback POI recommendation.
    
    Args:
        season: Current season for context
        time_period: Current time period
    
    Returns:
        Formatted POI recommendation
    """
    poi = random.choice(FALLBACK_POIS)
    
    # Choose emoji based on type
    emoji_map = {
        'Historic': '🏛️',
        'Park': '🌳',
        'Market': '🛍️',
        'Garden': '🌺'
    }
    emoji = emoji_map.get(poi['type'], '🏛️')
    
    # Add seasonal context
    seasonal_note = ""
    if season == "spring" and poi['type'] in ['Park', 'Garden']:
        seasonal_note = " Spring is the perfect time to visit - everything is blooming beautifully!"
    elif season == "summer" and poi['type'] == 'Historic':
        seasonal_note = " Visit early or late in the day to avoid the summer heat!"
    elif season == "fall":
        seasonal_note = " Fall weather makes this perfect for exploring!"
    elif season == "winter":
        seasonal_note = " Even in Charleston's mild winter, this is a lovely place to visit!"
    
    recommendation = f"""{emoji} **{poi['name']}** (Backup Recommendation)

📍 {poi['address']}
⭐ {poi['rating']}/5
🎯 {poi['category']}

{poi['description']}{seasonal_note}

🗺️ [Get Directions](https://www.google.com/maps/search/{poi['name'].replace(' ', '+')}+Charleston+SC)

*Note: This is a curated backup recommendation. Randy's APIs are temporarily unavailable, but this is still a wonderful place to explore together!*"""

    logger.info(f"Generated fallback POI recommendation: {poi['name']}")
    return recommendation

def get_fallback_movie(season: str = None, time_period: str = None) -> str:
    """
    Generate a fallback movie recommendation.
    
    Args:
        season: Current season for context  
        time_period: Current time period
    
    Returns:
        Formatted movie recommendation
    """
    movie = random.choice(FALLBACK_MOVIES)
    
    # Add time context
    time_note = ""
    if time_period == "evening":
        time_note = " Perfect for tonight's movie night!"
    elif time_period == "afternoon":
        time_note = " Great for an afternoon viewing!"
    else:
        time_note = " Save this one for your next movie night!"
    
    recommendation = f"""🎬 **{movie['title']}** ({movie['year']}) (Backup Recommendation)

⭐ {movie['rating']}/10
🎭 {movie['genre']} • {movie['runtime']} min

{movie['description']}{time_note}

💡 Why this is perfect: {movie['reason']}

🎬 [Find on IMDb](https://www.imdb.com/find?q={movie['title'].replace(' ', '+')})
📺 [Search Streaming Services](https://www.google.com/search?q=watch+{movie['title'].replace(' ', '+')}+streaming)

*Note: This is a curated backup recommendation. Randy's APIs are temporarily unavailable, but this is still a fantastic choice for movie night!*"""

    logger.info(f"Generated fallback movie recommendation: {movie['title']}")
    return recommendation

def get_fallback_recommendation(rec_type: str, season: str = None, time_period: str = None) -> str:
    """
    Get a fallback recommendation of the specified type.
    
    Args:
        rec_type: Type of recommendation ('restaurant', 'poi', 'movie')
        season: Current season
        time_period: Current time period
    
    Returns:
        Formatted fallback recommendation
    """
    logger.warning(f"Using fallback recommendation for {rec_type}")
    
    if rec_type == 'restaurant':
        return get_fallback_restaurant(season, time_period)
    elif rec_type == 'poi':
        return get_fallback_poi(season, time_period)
    elif rec_type == 'movie':
        return get_fallback_movie(season, time_period)
    else:
        # Default fallback
        return get_fallback_restaurant(season, time_period) 