import React, { useEffect, useState } from "react";
import { fetchProjects, createProject } from "./api";
import { Link } from "react-router-dom";

export default function ProjectList() {
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', address: '', status: 'not_started', total_sqft: '' });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading projects...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Projects</h1>
      <button
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={() => setShowForm(f => !f)}
      >
        {showForm ? 'Cancel' : 'Add New Project'}
      </button>
      {showForm && (
        <form
          className="border p-4 mb-4 rounded bg-gray-50"
          onSubmit={async (e) => {
            e.preventDefault();
            setSubmitting(true);
            setFormError(null);
            try {
              const newProj = await createProject({
                ...form,
                total_sqft: form.total_sqft ? Number(form.total_sqft) : null,
              });
              setProjects(prev => [...prev, newProj]);
              setForm({ name: '', address: '', status: 'not_started', total_sqft: '' });
              setShowForm(false);
            } catch (err) {
              setFormError(err.message);
            } finally {
              setSubmitting(false);
            }
          }}
        >
          <div className="mb-2">
            <label className="block text-sm font-medium">Name *</label>
            <input
              className="border rounded px-2 py-1 w-full"
              required
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              disabled={submitting}
            />
          </div>
          <div className="mb-2">
            <label className="block text-sm font-medium">Address</label>
            <input
              className="border rounded px-2 py-1 w-full"
              value={form.address}
              onChange={e => setForm(f => ({ ...f, address: e.target.value }))}
              disabled={submitting}
            />
          </div>
          <div className="mb-2">
            <label className="block text-sm font-medium">Status</label>
            <select
              className="border rounded px-2 py-1 w-full"
              value={form.status}
              onChange={e => setForm(f => ({ ...f, status: e.target.value }))}
              disabled={submitting}
            >
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div className="mb-2">
            <label className="block text-sm font-medium">Total Sq Ft</label>
            <input
              className="border rounded px-2 py-1 w-full"
              type="number"
              value={form.total_sqft}
              onChange={e => setForm(f => ({ ...f, total_sqft: e.target.value }))}
              disabled={submitting}
            />
          </div>
          <button
            type="submit"
            className="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            disabled={submitting}
          >
            {submitting ? 'Creating...' : 'Create Project'}
          </button>
          {formError && <div className="text-red-500 mt-2">{formError}</div>}
        </form>
      )}
      <ul className="space-y-3">
        {projects.length === 0 && <li>No projects found.</li>}
        {projects.map((p) => (
          <li key={p.id} className="border p-4 rounded hover:bg-gray-50">
            <Link to={`/projects/${p.id}`} className="text-blue-600 hover:underline">
              <span className="font-semibold">{p.name}</span>
            </Link>
            <div className="text-sm text-gray-600">{p.address}</div>
            <div className="text-xs text-gray-400">Status: {p.status}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
