import os
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

class ChatModeAgentService:
    """
    Chat Mode Agent - AI assistant that HELPS but doesn't edit code
    Multi-step reasoning, debugging, planning, file search, log inspection
    """
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def process_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Process user query with multi-step reasoning without editing code
        """
        try:
            # Determine query type
            query_type = await self._classify_query(query)
            
            # Route to appropriate handler
            if query_type == "debugging":
                return await self._handle_debugging_query(query, context, session_id)
            elif query_type == "planning":
                return await self._handle_planning_query(query, context, session_id)
            elif query_type == "file_search":
                return await self._handle_file_search_query(query, context, session_id)
            elif query_type == "log_analysis":
                return await self._handle_log_analysis_query(query, context, session_id)
            elif query_type == "database_query":
                return await self._handle_database_query(query, context, session_id)
            elif query_type == "explanation":
                return await self._handle_explanation_query(query, context, session_id)
            else:
                return await self._handle_general_query(query, context, session_id)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process query"
            }
    
    async def _classify_query(self, query: str) -> str:
        """Classify the type of query to route appropriately"""
        
        query_lower = query.lower()
        
        # Debugging keywords
        if any(word in query_lower for word in ["debug", "error", "bug", "fix", "broken", "not working"]):
            return "debugging"
        
        # Planning keywords
        if any(word in query_lower for word in ["plan", "architecture", "structure", "how should", "strategy"]):
            return "planning"
        
        # File search keywords
        if any(word in query_lower for word in ["find file", "search", "locate", "where is"]):
            return "file_search"
        
        # Log analysis keywords
        if any(word in query_lower for word in ["log", "console", "error log", "analyze log"]):
            return "log_analysis"
        
        # Database query keywords
        if any(word in query_lower for word in ["database", "query", "sql", "data", "table"]):
            return "database_query"
        
        # Explanation keywords
        if any(word in query_lower for word in ["what is", "how does", "explain", "what does"]):
            return "explanation"
        
        return "general"
    
    async def _handle_debugging_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle debugging queries with multi-step reasoning"""
        
        system_message = """You are a senior software engineer and debugging expert.
        
        Help users debug issues through multi-step reasoning:
        1. Understand the problem
        2. Analyze potential causes
        3. Suggest investigation steps
        4. Provide solutions
        
        DO NOT edit or generate code - only provide guidance, explanations, and debugging strategies.
        
        Be thorough, methodical, and educational in your approach."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"debug_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        debug_prompt = f"""
        DEBUGGING REQUEST: {query}
        
        CONTEXT:
        - Current Code: {context.get('current_code', 'No code provided')}
        - Error Messages: {context.get('errors', 'No errors provided')}
        - Browser Console: {context.get('console_logs', 'No console logs')}
        - Recent Changes: {context.get('recent_changes', 'No recent changes')}
        
        Please provide a multi-step debugging approach:
        
        1. **Problem Analysis**: What might be causing this issue?
        2. **Investigation Steps**: What should I check first?
        3. **Possible Solutions**: What are the likely fixes?
        4. **Prevention**: How can I avoid this in the future?
        
        Focus on teaching debugging methodology rather than just giving answers.
        """
        
        response = await chat.send_message(UserMessage(text=debug_prompt))
        
        return {
            "success": True,
            "type": "debugging_assistance",
            "response": response,
            "suggestions": [
                "Check browser console for errors",
                "Verify component props and state",
                "Test with simplified inputs"
            ]
        }
    
    async def _handle_planning_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle project planning and architecture queries"""
        
        system_message = """You are a senior technical architect and project planner.
        
        Help users plan and structure their projects through strategic thinking:
        1. Break down complex requirements
        2. Suggest architectural approaches
        3. Identify potential challenges
        4. Recommend best practices
        
        Provide guidance without writing actual code - focus on planning and strategy."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"planning_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        planning_prompt = f"""
        PLANNING REQUEST: {query}
        
        PROJECT CONTEXT:
        - Project Type: {context.get('project_type', 'Not specified')}
        - Target Users: {context.get('target_users', 'Not specified')}
        - Technical Requirements: {context.get('tech_requirements', 'Not specified')}
        - Timeline: {context.get('timeline', 'Not specified')}
        
        Please provide strategic planning guidance:
        
        1. **Requirements Analysis**: What are the core needs?
        2. **Architecture Recommendations**: How should this be structured?
        3. **Implementation Strategy**: What's the best approach?
        4. **Risk Assessment**: What challenges should I anticipate?
        5. **Next Steps**: What should I work on first?
        
        Focus on strategic thinking and planning methodology.
        """
        
        response = await chat.send_message(UserMessage(text=planning_prompt))
        
        return {
            "success": True,
            "type": "planning_assistance",
            "response": response,
            "recommendations": [
                "Start with MVP features",
                "Plan for scalability",
                "Consider user experience"
            ]
        }
    
    async def _handle_file_search_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle file search and location queries"""
        
        project_files = context.get('project_files', [])
        search_term = self._extract_search_term(query)
        
        # Perform intelligent file search
        search_results = []
        
        for file in project_files:
            file_path = file.get('path', '')
            file_content = file.get('content', '')
            
            # Search in file path
            if search_term.lower() in file_path.lower():
                search_results.append({
                    "file": file_path,
                    "match_type": "filename",
                    "relevance": 0.9
                })
            
            # Search in file content
            elif search_term.lower() in file_content.lower():
                # Find the line with the match
                lines = file_content.split('\n')
                for i, line in enumerate(lines):
                    if search_term.lower() in line.lower():
                        search_results.append({
                            "file": file_path,
                            "match_type": "content",
                            "line_number": i + 1,
                            "line_content": line.strip(),
                            "relevance": 0.7
                        })
                        break
        
        # Sort by relevance
        search_results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return {
            "success": True,
            "type": "file_search",
            "query": query,
            "search_term": search_term,
            "results": search_results[:10],  # Top 10 results
            "total_found": len(search_results)
        }
    
    async def _handle_log_analysis_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle log analysis queries"""
        
        system_message = """You are an expert in log analysis and system monitoring.
        
        Analyze logs to help identify issues, patterns, and solutions:
        1. Parse log entries for errors and warnings
        2. Identify patterns and root causes
        3. Suggest investigation paths
        4. Recommend monitoring improvements
        
        Provide insights without writing code - focus on analysis and interpretation."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"logs_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        logs = context.get('logs', [])
        
        log_analysis_prompt = f"""
        LOG ANALYSIS REQUEST: {query}
        
        RECENT LOGS:
        {chr(10).join(logs[-50:]) if logs else 'No logs provided'}
        
        Please analyze these logs and provide:
        
        1. **Error Summary**: What errors are occurring?
        2. **Pattern Analysis**: Are there recurring issues?
        3. **Root Cause**: What might be causing these problems?
        4. **Investigation Steps**: What should I check next?
        5. **Monitoring Recommendations**: How can I better track this?
        
        Focus on helping me understand what the logs are telling us.
        """
        
        response = await chat.send_message(UserMessage(text=log_analysis_prompt))
        
        # Extract key metrics from logs
        error_count = len([log for log in logs if 'error' in log.lower()])
        warning_count = len([log for log in logs if 'warning' in log.lower()])
        
        return {
            "success": True,
            "type": "log_analysis",
            "response": response,
            "metrics": {
                "total_logs": len(logs),
                "errors": error_count,
                "warnings": warning_count
            }
        }
    
    async def _handle_database_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle database-related queries"""
        
        system_message = """You are a database expert and SQL consultant.
        
        Help users understand and work with databases:
        1. Explain database concepts
        2. Suggest query approaches
        3. Help with data modeling
        4. Provide best practices
        
        Guide without writing actual SQL - focus on explanation and strategy."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"database_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        db_prompt = f"""
        DATABASE QUERY: {query}
        
        DATABASE CONTEXT:
        - Schema: {context.get('database_schema', 'Not provided')}
        - Tables: {context.get('tables', 'Not specified')}
        - Current Issue: {context.get('db_issue', 'Not specified')}
        
        Please provide database guidance:
        
        1. **Understanding**: What data are we working with?
        2. **Approach**: What's the best strategy for this query?
        3. **Considerations**: What should I be careful about?
        4. **Optimization**: How can I make this efficient?
        5. **Best Practices**: What patterns should I follow?
        
        Focus on teaching database concepts and query strategy.
        """
        
        response = await chat.send_message(UserMessage(text=db_prompt))
        
        return {
            "success": True,
            "type": "database_consultation",
            "response": response
        }
    
    async def _handle_explanation_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle explanation and educational queries"""
        
        system_message = """You are an expert technical educator and mentor.
        
        Explain complex concepts in clear, understandable ways:
        1. Break down complex topics
        2. Use analogies and examples
        3. Provide context and background
        4. Suggest learning resources
        
        Focus on education and understanding rather than code implementation."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"explanation_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        explanation_prompt = f"""
        EXPLANATION REQUEST: {query}
        
        CONTEXT:
        - User Level: {context.get('user_level', 'intermediate')}
        - Specific Interest: {context.get('specific_focus', 'general understanding')}
        
        Please provide a clear explanation:
        
        1. **Overview**: What is this concept?
        2. **How It Works**: What's the underlying mechanism?
        3. **Why It Matters**: Why is this important to understand?
        4. **Real-World Examples**: How is this used in practice?
        5. **Learning Path**: What should I study next?
        
        Make it educational and easy to understand.
        """
        
        response = await chat.send_message(UserMessage(text=explanation_prompt))
        
        return {
            "success": True,
            "type": "explanation",
            "response": response
        }
    
    async def _handle_general_query(self, query: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle general queries"""
        
        system_message = """You are a helpful AI assistant specializing in web development and software engineering.
        
        Provide helpful, accurate information and guidance while being conversational and supportive.
        Focus on helping users learn and understand rather than just providing answers."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"general_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        response = await chat.send_message(UserMessage(text=query))
        
        return {
            "success": True,
            "type": "general_assistance",
            "response": response
        }
    
    def _extract_search_term(self, query: str) -> str:
        """Extract search term from file search query"""
        
        # Common patterns for file search queries
        patterns = [
            r'find\s+(?:file\s+)?(?:named\s+)?["\']?([^"\']+)["\']?',
            r'locate\s+["\']?([^"\']+)["\']?',
            r'search\s+for\s+["\']?([^"\']+)["\']?',
            r'where\s+is\s+["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: use the whole query
        return query.strip()
    
    async def multi_step_reasoning(self, problem: str, context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Perform multi-step reasoning for complex problems"""
        
        system_message = """You are an expert problem solver with advanced reasoning capabilities.
        
        Break down complex problems into steps:
        1. Problem decomposition
        2. Analysis of each component  
        3. Logical reasoning chain
        4. Solution synthesis
        5. Validation and alternatives
        
        Think step by step and show your reasoning process."""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"reasoning_{session_id}",
            system_message=system_message
        ).with_model("anthropic", "claude-3-5-sonnet-20241022")
        
        reasoning_prompt = f"""
        COMPLEX PROBLEM: {problem}
        
        AVAILABLE CONTEXT: {json.dumps(context, indent=2)}
        
        Please use multi-step reasoning to analyze this problem:
        
        Step 1: **Problem Breakdown** - What are the key components?
        Step 2: **Information Analysis** - What do we know and what's missing?
        Step 3: **Logical Chain** - What's the reasoning path?
        Step 4: **Solution Approach** - What's the best strategy?
        Step 5: **Validation** - How can we verify this approach?
        
        Show your thinking process clearly at each step.
        """
        
        response = await chat.send_message(UserMessage(text=reasoning_prompt))
        
        # Parse reasoning steps from response
        reasoning_steps = []
        step_pattern = r'Step \d+:.*?(?=Step \d+:|$)'
        matches = re.findall(step_pattern, response.text, re.DOTALL)
        
        for match in matches:
            reasoning_steps.append(match.strip())
        
        return {
            "success": True,
            "type": "multi_step_reasoning",
            "problem": problem,
            "reasoning_steps": reasoning_steps,
            "solution": response.text,
            "analysis": f"Multi-step analysis completed with {len(reasoning_steps)} reasoning steps",
            "context_used": context
        }