import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class VisualEditorService:
    """
    Visual Editor Service for drag-and-drop UI editing like Figma
    Converts visual operations into code changes
    """
    
    def __init__(self):
        self.components_library = self._load_components_library()
    
    def _load_components_library(self) -> Dict[str, Any]:
        """Load available UI components for the visual editor"""
        
        return {
            "layout": {
                "Container": {
                    "props": ["className", "children"],
                    "default_classes": "container mx-auto p-4",
                    "template": "<div className=\"{className}\">{children}</div>"
                },
                "Grid": {
                    "props": ["cols", "gap", "className", "children"],
                    "default_classes": "grid grid-cols-{cols} gap-{gap}",
                    "template": "<div className=\"{className}\">{children}</div>"
                },
                "Flex": {
                    "props": ["direction", "align", "justify", "className", "children"],
                    "default_classes": "flex flex-{direction} items-{align} justify-{justify}",
                    "template": "<div className=\"{className}\">{children}</div>"
                }
            },
            "components": {
                "Button": {
                    "props": ["variant", "size", "onClick", "children", "disabled"],
                    "variants": {
                        "primary": "bg-blue-600 hover:bg-blue-700 text-white",
                        "secondary": "bg-gray-200 hover:bg-gray-300 text-gray-900",
                        "outline": "border border-gray-300 hover:bg-gray-50"
                    },
                    "sizes": {
                        "sm": "px-3 py-1.5 text-sm",
                        "md": "px-4 py-2",
                        "lg": "px-6 py-3 text-lg"
                    },
                    "template": "<button className=\"{className}\" onClick={{{onClick}}} disabled={{{disabled}}}>{children}</button>"
                },
                "Input": {
                    "props": ["type", "placeholder", "value", "onChange", "className"],
                    "default_classes": "border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "template": "<input type=\"{type}\" placeholder=\"{placeholder}\" value={{{value}}} onChange={{{onChange}}} className=\"{className}\" />"
                },
                "Card": {
                    "props": ["className", "children"],
                    "default_classes": "bg-white rounded-lg shadow-md p-6",
                    "template": "<div className=\"{className}\">{children}</div>"
                }
            }
        }
    
    async def parse_visual_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Parse visual editor operation and convert to code changes"""
        try:
            operation_type = operation.get("type")
            
            if operation_type == "add_component":
                return await self._handle_add_component(operation)
            elif operation_type == "move_component":
                return await self._handle_move_component(operation)
            elif operation_type == "update_props":
                return await self._handle_update_props(operation)
            elif operation_type == "delete_component":
                return await self._handle_delete_component(operation)
            elif operation_type == "update_styles":
                return await self._handle_update_styles(operation)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation type: {operation_type}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to parse visual operation"
            }
    
    async def _handle_add_component(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle adding a new component"""
        
        component_type = operation.get("component_type")
        props = operation.get("props", {})
        parent_id = operation.get("parent_id")
        position = operation.get("position", "end")
        
        # Get component template
        component_def = self._get_component_definition(component_type)
        if not component_def:
            return {
                "success": False,
                "error": f"Component type '{component_type}' not found"
            }
        
        # Generate component code
        component_code = await self._generate_component_code(component_type, component_def, props)
        
        return {
            "success": True,
            "operation": "add_component",
            "component_type": component_type,
            "code": component_code,
            "parent_id": parent_id,
            "position": position,
            "component_id": f"comp_{datetime.now().timestamp()}"
        }
    
    def _get_component_definition(self, component_type: str) -> Optional[Dict[str, Any]]:
        """Get component definition from library"""
        
        # Check in layout components
        if component_type in self.components_library["layout"]:
            return self.components_library["layout"][component_type]
        
        # Check in regular components
        if component_type in self.components_library["components"]:
            return self.components_library["components"][component_type]
        
        return None
    
    async def _generate_component_code(self, component_type: str, component_def: Dict[str, Any], props: Dict[str, Any]) -> str:
        """Generate React code for a component"""
        
        template = component_def.get("template", "")
        
        # Handle className generation
        className = await self._build_class_name(component_type, component_def, props)
        
        # Prepare template variables
        template_vars = {
            "className": className,
            "children": props.get("children", ""),
            "type": props.get("type", "text"),
            "placeholder": props.get("placeholder", ""),
            "onClick": props.get("onClick", "() => {}"),
            "onChange": props.get("onChange", "() => {}"),
            "value": props.get("value", ""),
            "disabled": props.get("disabled", "false")
        }
        
        # Replace template variables
        code = template.format(**template_vars)
        
        return code
    
    async def _build_class_name(self, component_type: str, component_def: Dict[str, Any], props: Dict[str, Any]) -> str:
        """Build Tailwind className for component"""
        
        classes = []
        
        # Add default classes
        if "default_classes" in component_def:
            default = component_def["default_classes"]
            # Replace placeholders in default classes
            for key, value in props.items():
                default = default.replace(f"{{{key}}}", str(value))
            classes.append(default)
        
        # Add variant-based classes
        if "variants" in component_def and "variant" in props:
            variant_class = component_def["variants"].get(props["variant"], "")
            if variant_class:
                classes.append(variant_class)
        
        # Add size-based classes
        if "sizes" in component_def and "size" in props:
            size_class = component_def["sizes"].get(props["size"], "")
            if size_class:
                classes.append(size_class)
        
        # Add custom classes
        if "className" in props:
            classes.append(props["className"])
        
        return " ".join(filter(None, classes))
    
    async def _handle_move_component(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle moving a component"""
        
        component_id = operation.get("component_id")
        new_parent_id = operation.get("new_parent_id")
        new_position = operation.get("new_position")
        
        return {
            "success": True,
            "operation": "move_component",
            "component_id": component_id,
            "new_parent_id": new_parent_id,
            "new_position": new_position,
            "code_changes": {
                "type": "move",
                "from_parent": operation.get("old_parent_id"),
                "to_parent": new_parent_id
            }
        }
    
    async def _handle_update_props(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle updating component props"""
        
        component_id = operation.get("component_id")
        new_props = operation.get("new_props", {})
        component_type = operation.get("component_type")
        
        # Get component definition
        component_def = self._get_component_definition(component_type)
        
        # Generate updated component code
        updated_code = await self._generate_component_code(component_type, component_def, new_props)
        
        return {
            "success": True,
            "operation": "update_props",
            "component_id": component_id,
            "new_props": new_props,
            "updated_code": updated_code
        }
    
    async def _handle_delete_component(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deleting a component"""
        
        component_id = operation.get("component_id")
        
        return {
            "success": True,
            "operation": "delete_component",
            "component_id": component_id,
            "code_changes": {
                "type": "delete",
                "component_id": component_id
            }
        }
    
    async def _handle_update_styles(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle updating component styles (Tailwind classes)"""
        
        component_id = operation.get("component_id")
        style_changes = operation.get("style_changes", {})
        
        # Convert style changes to Tailwind classes
        tailwind_classes = await self._convert_styles_to_tailwind(style_changes)
        
        return {
            "success": True,
            "operation": "update_styles",
            "component_id": component_id,
            "style_changes": style_changes,
            "tailwind_classes": tailwind_classes
        }
    
    async def _convert_styles_to_tailwind(self, style_changes: Dict[str, Any]) -> List[str]:
        """Convert CSS-like style changes to Tailwind classes"""
        
        tailwind_classes = []
        
        # Mapping of CSS properties to Tailwind classes
        style_mapping = {
            "background-color": {
                "#ffffff": "bg-white",
                "#000000": "bg-black",
                "#ef4444": "bg-red-500",
                "#3b82f6": "bg-blue-500",
                "#10b981": "bg-green-500"
            },
            "color": {
                "#ffffff": "text-white",
                "#000000": "text-black",
                "#ef4444": "text-red-500",
                "#3b82f6": "text-blue-500"
            },
            "padding": {
                "8px": "p-2",
                "16px": "p-4",
                "24px": "p-6",
                "32px": "p-8"
            },
            "width": {
                "100%": "w-full",
                "50%": "w-1/2",
                "auto": "w-auto"
            },
            "font-size": {
                "12px": "text-xs",
                "14px": "text-sm",
                "16px": "text-base",
                "18px": "text-lg",
                "24px": "text-xl"
            }
        }
        
        for property_name, value in style_changes.items():
            if property_name in style_mapping and value in style_mapping[property_name]:
                tailwind_class = style_mapping[property_name][value]
                tailwind_classes.append(tailwind_class)
        
        return tailwind_classes