import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import AdminLayout from './admin/AdminLayout';
import AdminDashboard from './admin/AdminDashboard';
import UserManagement from './admin/UserManagement';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Placeholder components
const ProjectManagement = () => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-xl font-bold mb-4">Project Management</h2>
    <p className="text-gray-600">Project management features coming soon...</p>
  </div>
);

const Analytics = () => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-xl font-bold mb-4">Analytics</h2>
    <p className="text-gray-600">Analytics dashboard coming soon...</p>
  </div>
);

const SystemLogs = () => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-xl font-bold mb-4">System Logs</h2>
    <p className="text-gray-600">System logs viewer coming soon...</p>
  </div>
);

const PlatformSettings = () => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-xl font-bold mb-4">Platform Settings</h2>
    <p className="text-gray-600">Platform configuration coming soon...</p>
  </div>
);

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    checkAdminStatus();
  }, [user, isAuthenticated]);

  const checkAdminStatus = async () => {
    if (!isAuthenticated || !user) {
      navigate('/login');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      // Try to access admin dashboard to check permissions
      await axios.get(`${API}/admin/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsAdmin(true);
    } catch (err) {
      console.error('Admin check failed:', err);
      setIsAdmin(false);
      navigate('/'); // Redirect to home if not admin
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <AdminDashboard />;
      case 'users':
        return <UserManagement />;
      case 'projects':
        return <ProjectManagement />;
      case 'analytics':
        return <Analytics />;
      case 'logs':
        return <SystemLogs />;
      case 'settings':
        return <PlatformSettings />;
      default:
        return <AdminDashboard />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking admin privileges...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-4">You don't have admin privileges to access this page.</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <AdminLayout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </AdminLayout>
  );
};

export default AdminPage;