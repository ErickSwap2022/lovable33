import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Play, Code, Smartphone, Monitor, Share, Download, Settings } from "lucide-react";
import ChatPanel from "./ChatPanel";
import PreviewPanel from "./PreviewPanel";
import CodePanel from "./CodePanel";
import { useAuth } from "../hooks/useAuth";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EditorPage = () => {
  const location = useLocation();
  const initialPrompt = location.state?.prompt || "";
  const { isAuthenticated } = useAuth();
  
  const [activeTab, setActiveTab] = useState("preview"); // preview, code
  const [viewMode, setViewMode] = useState("desktop"); // desktop, mobile
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [sessionId] = useState(() => Date.now().toString());
  const [showAuthWarning, setShowAuthWarning] = useState(false);

  useEffect(() => {
    if (initialPrompt) {
      handleGenerate(initialPrompt);
    }
  }, [initialPrompt]);

  const handleGenerate = async (prompt) => {
    setIsGenerating(true);
    setChatMessages(prev => [...prev, { type: "user", content: prompt }]);
    
    try {
      // Call backend to generate code
      const response = await axios.post(`${API}/ai/generate-code`, {
        prompt: prompt,
        session_id: sessionId
      });
      
      if (response.data.success) {
        setGeneratedCode(response.data.code);
        setChatMessages(prev => [...prev, { 
          type: "assistant", 
          content: response.data.message || "I've created your application! You can see the preview on the right and edit the code in the Code tab." 
        }]);
      } else {
        throw new Error("Failed to generate code");
      }
    } catch (error) {
      console.error("Error generating code:", error);
      
      // Show auth warning if user is not authenticated
      if (!isAuthenticated && (error.response?.status === 401 || error.response?.status === 403)) {
        setShowAuthWarning(true);
      }
      
      setChatMessages(prev => [...prev, { 
        type: "assistant", 
        content: "I'm having trouble generating your code right now. " + 
                 (!isAuthenticated ? "Try signing up for full access to all features!" : "Please try again in a moment.")
      }]);
      
      // Fallback to mock code
      const mockCode = generateMockCode(prompt);
      setGeneratedCode(mockCode);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateMockCode = (prompt) => {
    return `import React, { useState } from 'react';

const App = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Welcome to Your App
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Generated from: "${prompt}"
        </p>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-4">Interactive Counter</h2>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setCount(count - 1)}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              -
            </button>
            <span className="text-3xl font-bold text-gray-800">{count}</span>
            <button 
              onClick={() => setCount(count + 1)}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              +
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;`;
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-lg font-semibold text-gray-900">Lovable Editor</h1>
            
            {/* View Mode Toggle */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode("desktop")}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === "desktop" 
                    ? "bg-white shadow-sm text-gray-900" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Monitor className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode("mobile")}
                className={`p-2 rounded-md transition-colors ${
                  viewMode === "mobile" 
                    ? "bg-white shadow-sm text-gray-900" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Smartphone className="w-4 h-4" />
              </button>
            </div>

            {/* Tab Toggle */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab("preview")}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  activeTab === "preview" 
                    ? "bg-white shadow-sm text-gray-900" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Play className="w-4 h-4 inline mr-1" />
                Preview
              </button>
              <button
                onClick={() => setActiveTab("code")}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  activeTab === "code" 
                    ? "bg-white shadow-sm text-gray-900" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Code className="w-4 h-4 inline mr-1" />
                Code
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
              <Share className="w-4 h-4" />
            </button>
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
              <Download className="w-4 h-4" />
            </button>
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Chat Panel */}
        <ChatPanel 
          messages={chatMessages}
          onGenerate={handleGenerate}
          isGenerating={isGenerating}
          sessionId={sessionId}
        />

        {/* Preview/Code Panel */}
        <div className="flex-1 bg-white">
          {activeTab === "preview" ? (
            <PreviewPanel 
              code={generatedCode}
              viewMode={viewMode}
              isLoading={isGenerating}
            />
          ) : (
            <CodePanel code={generatedCode} />
          )}
        </div>
      </div>
    </div>
  );
};

export default EditorPage;