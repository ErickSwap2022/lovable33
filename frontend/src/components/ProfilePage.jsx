import React, { useState } from "react";
import { User, Mail, Settings, LogOut, Edit3, Save, X } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import Header from "./Header";

const ProfilePage = () => {
  const { user, logout, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || "",
    username: user?.username || "",
    bio: user?.bio || ""
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = async () => {
    try {
      // Here you would make an API call to update the user
      // const response = await axios.put(`${API}/auth/profile`, formData);
      
      // For now, just update the local state
      updateUser({ ...user, ...formData });
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating profile:", error);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || "",
      username: user?.username || "",
      bio: user?.bio || ""
    });
    setIsEditing(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Profile Header */}
        <div className="bg-white rounded-lg shadow-sm border p-8 mb-8">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-6">
              {/* Avatar */}
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-white" />
              </div>
              
              {/* User Info */}
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-4">
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="text-2xl font-bold text-gray-900 bg-transparent border-b-2 border-blue-500 focus:outline-none"
                      placeholder="Your Name"
                    />
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600">@</span>
                      <input
                        type="text"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        className="text-gray-600 bg-transparent border-b border-gray-300 focus:outline-none focus:border-blue-500"
                        placeholder="username"
                      />
                    </div>
                    <textarea
                      name="bio"
                      value={formData.bio}
                      onChange={handleChange}
                      className="w-full text-gray-700 bg-transparent border border-gray-300 rounded-lg p-2 focus:outline-none focus:border-blue-500 resize-none"
                      placeholder="Tell us about yourself..."
                      rows={2}
                    />
                  </div>
                ) : (
                  <>
                    <h1 className="text-2xl font-bold text-gray-900">{user?.name}</h1>
                    <p className="text-gray-600 mb-2">
                      {user?.username ? `@${user.username}` : "No username set"}
                    </p>
                    <p className="text-gray-700">
                      {user?.bio || "No bio yet. Tell us about yourself!"}
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              {isEditing ? (
                <>
                  <button
                    onClick={handleSave}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    Save
                  </button>
                  <button
                    onClick={handleCancel}
                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors flex items-center"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors flex items-center"
                >
                  <Edit3 className="w-4 h-4 mr-2" />
                  Edit Profile
                </button>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 mt-8 pt-8 border-t border-gray-200">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{user?.projects_count || 0}</div>
              <div className="text-gray-600 text-sm">Projects</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{user?.followers_count || 0}</div>
              <div className="text-gray-600 text-sm">Followers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{user?.following_count || 0}</div>
              <div className="text-gray-600 text-sm">Following</div>
            </div>
          </div>
        </div>

        {/* Account Settings */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Account Settings</h2>
          
          <div className="space-y-4">
            {/* Email */}
            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="font-medium text-gray-900">Email Address</div>
                  <div className="text-gray-600 text-sm">{user?.email}</div>
                </div>
              </div>
              <button className="text-blue-600 hover:text-blue-500 font-medium">
                Change
              </button>
            </div>

            {/* Account Type */}
            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <Settings className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="font-medium text-gray-900">Account Type</div>
                  <div className="text-gray-600 text-sm">
                    {user?.is_premium ? "Premium" : "Free"}
                  </div>
                </div>
              </div>
              {!user?.is_premium && (
                <button className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all">
                  Upgrade to Premium
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-red-600 mb-6">Danger Zone</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
              <div>
                <div className="font-medium text-red-900">Sign Out</div>
                <div className="text-red-700 text-sm">Sign out of your account on this device</div>
              </div>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors flex items-center"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </button>
            </div>

            <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
              <div>
                <div className="font-medium text-red-900">Delete Account</div>
                <div className="text-red-700 text-sm">Permanently delete your account and all data</div>
              </div>
              <button className="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors">
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;