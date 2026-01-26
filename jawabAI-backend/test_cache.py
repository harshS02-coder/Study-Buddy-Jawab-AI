"""
Test script to verify caching functionality
Run this after starting the server to test caching behavior
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_pdf_cache():
    """Test PDF caching by uploading same file twice"""
    print("\n" + "="*60)
    print("🧪 TEST 1: PDF Caching")
    print("="*60)
    
    # First upload
    print("\n1️⃣ First upload (should process)...")
    with open("test.pdf", "rb") as f:
        files = {"file": ("test.pdf", f, "application/pdf")}
        data = {"use_case": "study"}
        
        start = time.time()
        response1 = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        time1 = time.time() - start
        
        result1 = response1.json()
        print(f"   ⏱️  Time: {time1:.2f}s")
        print(f"   📋 Document ID: {result1['document_id']}")
        print(f"   📊 Status: {result1['status']}")
        print(f"   💾 Cached: {result1.get('cached', False)}")
    
    # Wait for processing
    time.sleep(5)
    
    # Second upload (same file)
    print("\n2️⃣ Second upload (should use cache)...")
    with open("test.pdf", "rb") as f:
        files = {"file": ("test.pdf", f, "application/pdf")}
        data = {"use_case": "study"}
        
        start = time.time()
        response2 = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        time2 = time.time() - start
        
        result2 = response2.json()
        print(f"   ⏱️  Time: {time2:.2f}s")
        print(f"   📋 Document ID: {result2['document_id']}")
        print(f"   📊 Status: {result2['status']}")
        print(f"   💾 Cached: {result2.get('cached', False)}")
    
    # Compare
    print("\n📊 RESULTS:")
    print(f"   Same document_id: {result1['document_id'] == result2['document_id']}")
    print(f"   Cache used: {result2.get('cached', False)}")
    print(f"   Time saved: {time1 - time2:.2f}s ({((time1-time2)/time1*100):.0f}% faster)")

def test_query_cache(document_id: str):
    """Test query caching by asking same question twice"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Query Caching")
    print("="*60)
    
    question = "What is the main topic of this document?"
    
    # First query
    print(f"\n1️⃣ First query: '{question}'")
    payload1 = {
        "document_id": document_id,
        "question": question,
        "use_case": "study"
    }
    
    start = time.time()
    response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
    time1 = time.time() - start
    
    result1 = response1.json()
    print(f"   ⏱️  Time: {time1:.2f}s")
    print(f"   ✅ Answer length: {len(result1.get('answer', ''))} chars")
    print(f"   💾 Cached: {result1.get('cached', False)}")
    
    # Second query (same question)
    print(f"\n2️⃣ Second query (same question)...")
    start = time.time()
    response2 = requests.post(f"{BASE_URL}/chat", json=payload1)
    time2 = time.time() - start
    
    result2 = response2.json()
    print(f"   ⏱️  Time: {time2:.2f}s")
    print(f"   ✅ Answer length: {len(result2.get('answer', ''))} chars")
    print(f"   💾 Cached: {result2.get('cached', False)}")
    
    # Compare
    print("\n📊 RESULTS:")
    print(f"   Same answer: {result1.get('answer') == result2.get('answer')}")
    print(f"   Cache used: {result2.get('cached', False)}")
    print(f"   Time saved: {time1 - time2:.2f}s ({((time1-time2)/time1*100):.0f}% faster)")
    
    # Third query (different question)
    print(f"\n3️⃣ Third query (different question)...")
    payload2 = {
        "document_id": document_id,
        "question": "What are the key points?",
        "use_case": "study"
    }
    
    start = time.time()
    response3 = requests.post(f"{BASE_URL}/chat", json=payload2)
    time3 = time.time() - start
    
    result3 = response3.json()
    print(f"   ⏱️  Time: {time3:.2f}s")
    print(f"   ✅ Answer length: {len(result3.get('answer', ''))} chars")
    print(f"   💾 Cached: {result3.get('cached', False)}")

if __name__ == "__main__":
    print("\n🚀 Starting Cache Tests...")
    print("Make sure:")
    print("  1. Server is running (uvicorn app:app --reload)")
    print("  2. You have a test.pdf file in this directory")
    
    try:
        # Test PDF caching
        test_pdf_cache()
        
        # Get document_id from a valid upload
        # (In real test, you'd use the one from test_pdf_cache)
        doc_id = input("\n\n📝 Enter document_id to test query cache: ")
        
        if doc_id:
            test_query_cache(doc_id)
        
        print("\n\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the server is running!")
