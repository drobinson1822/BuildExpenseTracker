import React, { useState } from "react";

export default function ForecastTable({ items, expenses, onAdd, onEdit }) {
  const [adding, setAdding] = useState(false);
  const [newItem, setNewItem] = useState({
    category: "",
    estimated_cost: "",
    unit: "",
    notes: "",
    progress_percent: 0,
    status: "Not Started"
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
    setNewItem({ category: "", estimated_cost: "", unit: "", notes: "", progress_percent: 0, status: "Not Started" });
    setAdding(false);
  }

  function handleEdit(idx) {
    setEditIdx(idx);
    setEditItem({ ...items[idx] });
  }

  function handleEditSave(idx) {
    onEdit(items[idx].id, editItem);
    setEditIdx(null);
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border text-xs bg-white">
        <thead>
          <tr className="bg-gray-50">
            <th className="border px-1 py-0.5">Cat.</th>
            <th className="border px-1 py-0.5">Desc.</th>
            <th className="border px-1 py-0.5">Est.</th>
            <th className="border px-1 py-0.5">Actual</th>
            <th className="border px-1 py-0.5">Prog%</th>
            <th className="border px-1 py-0.5">Status</th>
            <th className="border px-1 py-0.5">Edit</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={item.id} className="hover:bg-blue-50">
              {editIdx === idx ? (
                <>
                  <td className="border p-2"><input className="w-full" value={editItem.category} onChange={e => setEditItem({ ...editItem, category: e.target.value })} /></td>
                  <td className="border p-2"><input className="w-full" value={editItem.notes} onChange={e => setEditItem({ ...editItem, notes: e.target.value })} /></td>
                  <td className="border p-2"><input className="w-full" type="number" value={editItem.estimated_cost} onChange={e => setEditItem({ ...editItem, estimated_cost: e.target.value })} /></td>
                  <td className="border p-2 text-right">
                    <input
                      className="w-full text-right"
                      type="number"
                      value={editItem.actual !== undefined ? editItem.actual : (actualsMap[item.id] || 0)}
                      onChange={e => setEditItem({ ...editItem, actual: e.target.value })}
                    />
                  </td>
                  <td className="border p-2"><input className="w-full" type="number" value={editItem.progress_percent} onChange={e => setEditItem({ ...editItem, progress_percent: e.target.value })} /></td>
                  <td className="border p-2"><input className="w-full" value={editItem.status} onChange={e => setEditItem({ ...editItem, status: e.target.value })} /></td>
                  <td className="border p-2">
                    <button className="text-green-600 mr-2" onClick={() => handleEditSave(idx)}>Save</button>
                    <button className="text-gray-500" onClick={() => setEditIdx(null)}>Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  <td className="border p-2">{item.category}</td>
                  <td className="border p-2">{item.notes}</td>
                  <td className="border p-2">${item.estimated_cost}</td>
                  <td className="border p-2 text-right">${actualsMap[item.id] || 0}</td>

                  <td className="border p-2">{item.progress_percent}%</td>
                  <td className="border p-2">{item.status}</td>
                  <td className="border p-2">
                    <button className="text-blue-600 mr-2" onClick={() => handleEdit(idx)}>Edit</button>
                  </td>
                </>
              )}
            </tr>
          ))}
          {adding ? (
            <tr className="bg-yellow-50">
              <td className="border p-2"><input className="w-full" value={newItem.category} onChange={e => setNewItem({ ...newItem, category: e.target.value })} /></td>
              <td className="border p-2"><input className="w-full" value={newItem.notes} onChange={e => setNewItem({ ...newItem, notes: e.target.value })} /></td>
              <td className="border p-2"><input className="w-full" type="number" value={newItem.estimated_cost} onChange={e => setNewItem({ ...newItem, estimated_cost: e.target.value })} /></td>
              <td className="border p-2 text-right">-</td>

              <td className="border p-2"><input className="w-full" type="number" value={newItem.progress_percent} onChange={e => setNewItem({ ...newItem, progress_percent: e.target.value })} /></td>
              <td className="border p-2"><input className="w-full" value={newItem.status} onChange={e => setNewItem({ ...newItem, status: e.target.value })} /></td>
              <td className="border p-2">
                <button className="text-green-600 mr-2" onClick={handleAdd}>Add</button>
                <button className="text-gray-500" onClick={() => setAdding(false)}>Cancel</button>
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
      <div className="mt-2">
        <button className="bg-blue-600 text-white px-4 py-1 rounded" onClick={() => setAdding(true)} disabled={adding}>Add Line Item</button>
      </div>
    </div>
  );
}
