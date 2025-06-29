# 🌀 Randy - Autonomous Recommendation Agent

Randy is your friendly AI agent that brings spontaneity to your life by autonomously sending personalized activity recommendations via email. Whether it's a new restaurant, an interesting place to visit, or a movie to watch, Randy finds things for you to do, and notifies you of them in helpful and friendly ways.

## ✨ Features

- **🤖 Autonomous Operation**: Randy decides when to send recommendations (respects quiet hours and cadence)
- **🎯 Multiple Domains**: Restaurants, Points of Interest, and Movies with rich content
- **🧠 Smart Memory**: Never recommends the same thing twice
- **📍 Location Aware**: Finds local restaurants and attractions in your region
- **✉️ Beautiful Emails**: Stunning HTML emails with embedded images, Randy's logo, and colored action buttons
- **🎭 Charming Personality**: Randy knows you personally and crafts focused recommendations
- **🖼️ Rich Content**: Movie posters, restaurant photos, website links, and ratings all beautifully presented
- **⏰ Built-in Scheduling**: Respects quiet hours and weekly cadence
- **⚙️ Easy Configuration**: Simple environment variable setup

## 🎨 What Makes Randy Special

Randy doesn't just send plain text recommendations - he creates **beautiful, personalized email experiences**:

- **🎬 Movie Night**: Embedded movie posters, IMDb links, trailer buttons, ratings and reviews
- **🍽️ Restaurant Adventures**: High-quality food photos, website buttons, directions, and phone numbers  
- **🏛️ Points of Interest**: Stunning location photos, tourism links, ratings, and detailed information
- **🌀 Randy's Touch**: Professional logo, couple-focused commentary, and Randy's charming personality throughout

Every email feels like it came from a premium recommendation service, not a simple script!

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd randy-recommendations-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your actual API keys and settings
nano .env  # or use your preferred editor
```

### 3. Get Your API Keys

#### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key

#### Google Places API Key (Free Tier)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable the "Places API"
4. Go to Credentials → Create Credentials → API Key
5. (Optional) Restrict the key to Places API for security

#### TMDB API Key (Free)
1. Go to [themoviedb.org](https://www.themoviedb.org)
2. Create an account
3. Go to Settings → API
4. Request an API key (it's free!)

#### Gmail App Password
1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings
3. Security → 2-Step Verification → App passwords
4. Generate an app password for "Mail"

### 4. Configure Your Settings

Edit your `.env` file:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Places API Key
GOOGLE_PLACES_API_KEY=your-google-places-api-key-here

# TMDB API Key
TMDB_API_KEY=your-tmdb-api-key-here

# Email Configuration
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password-here
RECIPIENT_EMAIL=your-email@gmail.com

# Randy's Configuration
# Your city/region for local recommendations
REGION=Charleston, SC

# When Randy should stop sending recommendations (24-hour format)
QUIET_HOURS_START=23

# When Randy can start sending recommendations again (24-hour format)
QUIET_HOURS_END=7

# How often Randy should make recommendations (in days)
RECOMMENDATION_CADENCE_DAYS=7
```

### 5. Test Randy

```bash
# Check configuration and status
python main.py status

# Force send a test recommendation (ignores timing)
python main.py force

# Normal run (respects timing and quiet hours)
python main.py
```

## 📋 Usage

### Command Line Options

```bash
# Normal operation - respects timing and quiet hours
python main.py

# Force send a recommendation (ignores timing)
python main.py force

# Check system status
python main.py status
```

### Setting up Automated Scheduling

#### Using Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add this line to run Randy every day at 10 AM
0 10 * * * cd /path/to/randy-recommendations-agent && /path/to/.venv/bin/python main.py

