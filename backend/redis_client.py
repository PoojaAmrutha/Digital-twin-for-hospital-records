# ============================================================================
# FILE: backend/redis_client.py
# Redis Cache Manager for Quick Data Access
# ============================================================================

import redis
import json
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()


class RedisClient:
    """
    Redis client for caching vital readings and alerts
    Provides fast access to frequently requested data
    """
    
    def __init__(self):
        """Initialize Redis connection"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        try:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            self.connected = True
            print("✅ Redis connected successfully")
        except redis.ConnectionError as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("    Continuing without Redis cache...")
            self.connected = False
            self.client = None
    
    def _is_available(self) -> bool:
        """Check if Redis is available"""
        return self.connected and self.client is not None
    
    # ========================================================================
    # VITALS CACHING
    # ========================================================================
    
    def set_latest_vitals(self, user_id: int, vitals: Dict, expiry: int = 3600):
        """
        Store latest vitals for quick access
        
        Args:
            user_id: User ID
            vitals: Dictionary containing vital measurements
            expiry: Cache expiry time in seconds (default: 1 hour)
        """
        if not self._is_available():
            return False
        
        try:
            key = f"vitals:user:{user_id}:latest"
            self.client.setex(key, expiry, json.dumps(vitals))
            return True
        except Exception as e:
            print(f"Redis error setting vitals: {e}")
            return False
    
    def get_latest_vitals(self, user_id: int) -> Optional[Dict]:
        """
        Get latest vitals from cache
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with vitals or None if not found
        """
        if not self._is_available():
            return None
        
        try:
            key = f"vitals:user:{user_id}:latest"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis error getting vitals: {e}")
            return None
    
    def set_vitals_history(self, user_id: int, vitals_list: List[Dict], expiry: int = 1800):
        """
        Cache recent vitals history
        
        Args:
            user_id: User ID
            vitals_list: List of vital readings
            expiry: Cache expiry in seconds (default: 30 minutes)
        """
        if not self._is_available():
            return False
        
        try:
            key = f"vitals:user:{user_id}:history"
            self.client.setex(key, expiry, json.dumps(vitals_list))
            return True
        except Exception as e:
            print(f"Redis error setting vitals history: {e}")
            return False
    
    def get_vitals_history(self, user_id: int) -> Optional[List[Dict]]:
        """Get cached vitals history"""
        if not self._is_available():
            return None
        
        try:
            key = f"vitals:user:{user_id}:history"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis error getting vitals history: {e}")
            return None
    
    # ========================================================================
    # ALERTS CACHING
    # ========================================================================
    
    def add_alert(self, user_id: int, alert: Dict):
        """
        Add alert to user's alert list (FIFO queue)
        
        Args:
            user_id: User ID
            alert: Alert dictionary
        """
        if not self._is_available():
            return False
        
        try:
            key = f"alerts:user:{user_id}"
            # Add to beginning of list
            self.client.lpush(key, json.dumps(alert))
            # Keep only last 100 alerts
            self.client.ltrim(key, 0, 99)
            # Set expiry to 24 hours
            self.client.expire(key, 86400)
            return True
        except Exception as e:
            print(f"Redis error adding alert: {e}")
            return False
    
    def get_alerts(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get recent alerts for user
        
        Args:
            user_id: User ID
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dictionaries
        """
        if not self._is_available():
            return []
        
        try:
            key = f"alerts:user:{user_id}"
            alerts_json = self.client.lrange(key, 0, limit - 1)
            return [json.loads(alert) for alert in alerts_json]
        except Exception as e:
            print(f"Redis error getting alerts: {e}")
            return []
    
    def clear_alerts(self, user_id: int):
        """Clear all alerts for user"""
        if not self._is_available():
            return False
        
        try:
            key = f"alerts:user:{user_id}"
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis error clearing alerts: {e}")
            return False
    
    # ========================================================================
    # HEALTH SCORE CACHING
    # ========================================================================
    
    def set_health_score(self, user_id: int, score_data: Dict, expiry: int = 1800):
        """
        Cache health score
        
        Args:
            user_id: User ID
            score_data: Health score dictionary
            expiry: Cache expiry in seconds (default: 30 minutes)
        """
        if not self._is_available():
            return False
        
        try:
            key = f"health_score:user:{user_id}"
            self.client.setex(key, expiry, json.dumps(score_data))
            return True
        except Exception as e:
            print(f"Redis error setting health score: {e}")
            return False
    
    def get_health_score(self, user_id: int) -> Optional[Dict]:
        """Get cached health score"""
        if not self._is_available():
            return None
        
        try:
            key = f"health_score:user:{user_id}"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis error getting health score: {e}")
            return None
    
    # ========================================================================
    # PATIENT LIST CACHING (for hospital dashboard)
    # ========================================================================
    
    def set_patient_list(self, patients: List[Dict], expiry: int = 60):
        """
        Cache patient list for hospital dashboard
        
        Args:
            patients: List of patient dictionaries
            expiry: Cache expiry in seconds (default: 1 minute)
        """
        if not self._is_available():
            return False
        
        try:
            key = "hospital:patients:list"
            self.client.setex(key, expiry, json.dumps(patients))
            return True
        except Exception as e:
            print(f"Redis error setting patient list: {e}")
            return False
    
    def get_patient_list(self) -> Optional[List[Dict]]:
        """Get cached patient list"""
        if not self._is_available():
            return None
        
        try:
            key = "hospital:patients:list"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis error getting patient list: {e}")
            return None
    
    # ========================================================================
    # STATISTICS CACHING
    # ========================================================================
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """
        Increment a statistic counter
        
        Args:
            stat_name: Name of the statistic
            amount: Amount to increment by
        """
        if not self._is_available():
            return False
        
        try:
            key = f"stats:{stat_name}"
            self.client.incrby(key, amount)
            return True
        except Exception as e:
            print(f"Redis error incrementing stat: {e}")
            return False
    
    def get_stat(self, stat_name: str) -> int:
        """Get a statistic value"""
        if not self._is_available():
            return 0
        
        try:
            key = f"stats:{stat_name}"
            value = self.client.get(key)
            return int(value) if value else 0
        except Exception as e:
            print(f"Redis error getting stat: {e}")
            return 0
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def clear_user_cache(self, user_id: int):
        """
        Clear all cached data for a specific user
        
        Args:
            user_id: User ID
        """
        if not self._is_available():
            return False
        
        try:
            keys_to_delete = [
                f"vitals:user:{user_id}:latest",
                f"vitals:user:{user_id}:history",
                f"alerts:user:{user_id}",
                f"health_score:user:{user_id}"
            ]
            self.client.delete(*keys_to_delete)
            return True
        except Exception as e:
            print(f"Redis error clearing user cache: {e}")
            return False
    
    def clear_all_cache(self):
        """Clear all cached data (use carefully!)"""
        if not self._is_available():
            return False
        
        try:
            self.client.flushdb()
            print("⚠️  All Redis cache cleared")
            return True
        except Exception as e:
            print(f"Redis error clearing all cache: {e}")
            return False
    
    def get_cache_info(self) -> Dict:
        """Get Redis cache information"""
        if not self._is_available():
            return {"status": "disconnected"}
        
        try:
            info = self.client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": self.client.dbsize(),
                "uptime_days": info.get("uptime_in_days")
            }
        except Exception as e:
            print(f"Redis error getting info: {e}")
            return {"status": "error", "error": str(e)}
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        if not self._is_available():
            return False
        
        try:
            return self.client.ping()
        except:
            return False


# Global Redis client instance
redis_client = RedisClient()


# Test function
if __name__ == "__main__":
    print("Testing Redis client...")
    
    # Test connection
    if redis_client.health_check():
        print("✅ Redis is healthy")
        
        # Test vitals caching
        test_vitals = {
            "heart_rate": 75,
            "spo2": 98,
            "temperature": 36.8,
            "stress_level": 2.0
        }
        
        redis_client.set_latest_vitals(1, test_vitals)
        cached = redis_client.get_latest_vitals(1)
        print(f"✅ Cached vitals: {cached}")
        
        # Test alert caching
        test_alert = {
            "type": "warning",
            "title": "Test Alert",
            "message": "This is a test"
        }
        
        redis_client.add_alert(1, test_alert)
        alerts = redis_client.get_alerts(1)
        print(f"✅ Cached alerts: {len(alerts)} alert(s)")
        
        # Get cache info
        info = redis_client.get_cache_info()
        print(f"✅ Cache info: {info}")
    else:
        print("❌ Redis is not available")