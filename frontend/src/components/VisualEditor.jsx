import React, { useState, useRef } from 'react';
import { 
  MousePointer, 
  Square, 
  Type, 
  Image, 
  Layout, 
  Palette,
  Move,
  Trash2,
  Copy
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VisualEditor = ({ code, onCodeUpdate }) => {
  const [selectedTool, setSelectedTool] = useState('select');
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  const tools = [
    { id: 'select', icon: MousePointer, label: 'Select' },
    { id: 'container', icon: Square, label: 'Container' },
    { id: 'text', icon: Type, label: 'Text' },
    { id: 'button', icon: Square, label: 'Button' },
    { id: 'input', icon: Square, label: 'Input' },
    { id: 'image', icon: Image, label: 'Image' }
  ];

  const [components, setComponents] = useState([
    {
      id: 'comp_1',
      type: 'Container',
      x: 50,
      y: 50,
      width: 300,
      height: 200,
      props: {
        className: 'bg-white border border-gray-200 rounded-lg p-4'
      }
    }
  ]);

  const handleCanvasClick = async (e) => {
    if (selectedTool === 'select') return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newComponent = {
      id: `comp_${Date.now()}`,
      type: selectedTool,
      x,
      y,
      width: selectedTool === 'text' ? 120 : selectedTool === 'button' ? 100 : 200,
      height: selectedTool === 'text' ? 30 : selectedTool === 'button' ? 40 : 100,
      props: getDefaultProps(selectedTool)
    };
    
    const updatedComponents = [...components, newComponent];
    setComponents(updatedComponents);
    
    // Apply visual operation to code
    await applyVisualOperation({
      type: 'add_component',
      component_type: selectedTool,
      props: newComponent.props,
      position: 'end'
    });
  };

  const getDefaultProps = (componentType) => {
    const defaultProps = {
      container: { className: 'bg-white border border-gray-200 rounded-lg p-4' },
      text: { children: 'Text', className: 'text-gray-900' },
      button: { children: 'Button', variant: 'primary', className: 'px-4 py-2 bg-blue-600 text-white rounded-lg' },
      input: { placeholder: 'Enter text...', className: 'border border-gray-300 rounded px-3 py-2' },
      image: { src: '/placeholder.jpg', alt: 'Image', className: 'rounded' }
    };
    
    return defaultProps[componentType] || {};
  };

  const applyVisualOperation = async (operation) => {
    try {
      const response = await axios.post(`${API}/visual-editor/apply`, {
        current_code: code,
        operations: [operation]
      });
      
      if (response.data.success) {
        onCodeUpdate(response.data.modified_code);
      }
    } catch (error) {
      console.error('Failed to apply visual operation:', error);
    }
  };

  const handleComponentMouseDown = (e, component) => {
    if (selectedTool !== 'select') return;
    
    e.preventDefault();
    setSelectedComponent(component);
    setIsDragging(true);
    
    const rect = e.currentTarget.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  const handleMouseMove = (e) => {
    if (!isDragging || !selectedComponent) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const newX = e.clientX - rect.left - dragOffset.x;
    const newY = e.clientY - rect.top - dragOffset.y;
    
    setComponents(components.map(comp => 
      comp.id === selectedComponent.id 
        ? { ...comp, x: newX, y: newY }
        : comp
    ));
  };

  const handleMouseUp = () => {
    if (isDragging && selectedComponent) {
      // Apply move operation to code
      applyVisualOperation({
        type: 'move_component',
        component_id: selectedComponent.id,
        new_parent_id: 'root',
        new_position: 'end'
      });
    }
    
    setIsDragging(false);
  };

  const updateComponentProps = async (componentId, newProps) => {
    setComponents(components.map(comp => 
      comp.id === componentId 
        ? { ...comp, props: { ...comp.props, ...newProps } }
        : comp
    ));
    
    const component = components.find(c => c.id === componentId);
    if (component) {
      await applyVisualOperation({
        type: 'update_props',
        component_id: componentId,
        component_type: component.type,
        new_props: { ...component.props, ...newProps }
      });
    }
  };

  const deleteComponent = async (componentId) => {
    setComponents(components.filter(comp => comp.id !== componentId));
    setSelectedComponent(null);
    
    await applyVisualOperation({
      type: 'delete_component',
      component_id: componentId
    });
  };

  const ComponentRenderer = ({ component }) => {
    const isSelected = selectedComponent?.id === component.id;
    
    const baseStyle = {
      position: 'absolute',
      left: component.x,
      top: component.y,
      width: component.width,
      height: component.height,
      cursor: selectedTool === 'select' ? 'move' : 'default',
      border: isSelected ? '2px solid #3b82f6' : '1px solid #e5e7eb'
    };

    const renderComponentContent = () => {
      switch (component.type) {
        case 'text':
          return (
            <div className={component.props.className || 'text-gray-900'}>
              {component.props.children || 'Text'}
            </div>
          );
        case 'button':
          return (
            <button className={component.props.className || 'px-4 py-2 bg-blue-600 text-white rounded-lg'}>
              {component.props.children || 'Button'}
            </button>
          );
        case 'input':
          return (
            <input 
              placeholder={component.props.placeholder || 'Enter text...'}
              className={component.props.className || 'border border-gray-300 rounded px-3 py-2 w-full'}
            />
          );
        case 'container':
        default:
          return (
            <div className={component.props.className || 'bg-white border border-gray-200 rounded-lg p-4'}>
              Container
            </div>
          );
      }
    };

    return (
      <div
        style={baseStyle}
        onMouseDown={(e) => handleComponentMouseDown(e, component)}
        onClick={() => setSelectedComponent(component)}
        className="flex items-center justify-center"
      >
        {renderComponentContent()}
        
        {isSelected && (
          <div className="absolute -top-8 right-0 flex space-x-1">
            <button 
              onClick={() => deleteComponent(component.id)}
              className="p-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          </div>
        )}
      </div>
    );
  };

  const PropertyPanel = () => {
    if (!selectedComponent) return null;

    return (
      <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
        <h3 className="font-medium text-gray-900 mb-3">Properties</h3>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <div className="text-sm text-gray-500 capitalize">{selectedComponent.type}</div>
          </div>

          {selectedComponent.type === 'text' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Text Content
              </label>
              <input
                type="text"
                value={selectedComponent.props.children || ''}
                onChange={(e) => updateComponentProps(selectedComponent.id, { children: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {selectedComponent.type === 'button' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Button Text
                </label>
                <input
                  type="text"
                  value={selectedComponent.props.children || ''}
                  onChange={(e) => updateComponentProps(selectedComponent.id, { children: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Variant
                </label>
                <select
                  value={selectedComponent.props.variant || 'primary'}
                  onChange={(e) => updateComponentProps(selectedComponent.id, { variant: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                >
                  <option value="primary">Primary</option>
                  <option value="secondary">Secondary</option>
                  <option value="outline">Outline</option>
                </select>
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Background Color
            </label>
            <div className="flex space-x-2">
              {['bg-white', 'bg-gray-100', 'bg-blue-100', 'bg-green-100', 'bg-red-100'].map(color => (
                <button
                  key={color}
                  onClick={() => updateComponentProps(selectedComponent.id, { 
                    className: selectedComponent.props.className?.replace(/bg-\w+-?\d*\b/g, '') + ` ${color}` 
                  })}
                  className={`w-6 h-6 rounded border ${color}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-full">
      {/* Tools Panel */}
      <div className="w-16 bg-gray-50 border-r border-gray-200 p-2">
        <div className="space-y-2">
          {tools.map(tool => {
            const IconComponent = tool.icon;
            return (
              <button
                key={tool.id}
                onClick={() => setSelectedTool(tool.id)}
                className={`w-12 h-12 flex items-center justify-center rounded-lg transition-colors ${
                  selectedTool === tool.id 
                    ? 'bg-blue-100 text-blue-600 border border-blue-200' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                title={tool.label}
              >
                <IconComponent className="h-5 w-5" />
              </button>
            );
          })}
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 bg-gray-100 relative overflow-hidden">
        <div
          ref={canvasRef}
          className="w-full h-full relative cursor-crosshair"
          onClick={handleCanvasClick}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {/* Grid Pattern */}
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `
                linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px'
            }}
          />

          {/* Components */}
          {components.map(component => (
            <ComponentRenderer key={component.id} component={component} />
          ))}
        </div>
      </div>

      {/* Properties Panel */}
      <div className="w-64 bg-white border-l border-gray-200 p-4">
        <PropertyPanel />
      </div>
    </div>
  );
};

export default VisualEditor;