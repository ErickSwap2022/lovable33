import React from "react";
import { Loader } from "lucide-react";

const PreviewPanel = ({ code, viewMode, isLoading }) => {
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Generating your app...</p>
        </div>
      </div>
    );
  }

  if (!code) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-200 rounded-lg mx-auto mb-4 flex items-center justify-center">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-red-500 transform rotate-45"></div>
          </div>
          <p className="text-gray-600">Start chatting to see your app preview</p>
        </div>
      </div>
    );
  }

  // Simulate the generated app preview
  return (
    <div className="h-full bg-white">
      <div className={`h-full ${viewMode === "mobile" ? "max-w-sm mx-auto bg-gray-100 p-4" : ""}`}>
        <div className={`h-full ${viewMode === "mobile" ? "bg-white rounded-lg shadow-lg overflow-hidden" : ""}`}>
          <iframe
            srcDoc={generatePreviewHTML(code)}
            className="w-full h-full border-0"
            title="App Preview"
          />
        </div>
      </div>
    </div>
  );
};

const generatePreviewHTML = (code) => {
  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview</title>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
        <div id="root"></div>
        <script type="text/babel">
            ${code}
            
            const container = document.getElementById('root');
            const root = ReactDOM.createRoot(container);
            root.render(<App />);
        </script>
    </body>
    </html>
  `;
};

export default PreviewPanel;