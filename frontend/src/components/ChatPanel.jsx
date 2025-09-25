import React, { useState, useRef, useEffect } from "react";
import { Send, Loader } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatPanel = ({ messages, onGenerate, isGenerating, sessionId }) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() && !isGenerating) {
      const messageText = input.trim();
      setInput("");
      
      // Call the onGenerate function which handles both UI updates and API calls
      onGenerate(messageText);
    }
  };

  const handleChatMessage = async (messageText) => {
    try {
      // This is for additional chat messages (not code generation)
      const response = await axios.post(`${API}/chat/${sessionId}`, {
        type: "user",
        content: messageText
      });
      
      if (response.data.success) {
        // Handle the response if needed
        console.log("Chat message sent successfully");
      }
    } catch (error) {
      console.error("Error sending chat message:", error);
    }
  };

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="font-semibold text-gray-900">Chat with Lovable</h2>
        <p className="text-sm text-gray-600">Describe what you want to build</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-8">
            Start a conversation to begin building your app
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.type === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-white text-gray-900 border border-gray-200"
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        ))}
        
        {isGenerating && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-900 border border-gray-200 p-3 rounded-lg flex items-center space-x-2">
              <Loader className="w-4 h-4 animate-spin" />
              <span className="text-sm">Generating your app...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Lovable to modify your app..."
            disabled={isGenerating}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!input.trim() || isGenerating}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        
        {/* Helper text */}
        <p className="text-xs text-gray-500 mt-2 text-center">
          Session ID: {sessionId?.slice(0, 8)}...
        </p>
      </div>
    </div>
  );
};

export default ChatPanel;