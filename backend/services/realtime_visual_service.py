import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

class RealtimeVisualService:
    """
    Real-time Visual Editor with Hot Module Reloading
    Provides immediate visual feedback like Vite HMR
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.component_cache = {}
        
    async def start_visual_session(self, session_id: str, initial_code: str) -> Dict[str, Any]:
        """Start a real-time visual editing session"""
        
        try:
            # Parse initial code structure
            parsed_structure = await self._parse_code_structure(initial_code)
            
            # Create session
            session = {
                "session_id": session_id,
                "current_code": initial_code,
                "component_tree": parsed_structure,
                "change_history": [],
                "created_at": datetime.utcnow(),
                "last_update": datetime.utcnow()
            }
            
            self.active_sessions[session_id] = session
            
            return {
                "success": True,
                "session_id": session_id,
                "component_tree": parsed_structure,
                "message": "Visual editing session started"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start visual session"
            }
    
    async def apply_realtime_change(self, session_id: str, change: Dict[str, Any]) -> Dict[str, Any]:
        """Apply visual change with immediate feedback"""
        
        try:
            if session_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = self.active_sessions[session_id]
            
            # Apply change to component tree
            updated_tree = await self._apply_change_to_tree(session["component_tree"], change)
            
            # Generate updated code
            updated_code = await self._generate_code_from_tree(updated_tree)
            
            # Create change record
            change_record = {
                "timestamp": datetime.utcnow(),
                "change_type": change["type"],
                "component_id": change.get("component_id"),
                "old_value": change.get("old_value"),
                "new_value": change.get("new_value"),
                "change_data": change
            }
            
            # Update session
            session["current_code"] = updated_code
            session["component_tree"] = updated_tree
            session["change_history"].append(change_record)
            session["last_update"] = datetime.utcnow()
            
            # Generate hot reload patch
            hot_reload_patch = await self._generate_hot_reload_patch(change, updated_code)
            
            return {
                "success": True,
                "updated_code": updated_code,
                "component_tree": updated_tree,
                "hot_reload_patch": hot_reload_patch,
                "change_applied": change_record,
                "message": "Change applied with real-time feedback"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to apply real-time change"
            }
    
    async def _parse_code_structure(self, code: str) -> Dict[str, Any]:
        """Parse React code into component tree structure"""
        
        # Basic JSX parsing - in production, use proper AST parser
        import re
        
        components = []
        component_id = 0
        
        # Find JSX elements
        jsx_pattern = r'<(\w+)([^>]*?)(?:\s*/\s*>|>(.*?)</\1>)'
        matches = re.finditer(jsx_pattern, code, re.DOTALL)
        
        for match in matches:
            tag_name = match.group(1)
            attributes = match.group(2) if match.group(2) else ""
            content = match.group(3) if match.group(3) else ""
            
            # Parse attributes
            attrs = {}
            attr_pattern = r'(\w+)=(?:"([^"]*)"|{([^}]*)})'
            for attr_match in re.finditer(attr_pattern, attributes):
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2) or attr_match.group(3)
                attrs[attr_name] = attr_value
            
            component = {
                "id": f"comp_{component_id}",
                "type": tag_name,
                "attributes": attrs,
                "content": content.strip() if content else "",
                "position": {
                    "start": match.start(),
                    "end": match.end()
                },
                "children": []
            }
            
            components.append(component)
            component_id += 1
        
        return {
            "components": components,
            "root_component": components[0] if components else None,
            "structure_version": 1
        }
    
    async def _apply_change_to_tree(self, component_tree: Dict[str, Any], change: Dict[str, Any]) -> Dict[str, Any]:
        """Apply visual change to component tree"""
        
        change_type = change["type"]
        updated_tree = json.loads(json.dumps(component_tree))  # Deep copy
        
        if change_type == "update_style":
            return await self._apply_style_change(updated_tree, change)
        elif change_type == "update_content":
            return await self._apply_content_change(updated_tree, change)
        elif change_type == "add_component":
            return await self._apply_add_component(updated_tree, change)
        elif change_type == "remove_component":
            return await self._apply_remove_component(updated_tree, change)
        elif change_type == "move_component":
            return await self._apply_move_component(updated_tree, change)
        
        return updated_tree
    
    async def _apply_style_change(self, tree: Dict[str, Any], change: Dict[str, Any]) -> Dict[str, Any]:
        """Apply style change to component"""
        
        component_id = change["component_id"]
        style_property = change["style_property"]
        new_value = change["new_value"]
        
        # Find component in tree
        for component in tree["components"]:
            if component["id"] == component_id:
                if "className" not in component["attributes"]:
                    component["attributes"]["className"] = ""
                
                # Convert style to Tailwind class
                tailwind_class = await self._convert_style_to_tailwind(style_property, new_value)
                
                # Update className
                current_classes = component["attributes"]["className"].split()
                
                # Remove old classes for this property
                current_classes = [cls for cls in current_classes if not self._is_same_property_class(cls, style_property)]
                
                # Add new class
                current_classes.append(tailwind_class)
                
                component["attributes"]["className"] = " ".join(current_classes).strip()
                break
        
        return tree
    
    async def _apply_content_change(self, tree: Dict[str, Any], change: Dict[str, Any]) -> Dict[str, Any]:
        """Apply content change to component"""
        
        component_id = change["component_id"]
        new_content = change["new_content"]
        
        for component in tree["components"]:
            if component["id"] == component_id:
                component["content"] = new_content
                break
        
        return tree
    
    async def _convert_style_to_tailwind(self, property: str, value: str) -> str:
        """Convert CSS property to Tailwind class"""
        
        # Style mapping for common properties
        style_mappings = {
            "background-color": {
                "#ffffff": "bg-white",
                "#000000": "bg-black", 
                "#ef4444": "bg-red-500",
                "#3b82f6": "bg-blue-500",
                "#10b981": "bg-green-500",
                "#f59e0b": "bg-yellow-500",
                "#8b5cf6": "bg-purple-500"
            },
            "color": {
                "#ffffff": "text-white",
                "#000000": "text-black",
                "#ef4444": "text-red-500",
                "#3b82f6": "text-blue-500",
                "#10b981": "text-green-500"
            },
            "font-size": {
                "12px": "text-xs",
                "14px": "text-sm",
                "16px": "text-base",
                "18px": "text-lg",
                "20px": "text-xl",
                "24px": "text-2xl",
                "30px": "text-3xl"
            },
            "padding": {
                "4px": "p-1",
                "8px": "p-2",
                "12px": "p-3",
                "16px": "p-4",
                "20px": "p-5",
                "24px": "p-6"
            },
            "margin": {
                "4px": "m-1",
                "8px": "m-2",
                "12px": "m-3",
                "16px": "m-4",
                "20px": "m-5",
                "24px": "m-6"
            },
            "border-radius": {
                "4px": "rounded",
                "6px": "rounded-md",
                "8px": "rounded-lg",
                "12px": "rounded-xl",
                "50%": "rounded-full"
            }
        }
        
        if property in style_mappings and value in style_mappings[property]:
            return style_mappings[property][value]
        
        # Fallback for unmapped values
        return f"style-{property}-{value}".replace("#", "").replace("px", "")
    
    def _is_same_property_class(self, css_class: str, property: str) -> bool:
        """Check if CSS class applies to the same property"""
        
        property_prefixes = {
            "background-color": ["bg-"],
            "color": ["text-"],
            "font-size": ["text-"],
            "padding": ["p-", "px-", "py-", "pt-", "pb-", "pl-", "pr-"],
            "margin": ["m-", "mx-", "my-", "mt-", "mb-", "ml-", "mr-"],
            "border-radius": ["rounded"]
        }
        
        if property in property_prefixes:
            return any(css_class.startswith(prefix) for prefix in property_prefixes[property])
        
        return False
    
    async def _generate_code_from_tree(self, component_tree: Dict[str, Any]) -> str:
        """Generate React code from component tree"""
        
        components = component_tree["components"]
        
        if not components:
            return "// No components found"
        
        # Generate imports
        code_parts = ["import React, { useState } from 'react';", ""]
        
        # Generate component code
        code_parts.append("const App = () => {")
        code_parts.append("  return (")
        
        # Generate JSX for each component
        for i, component in enumerate(components):
            jsx = self._generate_jsx_for_component(component, indent="    ")
            if i == 0:  # Root component
                code_parts.append(jsx)
        
        code_parts.append("  );")
        code_parts.append("};")
        code_parts.append("")
        code_parts.append("export default App;")
        
        return "\n".join(code_parts)
    
    def _generate_jsx_for_component(self, component: Dict[str, Any], indent: str = "") -> str:
        """Generate JSX for a single component"""
        
        tag_name = component["type"]
        attributes = component["attributes"]
        content = component["content"]
        
        # Build attribute string
        attr_parts = []
        for attr_name, attr_value in attributes.items():
            if attr_value:
                attr_parts.append(f'{attr_name}="{attr_value}"')
        
        attr_string = " " + " ".join(attr_parts) if attr_parts else ""
        
        # Generate JSX
        if content:
            return f"{indent}<{tag_name}{attr_string}>\n{indent}  {content}\n{indent}</{tag_name}>"
        else:
            return f"{indent}<{tag_name}{attr_string} />"
    
    async def _generate_hot_reload_patch(self, change: Dict[str, Any], updated_code: str) -> Dict[str, Any]:
        """Generate hot reload patch for immediate UI update"""
        
        change_type = change["type"]
        
        if change_type == "update_style":
            return {
                "type": "style_update",
                "component_id": change["component_id"],
                "style_property": change["style_property"],
                "new_value": change["new_value"],
                "css_update": await self._generate_css_update(change),
                "dom_selector": f"[data-component-id='{change['component_id']}']"
            }
        
        elif change_type == "update_content":
            return {
                "type": "content_update",
                "component_id": change["component_id"],
                "new_content": change["new_content"],
                "dom_selector": f"[data-component-id='{change['component_id']}']"
            }
        
        else:
            # For structural changes, full re-render needed
            return {
                "type": "full_reload",
                "updated_code": updated_code,
                "reason": "Structural change requires full reload"
            }
    
    async def _generate_css_update(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CSS update for hot reload"""
        
        property = change["style_property"]
        value = change["new_value"]
        
        return {
            "property": property,
            "value": value,
            "css_rule": f"{property}: {value};"
        }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a visual editing session"""
        
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        session = self.active_sessions[session_id]
        
        return {
            "success": True,
            "session": {
                "session_id": session_id,
                "created_at": session["created_at"],
                "last_update": session["last_update"],
                "change_count": len(session["change_history"]),
                "component_count": len(session["component_tree"]["components"])
            }
        }
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a visual editing session"""
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return {
                "success": True,
                "message": "Session closed successfully"
            }
        
        return {
            "success": False,
            "error": "Session not found"
        }