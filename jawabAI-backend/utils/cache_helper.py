import hashlib
import json
from typing import Optional
from storage.redis_client import redis_client

class CacheHelper:
    """
    Helper class for caching PDF processing and query responses
    
    Cache Strategy:
    1. PDF Cache: Hash PDF content to check if already processed
    2. Query Cache: Hash (PDF + Query) to cache responses
    """
    
    def __init__(self):
        self.redis = redis_client
    
    def get_file_hash(self, file_content: bytes) -> str:
        """
        Generate SHA256 hash of PDF file content
        This ensures same PDF = same hash
        """
        return hashlib.sha256(file_content).hexdigest()
    
    def get_query_cache_key(self, document_id: str, query: str) -> str:
        """
        Generate cache key for query responses
        Format: query:{document_id}:{query_hash}
        """
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        return f"query:{document_id}:{query_hash}"
    
    def cache_pdf_mapping(self, file_hash: str, document_id: str, use_case: str, ttl: int = 86400):
        """
        Cache the mapping between file hash and document_id per use_case
        TTL: 24 hours (86400 seconds)
        
        This prevents re-processing the same PDF for the same use_case
        """
        key = f"pdf:hash:{use_case}:{file_hash}"
        self.redis.setex(key, ttl, document_id)
        print(f"✅ Cached PDF mapping for {use_case}: {file_hash[:16]}... -> {document_id}")
    
    def get_cached_document_id(self, file_hash: str, use_case: str) -> Optional[str]:
        """
        Check if this PDF was already processed for this use_case
        Returns document_id if found, None otherwise
        """
        key = f"pdf:hash:{use_case}:{file_hash}"
        cached_id = self.redis.get(key)
        if cached_id:
            print(f"🎯 Cache HIT for {use_case}: PDF already processed as {cached_id}")
        return cached_id
    
    def cache_query_response(self, document_id: str, query: str, response: dict, ttl: int = 3600):
        """
        Cache query response for 1 hour (3600 seconds)
        
        This speeds up repeated queries on same document
        """
        key = self.get_query_cache_key(document_id, query)
        self.redis.setex(key, ttl, json.dumps(response))
        print(f"✅ Cached query response: {key}")
    
    def get_cached_query_response(self, document_id: str, query: str) -> Optional[dict]:
        """
        Retrieve cached query response
        Returns cached response if found, None otherwise
        """
        key = self.get_query_cache_key(document_id, query)
        cached = self.redis.get(key)
        if cached:
            print(f"🎯 Cache HIT: Query response found")
            return json.loads(cached)
        return None

# Global instance
cache_helper = CacheHelper()
