import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import Login from "./Login";
import Register from "./Register";
import ProjectList from "./ProjectList";
import ProjectDetail from "./ProjectDetail";

function AppHeader() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header className="bg-blue-700 text-white p-4 mb-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Construction Cost Tracker</h1>
          <p className="text-sm">MVP - Forecast, Track, and Visualize Home Build Costs</p>
        </div>
        {isAuthenticated && (
          <div className="flex items-center space-x-4">
            <span className="text-sm">Welcome, {user?.full_name || user?.email}</span>
            <button
              onClick={logout}
              className="bg-blue-600 hover:bg-blue-800 px-3 py-1 rounded text-sm"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

function AppContent() {
  return (
    <div className="min-h-screen bg-gray-100">
      <AppHeader />
      <main className="container mx-auto px-4">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={
            <ProtectedRoute>
              <ProjectList />
            </ProtectedRoute>
          } />
          <Route path="/projects/:id" element={
            <ProtectedRoute>
              <ProjectDetail />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
