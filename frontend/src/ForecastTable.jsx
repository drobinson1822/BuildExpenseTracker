import React, { useState } from "react";

export default function ForecastTable({ items, expenses, onAdd, onEdit }) {
  const [adding, setAdding] = useState(false);
  const [newItem, setNewItem] = useState({
    category: "",
    estimated_cost: "",
    unit: "",
    notes: "",
    progress_percent: 0,
    status: "not_started",
    start_date: "",
    end_date: ""
  });
  const [editIdx, setEditIdx] = useState(null);
  const [editItem, setEditItem] = useState({});

  // Map forecast item id to sum of actual expenses
  const actualsMap = {};
  for (const exp of expenses) {
    if (!actualsMap[exp.forecast_line_item_id]) actualsMap[exp.forecast_line_item_id] = 0;
    actualsMap[exp.forecast_line_item_id] += exp.amount_spent;
  }

  function handleAdd() {
    onAdd(newItem);
    setNewItem({ category: "", estimated_cost: "", unit: "", notes: "", progress_percent: 0, status: "not_started", start_date: "", end_date: "" });
    setAdding(false);
  }

  function handleEdit(idx) {
    setEditIdx(idx);
    setEditItem({ ...items[idx] });
  }

  async function handleEditSave(idx) {
    // Await the parent onEdit to ensure state is updated before closing edit mode
    await onEdit(items[idx].id, editItem);
    setEditIdx(null);
  }

  function handleCellClick(idx) {
    setEditIdx(idx);
    setEditItem({ ...items[idx] });
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border bg-white text-sm rounded-xl overflow-hidden shadow-sm">
  <thead>
    <tr className="bg-gray-100 text-gray-700">
      <th className="px-4 py-2 font-semibold">Category</th>
      <th className="px-4 py-2 font-semibold">Description</th>
      <th className="px-4 py-2 font-semibold">Start Date</th>
      <th className="px-4 py-2 font-semibold">End Date</th>
      <th className="px-4 py-2 font-semibold">Est. Cost</th>
      <th className="px-4 py-2 font-semibold">Actual</th>
      <th className="px-4 py-2 font-semibold">Progress</th>
      <th className="px-4 py-2 font-semibold">Status</th>
      <th className="px-4 py-2 font-semibold"></th>
    </tr>
  </thead>
  <tbody>
    {items.map((item, idx) => (
      <tr
        key={item.id}
        className={`transition hover:bg-blue-50 ${editIdx === idx ? 'bg-blue-100' : ''}`}
        onClick={() => editIdx === null && handleCellClick(idx)}
        style={{ cursor: editIdx === null ? 'pointer' : 'default' }}
      >
        {editIdx === idx ? (
          <>
            <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" value={editItem.category} onChange={e => setEditItem({ ...editItem, category: e.target.value })} /></td>
            <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" value={editItem.notes} onChange={e => setEditItem({ ...editItem, notes: e.target.value })} /></td>
            <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="date" value={editItem.start_date || ''} onChange={e => setEditItem({ ...editItem, start_date: e.target.value })} /></td>
            <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="date" value={editItem.end_date || ''} onChange={e => setEditItem({ ...editItem, end_date: e.target.value })} /></td>
            <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="number" value={editItem.estimated_cost} onChange={e => setEditItem({ ...editItem, estimated_cost: e.target.value })} /></td>
            <td className="border px-4 py-2 text-right"><input className="w-full bg-white border rounded px-2 py-1 text-right" type="number" value={editItem.actual !== undefined ? editItem.actual : (actualsMap[item.id] || 0)} onChange={e => setEditItem({ ...editItem, actual: e.target.value })} /></td>
            <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="number" value={editItem.progress_percent} onChange={e => setEditItem({ ...editItem, progress_percent: e.target.value })} /></td>
            <td className="border px-4 py-2"><select className="w-full bg-white border rounded px-2 py-1" value={editItem.status} onChange={e => setEditItem({ ...editItem, status: e.target.value })}>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select></td>
            <td className="border px-4 py-2 flex gap-2 items-center justify-center">
              <button className="text-green-600 hover:bg-green-50 rounded p-1" onClick={e => { e.stopPropagation(); handleEditSave(idx); }} title="Save"><svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg></button>
              <button className="text-gray-500 hover:bg-gray-100 rounded p-1" onClick={e => { e.stopPropagation(); setEditIdx(null); }} title="Cancel"><svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg></button>
            </td>
          </>
        ) : (
          <>
            <td className="border px-4 py-2">{item.category}</td>
            <td className="border px-4 py-2">{item.notes}</td>
            <td className="border px-4 py-2">{item.start_date || <span className="text-gray-400">N/A</span>}</td>
            <td className="border px-4 py-2">{item.end_date || <span className="text-gray-400">N/A</span>}</td>
            <td className="border px-4 py-2">${item.estimated_cost}</td>
            <td className="border px-4 py-2 text-right">${actualsMap[item.id] || 0}</td>
            <td className="border px-4 py-2">{item.progress_percent}%</td>
            <td className="border px-4 py-2">{
              item.status === "not_started"
                ? "Not Started"
                : item.status === "in_progress"
                ? "In Progress"
                : item.status === "completed"
                ? "Completed"
                : item.status
            }</td>
            <td className="border px-4 py-2"></td>
          </>
        )}
      </tr>
    ))}
    {adding ? (
      <tr className="bg-yellow-50">
        <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" value={newItem.category} onChange={e => setNewItem({ ...newItem, category: e.target.value })} /></td>
        <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" value={newItem.notes} onChange={e => setNewItem({ ...newItem, notes: e.target.value })} /></td>
        <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="date" value={newItem.start_date} onChange={e => setNewItem({ ...newItem, start_date: e.target.value })} /></td>
        <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="date" value={newItem.end_date} onChange={e => setNewItem({ ...newItem, end_date: e.target.value })} /></td>
        <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="number" value={newItem.estimated_cost} onChange={e => setNewItem({ ...newItem, estimated_cost: e.target.value })} /></td>
        <td className="border px-4 py-2 text-right">-</td>
        <td className="border px-4 py-2"><input className="w-full bg-white border rounded px-2 py-1" type="number" value={newItem.progress_percent} onChange={e => setNewItem({ ...newItem, progress_percent: e.target.value })} /></td>
        <td className="border px-4 py-2"><select className="w-full bg-white border rounded px-2 py-1" value={newItem.status} onChange={e => setNewItem({ ...newItem, status: e.target.value })}>
          <option value="not_started">Not Started</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select></td>
        <td className="border px-4 py-2 flex gap-2 items-center justify-center">
          <button className="text-green-600 hover:bg-green-50 rounded p-1" onClick={handleAdd} title="Add"><svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg></button>
          <button className="text-gray-500 hover:bg-gray-100 rounded p-1" onClick={() => setAdding(false)} title="Cancel"><svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg></button>
        </td>
      </tr>
    ) : null}
  </tbody>
</table>
<div className="mt-4">
  <button className="bg-blue-600 text-white px-5 py-2 rounded-lg shadow hover:bg-blue-700 transition" onClick={() => setAdding(true)} disabled={adding}>Add Line Item</button>
</div>
      <div className="mt-2">
        <button className="bg-blue-600 text-white px-4 py-1 rounded" onClick={() => setAdding(true)} disabled={adding}>Add Line Item</button>
      </div>
    </div>
  );
}
