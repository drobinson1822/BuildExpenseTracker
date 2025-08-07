import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ProjectList from "./ProjectList";
import ProjectDetail from "./ProjectDetail";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <header className="bg-blue-700 text-white p-4 mb-4">
          <h1 className="text-2xl font-bold">Construction Cost Tracker</h1>
          <p className="text-sm">MVP - Forecast, Track, and Visualize Home Build Costs</p>
        </header>
        <main className="container mx-auto px-4">
          <Routes>
            <Route path="/" element={<ProjectList />} />
            <Route path="/projects/:id" element={<ProjectDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
