#!/usr/bin/env python3
"""
Enhanced Backend API Test Suite for New Lovable Clone Features
Tests the new enhanced AI services, chat mode agent, and real-time visual services
Focus on EXTREME QUALITY verification as requested
"""

import requests
import json
import uuid
import time
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://devsage-2.preview.emergentagent.com/api"

class EnhancedLovableAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_session_id = str(uuid.uuid4())
        
        # Test data
        self.test_user_email = f"testuser_{int(time.time())}@example.com"
        self.test_user_password = "SecurePassword123!"
        self.test_user_name = "Test User"
        
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message="", response_data=None):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results["failed"] += 1
            error_info = {
                "test": test_name,
                "message": message,
                "response": response_data
            }
            self.results["errors"].append(error_info)
            print(f"❌ {test_name}: FAILED - {message}")
    
    def make_request(self, method, endpoint, data=None, headers=None, params=None, timeout=60):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if token exists
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {method} {url}: {e}")
            return None
    
    def setup_authentication(self):
        """Setup authentication for testing"""
        print("🔐 Setting up authentication...")
        
        # Try registration first
        data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "name": self.test_user_name,
            "username": f"testuser_{int(time.time())}"
        }
        
        response = self.make_request("POST", "/auth/register", data)
        
        if response and response.status_code == 200:
            try:
                result = response.json()
                if "access_token" in result and "user" in result:
                    self.auth_token = result["access_token"]
                    self.test_user_id = result["user"]["id"]
                    print(f"✅ Authentication setup successful - User ID: {self.test_user_id}")
                    return True
            except json.JSONDecodeError:
                pass
        
        print("❌ Authentication setup failed")
        return False
    
    # =============================================================================
    # ENHANCED AI SERVICE TESTS (4-PHASE SERVICE)
    # =============================================================================
    
    def test_enhanced_ai_generate_code_basic(self):
        """Test enhanced AI code generation with basic prompt"""
        data = {
            "prompt": "Create a simple React counter component with increment and decrement buttons",
            "session_id": self.test_session_id
        }
        
        print("🤖 Testing Enhanced AI Code Generation (Basic)...")
        response = self.make_request("POST", "/ai/generate-code", data, timeout=90)
        
        if response is None:
            self.log_result("Enhanced AI Generate Code (Basic)", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"] and "code" in result:
                    code_length = len(result["code"])
                    has_metadata = "metadata" in result and result["metadata"]
                    
                    # Quality checks
                    quality_checks = {
                        "has_code": bool(result.get("code")),
                        "code_length_adequate": code_length > 500,  # At least 500 characters
                        "has_metadata": has_metadata,
                        "has_react_component": "function" in result["code"] or "const" in result["code"],
                        "has_increment_logic": "increment" in result["code"].lower() or "++" in result["code"],
                        "has_decrement_logic": "decrement" in result["code"].lower() or "--" in result["code"]
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 4:  # At least 4/6 quality checks
                        self.log_result("Enhanced AI Generate Code (Basic)", True, 
                                      f"Generated {code_length} chars, {passed_checks}/{total_checks} quality checks passed")
                        return True
                    else:
                        self.log_result("Enhanced AI Generate Code (Basic)", False, 
                                      f"Quality insufficient: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Enhanced AI Generate Code (Basic)", False, "Missing success or code in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Enhanced AI Generate Code (Basic)", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Enhanced AI Generate Code (Basic)", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_enhanced_ai_generate_code_complex(self):
        """Test enhanced AI code generation with complex e-commerce prompt"""
        data = {
            "prompt": "create a complete e-commerce dashboard with product management",
            "session_id": self.test_session_id,
            "context": {
                "framework": "react",
                "features": ["product_crud", "dashboard", "analytics", "inventory"],
                "complexity": "high"
            }
        }
        
        print("🛒 Testing Enhanced AI Code Generation (Complex E-commerce)...")
        response = self.make_request("POST", "/ai/generate-code", data, timeout=120)
        
        if response is None:
            self.log_result("Enhanced AI Generate Code (E-commerce)", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"] and "code" in result:
                    code = result["code"]
                    code_length = len(code)
                    metadata = result.get("metadata", {})
                    
                    # EXTREME QUALITY checks for e-commerce dashboard
                    quality_checks = {
                        "substantial_code": code_length > 2000,  # At least 2000 characters for complex app
                        "has_components": code.count("function") + code.count("const") >= 3,  # Multiple components
                        "has_product_management": any(term in code.lower() for term in ["product", "item", "inventory"]),
                        "has_dashboard_elements": any(term in code.lower() for term in ["dashboard", "chart", "stats", "analytics"]),
                        "has_crud_operations": any(term in code.lower() for term in ["add", "edit", "delete", "update", "create"]),
                        "has_state_management": "useState" in code or "state" in code.lower(),
                        "has_proper_structure": "{" in code and "}" in code and "return" in code,
                        "has_styling": any(term in code for term in ["className", "style", "css"]),
                        "has_metadata": bool(metadata),
                        "professional_quality": "export" in code or "import" in code
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    # For EXTREME QUALITY, we need at least 7/10 checks to pass
                    if passed_checks >= 7:
                        self.log_result("Enhanced AI Generate Code (E-commerce)", True, 
                                      f"EXTREME QUALITY: Generated {code_length} chars, {passed_checks}/{total_checks} quality checks passed")
                        
                        # Additional analysis
                        print(f"   📊 Code Analysis:")
                        print(f"   - Length: {code_length} characters")
                        print(f"   - Components: {code.count('function') + code.count('const')} detected")
                        print(f"   - Has Product Management: {quality_checks['has_product_management']}")
                        print(f"   - Has Dashboard Elements: {quality_checks['has_dashboard_elements']}")
                        print(f"   - Has CRUD Operations: {quality_checks['has_crud_operations']}")
                        print(f"   - Professional Structure: {quality_checks['professional_quality']}")
                        
                        return True
                    else:
                        self.log_result("Enhanced AI Generate Code (E-commerce)", False, 
                                      f"QUALITY INSUFFICIENT: {passed_checks}/{total_checks} checks passed. Expected EXTREME QUALITY.", 
                                      {"code_length": code_length, "failed_checks": [k for k, v in quality_checks.items() if not v]})
                        return False
                else:
                    self.log_result("Enhanced AI Generate Code (E-commerce)", False, "Missing success or code in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Enhanced AI Generate Code (E-commerce)", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Enhanced AI Generate Code (E-commerce)", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_enhanced_ai_response_time(self):
        """Test enhanced AI service response time"""
        data = {
            "prompt": "Create a React todo app with add, edit, delete functionality",
            "session_id": self.test_session_id
        }
        
        print("⏱️ Testing Enhanced AI Response Time...")
        start_time = time.time()
        response = self.make_request("POST", "/ai/generate-code", data, timeout=120)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response is None:
            self.log_result("Enhanced AI Response Time", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    # Response time should be reasonable (under 60 seconds for quality generation)
                    if response_time < 60:
                        self.log_result("Enhanced AI Response Time", True, f"Response time: {response_time:.2f}s (Good)")
                        return True
                    elif response_time < 90:
                        self.log_result("Enhanced AI Response Time", True, f"Response time: {response_time:.2f}s (Acceptable)")
                        return True
                    else:
                        self.log_result("Enhanced AI Response Time", False, f"Response time too slow: {response_time:.2f}s")
                        return False
                else:
                    self.log_result("Enhanced AI Response Time", False, f"Request failed but took {response_time:.2f}s", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Enhanced AI Response Time", False, f"Invalid JSON after {response_time:.2f}s", response.text)
                return False
        else:
            self.log_result("Enhanced AI Response Time", False, f"Status: {response.status_code}, Time: {response_time:.2f}s", response.text)
            return False
    
    # =============================================================================
    # CHAT MODE AGENT SERVICE TESTS
    # =============================================================================
    
    def test_chat_agent_query_debugging(self):
        """Test chat agent for debugging assistance"""
        data = {
            "query": "I have a React component that's not re-rendering when state changes. The useState hook seems to be called but the UI doesn't update. What could be wrong?",
            "context": {
                "framework": "react",
                "issue_type": "debugging",
                "component_type": "functional"
            },
            "session_id": self.test_session_id
        }
        
        print("🐛 Testing Chat Agent Query (Debugging)...")
        response = self.make_request("POST", "/chat-agent/query", data, timeout=60)
        
        if response is None:
            self.log_result("Chat Agent Query (Debugging)", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    response_text = result.get("response", "")
                    suggestions = result.get("suggestions", [])
                    
                    # Quality checks for debugging response
                    quality_checks = {
                        "has_response": bool(response_text),
                        "substantial_response": len(response_text) > 100,
                        "mentions_react": "react" in response_text.lower(),
                        "mentions_state": "state" in response_text.lower(),
                        "provides_solutions": any(word in response_text.lower() for word in ["try", "check", "ensure", "make sure", "solution"]),
                        "has_suggestions": bool(suggestions) or "suggestion" in response_text.lower()
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 4:
                        self.log_result("Chat Agent Query (Debugging)", True, 
                                      f"Quality debugging response: {passed_checks}/{total_checks} checks passed")
                        return True
                    else:
                        self.log_result("Chat Agent Query (Debugging)", False, 
                                      f"Poor debugging response: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Chat Agent Query (Debugging)", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Chat Agent Query (Debugging)", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Chat Agent Query (Debugging)", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_chat_agent_query_planning(self):
        """Test chat agent for project planning assistance"""
        data = {
            "query": "I want to build a social media app with user authentication, posts, comments, and real-time notifications. What's the best architecture and tech stack?",
            "context": {
                "project_type": "social_media",
                "features": ["auth", "posts", "comments", "notifications"],
                "scale": "medium"
            },
            "session_id": self.test_session_id
        }
        
        print("📋 Testing Chat Agent Query (Planning)...")
        response = self.make_request("POST", "/chat-agent/query", data, timeout=60)
        
        if response is None:
            self.log_result("Chat Agent Query (Planning)", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    response_text = result.get("response", "")
                    
                    # Quality checks for planning response
                    quality_checks = {
                        "has_response": bool(response_text),
                        "comprehensive_response": len(response_text) > 200,
                        "mentions_architecture": any(term in response_text.lower() for term in ["architecture", "structure", "design", "pattern"]),
                        "mentions_tech_stack": any(term in response_text.lower() for term in ["stack", "technology", "framework", "database"]),
                        "addresses_auth": "auth" in response_text.lower(),
                        "addresses_realtime": any(term in response_text.lower() for term in ["real-time", "realtime", "websocket", "socket"]),
                        "provides_recommendations": any(term in response_text.lower() for term in ["recommend", "suggest", "consider", "use"])
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 5:
                        self.log_result("Chat Agent Query (Planning)", True, 
                                      f"Comprehensive planning response: {passed_checks}/{total_checks} checks passed")
                        return True
                    else:
                        self.log_result("Chat Agent Query (Planning)", False, 
                                      f"Inadequate planning response: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Chat Agent Query (Planning)", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Chat Agent Query (Planning)", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Chat Agent Query (Planning)", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_chat_agent_multi_step_reasoning(self):
        """Test chat agent multi-step reasoning capability"""
        data = {
            "problem": "My e-commerce website is slow. Users are complaining about long load times, especially on the product listing page. The database has 100,000 products and we're getting 1000 concurrent users. How should I optimize this?",
            "context": {
                "problem_type": "performance",
                "scale": "large",
                "specific_issues": ["slow_loading", "database_performance", "high_concurrency"]
            },
            "session_id": self.test_session_id
        }
        
        print("🧠 Testing Chat Agent Multi-Step Reasoning...")
        response = self.make_request("POST", "/chat-agent/multi-step-reasoning", data, timeout=90)
        
        if response is None:
            self.log_result("Chat Agent Multi-Step Reasoning", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    reasoning_steps = result.get("reasoning_steps", [])
                    final_solution = result.get("solution", "")
                    analysis = result.get("analysis", "")
                    
                    # Quality checks for multi-step reasoning
                    quality_checks = {
                        "has_reasoning_steps": bool(reasoning_steps),
                        "multiple_steps": len(reasoning_steps) >= 3 if reasoning_steps else False,
                        "has_final_solution": bool(final_solution),
                        "has_analysis": bool(analysis),
                        "addresses_database": any("database" in str(step).lower() for step in reasoning_steps) if reasoning_steps else "database" in final_solution.lower(),
                        "addresses_caching": any(term in str(result).lower() for term in ["cache", "caching", "redis", "memcached"]),
                        "addresses_optimization": any(term in str(result).lower() for term in ["optimize", "optimization", "performance", "speed"]),
                        "addresses_scaling": any(term in str(result).lower() for term in ["scale", "scaling", "load", "concurrent"])
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 6:
                        self.log_result("Chat Agent Multi-Step Reasoning", True, 
                                      f"Excellent reasoning: {passed_checks}/{total_checks} checks passed, {len(reasoning_steps) if reasoning_steps else 0} steps")
                        return True
                    else:
                        self.log_result("Chat Agent Multi-Step Reasoning", False, 
                                      f"Poor reasoning: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Chat Agent Multi-Step Reasoning", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Chat Agent Multi-Step Reasoning", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Chat Agent Multi-Step Reasoning", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # REAL-TIME VISUAL SERVICE TESTS
    # =============================================================================
    
    def test_realtime_visual_start_session(self):
        """Test starting a real-time visual editing session"""
        data = {
            "session_id": f"visual_{self.test_session_id}",
            "initial_code": """
function App() {
  const [count, setCount] = useState(0);
  
  return (
    <div className="app">
      <h1>Counter App</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(count - 1)}>Decrement</button>
    </div>
  );
}
            """.strip()
        }
        
        print("🎨 Testing Real-time Visual Start Session...")
        response = self.make_request("POST", "/realtime-visual/start-session", data, timeout=30)
        
        if response is None:
            self.log_result("Real-time Visual Start Session", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    session_info = result.get("session", {})
                    
                    # Quality checks for session start
                    quality_checks = {
                        "has_session_info": bool(session_info),
                        "has_session_id": "session_id" in session_info,
                        "has_initial_state": "initial_code" in session_info or "code" in session_info,
                        "session_active": session_info.get("status") == "active" if session_info else False
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 3:
                        self.log_result("Real-time Visual Start Session", True, 
                                      f"Session started successfully: {passed_checks}/{total_checks} checks passed")
                        return True
                    else:
                        self.log_result("Real-time Visual Start Session", False, 
                                      f"Session start incomplete: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Real-time Visual Start Session", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Real-time Visual Start Session", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Real-time Visual Start Session", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_realtime_visual_apply_change(self):
        """Test applying real-time visual changes"""
        data = {
            "session_id": f"visual_{self.test_session_id}",
            "change": {
                "type": "style_update",
                "target": "button",
                "property": "backgroundColor",
                "value": "#007bff",
                "selector": "button"
            }
        }
        
        print("⚡ Testing Real-time Visual Apply Change...")
        response = self.make_request("POST", "/realtime-visual/apply-change", data, timeout=30)
        
        if response is None:
            self.log_result("Real-time Visual Apply Change", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    updated_code = result.get("updated_code", "")
                    change_applied = result.get("change_applied", False)
                    
                    # Quality checks for change application
                    quality_checks = {
                        "has_updated_code": bool(updated_code),
                        "change_confirmed": change_applied,
                        "code_modified": len(updated_code) > 0,
                        "maintains_structure": "function" in updated_code and "return" in updated_code
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 3:
                        self.log_result("Real-time Visual Apply Change", True, 
                                      f"Change applied successfully: {passed_checks}/{total_checks} checks passed")
                        return True
                    else:
                        self.log_result("Real-time Visual Apply Change", False, 
                                      f"Change application failed: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Real-time Visual Apply Change", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Real-time Visual Apply Change", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Real-time Visual Apply Change", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_realtime_visual_get_session_info(self):
        """Test getting real-time visual session information"""
        session_id = f"visual_{self.test_session_id}"
        
        print("📊 Testing Real-time Visual Get Session Info...")
        response = self.make_request("GET", f"/realtime-visual/session/{session_id}", timeout=30)
        
        if response is None:
            self.log_result("Real-time Visual Get Session Info", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    session_info = result.get("session", {})
                    
                    # Quality checks for session info
                    quality_checks = {
                        "has_session_info": bool(session_info),
                        "has_session_id": "session_id" in session_info,
                        "has_status": "status" in session_info,
                        "has_code_state": any(key in session_info for key in ["current_code", "code", "initial_code"])
                    }
                    
                    passed_checks = sum(quality_checks.values())
                    total_checks = len(quality_checks)
                    
                    if passed_checks >= 3:
                        self.log_result("Real-time Visual Get Session Info", True, 
                                      f"Session info retrieved: {passed_checks}/{total_checks} checks passed")
                        return True
                    else:
                        self.log_result("Real-time Visual Get Session Info", False, 
                                      f"Incomplete session info: {passed_checks}/{total_checks} checks passed", result)
                        return False
                else:
                    self.log_result("Real-time Visual Get Session Info", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Real-time Visual Get Session Info", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Real-time Visual Get Session Info", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # MAIN TEST RUNNER
    # =============================================================================
    
    def run_enhanced_tests(self):
        """Run all enhanced functionality tests"""
        print("🚀 Starting Enhanced Lovable Clone API Test Suite")
        print("🎯 Focus: EXTREME QUALITY verification of new features")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test API root
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            self.log_result("API Root", True, "API is online")
        else:
            self.log_result("API Root", False, "API is not responding")
            return False
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return False
        
        print("\n" + "=" * 80)
        print("🤖 TESTING ENHANCED AI SERVICE (4-PHASE SERVICE)")
        print("=" * 80)
        
        # Enhanced AI Service Tests
        self.test_enhanced_ai_generate_code_basic()
        self.test_enhanced_ai_generate_code_complex()
        self.test_enhanced_ai_response_time()
        
        print("\n" + "=" * 80)
        print("💬 TESTING CHAT MODE AGENT SERVICE")
        print("=" * 80)
        
        # Chat Mode Agent Tests
        self.test_chat_agent_query_debugging()
        self.test_chat_agent_query_planning()
        self.test_chat_agent_multi_step_reasoning()
        
        print("\n" + "=" * 80)
        print("🎨 TESTING REAL-TIME VISUAL SERVICE")
        print("=" * 80)
        
        # Real-time Visual Service Tests
        self.test_realtime_visual_start_session()
        self.test_realtime_visual_apply_change()
        self.test_realtime_visual_get_session_info()
        
        # Print comprehensive results
        print("\n" + "=" * 80)
        print("📊 ENHANCED FEATURES TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        # Categorize results
        categories = {
            "Enhanced AI Service": ["Enhanced AI Generate Code (Basic)", "Enhanced AI Generate Code (E-commerce)", "Enhanced AI Response Time"],
            "Chat Mode Agent": ["Chat Agent Query (Debugging)", "Chat Agent Query (Planning)", "Chat Agent Multi-Step Reasoning"],
            "Real-time Visual": ["Real-time Visual Start Session", "Real-time Visual Apply Change", "Real-time Visual Get Session Info"]
        }
        
        print("\n📋 RESULTS BY CATEGORY:")
        print("-" * 50)
        for category, tests in categories.items():
            failed_tests = [error['test'] for error in self.results['errors']]
            failed_in_category = sum(1 for test in tests if test in failed_tests)
            passed_in_category = len(tests) - failed_in_category
            print(f"{category}: {passed_in_category}/{len(tests)} passed")
        
        # Quality Analysis
        print("\n🎯 QUALITY ANALYSIS:")
        print("-" * 50)
        
        ai_quality_score = 0
        chat_quality_score = 0
        visual_quality_score = 0
        
        for error in self.results['errors']:
            if "Enhanced AI" in error['test']:
                if "EXTREME QUALITY" in error['message']:
                    print(f"🔴 AI Service: Failed EXTREME QUALITY standards")
                else:
                    print(f"🟡 AI Service: Basic functionality issues")
            elif "Chat Agent" in error['test']:
                print(f"🔴 Chat Agent: {error['test']} - {error['message']}")
            elif "Real-time Visual" in error['test']:
                print(f"🔴 Visual Service: {error['test']} - {error['message']}")
        
        # Success indicators
        passed_tests = [f"✅ {i+1}. {test}" for i, test in enumerate([
            "Enhanced AI Generate Code (Basic)", "Enhanced AI Generate Code (E-commerce)", "Enhanced AI Response Time",
            "Chat Agent Query (Debugging)", "Chat Agent Query (Planning)", "Chat Agent Multi-Step Reasoning",
            "Real-time Visual Start Session", "Real-time Visual Apply Change", "Real-time Visual Get Session Info"
        ]) if test not in [error['test'] for error in self.results['errors']]]
        
        if passed_tests:
            print("\n🟢 WORKING FEATURES:")
            for test in passed_tests:
                print(f"  {test}")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS DETAILS:")
            print("-" * 50)
            for error in self.results['errors']:
                print(f"❌ {error['test']}")
                print(f"   Issue: {error['message']}")
                if error['response'] and len(str(error['response'])) < 200:
                    print(f"   Response: {error['response']}")
                print()
        
        print("\n🎯 EXTREME QUALITY ASSESSMENT:")
        print("-" * 50)
        if self.results['failed'] == 0:
            print("🟢 ALL TESTS PASSED - EXTREME QUALITY ACHIEVED!")
        elif self.results['failed'] <= 2:
            print("🟡 MOSTLY WORKING - Minor issues detected")
        else:
            print("🔴 SIGNIFICANT ISSUES - Quality standards not met")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = EnhancedLovableAPITester()
    success = tester.run_enhanced_tests()
    sys.exit(0 if success else 1)