import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ChevronDown, User, Settings, LogOut, Menu, X } from "lucide-react";
import { useAuth } from "../hooks/useAuth";

const Header = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate("/editor");
    } else {
      navigate("/signup");
    }
  };

  return (
    <header className="w-full px-8 py-4 bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between">
        {/* Logo and Navigation */}
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gradient-to-br from-orange-400 to-red-500 transform rotate-45"></div>
            <span className="text-xl font-bold text-gray-900">Lovable</span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link 
              to="/templates" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Templates
            </Link>
            <Link 
              to="/projects" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Projects
            </Link>
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
              to="/learn" 
              className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
            >
              Learn
            </Link>
          </nav>
        </div>

        {/* Desktop Auth/User Menu */}
        <div className="hidden md:flex items-center space-x-4">
          {isAuthenticated ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="font-medium">{user?.name}</span>
                <ChevronDown className="w-4 h-4" />
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <Link
                    to="/profile"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <User className="w-4 h-4 mr-2" />
                    Profile
                  </Link>
                  <Link
                    to="/projects"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    My Projects
                  </Link>
                  <hr className="my-1" />
                  <button
                    onClick={() => {
                      logout();
                      setShowUserMenu(false);
                    }}
                    className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link 
                to="/login" 
                className="text-gray-700 hover:text-gray-900 font-medium transition-colors"
              >
                Log in
              </Link>
              <button 
                onClick={handleGetStarted}
                className="px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-lg transition-all duration-200 hover:shadow-lg"
              >
                Get started
              </button>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setShowMobileMenu(!showMobileMenu)}
          className="md:hidden text-gray-700 hover:text-gray-900"
        >
          {showMobileMenu ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {showMobileMenu && (
        <div className="md:hidden mt-4 pb-4 border-t border-gray-200">
          <nav className="flex flex-col space-y-2 mt-4">
            <Link 
              to="/templates"
              className="text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
              onClick={() => setShowMobileMenu(false)}
            >
              Templates
            </Link>
            <Link 
              to="/projects"
              className="text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
              onClick={() => setShowMobileMenu(false)}
            >
              Projects
            </Link>
            <Link 
              to="/community"
              className="text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
              onClick={() => setShowMobileMenu(false)}
            >
              Community
            </Link>
            <Link 
              to="/pricing"
              className="text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
              onClick={() => setShowMobileMenu(false)}
            >
              Pricing
            </Link>
            <Link 
              to="/learn"
              className="text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
              onClick={() => setShowMobileMenu(false)}
            >
              Learn
            </Link>
            
            <hr className="my-2" />
            
            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setShowMobileMenu(false);
                  }}
                  className="flex items-center text-red-600 hover:text-red-700 font-medium py-2 px-4 rounded-lg hover:bg-red-50 transition-colors w-full text-left"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login"
                  className="text-gray-700 hover:text-gray-900 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
                  onClick={() => setShowMobileMenu(false)}
                >
                  Log in
                </Link>
                <button 
                  onClick={() => {
                    handleGetStarted();
                    setShowMobileMenu(false);
                  }}
                  className="mx-4 mt-2 px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white font-medium rounded-lg transition-all duration-200"
                >
                  Get started
                </button>
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;