# Or run every 6 hours (Randy will check if it's due)
0 */6 * * * cd /path/to/randy-recommendations-agent && /path/to/.venv/bin/python main.py
```

#### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 10 AM)
4. Set action to run: `python main.py`
5. Set start directory to your Randy folder

## 🏗️ Architecture

Randy is built using the **OpenAI Agents SDK** and follows a clean, modular architecture:

```
randy-recommendations-agent/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── tools/               # Agent tools (@function_tool)
│   │   ├── restaurant_tool.py
│   │   ├── poi_tool.py
│   │   ├── movie_tool.py
│   │   └── email_tool.py
│   ├── memory/              # Recommendation history
│   │   └── recommendation_history.py
│   ├── core/                # Randy agent core
│   │   └── randy_agent.py
│   └── scheduler/           # Timing and scheduling
│       └── timing.py
├── data/                    # Generated data files
│   ├── recommendation_history.json
│   ├── schedule.json
│   └── randy.log
└── main.py                  # Main orchestrator
```

## 🔧 Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `REGION` | Your location for local recommendations | Charleston, SC |
| `QUIET_HOURS_START` | Hour to stop sending (24hr format) | 23 (11 PM) |
| `QUIET_HOURS_END` | Hour to resume sending | 7 (7 AM) |
| `RECOMMENDATION_CADENCE_DAYS` | Days between recommendations | 7 |

## 📊 Monitoring

Randy provides detailed status information:

```bash
python main.py status
```

This shows:
- Configuration status
- Current timing and quiet hours
- Recommendation schedule
- Memory statistics
- Next recommendation due date

## 🔍 Troubleshooting

### Common Issues

**"Configuration error: Missing required environment variables"**
- Make sure you've copied `env.example` to `.env`
- Check that all API keys are filled in correctly

**"Email authentication failed"**
- Ensure you're using a Gmail App Password, not your regular password
- Make sure 2-factor authentication is enabled on your Gmail account

**"Sorry, I couldn't find any restaurants"**
- Check your Google Places API key
- Make sure the Places API is enabled in Google Cloud Console
- Verify your region setting in `.env`

**"Randy didn't generate a proper response"**
- Check your OpenAI API key
- Ensure you have sufficient API credits
- Check the logs in `data/randy.log`

### Debug Mode

For detailed logging, check:
```bash
# View recent logs
tail -f data/randy.log

# Check specific files
ls -la data/
```

### Testing Individual Components

You can test each component separately:

```python
# Test configuration
from config.settings import settings
settings.validate()

# Test scheduling
from src.scheduler.timing import scheduler
print(scheduler.get_schedule_summary())

# Test memory
from src.memory.recommendation_history import memory
print(memory.get_memory_summary())
```

## 🎯 How Randy Works

1. **🕐 Timing Check**: Randy first checks if a recommendation is due and if it's not in quiet hours
2. **🎲 Intelligent Selection**: Randy randomly picks between restaurants, points of interest, or movies (with variety logic)
3. **🔍 Data Gathering**: Randy uses the appropriate API tool to get rich data (photos, ratings, links, etc.)
4. **🧠 Memory Check**: The system ensures no duplicates are recommended
5. **🎨 Email Crafting**: Randy transforms raw data into beautiful HTML with his personality, embedded images, and colored buttons
6. **📧 Professional Delivery**: The stunning email is sent via Gmail SMTP with Randy's logo and branding
7. **💾 Memory Update**: The recommendation is stored to prevent future duplicates
8. **📅 Schedule Update**: The next recommendation time is calculated

## 🌟 Technical Excellence

- **🤖 True Autonomy**: Randy makes intelligent decisions about what to recommend using OpenAI Agents SDK
- **🎭 Rich Personality**: Each email feels personal with couple-focused commentary and enthusiasm
- **📱 Professional Design**: Responsive HTML emails that look great on mobile and desktop
- **⏰ Smart Scheduling**: Respects your quiet hours and preferences with variety logic
- **🔒 No Duplicates**: Sophisticated memory system ensures no repeated recommendations  
- **🛠️ Easy Setup**: Built for non-technical users with clear instructions and comprehensive error handling
- **🔧 Extensible**: Clean, modular architecture makes it easy to add new features

## 📈 Future Enhancements (Phase 2+)

Randy is currently in **Phase 1.5 COMPLETE** status with rich HTML emails, embedded images, and enhanced personality! Here's what's coming next:

- **☁️ Cloud Deployment**: AWS Lambda deployment for 100% reliability
- **🌤️ Weather Integration**: Weather-aware recommendations for outdoor activities  
- **📚 More Domains**: Books, local events, weekend getaways, and seasonal activities
- **💬 Feedback Learning**: Learning from your responses to improve recommendations
- **📱 Multi-Channel**: SMS notifications and other communication channels
- **⚙️ Advanced Personalization**: Configurable personality styles and preferences
- **📊 Analytics**: Engagement tracking and recommendation optimization
- **🔄 Continuous Learning**: Adaptive frequency and intelligent timing optimization

## 🤝 Contributing

This is a personal project, but feel free to fork and customize Randy for your own use! The modular architecture makes it easy to:

- Add new recommendation domains
- Customize Randy's personality
- Add new notification channels
- Enhance the scheduling logic

## 📄 License

This project is for personal use. Please respect the API terms of service for OpenAI, Google Places, and TMDB.

---

**Happy exploring with Randy! 🌀**
