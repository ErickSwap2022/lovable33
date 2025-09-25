import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  MoreVertical, 
  UserCheck, 
  UserX, 
  Shield,
  Mail,
  Calendar,
  FolderOpen
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showActionModal, setShowActionModal] = useState(false);

  const usersPerPage = 20;

  useEffect(() => {
    fetchUsers();
  }, [currentPage]);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      const skip = (currentPage - 1) * usersPerPage;
      const response = await axios.get(`${API}/admin/users?skip=${skip}&limit=${usersPerPage}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load users');
      console.error('Users error:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateUserStatus = async (userId, isActive) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/admin/users/${userId}/status`, 
        { is_active: isActive },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Update user in local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, is_active: isActive } : user
      ));
      
      setShowActionModal(false);
      setSelectedUser(null);
    } catch (err) {
      console.error('Error updating user status:', err);
      alert('Failed to update user status');
    }
  };

  const makeAdmin = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/admin/users/${userId}/make-admin`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('User granted admin privileges successfully');
      setShowActionModal(false);
      setSelectedUser(null);
    } catch (err) {
      console.error('Error making user admin:', err);
      alert('Failed to grant admin privileges');
    }
  };

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (user.username && user.username.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage platform users and permissions</p>
        </div>
        <div className="flex space-x-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Export Users
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search users..."
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex space-x-2">
            <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
              <Filter className="h-4 w-4 mr-1" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Projects
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {user.email.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.username || 'No username'}
                        </div>
                        <div className="text-sm text-gray-500 flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {user.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {user.is_verified && (
                      <span className="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        Verified
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <FolderOpen className="h-4 w-4 mr-1 text-gray-400" />
                      {user.projects_count}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      {formatDate(user.created_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => {
                        setSelectedUser(user);
                        setShowActionModal(true);
                      }}
                      className="p-2 hover:bg-gray-100 rounded-full"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-700">
              Showing page {currentPage}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={filteredUsers.length < usersPerPage}
                className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Action Modal */}
      {showActionModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Manage User: {selectedUser.email}
            </h3>
            
            <div className="space-y-3">
              <button
                onClick={() => updateUserStatus(selectedUser.id, !selectedUser.is_active)}
                className={`w-full flex items-center px-4 py-2 rounded-lg ${
                  selectedUser.is_active
                    ? 'text-red-700 bg-red-50 hover:bg-red-100'
                    : 'text-green-700 bg-green-50 hover:bg-green-100'
                }`}
              >
                {selectedUser.is_active ? (
                  <>
                    <UserX className="h-4 w-4 mr-2" />
                    Deactivate User
                  </>
                ) : (
                  <>
                    <UserCheck className="h-4 w-4 mr-2" />
                    Activate User
                  </>
                )}
              </button>

              <button
                onClick={() => makeAdmin(selectedUser.id)}
                className="w-full flex items-center px-4 py-2 text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg"
              >
                <Shield className="h-4 w-4 mr-2" />
                Make Admin
              </button>
            </div>

            <div className="mt-6 flex space-x-3">
              <button
                onClick={() => {
                  setShowActionModal(false);
                  setSelectedUser(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
};

export default UserManagement;