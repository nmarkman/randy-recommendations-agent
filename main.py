#!/usr/bin/env python3
"""
Randy - Autonomous Recommendation Agent
Main orchestrator that coordinates timing, recommendations, and memory.
"""
import sys
import asyncio
from datetime import datetime
from agents import Runner, set_default_openai_key

# Import Randy's components
from config.settings import settings
from src.core.randy_agent import randy
from src.scheduler.timing import scheduler
from src.memory.recommendation_history import memory

def setup_logging():
    """Set up basic logging."""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data/randy.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('Randy')

async def run_randy_recommendation():
    """
    Run Randy to generate and send a recommendation.
    
    Returns:
        Tuple of (success, message)
    """
    logger = setup_logging()
    
    try:
        # Create context-aware prompt
        prompt = randy.create_context_prompt()
        logger.info(f"Generated context prompt: {prompt}")
        
        # Run Randy agent
        logger.info("Starting Randy agent...")
        result = await Runner.run(randy.agent, prompt)
        
        if result and result.final_output:
            logger.info("Randy completed successfully!")
            logger.info(f"Randy's response: {result.final_output}")
            
            # Extract recommendation details for memory storage
            try:
                name, rec_type = randy.extract_recommendation_details(result.final_output)
                success = memory.add_recommendation(rec_type, name, result.final_output)
                if success:
                    logger.info(f"Saved {rec_type} recommendation '{name}' to memory")
                else:
                    logger.warning(f"Failed to save recommendation to memory (might be duplicate)")
            except Exception as e:
                logger.warning(f"Could not save recommendation to memory: {e}")
            
            # Mark recommendation as sent in scheduler
            scheduler.mark_recommendation_sent()
            logger.info("Marked recommendation as sent in scheduler")
            
            return True, result.final_output
        else:
            logger.error("Randy didn't generate a proper response")
            return False, "Randy didn't generate a response"
            
    except Exception as e:
        logger.error(f"Error running Randy: {str(e)}")
        return False, f"Error: {str(e)}"

def check_configuration():
    """
    Validate that all required configuration is present.
    
    Returns:
        Tuple of (valid, message)
    """
    try:
        # Validate settings
        settings.validate()
        
        # Set OpenAI API key
        set_default_openai_key(settings.OPENAI_API_KEY)
        
        return True, "Configuration valid"
        
    except ValueError as e:
        return False, f"Configuration error: {str(e)}"
    except Exception as e:
        return False, f"Setup error: {str(e)}"

def print_status():
    """Print current system status."""
    print("\n" + "="*60)
    print("🌀 RANDY RECOMMENDATION AGENT STATUS")
    print("="*60)
    
    # Configuration status
    config_valid, config_msg = check_configuration()
    print(f"Configuration: {'✅' if config_valid else '❌'} {config_msg}")
    
    # Schedule status
    schedule_info = scheduler.get_schedule_summary()
    print(f"\nSchedule Status:")
    print(f"  Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Quiet Hours: {schedule_info['quiet_hours_range']}")
    print(f"  In Quiet Hours: {'Yes' if schedule_info['is_quiet_hours'] else 'No'}")
    print(f"  Recommendation Due: {'Yes' if schedule_info['is_due'] else 'No'}")
    print(f"  Should Send: {'✅' if schedule_info['should_send'] else '❌'}")
    print(f"  Reason: {schedule_info['reason']}")
    print(f"  Last Sent: {schedule_info['last_recommendation'] or 'Never'}")
    print(f"  Next Due: {schedule_info['next_recommendation_due']}")
    
    # Memory status
    memory_info = memory.get_memory_summary()
    print(f"\nMemory Status:")
    print(f"  Total Recommendations: {memory_info['total_recommendations']}")
    print(f"  Recent (7 days): {memory_info['recent_recommendations_count']}")
    if memory_info['recommendations_by_type']:
        print(f"  By Type: {memory_info['recommendations_by_type']}")
    
    print("="*60)

async def main():
    """Main entry point."""
    logger = setup_logging()
    
    # Check if this is a status check
    if len(sys.argv) > 1 and sys.argv[1] in ['status', '--status', '-s']:
        print_status()
        return
    
    # Check if this is a force run
    force_run = len(sys.argv) > 1 and sys.argv[1] in ['force', '--force', '-f']
    
    print("\n🌀 Randy Recommendation Agent Starting...")
    
    # Validate configuration
    config_valid, config_msg = check_configuration()
    if not config_valid:
        print(f"❌ {config_msg}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        print("Copy env.example to .env and fill in your API keys.")
        sys.exit(1)
    
    print(f"✅ {config_msg}")
    
    # Check timing (unless forced)
    if not force_run:
        should_send, reason = scheduler.should_send_recommendation()
        if not should_send:
            print(f"⏰ {reason}")
            print("\nUse 'python main.py force' to send anyway, or 'python main.py status' to check status.")
            return
    
    print("🎯 Ready to send recommendation!")
    
    # Run Randy
    success, message = await run_randy_recommendation()
    
    if success:
        print("✅ Randy successfully sent a recommendation!")
        print(f"📧 Check your email: {settings.RECIPIENT_EMAIL}")
        
        # Show updated status
        print("\n📊 Updated Status:")
        schedule_info = scheduler.get_schedule_summary()
        print(f"  Next recommendation due: {schedule_info['next_recommendation_due']}")
        
    else:
        print(f"❌ Randy failed: {message}")
        sys.exit(1)

def sync_main():
    """Synchronous wrapper for main."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Randy interrupted. Goodbye!")
    except Exception as e:
        print(f"💥 Randy crashed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    sync_main() 