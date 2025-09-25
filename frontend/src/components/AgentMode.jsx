import React, { useState } from 'react';
import { 
  Zap, 
  Brain, 
  CheckCircle, 
  AlertTriangle, 
  Code, 
  Search,
  Activity
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AgentMode = ({ onCodeGenerated, sessionId }) => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [agentStatus, setAgentStatus] = useState('idle'); // idle, planning, generating, optimizing, complete
  const [generationPlan, setGenerationPlan] = useState(null);
  const [confidenceScore, setConfidenceScore] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleAgentGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setAgentStatus('planning');
    
    try {
      const response = await axios.post(`${API}/ai/agent-generate`, {
        prompt: prompt,
        session_id: sessionId,
        context: {
          mode: 'autonomous',
          error_reduction: true,
          optimization: true
        }
      });
      
      if (response.data.success) {
        setGenerationPlan(response.data.plan);
        setConfidenceScore(response.data.confidence_score);
        setAnalysis(response.data.analysis);
        setAgentStatus('complete');
        
        // Pass generated code to parent
        onCodeGenerated(response.data.code);
      } else {
        setAgentStatus('error');
        console.error('Agent generation failed:', response.data.error);
      }
    } catch (error) {
      setAgentStatus('error');
      console.error('Agent generation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const AgentStatusIndicator = () => {
    const statusConfig = {
      idle: { icon: Brain, color: 'text-gray-400', bg: 'bg-gray-100', text: 'Agent Ready' },
      planning: { icon: Brain, color: 'text-blue-600', bg: 'bg-blue-100', text: 'Planning Architecture...' },
      generating: { icon: Code, color: 'text-purple-600', bg: 'bg-purple-100', text: 'Generating Code...' },
      optimizing: { icon: Zap, color: 'text-yellow-600', bg: 'bg-yellow-100', text: 'Optimizing Performance...' },
      complete: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', text: 'Generation Complete' },
      error: { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100', text: 'Error Occurred' }
    };

    const config = statusConfig[agentStatus];
    const IconComponent = config.icon;

    return (
      <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${config.bg}`}>
        <IconComponent className={`h-4 w-4 ${config.color} ${isGenerating ? 'animate-pulse' : ''}`} />
        <span className={`text-sm font-medium ${config.color}`}>{config.text}</span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
      {/* Agent Mode Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Agent Mode</h3>
            <p className="text-sm text-gray-500">AI with 91% error reduction</p>
          </div>
        </div>
        <AgentStatusIndicator />
      </div>

      {/* Input Area */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Describe your application
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Build a task management app with real-time collaboration..."
            className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            disabled={isGenerating}
          />
        </div>

        <button
          onClick={handleAgentGenerate}
          disabled={isGenerating || !prompt.trim()}
          className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
            isGenerating || !prompt.trim()
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700'
          }`}
        >
          {isGenerating ? (
            <>
              <Activity className="h-4 w-4 animate-spin" />
              <span>Agent Working...</span>
            </>
          ) : (
            <>
              <Zap className="h-4 w-4" />
              <span>Generate with Agent</span>
            </>
          )}
        </button>
      </div>

      {/* Generation Plan Display */}
      {generationPlan && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-medium text-blue-900 mb-2">Development Plan</h4>
          <div className="space-y-2 text-sm text-blue-800">
            <div><strong>Architecture:</strong> {generationPlan.architecture}</div>
            <div><strong>Components:</strong> {generationPlan.components?.join(', ')}</div>
            <div><strong>Implementation:</strong> {generationPlan.implementation_order?.join(' → ')}</div>
          </div>
        </div>
      )}

      {/* Analysis & Confidence Score */}
      {analysis && confidenceScore && (
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-900">Confidence Score</span>
            </div>
            <div className="text-2xl font-bold text-green-600 mt-1">
              {Math.round(confidenceScore * 100)}%
            </div>
          </div>

          <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">Status</span>
            </div>
            <div className="text-sm font-medium text-purple-600 mt-1">
              {analysis.validation_status === 'clean' ? 'No Issues Found' : 
               analysis.auto_fixed ? 'Auto-Fixed Issues' : 'Validated'}
            </div>
          </div>
        </div>
      )}

      {/* Agent Features */}
      <div className="mt-6 grid grid-cols-2 gap-3">
        <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
          <CheckCircle className="h-3 w-3 text-green-500" />
          <span className="text-xs text-gray-600">Auto-debugging</span>
        </div>
        <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
          <CheckCircle className="h-3 w-3 text-green-500" />
          <span className="text-xs text-gray-600">Performance optimization</span>
        </div>
        <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
          <CheckCircle className="h-3 w-3 text-green-500" />
          <span className="text-xs text-gray-600">Error prevention</span>
        </div>
        <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
          <CheckCircle className="h-3 w-3 text-green-500" />
          <span className="text-xs text-gray-600">Best practices</span>
        </div>
      </div>
    </div>
  );
};

export default AgentMode;