"""
Scheduling logic for Randy's recommendations.
Handles timing, cadence, and quiet hours.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.settings import settings

class RecommendationScheduler:
    """Manages timing and scheduling for recommendations."""
    
    def __init__(self, schedule_file: str = "data/schedule.json"):
        self.schedule_file = schedule_file
        self._ensure_data_directory()
        self.schedule_data = self._load_schedule()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.schedule_file), exist_ok=True)
    
    def _load_schedule(self) -> Dict[str, Any]:
        """Load schedule data from JSON file."""
        if not os.path.exists(self.schedule_file):
            return {
                "last_recommendation_date": None,
                "last_recommendation_timestamp": None,
                "next_recommendation_due": None
            }
        
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "last_recommendation_date": None,
                "last_recommendation_timestamp": None,
                "next_recommendation_due": None
            }
    
    def _save_schedule(self):
        """Save schedule data to JSON file."""
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save schedule data: {e}")
    
    def is_in_quiet_hours(self, check_time: Optional[datetime] = None) -> bool:
        """
        Check if the current time is within quiet hours.
        
        Args:
            check_time: Time to check (defaults to now)
        
        Returns:
            True if in quiet hours
        """
        if check_time is None:
            check_time = datetime.now()
        
        current_hour = check_time.hour
        start_hour = settings.QUIET_HOURS_START
        end_hour = settings.QUIET_HOURS_END
        
        # Handle quiet hours that span midnight
        if start_hour > end_hour:
            # Quiet hours span midnight (e.g., 23:00 to 7:00)
            return current_hour >= start_hour or current_hour < end_hour
        else:
            # Quiet hours don't span midnight
            return start_hour <= current_hour < end_hour
    
    def is_recommendation_due(self) -> bool:
        """
        Check if a recommendation is due based on cadence.
        
        Returns:
            True if recommendation is due
        """
        last_timestamp = self.schedule_data.get("last_recommendation_timestamp")
        
        # If no previous recommendation, it's due
        if not last_timestamp:
            return True
        
        # Check if enough time has passed
        last_time = datetime.fromtimestamp(last_timestamp)
        time_since_last = datetime.now() - last_time
        cadence_delta = timedelta(days=settings.RECOMMENDATION_CADENCE_DAYS)
        
        return time_since_last >= cadence_delta
    
    def should_send_recommendation(self) -> tuple[bool, str]:
        """
        Determine if a recommendation should be sent now.
        
        Returns:
            Tuple of (should_send, reason)
        """
        # Check if recommendation is due
        if not self.is_recommendation_due():
            last_date = self.schedule_data.get("last_recommendation_date", "unknown")
            days_left = self._days_until_next_recommendation()
            return False, f"Not due yet. Last sent: {last_date}. Next due in {days_left} days."
        
        # Check quiet hours
        if self.is_in_quiet_hours():
            current_time = datetime.now().strftime("%H:%M")
            return False, f"In quiet hours ({settings.QUIET_HOURS_START}:00-{settings.QUIET_HOURS_END}:00). Current time: {current_time}"
        
        return True, "Ready to send recommendation!"
    
    def _days_until_next_recommendation(self) -> int:
        """Calculate days until next recommendation is due."""
        last_timestamp = self.schedule_data.get("last_recommendation_timestamp")
        if not last_timestamp:
            return 0
        
        last_time = datetime.fromtimestamp(last_timestamp)
        next_due = last_time + timedelta(days=settings.RECOMMENDATION_CADENCE_DAYS)
        days_left = (next_due - datetime.now()).days
        
        return max(0, days_left)
    
    def mark_recommendation_sent(self):
        """Mark that a recommendation has been sent."""
        now = datetime.now()
        self.schedule_data.update({
            "last_recommendation_date": now.isoformat(),
            "last_recommendation_timestamp": now.timestamp(),
            "next_recommendation_due": (now + timedelta(days=settings.RECOMMENDATION_CADENCE_DAYS)).isoformat()
        })
        self._save_schedule()
    
    def get_next_recommendation_time(self) -> Optional[datetime]:
        """
        Get the next time a recommendation should be sent.
        
        Returns:
            Next recommendation datetime or None if no previous recommendation
        """
        last_timestamp = self.schedule_data.get("last_recommendation_timestamp")
        if not last_timestamp:
            return None
        
        last_time = datetime.fromtimestamp(last_timestamp)
        return last_time + timedelta(days=settings.RECOMMENDATION_CADENCE_DAYS)
    
    def get_schedule_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current schedule status.
        
        Returns:
            Dictionary with schedule information
        """
        now = datetime.now()
        next_time = self.get_next_recommendation_time()
        should_send, reason = self.should_send_recommendation()
        
        return {
            "current_time": now.isoformat(),
            "is_quiet_hours": self.is_in_quiet_hours(),
            "quiet_hours_range": f"{settings.QUIET_HOURS_START}:00-{settings.QUIET_HOURS_END}:00",
            "is_due": self.is_recommendation_due(),
            "should_send": should_send,
            "reason": reason,
            "last_recommendation": self.schedule_data.get("last_recommendation_date"),
            "next_recommendation_due": next_time.isoformat() if next_time else "Not scheduled",
            "cadence_days": settings.RECOMMENDATION_CADENCE_DAYS
        }

# Global scheduler instance
scheduler = RecommendationScheduler() 