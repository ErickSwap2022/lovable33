import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./components/HomePage";
import AuthPage from "./components/AuthPage";
import EditorPage from "./components/EditorPage";
import TemplatesPage from "./components/TemplatesPage";
import ProjectsPage from "./components/ProjectsPage";
import ProfilePage from "./components/ProfilePage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<AuthPage mode="login" />} />
            <Route path="/signup" element={<AuthPage mode="signup" />} />
            <Route path="/templates" element={<TemplatesPage />} />
            
            {/* Protected Routes */}
            <Route path="/editor" element={
              <ProtectedRoute>
                <EditorPage />
              </ProtectedRoute>
            } />
            <Route path="/projects" element={
              <ProtectedRoute>
                <ProjectsPage />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
            
            {/* Community Routes (Public but enhanced when authenticated) */}
            <Route path="/community" element={<div>Community Page - Coming Soon</div>} />
            <Route path="/pricing" element={<div>Pricing Page - Coming Soon</div>} />
            <Route path="/enterprise" element={<div>Enterprise Page - Coming Soon</div>} />
            <Route path="/learn" element={<div>Learn Page - Coming Soon</div>} />
            <Route path="/launched" element={<ProjectsPage />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;