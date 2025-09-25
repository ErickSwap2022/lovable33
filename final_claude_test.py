#!/usr/bin/env python3
"""
Final Claude Integration Test - Focused on the specific user request
"""

import requests
import json
import uuid
import time

BACKEND_URL = "https://devsage-2.preview.emergentagent.com/api"

def test_claude_generate_code():
    """Test the specific endpoint requested by user"""
    print("🎯 Testing /api/ai/generate-code with Claude configuration")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    test_data = {
        "prompt": "create a simple todo app",
        "session_id": session_id
    }
    
    print(f"📝 Request data:")
    print(f"   Prompt: {test_data['prompt']}")
    print(f"   Session ID: {test_data['session_id']}")
    print(f"   Endpoint: {BACKEND_URL}/ai/generate-code")
    
    try:
        print(f"\n📤 Sending POST request...")
        response = requests.post(
            f"{BACKEND_URL}/ai/generate-code",
            json=test_data,
            timeout=60
        )
        
        print(f"📥 Response received:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response Size: {len(response.text)} bytes")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n✅ JSON Response Analysis:")
                print(f"   Success: {result.get('success', 'Not specified')}")
                print(f"   Message: {result.get('message', 'No message')}")
                print(f"   Has Code: {'Yes' if result.get('code') else 'No'}")
                
                if result.get('code'):
                    code_length = len(result['code'])
                    print(f"   Code Length: {code_length} characters")
                    
                    # Show first 300 characters of generated code
                    code_preview = result['code'][:300]
                    print(f"   Code Preview:")
                    print(f"   {'-' * 40}")
                    print(f"   {code_preview}...")
                    print(f"   {'-' * 40}")
                
                if result.get('metadata'):
                    metadata = result['metadata']
                    print(f"   Metadata Keys: {list(metadata.keys())}")
                    if 'title' in metadata:
                        print(f"   Generated Title: {metadata['title']}")
                    if 'tech_stack' in metadata:
                        print(f"   Tech Stack: {metadata['tech_stack']}")
                
                # Final verdict
                if result.get('success') and result.get('code') and len(result['code']) > 100:
                    print(f"\n🎉 CLAUDE INTEGRATION TEST: PASSED")
                    print(f"   ✅ Claude (Anthropic) is working correctly")
                    print(f"   ✅ Code generation is functional")
                    print(f"   ✅ Response structure is correct")
                    return True
                else:
                    print(f"\n❌ CLAUDE INTEGRATION TEST: FAILED")
                    print(f"   ❌ Code generation not working properly")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON DECODE ERROR: {e}")
                print(f"   Raw response: {response.text[:500]}...")
                return False
        else:
            print(f"\n❌ HTTP ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ REQUEST ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_claude_generate_code()
    
    if success:
        print(f"\n🎉 Claude integration is working correctly!")
        exit(0)
    else:
        print(f"\n💥 Claude integration has issues!")
        exit(1)