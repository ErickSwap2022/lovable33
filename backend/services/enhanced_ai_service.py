import os
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class EnhancedAIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def generate_code(self, prompt: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate React code with enhanced features"""
        try:
            # Enhanced system message for better code generation
            system_message = """You are an expert React/TypeScript developer and UI/UX designer. Generate production-ready, modern web applications.

TECHNICAL REQUIREMENTS:
- Use React 18+ with functional components and hooks
- Use TypeScript for type safety
- Use Tailwind CSS for styling with modern design principles
- Implement responsive design (mobile-first)
- Include proper accessibility (ARIA labels, semantic HTML)
- Add smooth animations and transitions
- Use modern ES6+ syntax

DESIGN PRINCIPLES:
- Clean, minimalist interfaces
- Consistent spacing and typography
- Professional color schemes
- Intuitive user experience
- Modern UI patterns (cards, gradients, shadows)

STRUCTURE:
- Always return complete, production-ready components
- Include proper imports
- Use meaningful component and variable names
- Add helpful comments for complex logic
- Ensure code is properly formatted

RESPONSE FORMAT:
Return ONLY valid React/TypeScript code without markdown formatting."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"enhanced_code_{session_id}",
                system_message=system_message
            ).with_model("anthropic", "claude-3-5-sonnet-20241022")

            # Enhanced prompt with context
            enhanced_prompt = self._build_enhanced_prompt(prompt, context)

            user_message = UserMessage(text=enhanced_prompt)
            response = await chat.send_message(user_message)
            
            # Clean and validate the response
            code = self._clean_code_response(response)
            
            # Generate additional metadata
            metadata = await self.generate_metadata(prompt, code, session_id)
            
            return {
                "code": code,
                "metadata": metadata,
                "prompt": prompt,
                "success": True
            }
            
        except Exception as e:
            print(f"Error generating enhanced code: {e}")
            return {
                "code": self._get_fallback_component(prompt),
                "metadata": {
                    "title": "Fallback Component",
                    "description": "A basic component generated due to an error",
                    "tech_stack": ["React", "Tailwind CSS"],
                    "features": ["Basic UI"]
                },
                "prompt": prompt,
                "success": False,
                "error": str(e)
            }
    
    def _build_enhanced_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Build an enhanced prompt with context"""
        base_prompt = f"Create a React application for: {prompt}\n\n"
        
        base_prompt += """REQUIREMENTS:
- Modern, professional design
- Fully responsive layout
- Smooth animations and hover effects
- Proper accessibility features
- Clean, maintainable code structure
- Interactive elements where appropriate
- Beautiful color scheme and typography
"""
        
        if context:
            if context.get("style"):
                base_prompt += f"- Style preference: {context['style']}\n"
            if context.get("features"):
                base_prompt += f"- Required features: {', '.join(context['features'])}\n"
            if context.get("tech_stack"):
                base_prompt += f"- Tech stack: {', '.join(context['tech_stack'])}\n"
        
        base_prompt += "\nGenerate complete, production-ready code with excellent UX."
        
        return base_prompt
    
    def _clean_code_response(self, response: str) -> str:
        """Clean and format the AI response"""
        code = response.strip()
        
        # Remove markdown code blocks if present
        if code.startswith('```'):
            lines = code.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        return code.strip()
    
    async def generate_metadata(self, prompt: str, code: str, session_id: str) -> Dict[str, Any]:
        """Generate metadata for the generated code"""
        try:
            system_message = """Analyze the React code and generate metadata in JSON format.

Return a JSON object with:
- title: A descriptive title for the component
- description: A brief description of what it does
- tech_stack: Array of technologies used
- features: Array of key features implemented
- color_scheme: The main colors used
- complexity: "simple", "medium", or "complex"
- category: The type of application (e.g., "Landing Page", "Dashboard", "E-commerce")"""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"metadata_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")

            analysis_prompt = f"""Analyze this React component and generate metadata:

Original prompt: {prompt}

Code:
{code}

Return only valid JSON without any markdown formatting."""

            user_message = UserMessage(text=analysis_prompt)
            response = await chat.send_message(user_message)
            
            # Parse JSON response
            try:
                metadata = json.loads(response.strip())
            except json.JSONDecodeError:
                # Fallback metadata
                metadata = {
                    "title": "React Component",
                    "description": "A React component generated from user prompt",
                    "tech_stack": ["React", "Tailwind CSS"],
                    "features": ["Responsive Design", "Modern UI"],
                    "color_scheme": ["blue", "gray"],
                    "complexity": "medium",
                    "category": "General"
                }
            
            return metadata
            
        except Exception as e:
            print(f"Error generating metadata: {e}")
            return {
                "title": "React Component",
                "description": "A React component",
                "tech_stack": ["React"],
                "features": [],
                "color_scheme": [],
                "complexity": "medium",
                "category": "General"
            }
    
    async def suggest_improvements(self, code: str, session_id: str) -> List[str]:
        """Suggest improvements for existing code"""
        try:
            system_message = """You are a senior React developer doing code review. Analyze the code and suggest specific improvements.

Focus on:
- Performance optimizations
- Accessibility improvements
- Better user experience
- Code quality and maintainability
- Modern React patterns

Return a JSON array of improvement suggestions."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"improvements_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")

            user_message = UserMessage(text=f"Analyze this React code and suggest improvements:\n\n{code}")
            response = await chat.send_message(user_message)
            
            try:
                suggestions = json.loads(response.strip())
                return suggestions if isinstance(suggestions, list) else []
            except json.JSONDecodeError:
                return ["Consider adding error boundaries", "Implement loading states", "Add accessibility features"]
                
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []
    
    async def generate_tests(self, code: str, session_id: str) -> str:
        """Generate Jest/React Testing Library tests for the code"""
        try:
            system_message = """Generate comprehensive Jest and React Testing Library tests for the given React component.

Include:
- Render tests
- User interaction tests  
- Accessibility tests
- Edge case testing
- Proper test structure and descriptions

Use modern testing patterns and best practices."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"tests_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")

            user_message = UserMessage(text=f"Generate tests for this React component:\n\n{code}")
            response = await chat.send_message(user_message)
            
            return self._clean_code_response(response)
            
        except Exception as e:
            print(f"Error generating tests: {e}")
            return "// Error generating tests"
    
    def _get_fallback_component(self, prompt: str) -> str:
        """Return an enhanced fallback component"""
        return f"""import React, {{ useState, useEffect }} from 'react';

const App = () => {{
  const [isLoaded, setIsLoaded] = useState(false);
  const [message, setMessage] = useState('Hello, World!');

  useEffect(() => {{
    const timer = setTimeout(() => setIsLoaded(true), 500);
    return () => clearTimeout(timer);
  }}, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="container mx-auto px-6 py-12">
        <div className={{`transition-all duration-700 transform ${{
          isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
        }}`}}>
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-8">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mx-auto mb-6 flex items-center justify-center">
                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd"/>
                </svg>
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Your Application
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Generated from: "{prompt}"
              </p>
            </div>
            
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Interactive Demo
              </h2>
              <div className="flex flex-col items-center space-y-4">
                <p className="text-lg text-gray-700 mb-4">{{message}}</p>
                <div className="flex space-x-4">
                  <button 
                    onClick={{() => setMessage('Button clicked! 🎉')}}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
                  >
                    Click Me
                  </button>
                  <button 
                    onClick={{() => setMessage('Reset complete!')}}
                    className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transform hover:scale-105 transition-all duration-200"
                  >
                    Reset
                  </button>
                </div>
              </div>
            </div>
            
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-900 mb-2">Modern Design</h3>
                <p className="text-gray-600 text-sm">Clean, responsive interface built with Tailwind CSS</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-900 mb-2">Interactive</h3>
                <p className="text-gray-600 text-sm">Engaging user experience with smooth animations</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="font-semibold text-gray-900 mb-2">Accessible</h3>
                <p className="text-gray-600 text-sm">Built with accessibility and usability in mind</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}};

export default App;"""