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
      setForecastItems((prev) => prev.map(i => i.id === itemId ? updated : i));

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
    <div className="max-w-5xl mx-auto p-4">
      <Link to="/" className="text-blue-600 hover:underline">&larr; Back to Projects</Link>
      <h1 className="text-2xl font-bold mt-2 mb-1">{project.name}</h1>
      <div className="mb-2 text-gray-700">{project.address}</div>
      <div className="flex flex-wrap gap-4 items-center mb-4">
        <div className="text-lg font-semibold">Total Forecast: <span className="text-blue-700">${totalForecast.toLocaleString()}</span></div>
        <div className={`text-lg font-semibold ${totalActual <= totalForecast ? 'text-green-700' : 'text-red-700'}`}>Actual: ${totalActual.toLocaleString()}</div>
        <div className="text-gray-500 text-sm flex items-center gap-2">
          <span>Status:</span>
          <select
            className="border rounded px-2 py-1 text-sm"
            value={project.status}
            onChange={async (e) => {
              const newStatus = e.target.value;
              try {
                const res = await fetch(`http://localhost:8000/api/projects/${project.id}`, {
                  method: "PUT",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ ...project, status: newStatus })
                });
                if (!res.ok) throw new Error("Failed to update project status");
                const updated = await res.json();
                setProject(updated);
              } catch (err) {
                alert("Failed to update status: " + err.message);
              }
            }}
          >
            <option value="not_started">Not Started</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>
      <h2 className="text-xl font-semibold mt-4 mb-2">Budget Table</h2>
      <ForecastTable
        items={forecastItems}
        expenses={expenses}
        onAdd={handleAddLineItem}
        onEdit={handleEditLineItem}
      />
    </div>
  );
}
