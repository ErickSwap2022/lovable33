// Mock data for the Lovable clone platform

export const mockProjects = [
  {
    id: "1",
    name: "E-commerce Landing",
    description: "Modern e-commerce landing page with product showcase",
    createdAt: "2024-12-20T10:00:00Z",
    updatedAt: "2024-12-20T15:30:00Z",
    thumbnail: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400",
    isPublic: true,
    technologies: ["React", "Tailwind CSS", "Framer Motion"]
  },
  {
    id: "2", 
    name: "SaaS Dashboard",
    description: "Clean dashboard interface for SaaS applications",
    createdAt: "2024-12-19T14:20:00Z",
    updatedAt: "2024-12-20T09:15:00Z",
    thumbnail: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400",
    isPublic: false,
    technologies: ["React", "Chart.js", "Material-UI"]
  },
  {
    id: "3",
    name: "Blog Platform",
    description: "Personal blog with CMS integration",
    createdAt: "2024-12-18T11:45:00Z", 
    updatedAt: "2024-12-19T16:22:00Z",
    thumbnail: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=400",
    isPublic: true,
    technologies: ["React", "Next.js", "Supabase"]
  }
];

export const mockTemplates = [
  {
    id: "t1",
    name: "Landing Page",
    description: "Perfect for showcasing your product or service",
    category: "Marketing",
    thumbnail: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
    features: ["Hero Section", "Features Grid", "Testimonials", "CTA"]
  },
  {
    id: "t2", 
    name: "Dashboard",
    description: "Complete admin dashboard with charts and analytics",
    category: "Business",
    thumbnail: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400",
    features: ["Charts", "Tables", "Navigation", "Responsive"]
  },
  {
    id: "t3",
    name: "E-commerce",
    description: "Online store with shopping cart and checkout",
    category: "Commerce", 
    thumbnail: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400",
    features: ["Product Grid", "Cart", "Checkout", "Search"]
  },
  {
    id: "t4",
    name: "Portfolio", 
    description: "Showcase your work with this professional portfolio",
    category: "Personal",
    thumbnail: "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400",
    features: ["Gallery", "About", "Contact", "Resume"]
  }
];

export const mockUserProfiles = [
  {
    id: "u1",
    name: "Sarah Chen",
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b5bb?w=100",
    role: "Product Designer",
    projects: 12,
    followers: 234
  },
  {
    id: "u2",
    name: "Alex Morgan", 
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100",
    role: "Frontend Developer", 
    projects: 8,
    followers: 156
  },
  {
    id: "u3",
    name: "Maria Garcia",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100", 
    role: "Full Stack Developer",
    projects: 15,
    followers: 342
  }
];

export const mockCommunityPosts = [
  {
    id: "p1",
    author: mockUserProfiles[0],
    title: "Building a Modern SaaS Landing Page", 
    excerpt: "Here's how I created a conversion-optimized landing page using Lovable's AI...",
    likes: 42,
    comments: 8,
    createdAt: "2024-12-20T08:30:00Z",
    tags: ["design", "saas", "landing-page"]
  },
  {
    id: "p2", 
    author: mockUserProfiles[1],
    title: "5 Tips for Better Dashboard UX",
    excerpt: "Dashboard design principles that make your data visualization more effective...", 
    likes: 67,
    comments: 12,
    createdAt: "2024-12-19T15:45:00Z",
    tags: ["ux", "dashboard", "tips"]
  },
  {
    id: "p3",
    author: mockUserProfiles[2], 
    title: "Rapid Prototyping with AI",
    excerpt: "How AI-powered development tools are changing the way we build applications...",
    likes: 89,
    comments: 15,
    createdAt: "2024-12-19T10:20:00Z", 
    tags: ["ai", "prototyping", "development"]
  }
];

export const mockCodeTemplates = {
  "landing-page": `import React from 'react';

const App = () => {
  return (
    <div className="min-h-screen bg-white">
      <header className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-4xl font-bold mb-4">Welcome to Our Product</h1>
          <p className="text-xl mb-8">The best solution for your business needs</p>
          <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100">
            Get Started
          </button>
        </div>
      </header>
      
      <main className="py-16">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <h3 className="text-2xl font-bold mb-4">Fast</h3>
              <p>Lightning fast performance for all your needs</p>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold mb-4">Reliable</h3>
              <p>99.9% uptime guarantee you can count on</p>
            </div>
            <div className="text-center">
              <h3 className="text-2xl font-bold mb-4">Secure</h3>
              <p>Enterprise-grade security for your data</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;`,

  "dashboard": `import React, { useState } from 'react';

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <aside className="w-64 bg-white shadow-lg">
          <div className="p-6">
            <h2 className="text-2xl font-bold">Dashboard</h2>
          </div>
          <nav className="mt-6">
            <a href="#" className="block px-6 py-3 text-gray-700 hover:bg-gray-100">
              Overview
            </a>
            <a href="#" className="block px-6 py-3 text-gray-700 hover:bg-gray-100">
              Analytics
            </a>
            <a href="#" className="block px-6 py-3 text-gray-700 hover:bg-gray-100">
              Users
            </a>
          </nav>
        </aside>
        
        <main className="flex-1 p-8">
          <h1 className="text-3xl font-bold mb-8">Welcome Back!</h1>
          
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm">Total Users</h3>
              <p className="text-3xl font-bold">12,456</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm">Revenue</h3>
              <p className="text-3xl font-bold">$45,678</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm">Orders</h3>
              <p className="text-3xl font-bold">1,234</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-500 text-sm">Growth</h3>
              <p className="text-3xl font-bold">+12%</p>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold mb-4">Recent Activity</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>New user registration</span>
                <span className="text-gray-500">2 min ago</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Order #1234 completed</span>
                <span className="text-gray-500">5 min ago</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;`
};