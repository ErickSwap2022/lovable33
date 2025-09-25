import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem("lovable_token");
    const storedUser = localStorage.getItem("lovable_user");

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      
      // Set axios default header
      axios.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;
    }
    
    setLoading(false);
  }, []);

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`);
          setUser(response.data);
        } catch (error) {
          console.error("Token verification failed:", error);
          logout();
        }
      }
    };

    if (token && !loading) {
      verifyToken();
    }
  }, [token, loading]);

  const login = (authToken, userData) => {
    setToken(authToken);
    setUser(userData);
    
    // Store in localStorage
    localStorage.setItem("lovable_token", authToken);
    localStorage.setItem("lovable_user", JSON.stringify(userData));
    
    // Set axios default header
    axios.defaults.headers.common["Authorization"] = `Bearer ${authToken}`;
    
    // Navigate to dashboard or home
    navigate("/");
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    
    // Clear localStorage
    localStorage.removeItem("lovable_token");
    localStorage.removeItem("lovable_user");
    
    // Clear axios default header
    delete axios.defaults.headers.common["Authorization"];
    
    // Navigate to login
    navigate("/login");
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem("lovable_user", JSON.stringify(userData));
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated: !!token && !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};