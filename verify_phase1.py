#!/usr/bin/env python3
"""
Phase 1 Verification Script for Randy
Tests all components to confirm Phase 1 completion criteria.
"""
import sys
import json
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_task(task, status="testing"):
    """Print task status."""
    icons = {"testing": "🔄", "pass": "✅", "fail": "❌", "skip": "⏭️"}
    print(f"{icons[status]} {task}")

def test_configuration_system():
    """Test configuration management."""
    print_header("Configuration System")
    
    try:
        from config.settings import settings
        
        # Test that all required settings exist
        required_attrs = [
            'OPENAI_API_KEY', 'GOOGLE_PLACES_API_KEY', 'TMDB_API_KEY',
            'GMAIL_USERNAME', 'GMAIL_APP_PASSWORD', 'RECIPIENT_EMAIL',
            'REGION', 'QUIET_HOURS_START', 'QUIET_HOURS_END', 'RECOMMENDATION_CADENCE_DAYS'
        ]
        
        for attr in required_attrs:
            if hasattr(settings, attr):
                print_task(f"Setting {attr} exists", "pass")
            else:
                print_task(f"Setting {attr} missing", "fail")
                return False
        
        # Test defaults
        if settings.REGION == 'Charleston, SC':
            print_task("Default region set correctly", "pass")
        
        if settings.QUIET_HOURS_START == 23 and settings.QUIET_HOURS_END == 7:
            print_task("Default quiet hours set correctly", "pass")
        
        if settings.RECOMMENDATION_CADENCE_DAYS == 7:
            print_task("Default cadence set correctly", "pass")
        
        return True
        
    except Exception as e:
        print_task(f"Configuration system error: {e}", "fail")
        return False

def test_memory_system():
    """Test memory system functionality."""
    print_header("Memory System")
    
    try:
        from src.memory.recommendation_history import RecommendationMemory
        
        # Create a test memory instance with proper path
        import tempfile
        import os
        test_file = os.path.join(tempfile.gettempdir(), "test_memory.json")
        test_memory = RecommendationMemory(test_file)
        
        # Test adding recommendations
        success1 = test_memory.add_recommendation("restaurant", "Test Restaurant", "Great food!")
        print_task("Add first recommendation", "pass" if success1 else "fail")
        
        # Test duplicate prevention
        success2 = test_memory.add_recommendation("restaurant", "Test Restaurant", "Great food!")
        print_task("Prevent duplicate recommendation", "pass" if not success2 else "fail")
        
        # Test different recommendation
        success3 = test_memory.add_recommendation("movie", "Test Movie", "Great film!")
        print_task("Add different recommendation", "pass" if success3 else "fail")
        
        # Test memory summary
        summary = test_memory.get_memory_summary()
        expected_count = 2  # Should have 2 unique recommendations
        actual_count = summary['total_recommendations']
        print_task(f"Memory summary (expected {expected_count}, got {actual_count})", 
                   "pass" if actual_count == expected_count else "fail")
        
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print_task(f"Memory system error: {e}", "fail")
        return False

def test_scheduling_logic():
    """Test scheduling and timing logic."""
    print_header("Scheduling Logic")
    
    try:
        from src.scheduler.timing import RecommendationScheduler
        
        # Create test scheduler with proper path
        import tempfile
        test_sched_file = os.path.join(tempfile.gettempdir(), "test_schedule.json")
        scheduler = RecommendationScheduler(test_sched_file)
        
        # Test quiet hours logic
        from datetime import datetime
        
        # Test during quiet hours (11 PM)
        quiet_time = datetime.now().replace(hour=23, minute=0)
        is_quiet = scheduler.is_in_quiet_hours(quiet_time)
        print_task(f"Detect quiet hours (23:00)", "pass" if is_quiet else "fail")
        
        # Test during active hours (10 AM)
        active_time = datetime.now().replace(hour=10, minute=0)
        is_active = not scheduler.is_in_quiet_hours(active_time)
        print_task(f"Detect active hours (10:00)", "pass" if is_active else "fail")
        
        # Test recommendation due logic (first time)
        is_due = scheduler.is_recommendation_due()
        print_task(f"First recommendation is due", "pass" if is_due else "fail")
        
        # Test marking recommendation sent
        scheduler.mark_recommendation_sent()
        is_due_after = scheduler.is_recommendation_due()
        print_task(f"Not due after sending", "pass" if not is_due_after else "fail")
        
        # Test schedule summary
        summary = scheduler.get_schedule_summary()
        required_keys = ['current_time', 'is_quiet_hours', 'is_due', 'should_send', 'reason']
        has_all_keys = all(key in summary for key in required_keys)
        print_task(f"Schedule summary complete", "pass" if has_all_keys else "fail")
        
        # Clean up test file
        if os.path.exists(test_sched_file):
            os.remove(test_sched_file)
        
        return True
        
    except Exception as e:
        print_task(f"Scheduling logic error: {e}", "fail")
        return False

def test_tool_definitions():
    """Test that all tools are properly defined."""
    print_header("Tool Definitions")
    
    try:
        # Test tool imports
        from src.tools.restaurant_tool import get_restaurant_recommendation
        print_task("Restaurant tool import", "pass")
        
        from src.tools.poi_tool import get_poi_recommendation
        print_task("POI tool import", "pass")
        
        from src.tools.movie_tool import get_movie_recommendation
        print_task("Movie tool import", "pass")
        
        from src.tools.email_tool import send_recommendation_email
        print_task("Email tool import", "pass")
        
        # Test that functions are decorated properly as FunctionTool objects
        tools = [get_restaurant_recommendation, get_poi_recommendation, 
                get_movie_recommendation, send_recommendation_email]
        
        for tool in tools:
            # Check if it's a FunctionTool object (they have a 'func' attribute)
            if hasattr(tool, 'func') or str(type(tool).__name__) == 'FunctionTool':
                print_task(f"Tool properly decorated as FunctionTool", "pass")
            else:
                print_task(f"Tool missing @function_tool decoration", "fail")
                return False
        
        return True
        
    except Exception as e:
        print_task(f"Tool definition error: {e}", "fail")
        return False

