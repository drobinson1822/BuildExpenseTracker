import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchProject, fetchForecastItems, fetchExpenses, createOrUpdateExpense } from "./api";
import ForecastTable from "./ForecastTable";

export default function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [forecastItems, setForecastItems] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- Budget summary calculations ---
  // Proposed = sum of all forecast line items
  const totalForecast = forecastItems.reduce((sum, i) => sum + Number(i.estimated_cost || 0), 0);
  // Actual = sum of all actual expenses for this project
  const totalActual = expenses.reduce((sum, e) => sum + Number(e.amount_spent || 0), 0);

  // Add line item
  async function handleAddLineItem(newItem) {
    try {
      const res = await fetch("http://localhost:8000/api/forecast-items/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newItem,
          project_id: Number(id),
          estimated_cost: Number(newItem.estimated_cost),
          progress_percent: Number(newItem.progress_percent)
        })
      });
      if (!res.ok) throw new Error("Failed to add forecast item");
      const added = await res.json();
      setForecastItems((prev) => [...prev, added]);
    } catch (e) {
      alert(e.message);
    }
  }

  // Utility: aggregate project status from forecastItems
  function aggregateProjectStatus(items) {
    if (items.length === 0) return "not_started";
    const allStatuses = items.map(i => i.status);
    if (allStatuses.every(s => s === "completed")) return "completed";
    if (allStatuses.every(s => s === "not_started")) return "not_started";
    return "in_progress";
  }

  // Sync project status to backend if needed
  async function syncProjectStatus(newStatus) {
    if (!project) return;
    if (project.status !== newStatus) {
      try {
        const res = await fetch(`http://localhost:8000/api/projects/${project.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...project, status: newStatus })
        });
        if (!res.ok) throw new Error("Failed to update project status");
        const updated = await res.json();
        setProject(updated);
      } catch (e) {
        // Optionally show error
      }
    }
  }

  // Edit line item
  async function handleEditLineItem(itemId, changes) {
    try {
      // Update forecast line item
      const res = await fetch(`http://localhost:8000/api/forecast-items/${itemId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...changes,
          project_id: Number(id),
          estimated_cost: Number(changes.estimated_cost),
          progress_percent: Number(changes.progress_percent)
        })
      });
      if (!res.ok) throw new Error("Failed to update line item");
      const updated = await res.json();
      setForecastItems((prev) => {
        const newItems = prev.map(i => i.id === itemId ? updated : i);
        // After updating, recompute project status and sync if needed
        const aggStatus = aggregateProjectStatus(newItems);
        syncProjectStatus(aggStatus);
        return newItems;
      });

      // Handle actual expense update if present
      if (changes.actual !== undefined) {
        // Find existing expense for this forecast line item
        const existing = expenses.find(e => e.forecast_line_item_id === itemId);
        const expensePayload = {
          project_id: Number(id),
          forecast_line_item_id: itemId,
          amount_spent: Number(changes.actual),
          date: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
        };
        let saved;
        if (existing) {
          saved = await createOrUpdateExpense({ ...existing, ...expensePayload }, existing.id);
          setExpenses((prev) => prev.map(e => e.id === existing.id ? saved : e));
        } else {
          saved = await createOrUpdateExpense(expensePayload);
          setExpenses((prev) => [...prev, saved]);
        }
      }
    } catch (e) {
      alert(e.message);
    }
  }

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchProject(id),
      fetchForecastItems(),
      fetchExpenses()
    ])
      .then(([proj, items, exps]) => {
        setProject(proj);
        setForecastItems(items.filter(i => i.project_id === Number(id)));
        setExpenses(exps.filter(e => e.project_id === Number(id)));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-4">Loading project...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;
  if (!project) return <div className="p-4">Project not found.</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
  <Link to="/" className="text-blue-600 hover:underline">&larr; Back to Projects</Link>
  <div className="bg-white rounded-xl shadow-md p-6 flex flex-col md:flex-row md:items-center md:justify-between mt-4 mb-6 gap-6">
    <div className="flex-1 min-w-0">
      <h1 className="text-3xl font-bold mb-1 truncate">{project.name}</h1>
      <div className="flex flex-wrap gap-4 items-center text-gray-600 mb-2">
        <span className="inline-flex items-center"><svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 12.414a2 2 0 00-2.828 0l-4.243 4.243m6.364-6.364a4 4 0 115.656 5.656M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>{project.address}</span>
        {typeof project.total_sqft === "number" && (
          <span className="inline-flex items-center"><svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>Sq Ft: <span className="font-semibold ml-1">{project.total_sqft.toLocaleString()}</span></span>
        )}
        <span className="inline-flex items-center"><svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 4h10a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V9a2 2 0 012-2z" /></svg>Start: {project.start_date || <span className="text-gray-400">N/A</span>}</span>
        <span className="inline-flex items-center"><svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 9V7a5 5 0 00-10 0v2m12 4h-1a2 2 0 01-2-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2v4a2 2 0 01-2 2H5" /></svg>End: {project.target_completion_date || <span className="text-gray-400">N/A</span>}</span>
      </div>
    </div>
    <div className="flex flex-col gap-2 min-w-[220px] md:items-end">
      <div className="flex gap-4">
        <div className="text-lg font-semibold">Forecast: <span className="text-blue-700">${totalForecast.toLocaleString()}</span></div>
        <div className={`text-lg font-semibold ${totalActual <= totalForecast ? 'text-green-700' : 'text-red-700'}`}>Actual: ${totalActual.toLocaleString()}</div>
      </div>
      <div className="flex items-center gap-2 mt-1">
        <span className="text-gray-500">Status:</span>
        <select
          className="inline-block rounded-full px-3 py-1 text-sm font-medium bg-gray-100 border border-gray-200 text-gray-700 cursor-not-allowed"
          value={aggregateProjectStatus(forecastItems)}
          disabled
        >
          <option value="not_started">Not Started</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>
    </div>
  </div>
  <div className="border-t border-gray-200 mb-2"></div>
  <h2 className="text-xl font-semibold mt-2 mb-4">Budget Table</h2>
  <ForecastTable
    items={forecastItems}
    expenses={expenses}
    onAdd={handleAddLineItem}
    onEdit={handleEditLineItem}
  />
</div>
  );
}
