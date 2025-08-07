import React, { useEffect, useState } from "react";
import { fetchProjects } from "./api";
import { Link } from "react-router-dom";

export default function ProjectList() {
  const [projects, setProjects] = useState([]);
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
