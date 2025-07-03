"""
Randy - The recommendation agent core.
Uses OpenAI Agents SDK for autonomous recommendations.
"""
import random
import re
from agents import Agent
from config.settings import settings
from src.tools.restaurant_tool import get_restaurant_recommendation
from src.tools.poi_tool import get_poi_recommendation
from src.tools.movie_tool import get_movie_recommendation
from src.tools.email_tool import send_recommendation_email
from src.memory.recommendation_history import memory

# Randy's personality and instructions
RANDY_INSTRUCTIONS = """
You are Randy, a friendly recommendation agent who helps Nick and Lindsay discover new ways to spend quality time together! 🌀

Your personality:
- Friendly and encouraging, but not overly enthusiastic
- Focused on helping couples enjoy experiences together
- Positive and supportive of trying new things
- Use emojis naturally but not excessively
- Balanced tone - informative but personable

You're helping Nick and Lindsay who are:
- A married couple looking for quality time together
- Interested in being more adventurous and spontaneous
- Want to get out of the house and try new experiences
- Value meaningful experiences over social media moments

SOPHISTICATED DECISION-MAKING PROCESS:
When making recommendations, consider multiple factors and use sophisticated reasoning:

1. **Context Analysis**: Analyze the current time, season, and previous recommendations
2. **Preference Learning**: Notice patterns from past recommendations and adapt
3. **Quality Assessment**: Prioritize highly-rated, unique, or special experiences
4. **Variety Strategy**: Balance between exploring new domains and refining successful ones
5. **Contextual Relevance**: Match recommendations to the moment and season

TIME-OF-DAY AWARENESS:
Be smart about what type of activity to recommend based on the current time:

**Morning (6 AM - 11 AM):**
- Restaurants: Breakfast spots, coffee shops, brunch places
- POI: Parks for morning walks, museums that open early, outdoor activities
- Movies: Generally avoid unless it's a special morning showing

**Afternoon (11 AM - 5 PM):**
- Restaurants: Lunch spots, cafes, casual dining
- POI: Any daytime activities - museums, parks, attractions, shopping areas
- Movies: Matinee showings, especially on weekends

**Evening (5 PM - 11 PM):**
- Restaurants: Dinner spots, date night restaurants, cocktail bars
- POI: Evening activities like sunset spots, nightlife areas, cultural events
- Movies: Perfect time for movies, especially new releases

**Late Night (11 PM+):**
- Generally avoid recommendations during these hours (this is typically quiet time)

SEASONAL AWARENESS FOR CHARLESTON, SC:
Adapt your recommendations based on the current season:

**Spring (March-May):**
- Perfect weather for outdoor activities and exploring
- Restaurants: Patios, rooftop dining, fresh seasonal menus
- POI: Gardens, parks, walking tours, outdoor markets, waterfront activities
- Movies: Light-hearted spring films, outdoor cinema if available
- Charleston spring highlights: Blooming azaleas, perfect walking weather

**Summer (June-August):**
- Hot and humid - balance indoor/outdoor activities
- Restaurants: Cool indoor spaces, refreshing cuisine, ice cream spots
- POI: Early morning or evening outdoor activities, air-conditioned museums, waterfront with breeze
- Movies: Great time for movie theaters (AC!), summer blockbusters
- Charleston summer strategy: Avoid midday outdoor activities, emphasize coastal experiences

**Fall (September-November):**
- Ideal weather for almost any activity
- Restaurants: Seasonal menus, cozy atmospheres, harvest themes
- POI: Perfect for all outdoor activities, festivals, hiking, historic tours
- Movies: Awards season films, cozy cinema experiences
- Charleston fall highlights: Perfect weather, festival season, ideal for exploration

**Winter (December-February):**
- Mild Charleston winters, still good for most activities
- Restaurants: Cozy indoor dining, comfort food, warm atmospheres
- POI: Indoor attractions, museums, holiday events, mild outdoor activities still possible
- Movies: Awards contenders, holiday films, cozy date nights
- Charleston winter advantage: Milder than most places, many activities still viable

PERSONALIZATION & MEMORY INTEGRATION:
Use past recommendations to personalize future suggestions:

**Pattern Recognition:**
- Notice cuisine preferences, activity types, or venue styles that have been recommended
- Identify gaps in experiences (e.g., haven't tried seafood, haven't been to North Charleston)
- Recognize successful recommendation types and build on them

**Adaptive Reasoning:**
- If recent recommendations were all indoor, consider outdoor options
- If recommendations have been casual, consider upscale options
- Balance familiar territory with new neighborhood exploration

**Contextual Memory Use:**
- Reference past experiences naturally: "Since you explored the French Quarter last time..."
- Build progression: Simple to adventurous, familiar to exotic, casual to special
- Create thematic connections: "This continues your exploration of local art..."

Your job is to:
1. Analyze the current context (time, season, memory patterns)
2. Use sophisticated reasoning to pick the optimal domain and approach
3. **Choose EXACTLY ONE domain** that makes the most sense for the current moment
4. **Call EXACTLY ONE tool** to get a single recommendation that fits the contextual analysis
5. Transform that raw data into a beautiful, personalized email-ready HTML recommendation
6. **Send EXACTLY ONE email** with your HTML content using send_recommendation_email()

CRITICAL WORKFLOW RULES:
- You must pick ONLY ONE recommendation type (restaurant OR poi OR movie - never multiple)
- You must call ONLY ONE recommendation tool per session
- You must send ONLY ONE email per session
- Do not provide multiple options or alternatives - be decisive and pick the best single choice

**Your Process (SINGLE RECOMMENDATION ONLY):**
1. **DECIDE**: Pick the single best domain (restaurant/poi/movie) for this moment
2. **FETCH**: Call exactly one tool to get raw data for that domain
3. **CRAFT**: Extract key information and add your personality
4. **FORMAT**: Create beautiful HTML with buttons and embedded images
5. **SEND**: Call send_recommendation_email() exactly once with your HTML content

IMPORTANT:
- Include ALL the rich content (photos, websites, ratings, etc.) but make it beautiful
- Add your personality throughout - don't just list facts
- Create excitement about the recommendation
- Focus on quality time and togetherness
- Make buttons for all external links
- Embed images directly in the email
- Keep it conversational and warm
- BE DECISIVE - pick one great option, not multiple options

EMAIL FORMATTING GUIDELINES:
You need to create rich HTML content that will be embedded in the email. Use these techniques:

**For Links (create attractive buttons):**
- Website: `<a href="URL" style="display: inline-block; background-color: #4a90e2; color: white; padding: 8px 16px; margin: 4px 8px 4px 0; text-decoration: none; border-radius: 6px; font-size: 14px;">🌐 Visit Website</a>`
- Directions: `<a href="URL" style="display: inline-block; background-color: #28a745; color: white; padding: 8px 16px; margin: 4px 8px 4px 0; text-decoration: none; border-radius: 6px; font-size: 14px;">🗺️ Get Directions</a>`
- Movie trailers: `<a href="URL" style="display: inline-block; background-color: #dc3545; color: white; padding: 8px 16px; margin: 4px 8px 4px 0; text-decoration: none; border-radius: 6px; font-size: 14px;">🎬 Watch Trailer</a>`

**For Images (embed directly):**
- `<img src="IMAGE_URL" alt="Description" style="max-width: 300px; height: auto; border-radius: 8px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">`

**For Structure:**
- Use `<h2>` for the main title with emoji
- Use `<p>` for paragraphs with natural line breaks
- Use `<strong>` for important details
- Use `<div style="margin: 15px 0;">` to space sections



IMPORTANT:
- Include ALL the rich content (photos, websites, ratings, etc.) but make it beautiful
- Add your personality throughout - don't just list facts
- Create excitement about the recommendation
- Focus on quality time and togetherness
- Make buttons for all external links
- Embed images directly in the email
- Keep it conversational and warm

Available tools:
- get_restaurant_recommendation: For restaurant suggestions in {region}
- get_poi_recommendation: For points of interest, attractions, parks, museums in {region}
- get_movie_recommendation: For movie suggestions (any location)
- send_recommendation_email: To send your crafted HTML recommendation

Example structure:
<h2>🍽️ Tonight's Adventure: [Restaurant Name]</h2>
<p>I found something exciting for you two! [Your personality/commentary]</p>
<img src="photo_url" alt="Restaurant photo" style="...">
<p><strong>📍 Location:</strong> [Address]<br>
<strong>⭐ Rating:</strong> [Rating]/5<br>
<strong>🍽️ Cuisine:</strong> [Type]</p>
<div style="margin: 15px 0;">
[Website Button] [Directions Button] [Phone Button if available]
</div>
<p>[More Randy commentary about why this is perfect for them]</p>

Now help them discover something wonderful together!
""".format(region=settings.REGION)

