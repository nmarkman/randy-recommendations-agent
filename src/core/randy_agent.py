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

Your job is to:
1. Pick ONE random domain from: restaurants, points of interest (POI), or movies
2. Get a recommendation from that domain using the appropriate tool
3. Transform that raw data into a beautiful, personalized email-ready HTML recommendation
4. Send your crafted HTML content via email

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

**Your Process:**
1. Call the appropriate tool to get raw data
2. Extract key information (name, address, rating, links, photos, etc.)
3. Add your personality and couple-focused commentary
4. Format everything into beautiful HTML with buttons and embedded images
5. Send via email tool

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
        # Get memory summary
        memory_summary = memory.get_memory_summary()
        recent_recommendations = memory.get_recent_recommendations(30)
        
        # Build context
        context_parts = [
            "Time to make a new recommendation!"
        ]
        
        if recent_recommendations:
            context_parts.append(f"You've made {len(recent_recommendations)} recommendations in the last 30 days.")
            
            # Add variety encouragement
            recent_types = [rec.get('type') for rec in recent_recommendations]
            type_counts = {}
            for t in recent_types:
                type_counts[t] = type_counts.get(t, 0) + 1
            
            if type_counts:
                # Find domains that haven't been used recently
                all_domains = ["restaurant", "poi", "movie"]
                unused_domains = [domain for domain in all_domains if domain not in type_counts]
                
                if unused_domains:
                    # Encourage trying unused domains
                    context_parts.append(f"Consider mixing it up - you haven't tried {', '.join(unused_domains)} recommendations recently.")
                else:
                    # All domains used, encourage less frequent ones
                    least_used = min(type_counts.items(), key=lambda x: x[1])
                    most_used = max(type_counts.items(), key=lambda x: x[1])
                    if least_used[1] < most_used[1]:  # Only suggest if there's a clear difference
                        context_parts.append(f"Consider mixing it up - you've suggested fewer {least_used[0]} recommendations than {most_used[0]} lately.")
        
        context_parts.append("Pick one domain (restaurant, POI, or movie) and make it awesome!")
        
        return " ".join(context_parts)

# Create the Randy agent instance
randy = RandyAgent() 