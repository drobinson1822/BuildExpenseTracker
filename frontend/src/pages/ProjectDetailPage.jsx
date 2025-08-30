import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ForecastTable } from '../features/forecast/components';
import { Button } from '../components/ui';
import { projectService, forecastService, expenseService } from '../services';

const ProjectDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [forecastItems, setForecastItems] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjectData();
  }, [id]);

  const loadProjectData = async () => {
    try {
      const [projectData, forecastData, expenseData] = await Promise.all([
        projectService.getProject(id),
        forecastService.getForecastItems(id),
        expenseService.getExpenses(id)
      ]);
      
      setProject(projectData);
      setForecastItems(forecastData);
      setExpenses(expenseData);
    } catch (error) {
      console.error('Failed to load project data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddForecastItem = async (itemData) => {
    try {
      const newItem = await forecastService.createForecastItem({
        ...itemData,
        project_id: parseInt(id)
      });
      setForecastItems(prev => [...prev, newItem]);
    } catch (error) {
      console.error('Failed to add forecast item:', error);
    }
  };

  const handleEditForecastItem = async (itemId, itemData) => {
    try {
      const updatedItem = await forecastService.updateForecastItem(itemId, itemData);
      setForecastItems(prev => prev.map(item => item.id === itemId ? updatedItem : item));
    } catch (error) {
      console.error('Failed to update forecast item:', error);
    }
  };

  const handleDeleteForecastItem = async (itemId) => {
    try {
      await forecastService.deleteForecastItem(itemId);
      setForecastItems(prev => prev.filter(item => item.id !== itemId));
    } catch (error) {
      console.error('Failed to delete forecast item:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Project not found</p>
      </div>
    );
  }

  // Use project's total_budget as the fixed budget, not sum of estimates
  const totalBudget = parseFloat(project.total_budget || 0);
  
  // Calculate estimated final cost: actual cost of completed items + estimated cost of remaining items
  const completedItems = forecastItems.filter(item => item.status === 'Complete');
  const remainingItems = forecastItems.filter(item => item.status !== 'Complete');
  
  const actualCostOfCompleted = completedItems.reduce((sum, item) => sum + parseFloat(item.actual_cost || 0), 0);
  const estimatedCostOfRemaining = remainingItems.reduce((sum, item) => sum + parseFloat(item.estimated_cost || 0), 0);
  const estimatedFinalCost = actualCostOfCompleted + estimatedCostOfRemaining;
  
  // Calculate variance against the fixed project budget
  const variance = totalBudget - estimatedFinalCost;
  const budgetRemaining = Math.max(0, variance);
  const budgetRemainingPercent = totalBudget > 0 ? (budgetRemaining / totalBudget * 100) : 0;
  
  // Calculate completed items metrics
  const completedItemsCount = completedItems.length;
  const totalSpentOnCompleted = actualCostOfCompleted;
  const totalBudgetedForCompleted = completedItems.reduce((sum, item) => sum + parseFloat(item.estimated_cost || 0), 0);
  const totalEstimatedForCompleted = totalBudgetedForCompleted; // Same calculation, clearer naming
  const spendVariance = totalBudgetedForCompleted - totalSpentOnCompleted;
  
  // Calculate project progress (based on completed items)
  const projectProgress = forecastItems.length > 0 ? (completedItemsCount / forecastItems.length * 100) : 0;
  
  // Determine project status
  const isOnTrack = variance >= 0;
  const statusText = isOnTrack ? 'On Track' : 'Over Budget';
  const statusColor = isOnTrack ? 'text-green-600' : 'text-red-600';
  const statusBgColor = isOnTrack ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div className="mb-4">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Projects
        </button>
      </div>

      {/* Project Header */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-3 gap-8">
          {/* Left Side - Project Details */}
          <div className="col-span-2">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">{project.name}</h1>
            
            <div className="grid grid-cols-2 gap-x-8 gap-y-4">
              {/* Address */}
              <div className="flex flex-col">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Location</span>
                </div>
                <span className="text-lg text-gray-900">{project.address}</span>
              </div>

              {/* Status */}
              <div className="flex flex-col">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Status</span>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium w-fit ${
                  project.status === 'completed' ? 'bg-green-100 text-green-800' :
                  project.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {project.status?.replace('_', ' ') || 'Not Started'}
                </span>
              </div>

              {/* Timeline */}
              <div className="flex flex-col">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Timeline</span>
                </div>
                <div className="text-gray-900">
                  <div className="text-sm">
                    <span className="font-medium">Start:</span> {project.start_date ? new Date(project.start_date).toLocaleDateString() : 'Not set'}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">End:</span> {project.target_completion_date ? new Date(project.target_completion_date).toLocaleDateString() : 'Not set'}
                  </div>
                </div>
              </div>

              {/* Square Footage */}
              <div className="flex flex-col">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Size</span>
                </div>
                <span className="text-lg text-gray-900 font-semibold">
                  {project.total_sqft ? project.total_sqft.toLocaleString() : 'Not set'} sq ft
                </span>
              </div>
            </div>
          </div>

          {/* Right Side - Metrics */}
          <div className="space-y-3">
            {/* Budget Metrics Grid */}
            <div className="space-y-2">
              {/* Row 1: Total Budget and Total Spent */}
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 text-center">
                  <h3 className="text-xs font-semibold text-blue-900 mb-1">Total Budget</h3>
                  <p className="text-lg font-bold text-blue-700">${totalBudget.toLocaleString()}</p>
                </div>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-2 text-center">
                  <h3 className="text-xs font-semibold text-purple-900 mb-1">Total Spent</h3>
                  <p className="text-lg font-bold text-purple-700">${totalSpentOnCompleted.toLocaleString()}</p>
                </div>
              </div>
              
              {/* Row 2: Est Final Cost and Projected Budget Remains */}
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-2 text-center">
                  <h3 className="text-xs font-semibold text-gray-900 mb-1">Est. Final Cost</h3>
                  <p className="text-lg font-bold text-gray-700">${estimatedFinalCost.toLocaleString()}</p>
                </div>
                <div className={`${variance >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border rounded-lg p-2 text-center`}>
                  <h3 className={`text-xs font-semibold mb-1 ${variance >= 0 ? 'text-green-900' : 'text-red-900'}`}>
                    Projected Budget Remains
                  </h3>
                  <p className={`text-lg font-bold ${variance >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                    {variance >= 0 ? '+' : ''}${Math.abs(variance).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Budget Visualization */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-2">
              <h3 className="text-xs font-semibold text-gray-900 mb-2">Budget Overview</h3>
              <div className="relative">
                {/* Budget Bar Container */}
                <div className="w-full bg-gray-200 rounded-full h-4 relative overflow-hidden">
                  {/* Total Spent (Solid Fill) */}
                  <div 
                    className="bg-purple-600 h-4 rounded-full absolute top-0 left-0 z-20"
                    style={{ width: `${Math.min((totalSpentOnCompleted / totalBudget) * 100, 100)}%` }}
                  ></div>
                  
                  {/* Estimated Final Cost (Dashed Fill) */}
                  <div 
                    className="h-4 rounded-full absolute top-0 left-0 z-10"
                    style={{ 
                      width: `${Math.min((estimatedFinalCost / totalBudget) * 100, 100)}%`,
                      background: `repeating-linear-gradient(
                        45deg,
                        #6b7280,
                        #6b7280 2px,
                        transparent 2px,
                        transparent 4px
                      )`
                    }}
                  ></div>
                </div>
                
                {/* Legend */}
                <div className="mt-1 space-y-1 text-xs text-gray-600">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-purple-600 rounded mr-1"></div>
                      <span>Spent</span>
                    </div>
                    <span>${totalSpentOnCompleted.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded mr-1" style={{
                        background: `repeating-linear-gradient(
                          45deg,
                          #6b7280,
                          #6b7280 1px,
                          transparent 1px,
                          transparent 2px
                        )`
                      }}></div>
                      <span>Est. Final</span>
                    </div>
                    <span>${estimatedFinalCost.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Forecast Table */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-6">Forecast & Tracking</h2>
        
        {/* Completed Items Summary */}
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium">Completed Items ({completedItemsCount})</h3>
            <span className={`text-sm font-medium px-3 py-1 rounded-full ${spendVariance >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {spendVariance >= 0 ? 'Under Budget' : 'Over Budget'}
            </span>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center p-3 bg-white rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Total Estimated</div>
              <div className="text-xl font-bold text-blue-600">${totalEstimatedForCompleted.toLocaleString()}</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Total Spent</div>
              <div className="text-xl font-bold text-gray-900">${totalSpentOnCompleted.toLocaleString()}</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Spend Variance</div>
              <div className={`text-xl font-bold ${spendVariance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {spendVariance >= 0 ? '+' : ''}${Math.abs(spendVariance).toLocaleString()}
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Project Progress</span>
              <span className="font-medium">{Math.round(projectProgress)}%</span>
            </div>
            <div className="w-full bg-gray-300 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${Math.min(projectProgress, 100)}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>{completedItemsCount} of {forecastItems.length} items complete</span>
              <span>{Math.round(projectProgress)}% done</span>
            </div>
          </div>
        </div>

        <ForecastTable
          items={forecastItems}
          expenses={expenses}
          onAdd={handleAddForecastItem}
          onEdit={handleEditForecastItem}
          onDelete={handleDeleteForecastItem}
        />
      </div>
    </div>
  );
};

export default ProjectDetailPage;
