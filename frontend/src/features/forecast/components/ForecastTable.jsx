import React, { useState } from "react";
import { Button, Input } from '../../../components/ui';

export default function ForecastTable({ items, expenses, onAdd, onEdit, onDelete }) {
  const [adding, setAdding] = useState(false);
  const [newItem, setNewItem] = useState({
    category: "",
    description: "",
    estimated_cost: "",
    actual_cost: "",
    unit: "",
    notes: "",
    progress_percent: 0,
    status: "Not Started"
  });
  const [editIdx, setEditIdx] = useState(null);
  const [editItem, setEditItem] = useState({});
  const [showEditModal, setShowEditModal] = useState(false);

  // Get variance display with color and percentage
  const getVarianceDisplay = (estimated, actual) => {
    const est = parseFloat(estimated) || 0;
    const act = parseFloat(actual) || 0;
    const difference = est - act;
    const percentage = est > 0 ? ((difference / est) * 100) : 0;
    
    if (difference > 0) {
      return {
        amount: `$${Math.abs(difference).toLocaleString()}`,
        percentage: `(-${Math.abs(percentage).toFixed(1)}%)`,
        color: 'text-green-600'
      };
    } else if (difference < 0) {
      return {
        amount: `+$${Math.abs(difference).toLocaleString()}`,
        percentage: `(${Math.abs(percentage).toFixed(0)}%)`,
        color: 'text-red-600'
      };
    }
    return {
      amount: '$0',
      percentage: '(0%)',
      color: 'text-gray-600'
    };
  };

  // Get status badge styling
  const getStatusBadge = (status) => {
    switch (status) {
      case 'Complete':
        return 'bg-green-100 text-green-800';
      case 'In Progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  async function handleAdd() {
    try {
      const itemToAdd = {
        ...newItem,
        estimated_cost: newItem.estimated_cost === '' ? null : parseFloat(newItem.estimated_cost),
        actual_cost: newItem.actual_cost === '' ? null : parseFloat(newItem.actual_cost),
        progress_percent: newItem.progress_percent === '' ? 0 : parseInt(newItem.progress_percent, 10)
      };
      
      Object.keys(itemToAdd).forEach(key => {
        if (itemToAdd[key] === undefined || Number.isNaN(itemToAdd[key])) {
          delete itemToAdd[key];
        }
      });
      
      await onAdd(itemToAdd);
      
      setNewItem({ 
        category: "", 
        description: "",
        estimated_cost: "", 
        actual_cost: "",
        unit: "", 
        notes: "", 
        progress_percent: 0, 
        status: "Not Started"
      });
      setAdding(false);
    } catch (error) {
      console.error('Error adding forecast item:', error);
    }
  }

  function handleEdit(idx) {
    const item = items[idx];
    setEditIdx(idx);
    setEditItem({
      category: item.category || '',
      description: item.description || '',
      notes: item.notes || '',
      estimated_cost: item.estimated_cost ?? '',
      actual_cost: item.actual_cost ?? '',
      unit: item.unit || '',
      progress_percent: item.progress_percent ?? 0,
      status: item.status || 'Not Started',
      project_id: item.project_id
    });
    // Don't automatically open modal for inline editing
  }

  async function handleEditSave() {
    try {
      const itemId = items[editIdx].id;
      
      const updateData = {
        ...editItem,
        project_id: items[editIdx].project_id,
        estimated_cost: editItem.estimated_cost === '' ? null : parseFloat(editItem.estimated_cost),
        actual_cost: editItem.actual_cost === '' ? null : parseFloat(editItem.actual_cost),
        progress_percent: editItem.progress_percent === '' ? 0 : parseInt(editItem.progress_percent, 10)
      };
      
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === undefined || Number.isNaN(updateData[key])) {
          delete updateData[key];
        }
      });
      
      await onEdit(itemId, updateData);
      setEditIdx(null);
      setShowEditModal(false);
    } catch (error) {
      console.error('Error saving forecast item:', error);
    }
  }

  function handleEditCancel() {
    setEditIdx(null);
    setShowEditModal(false);
    setEditItem({});
  }

  async function handleDelete(idx) {
    if (window.confirm('Are you sure you want to delete this forecast item? This action cannot be undone.')) {
      try {
        const itemId = items[idx].id;
        await onDelete(itemId);
      } catch (error) {
        console.error('Error deleting forecast item:', error);
      }
    }
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Budgeted</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actual</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Variance</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((item, idx) => {
              const variance = getVarianceDisplay(item.estimated_cost, item.actual_cost);
              const isEditing = editIdx === idx;
              return (
                <tr key={item.id} className={`hover:bg-gray-50 ${isEditing ? 'bg-blue-50' : ''}`}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {isEditing ? (
                      <input
                        type="text"
                        value={editItem.category || ''}
                        onChange={e => setEditItem({ ...editItem, category: e.target.value })}
                        className="w-full min-w-[120px] px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Category"
                        autoFocus
                      />
                    ) : (
                      <span 
                        onClick={() => handleEdit(idx)}
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded block"
                        title="Click to edit"
                      >
                        {item.category}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {isEditing ? (
                      <input
                        type="text"
                        value={editItem.description || ''}
                        onChange={e => setEditItem({ ...editItem, description: e.target.value })}
                        className="w-full min-w-[150px] px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Description"
                      />
                    ) : (
                      <span 
                        onClick={() => handleEdit(idx)}
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded block"
                        title="Click to edit"
                      >
                        {item.description || '-'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {isEditing ? (
                      <div className="relative">
                        <span className="absolute left-2 top-1 text-gray-500 text-sm">$</span>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={editItem.estimated_cost || ''}
                          onChange={e => setEditItem({ ...editItem, estimated_cost: e.target.value })}
                          className="w-full min-w-[100px] pl-6 pr-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="0.00"
                        />
                      </div>
                    ) : (
                      <span 
                        onClick={() => handleEdit(idx)}
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded block"
                        title="Click to edit"
                      >
                        ${parseFloat(item.estimated_cost || 0).toLocaleString()}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {isEditing ? (
                      <div className="relative">
                        <span className="absolute left-2 top-1 text-gray-500 text-sm">$</span>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={editItem.actual_cost || ''}
                          onChange={e => setEditItem({ ...editItem, actual_cost: e.target.value })}
                          className="w-full min-w-[100px] pl-6 pr-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="0.00"
                        />
                      </div>
                    ) : (
                      <span 
                        onClick={() => handleEdit(idx)}
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded block"
                        title="Click to edit"
                      >
                        ${parseFloat(item.actual_cost || 0).toLocaleString()}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className={variance.color}>
                      <div className="font-medium">{variance.amount}</div>
                      <div className="text-xs">{variance.percentage}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {isEditing ? (
                      <select
                        value={editItem.status || 'Not Started'}
                        onChange={e => setEditItem({ ...editItem, status: e.target.value })}
                        className="w-full min-w-[120px] px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="Not Started">Not Started</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Complete">Complete</option>
                      </select>
                    ) : (
                      <span 
                        onClick={() => handleEdit(idx)}
                        className="cursor-pointer hover:bg-gray-100 px-1 py-1 rounded block"
                        title="Click to edit"
                      >
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(item.status)}`}>
                          {item.status}
                        </span>
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {isEditing ? (
                      <textarea
                        value={editItem.notes || ''}
                        onChange={e => setEditItem({ ...editItem, notes: e.target.value })}
                        className="w-full min-w-[150px] px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                        placeholder="Notes"
                        rows={2}
                      />
                    ) : (
                      <span 
                        onClick={() => handleEdit(idx)}
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded block"
                        title="Click to edit"
                      >
                        {item.notes || '-'}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {isEditing ? (
                      <div className="flex space-x-2">
                        <button 
                          onClick={handleEditSave}
                          className="text-green-600 hover:text-green-800 text-sm font-medium px-2 py-1 rounded hover:bg-green-50"
                          title="Save changes"
                        >
                          ✓
                        </button>
                        <button 
                          onClick={handleEditCancel}
                          className="text-gray-600 hover:text-gray-800 text-sm font-medium px-2 py-1 rounded hover:bg-gray-50"
                          title="Cancel editing"
                        >
                          ✕
                        </button>
                        <button 
                          onClick={() => setShowEditModal(true)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium px-2 py-1 rounded hover:bg-blue-50"
                          title="Open in modal"
                        >
                          ⤢
                        </button>
                      </div>
                    ) : (
                      <div className="flex space-x-3">
                        <button 
                          onClick={() => handleEdit(idx)} 
                          className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100"
                          title="Edit inline"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button 
                          onClick={() => handleDelete(idx)}
                          className="text-gray-400 hover:text-red-600 p-1 rounded hover:bg-red-50"
                          title="Delete"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
            {adding && (
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <Input 
                    placeholder="Category" 
                    value={newItem.category} 
                    onChange={e => setNewItem({ ...newItem, category: e.target.value })} 
                    className="w-full"
                  />
                </td>
                <td className="px-6 py-4">
                  <Input 
                    placeholder="Description" 
                    value={newItem.description} 
                    onChange={e => setNewItem({ ...newItem, description: e.target.value })} 
                    className="w-full"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Input 
                    type="number" 
                    placeholder="0" 
                    value={newItem.estimated_cost} 
                    onChange={e => setNewItem({ ...newItem, estimated_cost: e.target.value })} 
                    className="w-24"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Input 
                    type="number" 
                    placeholder="0" 
                    value={newItem.actual_cost} 
                    onChange={e => setNewItem({ ...newItem, actual_cost: e.target.value })} 
                    className="w-24"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">-</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <select 
                    value={newItem.status} 
                    onChange={e => setNewItem({ ...newItem, status: e.target.value })}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                  >
                    <option value="Not Started">Not Started</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Complete">Complete</option>
                  </select>
                </td>
                <td className="px-6 py-4">
                  <Input 
                    placeholder="Notes" 
                    value={newItem.notes} 
                    onChange={e => setNewItem({ ...newItem, notes: e.target.value })} 
                    className="w-full"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex space-x-2">
                    <button 
                      onClick={handleAdd} 
                      className="text-green-600 hover:text-green-800 text-sm font-medium"
                    >
                      Add
                    </button>
                    <button 
                      onClick={() => setAdding(false)} 
                      className="text-gray-600 hover:text-gray-800 text-sm font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4">
        <Button 
          onClick={() => setAdding(true)} 
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          Add Line Item
        </Button>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Edit Forecast Item</h3>
            </div>
            
            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <input
                    type="text"
                    value={editItem.category || ''}
                    onChange={e => setEditItem({ ...editItem, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    placeholder="Enter category"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    value={editItem.status || 'Not Started'}
                    onChange={e => setEditItem({ ...editItem, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option value="Not Started">Not Started</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Complete">Complete</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={editItem.description || ''}
                  onChange={e => setEditItem({ ...editItem, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="Brief description of the line item"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Budgeted Amount</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500 text-sm">$</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={editItem.estimated_cost || ''}
                      onChange={e => setEditItem({ ...editItem, estimated_cost: e.target.value })}
                      className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                      placeholder="0.00"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Actual Amount</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500 text-sm">$</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={editItem.actual_cost || ''}
                      onChange={e => setEditItem({ ...editItem, actual_cost: e.target.value })}
                      className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                      placeholder="0.00"
                    />
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={editItem.notes || ''}
                  onChange={e => setEditItem({ ...editItem, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm resize-none"
                  placeholder="Additional notes and comments"
                />
              </div>
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={handleEditCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={handleEditSave}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
