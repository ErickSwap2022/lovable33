import React, { useState } from "react";
import { Copy, Download, FileText } from "lucide-react";

const CodePanel = ({ code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!code) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">No code generated yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Code Header */}
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <span className="text-gray-300 text-sm font-medium">App.jsx</span>
          <span className="text-gray-500 text-xs">React</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Copy code"
          >
            <Copy className="w-4 h-4" />
          </button>
          <button
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Download code"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Code Content */}
      <div className="flex-1 overflow-auto">
        <pre className="p-4 text-sm text-gray-300 leading-relaxed">
          <code className="language-jsx">
            {code}
          </code>
        </pre>
      </div>

      {/* Copy Notification */}
      {copied && (
        <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-2 rounded-lg text-sm">
          Code copied!
        </div>
      )}
    </div>
  );
};

export default CodePanel;