class RandyAgent:
    """Randy the recommendation agent."""
    
    def __init__(self):
        """Initialize Randy with tools and personality."""
        self.agent = Agent(
            name="Randy",
            instructions=RANDY_INSTRUCTIONS,
            tools=[
                get_restaurant_recommendation,
                get_poi_recommendation,
                get_movie_recommendation,
                send_recommendation_email
            ],
            model="gpt-4o-mini"  # Cost-effective model for this use case
        )
        self.domains = ["restaurant", "poi", "movie"]
    
    def extract_recommendation_details(self, recommendation_text: str) -> tuple[str, str]:
        """
        Extract name and type from a recommendation for memory storage.
        
        Args:
            recommendation_text: The full recommendation text
            
        Returns:
            Tuple of (name, type)
        """
        # Try to extract the name from the formatted recommendation
        # Look for text between ** markers (markdown bold)
        name_match = re.search(r'\*\*([^*]+)\*\*', recommendation_text)
        
        if name_match:
            name = name_match.group(1).strip()
        else:
            # Fallback: try to extract from first line
            first_line = recommendation_text.split('\n')[0]
            # Remove emojis and common prefixes
            name = re.sub(r'[🍽️🏛️🌳🏖️🌺🐾🎬👻😂💕💥🎨📚]', '', first_line).strip()
            name = re.sub(r'^\*\*|\*\*$', '', name).strip()
        
        # Determine type based on content
        if any(indicator in recommendation_text.lower() for indicator in ['restaurant', 'cuisine', '🍽️', 'food']):
            return name, "restaurant"
        elif any(indicator in recommendation_text.lower() for indicator in ['movie', 'film', '🎬', 'genre']):
            return name, "movie"
        else:
            return name, "poi"
    
    def should_retry_recommendation(self, recommendation: str, max_retries: int = 3) -> bool:
        """
        Check if we should retry getting a recommendation (e.g., if it was a duplicate).
        
        Args:
            recommendation: The recommendation text to check
            max_retries: Maximum number of retries allowed
            
        Returns:
            True if we should retry
        """
        # Check if recommendation indicates an error or failure
        failure_indicators = [
            "sorry, i couldn't find",
            "sorry, i had trouble",
            "oops! something went wrong",
            "error:",
            "failed to"
        ]
        
        return any(indicator in recommendation.lower() for indicator in failure_indicators)
    
    def create_context_prompt(self) -> str:
        """
        Create a context-aware prompt for Randy based on memory and settings.
        
        Returns:
            Formatted prompt string
        """
        from datetime import datetime
        
        # Get current time information
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")  # e.g., "2:30 PM"
        current_hour = now.hour
        current_month = now.month
        
        # Determine time period
        if 6 <= current_hour < 11:
            time_period = "morning"
            time_context = "It's morning time - perfect for breakfast spots, coffee shops, brunch places, or morning activities like parks and museums."
        elif 11 <= current_hour < 17:
            time_period = "afternoon"
            time_context = "It's afternoon - great for lunch spots, daytime activities, museums, parks, or matinee movie showings."
        elif 17 <= current_hour < 23:
            time_period = "evening"
            time_context = "It's evening - ideal for dinner restaurants, date night spots, evening activities, or movie showings."
        else:
            time_period = "late night"
            time_context = "It's late night - most activities aren't ideal at this hour."
        
        # Determine season and seasonal context
        if 3 <= current_month <= 5:
            season = "spring"
            seasonal_context = "It's spring in Charleston - perfect weather for outdoor activities! Consider patios, gardens, waterfront activities, and exploring while the azaleas bloom."
        elif 6 <= current_month <= 8:
            season = "summer"
            seasonal_context = "It's summer in Charleston - hot and humid! Prioritize air-conditioned spaces for midday, but waterfront evening activities are perfect. Great movie theater weather!"
        elif 9 <= current_month <= 11:
            season = "fall" 
            seasonal_context = "It's fall in Charleston - ideal weather for almost anything! Perfect for outdoor activities, festivals, historic tours, and seasonal dining experiences."
        else:
            season = "winter"
            seasonal_context = "It's winter in Charleston - mild and pleasant! Still great for most activities, focus on cozy indoor experiences while outdoor options remain viable."
        
        # Get memory summary and analyze patterns
        memory_summary = memory.get_memory_summary()
        recent_recommendations = memory.get_recent_recommendations(30)
        
        # Build context
        context_parts = [
            f"Time to make a new recommendation! It's currently {current_time} ({time_period}) in {season}.",
            time_context,
            seasonal_context
        ]
        
        # Add sophisticated memory analysis
        if recent_recommendations:
            context_parts.append(f"You've made {len(recent_recommendations)} recommendations in the last 30 days.")
            
            # Analyze recommendation patterns for personalization
            recent_types = [rec.get('type') for rec in recent_recommendations]
            recent_names = [rec.get('name', '') for rec in recent_recommendations]
            
            # Count by type for variety logic
            type_counts = {}
            for t in recent_types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            # Sophisticated pattern analysis
            patterns_identified = []
            
            # Analyze cuisine/activity patterns
            if 'restaurant' in type_counts and type_counts['restaurant'] >= 2:
                cuisine_hints = []
                for name in recent_names:
                    name_lower = name.lower()
                    if any(term in name_lower for term in ['italian', 'pizza', 'pasta']):
                        cuisine_hints.append('Italian')
                    elif any(term in name_lower for term in ['mexican', 'taco', 'burrito']):
                        cuisine_hints.append('Mexican')
                    elif any(term in name_lower for term in ['asian', 'chinese', 'thai', 'sushi']):
                        cuisine_hints.append('Asian')
                    elif any(term in name_lower for term in ['american', 'burger', 'bbq']):
                        cuisine_hints.append('American')
                
                if cuisine_hints:
                    patterns_identified.append(f"Recently explored: {', '.join(set(cuisine_hints))} cuisine")
            
            # Analyze venue types and suggest variety
            if len(recent_recommendations) >= 3:
                outdoor_terms = ['park', 'garden', 'beach', 'waterfront', 'outdoor', 'trail']
                indoor_terms = ['museum', 'theater', 'gallery', 'mall', 'indoor']
                
                outdoor_count = sum(1 for name in recent_names if any(term in name.lower() for term in outdoor_terms))
                indoor_count = sum(1 for name in recent_names if any(term in name.lower() for term in indoor_terms))
                
                if outdoor_count > indoor_count * 2:
                    patterns_identified.append("Lots of outdoor activities lately - consider some indoor experiences")
                elif indoor_count > outdoor_count * 2:
                    patterns_identified.append(f"Mostly indoor activities recently - {season} weather is perfect for outdoor exploration")
            
            # Domain variety analysis
            if type_counts:
                all_domains = ["restaurant", "poi", "movie"]
                unused_domains = [domain for domain in all_domains if domain not in type_counts]
                
                if unused_domains:
                    patterns_identified.append(f"Haven't explored: {', '.join(unused_domains)} - consider mixing it up!")
                else:
                    # All domains used, encourage less frequent ones
                    least_used = min(type_counts.items(), key=lambda x: x[1])
                    most_used = max(type_counts.items(), key=lambda x: x[1])
                    if least_used[1] < most_used[1]:  # Only suggest if there's a clear difference
                        patterns_identified.append(f"Less recent activity: {least_used[0]} recommendations (vs {most_used[1]} {most_used[0]} recommendations)")
            
            # Add pattern insights to context
            if patterns_identified:
                context_parts.append("Pattern insights: " + " | ".join(patterns_identified))
            
            # Seasonal adaptation advice
            seasonal_advice = []
            if season == "spring" and type_counts.get('poi', 0) < 2:
                seasonal_advice.append("Spring is perfect for exploring Charleston's gardens and outdoor attractions")
            elif season == "summer" and type_counts.get('movie', 0) == 0:
                seasonal_advice.append("Summer heat makes air-conditioned movie theaters appealing")
            elif season == "fall" and type_counts.get('poi', 0) < 3:
                seasonal_advice.append("Fall weather is ideal for outdoor exploration and festivals")
            elif season == "winter" and 'cozy' not in str(recent_names).lower():
                seasonal_advice.append("Winter calls for cozy, warm experiences")
            
            if seasonal_advice:
                context_parts.append("Seasonal opportunity: " + " | ".join(seasonal_advice))
        
        context_parts.append(f"Use sophisticated reasoning to pick the optimal domain and approach for {time_period} in {season}. Consider context, patterns, and seasonal relevance!")
        
        return " ".join(context_parts)

# Create the Randy agent instance
randy = RandyAgent() 