import React, { useState, useEffect } from "react";
import { Search, Star, Eye, Download, Filter } from "lucide-react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Header from "./Header";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TemplatesPage = () => {
  const [templates, setTemplates] = useState([]);
  const [featuredTemplates, setFeaturedTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      searchTemplates();
    } else {
      fetchTemplates();
    }
  }, [selectedCategory, searchQuery]);

  const fetchInitialData = async () => {
    try {
      const [templatesRes, featuredRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/templates/`),
        axios.get(`${API}/templates/featured`),
        axios.get(`${API}/templates/categories`)
      ]);

      setTemplates(templatesRes.data);
      setFeaturedTemplates(featuredRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error("Error fetching templates:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const params = {};
      if (selectedCategory !== "all") {
        params.category = selectedCategory;
      }

      const response = await axios.get(`${API}/templates/`, { params });
      setTemplates(response.data);
    } catch (error) {
      console.error("Error fetching templates:", error);
    }
  };

  const searchTemplates = async () => {
    try {
      const response = await axios.get(`${API}/templates/search`, {
        params: { q: searchQuery }
      });
      setTemplates(response.data);
    } catch (error) {
      console.error("Error searching templates:", error);
    }
  };

  const useTemplate = async (templateId) => {
    try {
      const response = await axios.post(`${API}/templates/${templateId}/use`);
      
      // Navigate to editor with template
      navigate("/editor", { 
        state: { 
          prompt: `Use template: ${response.data.name}`,
          templateId: templateId,
          templateCode: response.data.code
        }
      });
    } catch (error) {
      console.error("Error using template:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Template
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Start building faster with our collection of professionally designed templates. 
            Each template is fully customizable and ready to use.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
            >
              <option value="all">All Categories</option>
              {categories.map((category) => (
                <option key={category.name} value={category.name}>
                  {category.name} ({category.count})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Featured Templates */}
        {featuredTemplates.length > 0 && !searchQuery && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredTemplates.map((template) => (
                <TemplateCard 
                  key={template.id} 
                  template={template} 
                  onUse={useTemplate}
                  featured={true}
                />
              ))}
            </div>
          </section>
        )}

        {/* All Templates */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {searchQuery ? `Search Results (${templates.length})` : "All Templates"}
          </h2>
          
          {templates.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No templates found</h3>
              <p className="text-gray-500">Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {templates.map((template) => (
                <TemplateCard 
                  key={template.id} 
                  template={template} 
                  onUse={useTemplate}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

const TemplateCard = ({ template, onUse, featured = false }) => {
  return (
    <div className={`bg-white rounded-lg shadow-sm border hover:shadow-lg transition-all duration-200 overflow-hidden group ${
      featured ? "ring-2 ring-blue-500" : ""
    }`}>
      {/* Template Preview */}
      <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
        {template.preview_image ? (
          <img 
            src={template.preview_image} 
            alt={template.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-400 text-center">
              <div className="w-12 h-12 bg-gray-300 rounded mx-auto mb-2"></div>
              <p className="text-sm">Preview</p>
            </div>
          </div>
        )}
        
        {featured && (
          <div className="absolute top-3 left-3">
            <div className="bg-yellow-400 text-yellow-900 px-2 py-1 rounded-full text-xs font-semibold flex items-center">
              <Star className="w-3 h-3 mr-1" />
              Featured
            </div>
          </div>
        )}
      </div>

      {/* Template Info */}
      <div className="p-4">
        <div className="mb-3">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{template.name}</h3>
          <p className="text-gray-600 text-sm line-clamp-2">{template.description}</p>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {template.tags?.slice(0, 3).map((tag) => (
            <span 
              key={tag}
              className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Stats */}
        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <Eye className="w-4 h-4 mr-1" />
              {template.usage_count || 0}
            </div>
            <div className="flex items-center">
              <Star className="w-4 h-4 mr-1" />
              {template.likes_count || 0}
            </div>
          </div>
          <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded text-xs">
            {template.category}
          </span>
        </div>

        {/* Action Button */}
        <button
          onClick={() => onUse(template.id)}
          className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center"
        >
          <Download className="w-4 h-4 mr-2" />
          Use Template
        </button>
      </div>
    </div>
  );
};

export default TemplatesPage;