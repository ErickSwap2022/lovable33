import os
import asyncio
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def generate_code(self, prompt: str, session_id: str) -> str:
        """Generate React code based on user prompt"""
        try:
            # Initialize chat with code generation system message
            system_message = """You are an expert React developer. Generate clean, modern React components based on user prompts.

Rules:
1. Always return complete, valid React functional components
2. Use modern React hooks (useState, useEffect, etc.) when needed
3. Use Tailwind CSS for styling
4. Make components responsive and accessible
5. Include interactive elements when appropriate
6. Return ONLY the React component code, no explanations
7. Use TypeScript syntax when beneficial
8. Include proper imports (React, useState, etc.)

Example format:
```jsx
import React, { useState } from 'react';

const App = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Your component JSX here */}
    </div>
  );
};

export default App;
```"""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"code_gen_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")

            # Create enhanced prompt for code generation
            enhanced_prompt = f"""Create a React component for: {prompt}

Requirements:
- Use functional components with hooks
- Style with Tailwind CSS
- Make it responsive and modern
- Include interactive elements where appropriate
- Ensure accessibility
- Return complete, ready-to-use code"""

            user_message = UserMessage(text=enhanced_prompt)
            response = await chat.send_message(user_message)
            
            # Extract code from response (remove markdown if present)
            code = response.strip()
            if code.startswith('```jsx') or code.startswith('```javascript') or code.startswith('```'):
                lines = code.split('\n')
                # Remove first and last lines if they're markdown
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                code = '\n'.join(lines)
            
            return code
            
        except Exception as e:
            print(f"Error generating code: {e}")
            # Return a fallback component
            return self._get_fallback_component(prompt)
    
    async def generate_response(self, prompt: str, session_id: str) -> str:
        """Generate conversational AI response"""
        try:
            system_message = """You are Lovable AI, a helpful assistant that helps users build applications through conversation.

Your role:
1. Help users refine their app ideas
2. Suggest improvements and features
3. Answer questions about the generated code
4. Provide guidance on UI/UX best practices
5. Be encouraging and supportive

Keep responses conversational, helpful, and focused on development."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"chat_{session_id}",
                system_message=system_message
            ).with_model("openai", "gpt-4o-mini")

            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble processing your request right now. Please try again in a moment."
    
    def _get_fallback_component(self, prompt: str) -> str:
        """Return a fallback component when AI generation fails"""
        return f"""import React, {{ useState }} from 'react';

const App = () => {{
  const [message, setMessage] = useState('Hello World');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Your Application
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Generated from: "{prompt}"
        </p>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-4">Welcome!</h2>
          <p className="text-gray-600 mb-4">{{message}}</p>
          <button 
            onClick={{() => setMessage('Component is working!')}}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Click me
          </button>
        </div>
      </div>
    </div>
  );
}};

export default App;"""