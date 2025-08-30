import React, { useState, useEffect } from 'react';
import { Button, Input } from '../../../components/ui';

const ProjectForm = ({ project, onSubmit, onCancel, loading = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    start_date: '',
    target_completion_date: '',
    status: 'not_started',
    total_sqft: '',
    total_budget: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (project) {
      setFormData({
        name: project.name || '',
        address: project.address || '',
        start_date: project.start_date || '',
        target_completion_date: project.target_completion_date || '',
        status: project.status || 'not_started',
        total_sqft: project.total_sqft || '',
        total_budget: project.total_budget || ''
      });
    }
  }, [project]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    }

    if (formData.total_sqft && isNaN(formData.total_sqft)) {
      newErrors.total_sqft = 'Total square feet must be a number';
    }

    if (formData.total_budget && isNaN(formData.total_budget)) {
      newErrors.total_budget = 'Total budget must be a number';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validateForm();
    
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setErrors({});

    try {
      await onSubmit({
        ...formData,
        total_sqft: formData.total_sqft ? parseInt(formData.total_sqft) : null,
        total_budget: formData.total_budget ? parseFloat(formData.total_budget) : null
      });
    } catch (error) {
      setErrors({ general: error.message || 'Failed to save project' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Input
          label="Project Name"
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          error={errors.name}
          required
          placeholder="Enter project name"
        />
      </div>

      <div>
        <Input
          label="Address"
          type="text"
          name="address"
          value={formData.address}
          onChange={handleChange}
          error={errors.address}
          placeholder="Enter project address"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Input
            label="Start Date"
            type="date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            error={errors.start_date}
          />
        </div>

        <div>
          <Input
            label="Target Completion Date"
            type="date"
            name="target_completion_date"
            value={formData.target_completion_date}
            onChange={handleChange}
            error={errors.target_completion_date}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="not_started">Not Started</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <div>
          <Input
            label="Total Square Feet"
            type="number"
            name="total_sqft"
            value={formData.total_sqft}
            onChange={handleChange}
            error={errors.total_sqft}
            placeholder="Enter total square feet"
          />
        </div>
      </div>

      <div>
        <Input
          label="Total Budget"
          type="number"
          name="total_budget"
          value={formData.total_budget}
          onChange={handleChange}
          error={errors.total_budget}
          placeholder="Enter total project budget"
          step="0.01"
        />
      </div>

      {errors.general && (
        <div className="text-red-600 text-sm text-center">
          {errors.general}
        </div>
      )}

      <div className="flex gap-3 justify-end">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={loading}
        >
          {loading ? 'Saving...' : (project ? 'Update Project' : 'Create Project')}
        </Button>
      </div>
    </form>
  );
};

export default ProjectForm;
