from typing import List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from models.template import Template, TemplateCreate

class TemplateService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_template(self, template_data: TemplateCreate, author_id: str) -> Template:
        """Create a new template"""
        template_dict = template_data.dict()
        template_dict["author_id"] = author_id
        
        template = Template(**template_dict)
        result = await self.db.templates.insert_one(template.dict())
        template.id = str(result.inserted_id)
        
        return template
    
    async def get_templates(self, category: str = None, skip: int = 0, limit: int = 20) -> List[Template]:
        """Get templates with optional category filter"""
        query = {}
        if category:
            query["category"] = category
        
        query["is_public"] = True
        
        templates = await self.db.templates.find(query).sort([
            ("is_featured", -1),
            ("usage_count", -1),
            ("created_at", -1)
        ]).skip(skip).limit(limit).to_list(limit)
        
        return [Template(**template) for template in templates]
    
    async def get_template_by_id(self, template_id: str) -> Template:
        """Get template by ID"""
        template = await self.db.templates.find_one({"id": template_id})
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return Template(**template)
    
    async def get_featured_templates(self, limit: int = 10) -> List[Template]:
        """Get featured templates"""
        templates = await self.db.templates.find({
            "is_featured": True,
            "is_public": True
        }).sort("usage_count", -1).limit(limit).to_list(limit)
        
        return [Template(**template) for template in templates]
    
    async def search_templates(self, query: str, skip: int = 0, limit: int = 20) -> List[Template]:
        """Search templates by name, description, or tags"""
        search_query = {
            "is_public": True,
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}}
            ]
        }
        
        templates = await self.db.templates.find(search_query).sort([
            ("usage_count", -1),
            ("created_at", -1)
        ]).skip(skip).limit(limit).to_list(limit)
        
        return [Template(**template) for template in templates]
    
    async def use_template(self, template_id: str) -> Template:
        """Increment usage count for template"""
        await self.db.templates.update_one(
            {"id": template_id},
            {"$inc": {"usage_count": 1}}
        )
        
        return await self.get_template_by_id(template_id)
    
    async def like_template(self, template_id: str, user_id: str) -> bool:
        """Like/unlike template"""
        # Check if already liked
        like = await self.db.template_likes.find_one({
            "template_id": template_id,
            "user_id": user_id
        })
        
        if like:
            # Unlike
            await self.db.template_likes.delete_one({
                "template_id": template_id,
                "user_id": user_id
            })
            await self.db.templates.update_one(
                {"id": template_id},
                {"$inc": {"likes_count": -1}}
            )
            return False
        else:
            # Like
            await self.db.template_likes.insert_one({
                "template_id": template_id,
                "user_id": user_id,
                "created_at": datetime.utcnow()
            })
            await self.db.templates.update_one(
                {"id": template_id},
                {"$inc": {"likes_count": 1}}
            )
            return True
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get template categories with counts"""
        pipeline = [
            {"$match": {"is_public": True}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        categories = await self.db.templates.aggregate(pipeline).to_list(None)
        
        return [
            {"name": cat["_id"], "count": cat["count"]}
            for cat in categories
        ]
    
    async def seed_default_templates(self):
        """Seed database with default templates"""
        default_templates = [
            {
                "name": "Landing Page",
                "description": "Modern landing page with hero section, features, and CTA",
                "category": "Marketing",
                "code": """import React from 'react';

const App = () => {
  return (
    <div className="min-h-screen bg-white">
      <header className="bg-blue-600 text-white py-20">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Welcome to Our Product</h1>
          <p className="text-xl mb-8 max-w-2xl mx-auto">The best solution for your business needs with cutting-edge technology</p>
          <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors">
            Get Started Free
          </button>
        </div>
      </header>
      
      <main className="py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-center mb-16">Why Choose Us?</h2>
          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Fast Performance</h3>
              <p className="text-gray-600">Lightning fast performance optimized for all your needs</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Reliable</h3>
              <p className="text-gray-600">99.9% uptime guarantee you can count on</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Secure</h3>
              <p className="text-gray-600">Enterprise-grade security for your data</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;""",
                "tags": ["landing", "hero", "features", "marketing"],
                "is_featured": True,
                "author_id": "system"
            },
            {
                "name": "Dashboard",
                "description": "Admin dashboard with sidebar navigation and analytics cards",
                "category": "Business",
                "code": """import React, { useState } from 'react';

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
        </div>
        <nav className="mt-6">
          {['Overview', 'Analytics', 'Users', 'Settings'].map((item) => (
            <button
              key={item}
              onClick={() => setActiveTab(item.toLowerCase())}
              className={`w-full text-left px-6 py-3 text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors ${
                activeTab === item.toLowerCase() ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600' : ''
              }`}
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>
      
      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back!</h1>
          <p className="text-gray-600">Here's what's happening with your business today.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { title: 'Total Users', value: '12,456', change: '+12%', color: 'blue' },
            { title: 'Revenue', value: '$45,678', change: '+8%', color: 'green' },
            { title: 'Orders', value: '1,234', change: '+23%', color: 'purple' },
            { title: 'Growth', value: '+12%', change: '+3%', color: 'orange' }
          ].map((stat, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-gray-500 text-sm font-medium">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
              <p className={`text-sm mt-2 text-${stat.color}-600`}>{stat.change} from last month</p>
            </div>
          ))}
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {[
              'New user registration from John Doe',
              'Order #1234 completed successfully',
              'Payment received for subscription',
              'New feature request submitted'
            ].map((activity, index) => (
              <div key={index} className="flex justify-between items-center py-3 border-b last:border-0">
                <span className="text-gray-700">{activity}</span>
                <span className="text-gray-500 text-sm">{5 + index} min ago</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;""",
                "tags": ["dashboard", "admin", "analytics", "business"],
                "is_featured": True,
                "author_id": "system"
            }
        ]
        
        for template_data in default_templates:
            existing = await self.db.templates.find_one({"name": template_data["name"]})
            if not existing:
                template = Template(**template_data)
                await self.db.templates.insert_one(template.dict())