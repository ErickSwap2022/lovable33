#!/usr/bin/env python3
"""
Multiple Claude Requests Test
Tests multiple concurrent requests to identify intermittent issues
"""

import requests
import json
import uuid
import time
import sys
import concurrent.futures
import threading

# Get backend URL from frontend .env
BACKEND_URL = "https://devsage-2.preview.emergentagent.com/api"

class MultipleClaudeTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.results = []
        self.lock = threading.Lock()
        
    def single_request_test(self, test_id):
        """Single request test"""
        session = requests.Session()
        test_session_id = str(uuid.uuid4())
        
        data = {
            "prompt": f"create a simple counter app - test {test_id}",
            "session_id": test_session_id
        }
        
        try:
            response = session.post(
                f"{self.base_url}/ai/generate-code",
                json=data,
                timeout=60
            )
            
            result = {
                "test_id": test_id,
                "status_code": response.status_code,
                "success": False,
                "error": None,
                "response_length": len(response.text) if response.text else 0
            }
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    result["success"] = json_response.get("success", False)
                    result["has_code"] = bool(json_response.get("code"))
                    result["code_length"] = len(json_response.get("code", ""))
                except json.JSONDecodeError as e:
                    result["error"] = f"JSON decode error: {e}"
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            result = {
                "test_id": test_id,
                "status_code": None,
                "success": False,
                "error": str(e),
                "response_length": 0
            }
        
        with self.lock:
            self.results.append(result)
            print(f"Test {test_id}: {'✅' if result['success'] else '❌'} - {result.get('error', 'OK')}")
        
        return result
    
    def run_multiple_tests(self, num_tests=5, is_concurrent=True):
        """Run multiple tests"""
        print(f"🚀 Running {num_tests} Claude integration tests")
        print(f"🔄 Concurrent: {is_concurrent}")
        print("=" * 50)
        
        start_time = time.time()
        
        if is_concurrent:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(self.single_request_test, i+1) for i in range(num_tests)]
                concurrent.futures.wait(futures)
        else:
            for i in range(num_tests):
                self.single_request_test(i+1)
                time.sleep(1)  # Small delay between requests
        
        end_time = time.time()
        
        # Analyze results
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        print(f"Total tests: {len(self.results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"Success rate: {len(successful)/len(self.results)*100:.1f}%")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        
        if failed:
            print(f"\n🔍 FAILED TESTS ANALYSIS:")
            for result in failed:
                print(f"   Test {result['test_id']}: {result['error']}")
        
        if successful:
            avg_code_length = sum(r.get("code_length", 0) for r in successful) / len(successful)
            print(f"\n📈 SUCCESSFUL TESTS STATS:")
            print(f"   Average code length: {avg_code_length:.0f} characters")
        
        return len(failed) == 0

if __name__ == "__main__":
    tester = MultipleClaudeTester()
    
    # Test sequential requests
    print("🔄 Testing Sequential Requests...")
    success_sequential = tester.run_multiple_tests(3, is_concurrent=False)
    
    # Reset results
    tester.results = []
    
    # Test concurrent requests
    print("\n🔄 Testing Concurrent Requests...")
    success_concurrent = tester.run_multiple_tests(3, is_concurrent=True)
    
    if success_sequential and success_concurrent:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)