"""
Memory system for tracking Randy's recommendation history.
Simple JSON-based storage to avoid duplicate recommendations.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class RecommendationMemory:
    """Simple memory system for tracking recommendations."""
    
    def __init__(self, memory_file: str = "data/recommendation_history.json"):
        self.memory_file = memory_file
        self._ensure_data_directory()
        self.history = self._load_history()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load recommendation history from JSON file."""
        if not os.path.exists(self.memory_file):
            return []
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history(self):
        """Save recommendation history to JSON file."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save recommendation history: {e}")
    
    def add_recommendation(self, recommendation_type: str, name: str, details: str) -> bool:
        """
        Add a new recommendation to history.
        
        Args:
            recommendation_type: Type of recommendation (restaurant, poi, movie)
            name: Name/title of the recommendation
            details: Full details of the recommendation
        
        Returns:
            True if added successfully
        """
        # Create a simple key for duplicate checking
        recommendation_key = f"{recommendation_type}:{name.lower()}"
        
        # Check if already recommended
        if self.has_been_recommended(recommendation_key):
            return False
        
        # Add to history
        recommendation_entry = {
            "type": recommendation_type,
            "name": name,
            "key": recommendation_key,
            "details": details,
            "date": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp()
        }
        
        self.history.append(recommendation_entry)
        self._save_history()
        return True
    
    def has_been_recommended(self, recommendation_key: str) -> bool:
        """
        Check if a recommendation has already been made.
        
        Args:
            recommendation_key: The key to check (format: "type:name")
        
        Returns:
            True if already recommended
        """
        return any(entry.get("key") == recommendation_key for entry in self.history)
    
    def get_recent_recommendations(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recommendations from the last N days.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of recent recommendations
        """
        cutoff_timestamp = datetime.now().timestamp() - (days * 24 * 60 * 60)
        return [
            entry for entry in self.history 
            if entry.get("timestamp", 0) > cutoff_timestamp
        ]
    
    def get_recommendations_by_type(self, recommendation_type: str) -> List[Dict[str, Any]]:
        """
        Get all recommendations of a specific type.
        
        Args:
            recommendation_type: Type to filter by (restaurant, poi, movie)
        
        Returns:
            List of recommendations of the specified type
        """
        return [
            entry for entry in self.history 
            if entry.get("type") == recommendation_type
        ]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the recommendation memory.
        
        Returns:
            Dictionary with memory statistics
        """
        total_recommendations = len(self.history)
        
        # Count by type
        type_counts = {}
        for entry in self.history:
            entry_type = entry.get("type", "unknown")
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        
        # Recent activity
        recent = self.get_recent_recommendations(7)
        
        return {
            "total_recommendations": total_recommendations,
            "recommendations_by_type": type_counts,
            "recent_recommendations_count": len(recent),
            "last_recommendation_date": self.history[-1].get("date") if self.history else None
        }
    
    def clear_old_recommendations(self, days: int = 365):
        """
        Clear recommendations older than specified days.
        
        Args:
            days: Number of days to keep recommendations
        """
        cutoff_timestamp = datetime.now().timestamp() - (days * 24 * 60 * 60)
        self.history = [
            entry for entry in self.history 
            if entry.get("timestamp", 0) > cutoff_timestamp
        ]
        self._save_history()

# Global memory instance
memory = RecommendationMemory() 