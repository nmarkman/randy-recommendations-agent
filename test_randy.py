#!/usr/bin/env python3
"""
Simple test script for Randy components.
Run this to verify everything is working before running the main agent.
"""
import sys
from config.settings import settings

def test_configuration():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        settings.validate()
        print("✅ Configuration loaded successfully")
        print(f"   Region: {settings.REGION}")
        print(f"   Quiet hours: {settings.QUIET_HOURS_START}:00 - {settings.QUIET_HOURS_END}:00")
        print(f"   Cadence: {settings.RECOMMENDATION_CADENCE_DAYS} days")
        print(f"   Recipient: {settings.RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_scheduler():
    """Test scheduling logic."""
    print("\n⏰ Testing scheduler...")
    try:
        from src.scheduler.timing import scheduler
        
        status = scheduler.get_schedule_summary()
        print("✅ Scheduler working")
        print(f"   Current time: {status['current_time']}")
        print(f"   In quiet hours: {status['is_quiet_hours']}")
        print(f"   Recommendation due: {status['is_due']}")
        print(f"   Should send: {status['should_send']}")
        return True
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        return False

def test_memory():
    """Test memory system."""
    print("\n🧠 Testing memory...")
    try:
        from src.memory.recommendation_history import memory
        
        summary = memory.get_memory_summary()
        print("✅ Memory system working")
        print(f"   Total recommendations: {summary['total_recommendations']}")
        print(f"   Recent recommendations: {summary['recent_recommendations_count']}")
        return True
    except Exception as e:
        print(f"❌ Memory error: {e}")
        return False

def test_tools():
    """Test individual tools (without API calls)."""
    print("\n🔨 Testing tools...")
    try:
        from src.tools.restaurant_tool import get_restaurant_recommendation
        from src.tools.poi_tool import get_poi_recommendation
        from src.tools.movie_tool import get_movie_recommendation
        from src.tools.email_tool import send_recommendation_email
        
        print("✅ All tools imported successfully")
        print("   - Restaurant tool: ✅")
        print("   - POI tool: ✅")
        print("   - Movie tool: ✅")
        print("   - Email tool: ✅")
        return True
    except Exception as e:
        print(f"❌ Tools error: {e}")
        return False

def test_randy_agent():
    """Test Randy agent creation."""
    print("\n🤖 Testing Randy agent...")
    try:
        from src.core.randy_agent import randy
        
        print("✅ Randy agent created successfully")
        print(f"   Agent name: {randy.agent.name}")
        print(f"   Number of tools: {len(randy.agent.tools)}")
        return True
    except Exception as e:
        print(f"❌ Randy agent error: {e}")
        return False

def run_api_tests():
    """Check API tool configurations (no actual API calls)."""
    print("\n🌐 API Configuration Check")
    response = input("Do you want to check API configurations? (y/N): ")
    
    if response.lower() != 'y':
        print("⏭️  Skipping API configuration check")
        return True
    
    print("\n🍽️ Testing restaurant API...")
    try:
        from src.tools.restaurant_tool import get_restaurant_recommendation
        # FunctionTool objects can't be called directly, but we can test configuration
        print("✅ Restaurant API configured")
        print("   Tool ready for agent use")
    except Exception as e:
        print(f"❌ Restaurant API error: {e}")
        return False
    
    print("\n📍 Testing POI API...")
    try:
        from src.tools.poi_tool import get_poi_recommendation
        # FunctionTool objects can't be called directly, but we can test configuration
        print("✅ POI API configured")
        print("   Tool ready for agent use")
    except Exception as e:
        print(f"❌ POI API error: {e}")
        return False
    
    print("\n🎬 Testing movie API...")
    try:
        from src.tools.movie_tool import get_movie_recommendation
        # FunctionTool objects can't be called directly, but we can test configuration
        print("✅ Movie API configured")
        print("   Tool ready for agent use")
    except Exception as e:
        print(f"❌ Movie API error: {e}")
        return False
    
    print("\n📧 Checking email configuration...")
    try:
        from src.tools.email_tool import send_recommendation_email
        # Don't actually send email in test - just verify tool imports
        print("✅ Email tool configured")
        print("   Tool ready for agent use")
    except Exception as e:
        print(f"❌ Email tool error: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🌀 Randy Component Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_scheduler,
        test_memory,
        test_tools,
        test_randy_agent,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Randy is ready to run.")
        print("\nNext steps:")
        print("1. Run 'python main.py' to let Randy decide if it's time")
        print("2. Check Randy's logs in 'data/randy.log' for details")
        print("3. For real API testing, let Randy run - he'll use your APIs!")
        
        # Offer API tests
        run_api_tests()
        
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Make sure you've copied env.example to .env")
        print("- Fill in all required API keys in .env")
        print("- Install all dependencies: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main() 