import React, { useState, useEffect } from "react";
import { Plus, Search, Filter, Eye, Star, Fork, Calendar, Globe, Lock } from "lucide-react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import Header from "./Header";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("my"); // "my", "public", "featured"
  const [searchQuery, setSearchQuery] = useState("");
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, [filter, isAuthenticated]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const params = {};
      
      if (filter === "public" || !isAuthenticated) {
        params.public = true;
      }

      const response = await axios.get(`${API}/projects/`, { params });
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    } finally {
      setLoading(false);
    }
  };

  const createNewProject = () => {
    navigate("/editor", { 
      state: { prompt: "Create a new project..." }
    });
  };

  const openProject = (project) => {
    navigate("/editor", {
      state: {
        projectId: project.id,
        prompt: project.initial_prompt || `Open project: ${project.name}`,
        existingCode: project.generated_code
      }
    });
  };

  const forkProject = async (projectId, e) => {
    e.stopPropagation();
    
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    try {
      const response = await axios.post(`${API}/projects/${projectId}/fork`);
      navigate("/editor", {
        state: {
          projectId: response.data.id,
          prompt: `Forked project: ${response.data.name}`,
          existingCode: response.data.generated_code
        }
      });
    } catch (error) {
      console.error("Error forking project:", error);
    }
  };

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {filter === "my" ? "My Projects" : filter === "public" ? "Public Projects" : "Featured Projects"}
            </h1>
            <p className="text-gray-600">
              {filter === "my" 
                ? "Manage and edit your applications" 
                : "Discover amazing projects built by the community"
              }
            </p>
          </div>
          
          {isAuthenticated && (
            <button
              onClick={createNewProject}
              className="mt-4 sm:mt-0 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Project
            </button>
          )}
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          {/* Filter Tabs */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            {[
              { key: "public", label: "Public", icon: Globe },
              ...(isAuthenticated ? [{ key: "my", label: "My Projects", icon: Lock }] : []),
              { key: "featured", label: "Featured", icon: Star }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setFilter(tab.key)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center ${
                    filter === tab.key
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Projects Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
              <Plus className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              {searchQuery ? "No projects found" : "No projects yet"}
            </h3>
            <p className="text-gray-500 mb-6">
              {searchQuery 
                ? "Try adjusting your search criteria" 
                : "Create your first project to get started"
              }
            </p>
            {isAuthenticated && !searchQuery && (
              <button
                onClick={createNewProject}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Create New Project
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpen={openProject}
                onFork={forkProject}
                isOwner={user?.id === project.owner_id}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

const ProjectCard = ({ project, onOpen, onFork, isOwner }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-sm border hover:shadow-lg transition-all duration-200 cursor-pointer group overflow-hidden"
      onClick={() => onOpen(project)}
    >
      {/* Project Preview */}
      <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
        {project.preview_image ? (
          <img 
            src={project.preview_image} 
            alt={project.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-400 text-center">
              <div className="w-12 h-12 bg-gray-300 rounded mx-auto mb-2"></div>
              <p className="text-sm">No Preview</p>
            </div>
          </div>
        )}
        
        {/* Status Indicators */}
        <div className="absolute top-3 left-3 flex gap-2">
          {project.is_public ? (
            <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium flex items-center">
              <Globe className="w-3 h-3 mr-1" />
              Public
            </div>
          ) : (
            <div className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs font-medium flex items-center">
              <Lock className="w-3 h-3 mr-1" />
              Private
            </div>
          )}
          
          {project.deployment_url && (
            <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
              Live
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => onFork(project.id, e)}
            className="bg-white/90 hover:bg-white text-gray-700 p-2 rounded-full shadow-sm hover:shadow-md transition-all"
            title="Fork Project"
          >
            <Fork className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Project Info */}
      <div className="p-4">
        <div className="mb-3">
          <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">{project.name}</h3>
          {project.description && (
            <p className="text-gray-600 text-sm line-clamp-2">{project.description}</p>
          )}
        </div>

        {/* Tech Stack */}
        <div className="flex flex-wrap gap-1 mb-3">
          {project.tech_stack?.slice(0, 3).map((tech) => (
            <span 
              key={tech}
              className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded"
            >
              {tech}
            </span>
          ))}
        </div>

        {/* Stats and Meta */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-3">
            <div className="flex items-center">
              <Eye className="w-4 h-4 mr-1" />
              {project.views_count || 0}
            </div>
            <div className="flex items-center">
              <Star className="w-4 h-4 mr-1" />
              {project.likes_count || 0}
            </div>
            <div className="flex items-center">
              <Fork className="w-4 h-4 mr-1" />
              {project.forks_count || 0}
            </div>
          </div>
          
          <div className="flex items-center text-xs">
            <Calendar className="w-3 h-3 mr-1" />
            {formatDate(project.updated_at)}
          </div>
        </div>

        {/* Owner info (for public projects) */}
        {!isOwner && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center">
              <div className="w-6 h-6 bg-gray-300 rounded-full mr-2"></div>
              <span className="text-sm text-gray-600">
                by {project.owner_name || "Anonymous"}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectsPage;