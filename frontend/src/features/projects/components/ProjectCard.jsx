import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../../../components/ui';

const ProjectCard = ({ project, onEdit, onDelete }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md hover:border-blue-300 transition-all duration-200 group">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
          {project.name}
        </h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
          {project.status?.replace('_', ' ').toUpperCase() || 'NOT STARTED'}
        </span>
      </div>
      
      {project.address && (
        <p className="text-gray-600 text-sm mb-3 truncate">{project.address}</p>
      )}
      
      {/* Key Details */}
      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between">
          <span className="text-gray-500">Start:</span>
          <span className="text-gray-900 font-medium">{formatDate(project.start_date)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Target:</span>
          <span className="text-gray-900 font-medium">{formatDate(project.target_completion_date)}</span>
        </div>
        {project.total_sqft && (
          <div className="flex justify-between">
            <span className="text-gray-500">Sq Ft:</span>
            <span className="text-gray-900 font-medium">{project.total_sqft.toLocaleString()}</span>
          </div>
        )}
        {project.total_budget && (
          <div className="flex justify-between">
            <span className="text-gray-500">Budget:</span>
            <span className="text-gray-900 font-semibold">${parseFloat(project.total_budget).toLocaleString()}</span>
          </div>
        )}
      </div>
      
      {/* Actions */}
      <div className="flex gap-2">
        <Link to={`/projects/${project.id}`} className="flex-1">
          <Button variant="primary" className="w-full text-sm py-2">
            View Details
          </Button>
        </Link>
        <Button variant="secondary" onClick={() => onEdit(project)} className="px-3 text-sm py-2">
          Edit
        </Button>
        <Button variant="danger" onClick={() => onDelete(project.id)} className="px-3 text-sm py-2">
          Delete
        </Button>
      </div>
    </div>
  );
};

export default ProjectCard;