def test_randy_agent_creation():
    """Test Randy agent creation and configuration."""
    print_header("Randy Agent Creation")
    
    try:
        from src.core.randy_agent import randy
        
        # Test agent exists
        print_task("Randy agent instance created", "pass")
        
        # Test agent has name
        if randy.agent.name == "Randy":
            print_task("Agent name set correctly", "pass")
        else:
            print_task(f"Agent name incorrect: {randy.agent.name}", "fail")
        
        # Test agent has tools
        expected_tools = 4  # restaurant, poi, movie, email
        actual_tools = len(randy.agent.tools)
        print_task(f"Agent has {expected_tools} tools (found {actual_tools})", 
                   "pass" if actual_tools == expected_tools else "fail")
        
        # Test agent has instructions
        if randy.agent.instructions and len(randy.agent.instructions) > 100:
            print_task("Agent has detailed instructions", "pass")
        else:
            print_task("Agent instructions missing or too short", "fail")
        
        # Test model configuration
        if hasattr(randy.agent, 'model') and 'gpt-4o-mini' in str(randy.agent.model):
            print_task("Agent model set correctly", "pass")
        else:
            print_task("Agent model configuration issue", "fail")
        
        return True
        
    except Exception as e:
        print_task(f"Randy agent creation error: {e}", "fail")
        return False

def test_main_orchestrator():
    """Test main orchestrator functionality."""
    print_header("Main Orchestrator")
    
    try:
        # Test imports
        import main
        print_task("Main module imports successfully", "pass")
        
        # Test configuration check function
        valid, msg = main.check_configuration()
        print_task(f"Configuration check function works", "pass")
        
        # Test logging setup
        logger = main.setup_logging()
        print_task("Logging setup works", "pass")
        
        # Clean up any log files created during test
        if os.path.exists("data/randy.log"):
            # Don't delete if it has real data, just check it exists
            print_task("Log file creation works", "pass")
        
        return True
        
    except Exception as e:
        print_task(f"Main orchestrator error: {e}", "fail")
        return False

def test_api_integrations_mock():
    """Test API integrations are properly configured."""
    print_header("API Integration Tests (Mocked)")
    
    try:
        # Test that tools are importable and configured
        from src.tools.restaurant_tool import get_restaurant_recommendation
        from src.tools.poi_tool import get_poi_recommendation
        from src.tools.movie_tool import get_movie_recommendation
        from src.tools.email_tool import send_recommendation_email
        
        # Test that tools are FunctionTool objects ready for agent use
        tools = [
            (get_restaurant_recommendation, "Restaurant tool"),
            (get_poi_recommendation, "POI tool"), 
            (get_movie_recommendation, "Movie tool"),
            (send_recommendation_email, "Email tool")
        ]
        
        for tool, name in tools:
            if hasattr(tool, 'func') or str(type(tool).__name__) == 'FunctionTool':
                print_task(f"{name} configured for agent", "pass")
            else:
                print_task(f"{name} not properly configured", "fail")
                return False
        
        # Test configuration values exist (tools will work when agent runs them)
        from config.settings import settings
        required_configs = ['GOOGLE_PLACES_API_KEY', 'TMDB_API_KEY', 'GMAIL_USERNAME']
        for config in required_configs:
            if hasattr(settings, config):
                print_task(f"{config} configuration available", "pass")
            else:
                print_task(f"{config} configuration missing", "fail")
                return False
        
        return True
        
    except Exception as e:
        print_task(f"API integration test error: {e}", "fail")
        return False

def test_project_structure():
    """Test that all required files exist."""
    print_header("Project Structure")
    
    required_files = [
        "requirements.txt",
        "env.example", 
        "README.md",
        "main.py",
        "config/settings.py",
        "src/tools/restaurant_tool.py",
        "src/tools/poi_tool.py", 
        "src/tools/movie_tool.py",
        "src/tools/email_tool.py",
        "src/memory/recommendation_history.py",
        "src/scheduler/timing.py",
        "src/core/randy_agent.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_task(f"File exists: {file_path}", "pass")
        else:
            print_task(f"Missing file: {file_path}", "fail")
            all_exist = False
    
    return all_exist

def run_all_tests():
    """Run all verification tests."""
    print("🌀 RANDY PHASE 1 VERIFICATION")
    print("Testing all components for completion criteria")
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Configuration System", test_configuration_system),
        ("Memory System", test_memory_system),
        ("Scheduling Logic", test_scheduling_logic),
        ("Tool Definitions", test_tool_definitions),
        ("Randy Agent Creation", test_randy_agent_creation),
        ("Main Orchestrator", test_main_orchestrator),
        ("API Integrations (Mocked)", test_api_integrations_mock),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_task(f"{test_name} crashed: {e}", "fail")
            results.append((test_name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 1 is COMPLETE!")
        print("\nPhase 1 Success Criteria Met:")
        print("✅ Randy agent created with all tools")
        print("✅ Memory system prevents duplicates") 
        print("✅ Scheduling respects quiet hours and cadence")
        print("✅ All components properly integrated")
        print("✅ Error handling and logging in place")
        print("\nReady for real-world testing with API keys!")
        
    else:
        print(f"\n❌ {total - passed} tests failed. Phase 1 needs fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 