#!/usr/bin/env python3
"""
Claude Integration Debug Test
Specifically tests the AI code generation endpoint with Claude configuration
"""

import requests
import json
import uuid
import time
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://devsage-2.preview.emergentagent.com/api"

class ClaudeDebugTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_session_id = str(uuid.uuid4())
        
        print(f"🔍 Claude Integration Debug Test")
        print(f"🔗 Testing against: {self.base_url}")
        print(f"📝 Session ID: {self.test_session_id}")
        print("=" * 60)
    
    def make_request(self, method, endpoint, data=None, headers=None, params=None):
        """Make HTTP request with detailed logging"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n📤 Making {method} request to: {url}")
        if data:
            print(f"📋 Request data: {json.dumps(data, indent=2)}")
        if params:
            print(f"🔗 Request params: {params}")
        if headers:
            print(f"🔑 Request headers: {headers}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=60)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, params=params, timeout=60)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📋 Response headers: {dict(response.headers)}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error for {method} {url}: {e}")
            return None
    
    def test_claude_code_generation(self):
        """Test Claude AI code generation with detailed analysis"""
        print("\n🤖 Testing Claude AI Code Generation Endpoint")
        print("-" * 50)
        
        # Test data
        test_data = {
            "prompt": "create a simple todo app",
            "session_id": self.test_session_id
        }
        
        print(f"🎯 Test prompt: '{test_data['prompt']}'")
        print(f"🆔 Session ID: {test_data['session_id']}")
        
        # Make the request
        response = self.make_request("POST", "/ai/generate-code", test_data)
        
        if response is None:
            print("❌ CRITICAL: Request failed completely")
            return False
        
        # Analyze response status
        print(f"\n📊 Response Analysis:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not specified')}")
        print(f"   Content-Length: {response.headers.get('content-length', 'Not specified')}")
        
        # Try to parse response body
        try:
            response_text = response.text
            print(f"   Response Length: {len(response_text)} characters")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"✅ Successfully parsed JSON response")
                    
                    # Detailed response analysis
                    print(f"\n🔍 Response Structure Analysis:")
                    print(f"   Keys present: {list(result.keys())}")
                    
                    # Check required fields
                    required_fields = ["success", "code", "metadata", "message"]
                    for field in required_fields:
                        if field in result:
                            print(f"   ✅ {field}: Present")
                            if field == "success":
                                print(f"      Value: {result[field]}")
                            elif field == "code":
                                code_length = len(str(result[field])) if result[field] else 0
                                print(f"      Length: {code_length} characters")
                                if code_length > 0:
                                    # Show first 200 characters of code
                                    code_preview = str(result[field])[:200]
                                    print(f"      Preview: {code_preview}...")
                            elif field == "metadata":
                                if isinstance(result[field], dict):
                                    print(f"      Keys: {list(result[field].keys())}")
                                else:
                                    print(f"      Type: {type(result[field])}")
                            elif field == "message":
                                print(f"      Value: {result[field]}")
                        else:
                            print(f"   ❌ {field}: Missing")
                    
                    # Check if generation was successful
                    if result.get("success") == True:
                        print(f"\n✅ Code generation reported as successful")
                        
                        # Validate code content
                        code = result.get("code", "")
                        if code and len(code) > 100:  # Reasonable minimum for a todo app
                            print(f"✅ Generated code appears substantial ({len(code)} chars)")
                            
                            # Check for React patterns
                            react_patterns = ["import React", "function", "const", "return", "export"]
                            found_patterns = [pattern for pattern in react_patterns if pattern in code]
                            print(f"✅ React patterns found: {found_patterns}")
                            
                            return True
                        else:
                            print(f"❌ Generated code is too short or empty: {len(code)} chars")
                            return False
                    else:
                        print(f"❌ Code generation reported as failed")
                        if "error" in result:
                            print(f"   Error: {result['error']}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response: {e}")
                    print(f"   Raw response (first 500 chars): {response_text[:500]}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response body: {response_text}")
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error analyzing response: {e}")
            return False
    
    def check_backend_logs(self):
        """Check backend logs for errors"""
        print("\n📋 Checking Backend Logs...")
        print("-" * 30)
        
        try:
            # Check supervisor backend logs
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout.strip()
                if logs:
                    print("📋 Recent backend error logs:")
                    print(logs)
                else:
                    print("✅ No recent error logs found")
            else:
                print("⚠️ Could not read backend error logs")
                
            # Also check stdout logs
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout.strip()
                if logs:
                    print("\n📋 Recent backend output logs:")
                    print(logs)
                    
        except Exception as e:
            print(f"⚠️ Could not check backend logs: {e}")
    
    def test_claude_configuration(self):
        """Test Claude configuration and environment"""
        print("\n🔧 Testing Claude Configuration...")
        print("-" * 40)
        
        # Check environment variables
        try:
            import subprocess
            
            # Check if EMERGENT_LLM_KEY is set in backend
            result = subprocess.run(
                ["grep", "-r", "EMERGENT_LLM_KEY", "/app/backend/.env"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✅ EMERGENT_LLM_KEY found in backend .env")
            else:
                print("❌ EMERGENT_LLM_KEY not found in backend .env")
                
        except Exception as e:
            print(f"⚠️ Could not check environment configuration: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive Claude integration test"""
        print("🚀 Starting Comprehensive Claude Integration Test")
        print("=" * 60)
        
        # Test API availability
        print("\n🔍 Step 1: Testing API Availability")
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            print("✅ API is online and responding")
        else:
            print("❌ API is not responding properly")
            return False
        
        # Test Claude configuration
        print("\n🔍 Step 2: Testing Claude Configuration")
        self.test_claude_configuration()
        
        # Test code generation
        print("\n🔍 Step 3: Testing Claude Code Generation")
        success = self.test_claude_code_generation()
        
        # Check backend logs
        print("\n🔍 Step 4: Checking Backend Logs")
        self.check_backend_logs()
        
        # Final result
        print("\n" + "=" * 60)
        print("📊 CLAUDE INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        if success:
            print("✅ Claude integration is working correctly")
            print("✅ Code generation endpoint is functional")
            print("✅ Claude (Anthropic) provider is responding properly")
        else:
            print("❌ Claude integration has issues")
            print("❌ Code generation is not working as expected")
            print("🔍 Check the detailed logs above for specific issues")
        
        return success

if __name__ == "__main__":
    tester = ClaudeDebugTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Claude integration test passed!")
        sys.exit(0)
    else:
        print("\n💥 Claude integration test failed!")
        sys.exit(1)