import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Paperclip, Globe, Database, ArrowUp } from "lucide-react";
import Header from "./Header";

const HomePage = () => {
  const [prompt, setPrompt] = useState("");
  const navigate = useNavigate();

  const handleStartBuilding = () => {
    if (prompt.trim()) {
      navigate("/editor", { state: { prompt } });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleStartBuilding();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-purple-300 to-orange-400">
      <Header />
      
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center px-8 py-20">
        <div className="text-center mb-12 max-w-4xl">
          <h1 className="text-6xl font-bold text-gray-900 mb-4 leading-tight">
            Build something{" "}
            <span className="inline-flex items-center">
              <span className="w-8 h-8 bg-gradient-to-br from-orange-400 to-red-500 transform rotate-45 mr-3"></span>
            </span>
            Lovable
          </h1>
          <p className="text-xl text-gray-700 font-medium">
            Create apps and websites by chatting with AI
          </p>
        </div>

        {/* Chat Interface */}
        <div className="w-full max-w-2xl">
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
            <div className="flex flex-col space-y-4">
              {/* Input Area */}
              <div className="relative">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask Lovable to create a landing page for my..."
                  className="w-full min-h-[120px] p-4 pr-12 text-gray-800 placeholder-gray-500 bg-transparent resize-none focus:outline-none text-lg"
                  style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}
                />
                
                {/* Submit Button */}
                <button
                  type="button"
                  onClick={handleStartBuilding}
                  disabled={!prompt.trim()}
                  className="absolute bottom-3 right-3 p-2 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full transition-all duration-200 hover:scale-105"
                >
                  <ArrowUp className="w-5 h-5" />
                </button>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-2">
                <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100/50 rounded-lg transition-colors">
                  <Plus className="w-4 h-4" />
                </button>
                
                <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100/50 rounded-lg transition-colors">
                  <Paperclip className="w-4 h-4" />
                  Attach
                </button>
                
                <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100/50 rounded-lg transition-colors">
                  <Globe className="w-4 h-4" />
                  Public
                </button>
                
                <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-emerald-700 hover:text-emerald-800 hover:bg-emerald-50/50 rounded-lg transition-colors">
                  <Database className="w-4 h-4" />
                  Supabase
                </button>

                {/* Audio/Voice Button */}
                <div className="flex-1"></div>
                <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100/50 rounded-lg transition-colors">
                  <div className="flex items-center gap-1">
                    <div className="w-1 h-3 bg-gray-400 rounded-full"></div>
                    <div className="w-1 h-4 bg-gray-400 rounded-full"></div>
                    <div className="w-1 h-2 bg-gray-400 rounded-full"></div>
                    <div className="w-1 h-4 bg-gray-400 rounded-full"></div>
                  </div>
                </button>
              </div>
            </div>
          </div>
          
          {/* Helper text */}
          <p className="text-center text-gray-600 text-sm mt-4">
            Press Ctrl+Enter to start building
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;