import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="w-full px-8 py-4">
      <div className="flex items-center justify-between">
        {/* Logo and Navigation */}
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gradient-to-br from-orange-400 to-red-500 transform rotate-45"></div>
            <span className="text-xl font-bold text-gray-900">Lovable</span>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link 
              to="/community" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Community
            </Link>
            <Link 
              to="/pricing" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Pricing
            </Link>
            <Link 
              to="/enterprise" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Enterprise
            </Link>
            <Link 
              to="/learn" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Learn
            </Link>
            <Link 
              to="/launched" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Launched
            </Link>
          </nav>
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center space-x-4">
          <Link 
            to="/login" 
            className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
          >
            Log in
          </Link>
          <Link 
            to="/signup" 
            className="px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-lg transition-all duration-200 hover:shadow-lg"
          >
            Get started
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;