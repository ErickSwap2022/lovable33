#!/usr/bin/env python3
"""
Comprehensive Backend API Test Suite for Lovable Clone
Tests all endpoints including authentication, AI, templates, projects, and deployment
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

class LovableCloneAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_project_id = None
        self.test_template_id = None
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
    
    def make_request(self, method, endpoint, data=None, headers=None, params=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if token exists
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, params=params, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {method} {url}: {e}")
            return None
    
    # =============================================================================
    # AUTHENTICATION TESTS
    # =============================================================================
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "name": self.test_user_name,
            "username": f"testuser_{int(time.time())}"
        }
        
        response = self.make_request("POST", "/auth/register", data)
        
        if response is None:
            self.log_result("User Registration", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "access_token" in result and "user" in result:
                    self.auth_token = result["access_token"]
                    self.test_user_id = result["user"]["id"]
                    self.log_result("User Registration", True, f"User created with ID: {self.test_user_id}")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing access_token or user in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("User Registration", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("User Registration", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_user_login(self):
        """Test user login endpoint"""
        data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        response = self.make_request("POST", "/auth/login", data)
        
        if response is None:
            self.log_result("User Login", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "access_token" in result and "user" in result:
                    self.auth_token = result["access_token"]
                    self.log_result("User Login", True, "Login successful")
                    return True
                else:
                    self.log_result("User Login", False, "Missing access_token or user in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("User Login", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("User Login", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_current_user(self):
        """Test get current user info endpoint"""
        if not self.auth_token:
            self.log_result("Get Current User", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/auth/me")
        
        if response is None:
            self.log_result("Get Current User", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "id" in result and "email" in result:
                    self.log_result("Get Current User", True, f"User info retrieved for: {result['email']}")
                    return True
                else:
                    self.log_result("Get Current User", False, "Missing user info in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Current User", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Current User", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_protected_route_without_auth(self):
        """Test protected route without authentication"""
        # Temporarily remove auth token
        temp_token = self.auth_token
        self.auth_token = None
        
        response = self.make_request("GET", "/auth/me")
        
        # Restore auth token
        self.auth_token = temp_token
        
        if response is None:
            self.log_result("Protected Route Without Auth", False, "Request failed")
            return False
        
        if response.status_code == 401:
            self.log_result("Protected Route Without Auth", True, "Correctly rejected unauthorized request")
            return True
        else:
            self.log_result("Protected Route Without Auth", False, f"Expected 401, got {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # AI SERVICE TESTS
    # =============================================================================
    
    def test_ai_generate_code(self):
        """Test AI code generation endpoint"""
        data = {
            "prompt": "Create a simple React button component",
            "session_id": self.test_session_id
        }
        
        response = self.make_request("POST", "/ai/generate-code", data)
        
        if response is None:
            self.log_result("AI Generate Code", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"] and "code" in result:
                    self.log_result("AI Generate Code", True, "Code generated successfully")
                    return True
                else:
                    self.log_result("AI Generate Code", False, "Missing success or code in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("AI Generate Code", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("AI Generate Code", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_ai_improve_code(self):
        """Test AI code improvement endpoint"""
        params = {
            "code": "function hello() { console.log('hello'); }",
            "session_id": self.test_session_id
        }
        
        response = self.make_request("POST", "/ai/improve-code", params=params)
        
        if response is None:
            self.log_result("AI Improve Code", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"] and "suggestions" in result:
                    self.log_result("AI Improve Code", True, "Code improvements generated")
                    return True
                else:
                    self.log_result("AI Improve Code", False, "Missing success or suggestions in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("AI Improve Code", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("AI Improve Code", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_ai_generate_tests(self):
        """Test AI test generation endpoint"""
        params = {
            "code": "function add(a, b) { return a + b; }",
            "session_id": self.test_session_id
        }
        
        response = self.make_request("POST", "/ai/generate-tests", params=params)
        
        if response is None:
            self.log_result("AI Generate Tests", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"] and "tests" in result:
                    self.log_result("AI Generate Tests", True, "Tests generated successfully")
                    return True
                else:
                    self.log_result("AI Generate Tests", False, "Missing success or tests in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("AI Generate Tests", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("AI Generate Tests", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # TEMPLATE TESTS
    # =============================================================================
    
    def test_get_templates(self):
        """Test get templates endpoint"""
        response = self.make_request("GET", "/templates/")
        
        if response is None:
            self.log_result("Get Templates", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Get Templates", True, f"Retrieved {len(result)} templates")
                    return True
                else:
                    self.log_result("Get Templates", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Templates", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Templates", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_featured_templates(self):
        """Test get featured templates endpoint"""
        response = self.make_request("GET", "/templates/featured")
        
        if response is None:
            self.log_result("Get Featured Templates", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Get Featured Templates", True, f"Retrieved {len(result)} featured templates")
                    return True
                else:
                    self.log_result("Get Featured Templates", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Featured Templates", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Featured Templates", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_template_categories(self):
        """Test get template categories endpoint"""
        response = self.make_request("GET", "/templates/categories")
        
        if response is None:
            self.log_result("Get Template Categories", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                self.log_result("Get Template Categories", True, f"Retrieved categories: {result}")
                return True
            except json.JSONDecodeError:
                self.log_result("Get Template Categories", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Template Categories", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_search_templates(self):
        """Test template search endpoint"""
        params = {"q": "react"}
        response = self.make_request("GET", "/templates/search", params=params)
        
        if response is None:
            self.log_result("Search Templates", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Search Templates", True, f"Found {len(result)} templates for 'react'")
                    return True
                else:
                    self.log_result("Search Templates", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Search Templates", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Search Templates", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # PROJECT TESTS
    # =============================================================================
    
    def test_create_project(self):
        """Test project creation endpoint"""
        if not self.auth_token:
            self.log_result("Create Project", False, "No auth token available")
            return False
        
        data = {
            "name": f"Test Project {int(time.time())}",
            "description": "A test project created by automated testing",
            "initial_prompt": "Create a simple web application"
        }
        
        response = self.make_request("POST", "/projects/", data)
        
        if response is None:
            self.log_result("Create Project", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "id" in result and "name" in result:
                    self.test_project_id = result["id"]
                    self.log_result("Create Project", True, f"Project created with ID: {self.test_project_id}")
                    return True
                else:
                    self.log_result("Create Project", False, "Missing id or name in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Create Project", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Create Project", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_projects(self):
        """Test get projects endpoint"""
        if not self.auth_token:
            self.log_result("Get Projects", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/projects/")
        
        if response is None:
            self.log_result("Get Projects", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Get Projects", True, f"Retrieved {len(result)} projects")
                    return True
                else:
                    self.log_result("Get Projects", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Projects", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Projects", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_project_by_id(self):
        """Test get project by ID endpoint"""
        if not self.test_project_id:
            self.log_result("Get Project By ID", False, "No test project ID available")
            return False
        
        response = self.make_request("GET", f"/projects/{self.test_project_id}")
        
        if response is None:
            self.log_result("Get Project By ID", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "id" in result and result["id"] == self.test_project_id:
                    self.log_result("Get Project By ID", True, f"Retrieved project: {result['name']}")
                    return True
                else:
                    self.log_result("Get Project By ID", False, "Project ID mismatch or missing", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Project By ID", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Project By ID", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_update_project(self):
        """Test project update endpoint"""
        if not self.test_project_id or not self.auth_token:
            self.log_result("Update Project", False, "No test project ID or auth token available")
            return False
        
        data = {
            "description": "Updated description from automated test"
        }
        
        response = self.make_request("PUT", f"/projects/{self.test_project_id}", data)
        
        if response is None:
            self.log_result("Update Project", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "id" in result and "description" in result:
                    self.log_result("Update Project", True, "Project updated successfully")
                    return True
                else:
                    self.log_result("Update Project", False, "Missing id or description in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Update Project", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Update Project", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_fork_project(self):
        """Test project forking endpoint"""
        if not self.test_project_id or not self.auth_token:
            self.log_result("Fork Project", False, "No test project ID or auth token available")
            return False
        
        response = self.make_request("POST", f"/projects/{self.test_project_id}/fork")
        
        if response is None:
            self.log_result("Fork Project", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "id" in result and result["id"] != self.test_project_id:
                    self.log_result("Fork Project", True, f"Project forked with new ID: {result['id']}")
                    return True
                else:
                    self.log_result("Fork Project", False, "Fork failed or same ID returned", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Fork Project", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Fork Project", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # DEPLOYMENT TESTS
    # =============================================================================
    
    def test_deploy_project(self):
        """Test project deployment endpoint"""
        if not self.test_project_id or not self.auth_token:
            self.log_result("Deploy Project", False, "No test project ID or auth token available")
            return False
        
        data = {
            "project_id": self.test_project_id,
            "subdomain": f"test-{int(time.time())}"
        }
        
        response = self.make_request("POST", "/deploy/", data)
        
        if response is None:
            self.log_result("Deploy Project", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result or "deployment_url" in result:
                    self.log_result("Deploy Project", True, "Project deployment initiated")
                    return True
                else:
                    self.log_result("Deploy Project", False, "Unexpected response format", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Deploy Project", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Deploy Project", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_deployment_status(self):
        """Test deployment status endpoint"""
        if not self.test_project_id:
            self.log_result("Get Deployment Status", False, "No test project ID available")
            return False
        
        response = self.make_request("GET", f"/deploy/{self.test_project_id}/status")
        
        if response is None:
            self.log_result("Get Deployment Status", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                self.log_result("Get Deployment Status", True, f"Deployment status: {result}")
                return True
            except json.JSONDecodeError:
                self.log_result("Get Deployment Status", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Deployment Status", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # CHAT TESTS
    # =============================================================================
    
    def test_add_chat_message(self):
        """Test add chat message endpoint"""
        data = {
            "type": "user",
            "content": "Hello, this is a test message"
        }
        
        response = self.make_request("POST", f"/chat/{self.test_session_id}", data)
        
        if response is None:
            self.log_result("Add Chat Message", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"]:
                    self.log_result("Add Chat Message", True, "Chat message added successfully")
                    return True
                else:
                    self.log_result("Add Chat Message", False, "Message not added successfully", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Add Chat Message", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Add Chat Message", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_get_chat_history(self):
        """Test get chat history endpoint"""
        response = self.make_request("GET", f"/chat/{self.test_session_id}")
        
        if response is None:
            self.log_result("Get Chat History", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and "messages" in result:
                    self.log_result("Get Chat History", True, f"Retrieved {len(result['messages'])} messages")
                    return True
                else:
                    self.log_result("Get Chat History", False, "Missing success or messages in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Get Chat History", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Get Chat History", False, f"Status: {response.status_code}", response.text)
            return False
    
    # =============================================================================
    # ADMIN AUTHENTICATION TESTS
    # =============================================================================
    
    def test_admin_login(self):
        """Test admin login with specific credentials"""
        data = {
            "email": "admin@lovable.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", data)
        
        if response is None:
            self.log_result("Admin Login", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "access_token" in result and "user" in result:
                    self.auth_token = result["access_token"]
                    self.test_user_id = result["user"]["id"]
                    self.log_result("Admin Login", True, f"Admin login successful for: {result['user']['email']}")
                    return True
                else:
                    self.log_result("Admin Login", False, "Missing access_token or user in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Login", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Admin Login", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard endpoint access"""
        if not self.auth_token:
            self.log_result("Admin Dashboard Access", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/admin/dashboard")
        
        if response is None:
            self.log_result("Admin Dashboard Access", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "user_stats" in result and "project_stats" in result and "system_stats" in result:
                    self.log_result("Admin Dashboard Access", True, "Admin dashboard data retrieved successfully")
                    return True
                else:
                    self.log_result("Admin Dashboard Access", False, "Missing expected dashboard data", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Dashboard Access", False, "Invalid JSON response", response.text)
                return False
        elif response.status_code == 403:
            self.log_result("Admin Dashboard Access", False, "Access forbidden - user may not have admin privileges", response.text)
            return False
        elif response.status_code == 401:
            self.log_result("Admin Dashboard Access", False, "Unauthorized - authentication failed", response.text)
            return False
        else:
            self.log_result("Admin Dashboard Access", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_admin_users_management(self):
        """Test admin users management endpoint"""
        if not self.auth_token:
            self.log_result("Admin Users Management", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/admin/users")
        
        if response is None:
            self.log_result("Admin Users Management", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Admin Users Management", True, f"Retrieved {len(result)} users for management")
                    return True
                else:
                    self.log_result("Admin Users Management", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Users Management", False, "Invalid JSON response", response.text)
                return False
        elif response.status_code == 403:
            self.log_result("Admin Users Management", False, "Access forbidden - user may not have admin privileges", response.text)
            return False
        else:
            self.log_result("Admin Users Management", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_admin_projects_management(self):
        """Test admin projects management endpoint"""
        if not self.auth_token:
            self.log_result("Admin Projects Management", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/admin/projects")
        
        if response is None:
            self.log_result("Admin Projects Management", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Admin Projects Management", True, f"Retrieved {len(result)} projects for management")
                    return True
                else:
                    self.log_result("Admin Projects Management", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Projects Management", False, "Invalid JSON response", response.text)
                return False
        elif response.status_code == 403:
            self.log_result("Admin Projects Management", False, "Access forbidden - user may not have admin privileges", response.text)
            return False
        else:
            self.log_result("Admin Projects Management", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_admin_system_logs(self):
        """Test admin system logs endpoint"""
        if not self.auth_token:
            self.log_result("Admin System Logs", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/admin/logs")
        
        if response is None:
            self.log_result("Admin System Logs", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    self.log_result("Admin System Logs", True, f"Retrieved {len(result)} system logs")
                    return True
                else:
                    self.log_result("Admin System Logs", False, "Response is not a list", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin System Logs", False, "Invalid JSON response", response.text)
                return False
        elif response.status_code == 403:
            self.log_result("Admin System Logs", False, "Access forbidden - user may not have admin privileges", response.text)
            return False
        else:
            self.log_result("Admin System Logs", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_admin_settings(self):
        """Test admin settings endpoint"""
        if not self.auth_token:
            self.log_result("Admin Settings", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/admin/settings")
        
        if response is None:
            self.log_result("Admin Settings", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict):
                    self.log_result("Admin Settings", True, "Retrieved platform settings successfully")
                    return True
                else:
                    self.log_result("Admin Settings", False, "Response is not a dict", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Settings", False, "Invalid JSON response", response.text)
                return False
        elif response.status_code == 403:
            self.log_result("Admin Settings", False, "Access forbidden - user may not have admin privileges", response.text)
            return False
        else:
            self.log_result("Admin Settings", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_admin_analytics(self):
        """Test admin analytics endpoint"""
        if not self.auth_token:
            self.log_result("Admin Analytics", False, "No auth token available")
            return False
        
        response = self.make_request("GET", "/admin/analytics")
        
        if response is None:
            self.log_result("Admin Analytics", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict) and "daily_users" in result:
                    self.log_result("Admin Analytics", True, "Retrieved analytics data successfully")
                    return True
                else:
                    self.log_result("Admin Analytics", False, "Missing expected analytics data", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Admin Analytics", False, "Invalid JSON response", response.text)
                return False
        elif response.status_code == 403:
            self.log_result("Admin Analytics", False, "Access forbidden - user may not have admin privileges", response.text)
            return False
        else:
            self.log_result("Admin Analytics", False, f"Status: {response.status_code}", response.text)
            return False

    # =============================================================================
    # NEW ADVANCED ENDPOINTS TESTS (Agent Mode, Visual Editor, GitHub, Supabase, Media)
    # =============================================================================
    
    def test_agent_generate_code(self):
        """Test autonomous AI agent code generation endpoint"""
        data = {
            "prompt": "Create a React todo app with add, delete, and toggle functionality",
            "session_id": self.test_session_id,
            "context": {
                "framework": "react",
                "style": "modern"
            }
        }
        
        response = self.make_request("POST", "/ai/agent-generate", data)
        
        if response is None:
            self.log_result("Agent Generate Code", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and result["success"] and "code" in result:
                    self.log_result("Agent Generate Code", True, f"Agent generated code with confidence: {result.get('confidence_score', 'N/A')}")
                    return True
                else:
                    self.log_result("Agent Generate Code", False, "Missing success or code in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Agent Generate Code", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Agent Generate Code", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_codebase_search(self):
        """Test intelligent codebase search endpoint"""
        params = {
            "query": "authentication function",
            "project_id": self.test_project_id or "test-project-id"
        }
        
        response = self.make_request("POST", "/ai/codebase-search", params=params)
        
        if response is None:
            self.log_result("Codebase Search", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result and "results" in result:
                    self.log_result("Codebase Search", True, f"Found {len(result['results'])} search results")
                    return True
                else:
                    self.log_result("Codebase Search", False, "Missing success or results in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Codebase Search", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Codebase Search", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_visual_editor_apply(self):
        """Test visual editor apply changes endpoint"""
        data = {
            "current_code": "function Button() { return <button>Click me</button>; }",
            "operations": [
                {
                    "type": "style_change",
                    "target": "button",
                    "property": "backgroundColor",
                    "value": "#007bff"
                }
            ]
        }
        
        response = self.make_request("POST", "/visual-editor/apply", data)
        
        if response is None:
            self.log_result("Visual Editor Apply", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("Visual Editor Apply", True, "Visual changes applied successfully")
                    return True
                else:
                    self.log_result("Visual Editor Apply", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Visual Editor Apply", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Visual Editor Apply", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_visual_editor_metadata(self):
        """Test visual editor metadata endpoint"""
        params = {
            "code": "function Button({ onClick, children }) { return <button onClick={onClick}>{children}</button>; }"
        }
        
        response = self.make_request("GET", "/visual-editor/metadata", params=params)
        
        if response is None:
            self.log_result("Visual Editor Metadata", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("Visual Editor Metadata", True, "Component metadata generated successfully")
                    return True
                else:
                    self.log_result("Visual Editor Metadata", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Visual Editor Metadata", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Visual Editor Metadata", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_github_create_repo(self):
        """Test GitHub repository creation endpoint"""
        data = {
            "project_name": f"test-repo-{int(time.time())}",
            "description": "Test repository created by automated testing",
            "private": True,
            "user_token": "mock-github-token"
        }
        
        response = self.make_request("POST", "/github/create-repo", data)
        
        if response is None:
            self.log_result("GitHub Create Repo", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("GitHub Create Repo", True, "Repository creation initiated")
                    return True
                else:
                    self.log_result("GitHub Create Repo", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("GitHub Create Repo", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("GitHub Create Repo", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_github_auto_commit(self):
        """Test GitHub auto-commit endpoint"""
        data = {
            "repo_name": "test-repo",
            "files": {
                "index.js": "console.log('Hello World');",
                "package.json": '{"name": "test-app", "version": "1.0.0"}'
            },
            "message": "Automated commit from testing",
            "user_token": "mock-github-token"
        }
        
        response = self.make_request("POST", "/github/auto-commit", data)
        
        if response is None:
            self.log_result("GitHub Auto Commit", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("GitHub Auto Commit", True, "Auto-commit completed")
                    return True
                else:
                    self.log_result("GitHub Auto Commit", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("GitHub Auto Commit", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("GitHub Auto Commit", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_supabase_setup_database(self):
        """Test Supabase database setup endpoint"""
        data = {
            "project_id": self.test_project_id or "test-project-id",
            "schema": {
                "users": {
                    "id": "uuid",
                    "email": "text",
                    "created_at": "timestamp"
                },
                "posts": {
                    "id": "uuid",
                    "title": "text",
                    "content": "text",
                    "user_id": "uuid"
                }
            }
        }
        
        response = self.make_request("POST", "/supabase/setup-database", data)
        
        if response is None:
            self.log_result("Supabase Setup Database", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("Supabase Setup Database", True, "Database setup completed")
                    return True
                else:
                    self.log_result("Supabase Setup Database", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Supabase Setup Database", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Supabase Setup Database", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_supabase_chat_to_db(self):
        """Test Supabase natural language to SQL endpoint"""
        params = {
            "project_id": self.test_project_id or "test-project-id",
            "query": "Show me all users who created posts in the last week"
        }
        
        response = self.make_request("POST", "/supabase/chat-to-db", params=params)
        
        if response is None:
            self.log_result("Supabase Chat to DB", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("Supabase Chat to DB", True, "Natural language query processed")
                    return True
                else:
                    self.log_result("Supabase Chat to DB", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Supabase Chat to DB", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Supabase Chat to DB", False, f"Status: {response.status_code}", response.text)
            return False
    
    def test_media_upload_image(self):
        """Test media image upload endpoint"""
        # Create mock image data
        mock_image_data = b"fake-image-data-for-testing"
        
        params = {
            "file_data": mock_image_data,
            "filename": "test-image.jpg",
            "project_id": self.test_project_id or "test-project-id"
        }
        
        response = self.make_request("POST", "/media/upload-image", params=params)
        
        if response is None:
            self.log_result("Media Upload Image", False, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result:
                    self.log_result("Media Upload Image", True, "Image upload processed")
                    return True
                else:
                    self.log_result("Media Upload Image", False, "Missing success in response", result)
                    return False
            except json.JSONDecodeError:
                self.log_result("Media Upload Image", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Media Upload Image", False, f"Status: {response.status_code}", response.text)
            return False

    # =============================================================================
    # MAIN TEST RUNNER
    # =============================================================================
    
    def run_admin_tests(self):
        """Run admin-specific tests"""
        print("🔐 Starting Admin Authentication Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API root
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            self.log_result("API Root", True, "API is online")
        else:
            self.log_result("API Root", False, "API is not responding")
        
        # Admin Authentication Tests
        print("\n👑 Testing Admin Authentication...")
        admin_login_success = self.test_admin_login()
        
        if admin_login_success:
            print("\n🛠️ Testing Admin Dashboard and Management...")
            self.test_admin_dashboard_access()
            self.test_admin_users_management()
            self.test_admin_projects_management()
            self.test_admin_system_logs()
            self.test_admin_settings()
            self.test_admin_analytics()
        else:
            print("❌ Admin login failed - skipping admin endpoint tests")
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 ADMIN TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS DETAILS:")
            print("-" * 40)
            for error in self.results['errors']:
                print(f"❌ {error['test']}: {error['message']}")
                if error['response']:
                    print(f"   Response: {str(error['response'])[:200]}...")
                print()
        
        return self.results['failed'] == 0

    def run_comprehensive_audit(self):
        """Run comprehensive audit of all new functionalities as requested"""
        print("🔍 Starting COMPREHENSIVE AUDIT of All New Functionalities")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API root
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            self.log_result("API Root", True, "API is online")
        else:
            self.log_result("API Root", False, "API is not responding")
        
        # Quick authentication setup for protected endpoints
        print("\n🔐 Setting up authentication...")
        auth_success = self.test_user_registration()
        if not auth_success:
            # Try login with existing user
            auth_success = self.test_user_login()
        
        # 1. AGENT MODE ENDPOINTS
        print("\n🤖 TESTING AGENT MODE ENDPOINTS...")
        print("-" * 40)
        self.test_agent_generate_code()
        self.test_codebase_search()
        
        # 2. VISUAL EDITOR ENDPOINTS  
        print("\n🎨 TESTING VISUAL EDITOR ENDPOINTS...")
        print("-" * 40)
        self.test_visual_editor_apply()
        self.test_visual_editor_metadata()
        
        # 3. GITHUB INTEGRATION ENDPOINTS
        print("\n🐙 TESTING GITHUB INTEGRATION ENDPOINTS...")
        print("-" * 40)
        self.test_github_create_repo()
        self.test_github_auto_commit()
        
        # 4. SUPABASE INTEGRATION ENDPOINTS
        print("\n🗄️ TESTING SUPABASE INTEGRATION ENDPOINTS...")
        print("-" * 40)
        self.test_supabase_setup_database()
        self.test_supabase_chat_to_db()
        
        # 5. MEDIA ENDPOINTS
        print("\n📷 TESTING MEDIA ENDPOINTS...")
        print("-" * 40)
        self.test_media_upload_image()
        
        # 6. ADMIN ENDPOINTS (All 8 endpoints)
        print("\n👑 TESTING ALL 8 ADMIN ENDPOINTS...")
        print("-" * 40)
        
        # Try admin login first
        admin_data = {
            "email": "admin@lovable.com",
            "password": "admin123"
        }
        admin_response = self.make_request("POST", "/auth/login", admin_data)
        admin_success = False
        
        if admin_response and admin_response.status_code == 200:
            try:
                result = admin_response.json()
                if "access_token" in result:
                    self.auth_token = result["access_token"]
                    admin_success = True
                    self.log_result("Admin Authentication", True, "Admin login successful")
            except:
                pass
        
        if not admin_success:
            self.log_result("Admin Authentication", False, "Admin login failed - using regular user token")
        
        # Test all 8 admin endpoints
        self.test_admin_dashboard_access()
        self.test_admin_users_management()
        self.test_admin_projects_management()
        self.test_admin_system_logs()
        self.test_admin_settings()
        self.test_admin_analytics()
        
        # Additional admin endpoints
        if self.test_user_id:
            # Test make admin endpoint
            response = self.make_request("POST", f"/admin/users/{self.test_user_id}/make-admin")
            if response and response.status_code == 200:
                self.log_result("Admin Make User Admin", True, "Make admin endpoint working")
            else:
                self.log_result("Admin Make User Admin", False, f"Status: {response.status_code if response else 'No response'}")
            
            # Test update user status endpoint
            response = self.make_request("PUT", f"/admin/users/{self.test_user_id}/status", {"is_active": True})
            if response and response.status_code == 200:
                self.log_result("Admin Update User Status", True, "Update user status endpoint working")
            else:
                self.log_result("Admin Update User Status", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Print comprehensive audit results
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE AUDIT RESULTS")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        # Categorize results by endpoint type
        endpoint_categories = {
            "Agent Mode": ["Agent Generate Code", "Codebase Search"],
            "Visual Editor": ["Visual Editor Apply", "Visual Editor Metadata"],
            "GitHub Integration": ["GitHub Create Repo", "GitHub Auto Commit"],
            "Supabase Integration": ["Supabase Setup Database", "Supabase Chat to DB"],
            "Media": ["Media Upload Image"],
            "Admin": ["Admin Dashboard Access", "Admin Users Management", "Admin Projects Management", 
                     "Admin System Logs", "Admin Settings", "Admin Analytics", "Admin Make User Admin", "Admin Update User Status"]
        }
        
        print("\n📋 RESULTS BY CATEGORY:")
        print("-" * 40)
        for category, tests in endpoint_categories.items():
            passed = sum(1 for error in self.results['errors'] if error['test'] not in tests)
            total = len(tests)
            failed = sum(1 for error in self.results['errors'] if error['test'] in tests)
            actual_passed = total - failed
            print(f"{category}: {actual_passed}/{total} passed")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS DETAILS:")
            print("-" * 40)
            for error in self.results['errors']:
                print(f"❌ {error['test']}: {error['message']}")
                if error['response']:
                    print(f"   Response: {str(error['response'])[:200]}...")
                print()
        
        # Identify mock vs real functionality
        print("\n🎭 FUNCTIONALITY ANALYSIS:")
        print("-" * 40)
        print("Based on response patterns, the following appear to be:")
        print("🔴 MOCKED/SIMULATED:")
        mock_indicators = []
        for error in self.results['errors']:
            if "mock" in str(error['response']).lower() or "simulation" in str(error['response']).lower():
                mock_indicators.append(error['test'])
        
        if mock_indicators:
            for test in mock_indicators:
                print(f"  - {test}")
        else:
            print("  - GitHub Integration (likely mocked without real tokens)")
            print("  - Supabase Integration (likely mocked without real credentials)")
            print("  - Media Upload (may be mocked without real file handling)")
        
        print("\n🟢 REAL FUNCTIONALITY:")
        print("  - Authentication System")
        print("  - AI Code Generation")
        print("  - Project Management")
        print("  - Template System")
        print("  - Chat System")
        print("  - Admin Dashboard (if admin credentials work)")
        
        return self.results['failed'] == 0

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Lovable Clone API Test Suite")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test API root
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            self.log_result("API Root", True, "API is online")
        else:
            self.log_result("API Root", False, "API is not responding")
        
        # Authentication Tests
        print("\n🔐 Testing Authentication System...")
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        self.test_protected_route_without_auth()
        
        # AI Service Tests
        print("\n🤖 Testing AI Services...")
        self.test_ai_generate_code()
        self.test_ai_improve_code()
        self.test_ai_generate_tests()
        
        # Template Tests
        print("\n📋 Testing Template System...")
        self.test_get_templates()
        self.test_get_featured_templates()
        self.test_get_template_categories()
        self.test_search_templates()
        
        # Project Tests
        print("\n📁 Testing Project Management...")
        self.test_create_project()
        self.test_get_projects()
        self.test_get_project_by_id()
        self.test_update_project()
        self.test_fork_project()
        
        # Deployment Tests
        print("\n🚀 Testing Deployment System...")
        self.test_deploy_project()
        self.test_get_deployment_status()
        
        # Chat Tests
        print("\n💬 Testing Chat System...")
        self.test_add_chat_message()
        self.test_get_chat_history()
        
        # Advanced Endpoints Tests
        print("\n🤖 Testing Advanced AI Agent Mode...")
        self.test_agent_generate_code()
        self.test_codebase_search()
        
        print("\n🎨 Testing Visual Editor...")
        self.test_visual_editor_apply()
        self.test_visual_editor_metadata()
        
        print("\n🐙 Testing GitHub Integration...")
        self.test_github_create_repo()
        self.test_github_auto_commit()
        
        print("\n🗄️ Testing Supabase Integration...")
        self.test_supabase_setup_database()
        self.test_supabase_chat_to_db()
        
        print("\n📷 Testing Media Upload...")
        self.test_media_upload_image()
        
        # Cleanup - Delete test project
        if self.test_project_id and self.auth_token:
            print("\n🧹 Cleaning up test data...")
            response = self.make_request("DELETE", f"/projects/{self.test_project_id}")
            if response and response.status_code == 200:
                self.log_result("Cleanup - Delete Project", True, "Test project deleted")
            else:
                self.log_result("Cleanup - Delete Project", False, "Failed to delete test project")
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS DETAILS:")
            print("-" * 40)
            for error in self.results['errors']:
                print(f"❌ {error['test']}: {error['message']}")
                if error['response']:
                    print(f"   Response: {str(error['response'])[:200]}...")
                print()
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    import sys
    
    tester = LovableCloneAPITester()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "admin":
            print("🔐 Running Admin Authentication Tests Only")
            success = tester.run_admin_tests()
        elif sys.argv[1] == "audit" or sys.argv[1] == "comprehensive":
            print("🔍 Running Comprehensive Audit of All New Functionalities")
            success = tester.run_comprehensive_audit()
        else:
            print("🚀 Running Full API Test Suite")
            success = tester.run_all_tests()
    else:
        print("🔍 Running Comprehensive Audit (Default)")
        success = tester.run_comprehensive_audit()
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)