import React, { useEffect, useState } from 'react';
import { Database, Search, Filter, Layers, Building, ChevronDown, ChevronRight, Download, RefreshCw, CheckCircle, ExternalLink } from 'lucide-react';
import { listCommonMaterials, getCommonMaterial, listMaterials } from '../api/client';

export default function MaterialMaster() {
  const [activeSubTab, setActiveSubTab] = useState('harmonized'); // harmonized | all_materials
  const [commonMaterials, setCommonMaterials] = useState([]);
  const [selectedCM, setSelectedCM] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Raw materials tab state
  const [rawMaterials, setRawMaterials] = useState([]);
  const [rawTotal, setRawTotal] = useState(0);
  const [rawPage, setRawPage] = useState(1);
  const [cpseFilter, setCpseFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchHarmonized = async () => {
    try {
      setLoading(true);
      const params = {};
      if (categoryFilter) params.category = categoryFilter;
      if (search) params.q = search;
      const res = await listCommonMaterials(params);
      setCommonMaterials(res);
      if (res.length > 0 && !selectedCM) {
        loadCommonDetail(res[0].id);
      }
    } catch (err) {
      console.error('Failed to load common materials:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCommonDetail = async (id) => {
    try {
      const res = await getCommonMaterial(id);
      setSelectedCM(res);
    } catch (err) {
      console.error('Failed to load CM detail:', err);
    }
  };

  const fetchRaw = async () => {
    try {
      setLoading(true);
      const params = { page: rawPage, page_size: 15 };
      if (cpseFilter) params.cpse = cpseFilter;
      if (categoryFilter) params.category = categoryFilter;
      if (statusFilter) params.status = statusFilter;
      if (search) params.q = search;
      const res = await listMaterials(params);
      setRawMaterials(res.items || []);
      setRawTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load raw materials:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeSubTab === 'harmonized') {
      fetchHarmonized();
    } else {
      fetchRaw();
    }
  }, [activeSubTab, categoryFilter, cpseFilter, statusFilter, rawPage]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (activeSubTab === 'harmonized') {
      fetchHarmonized();
    } else {
      setRawPage(1);
      fetchRaw();
    }
  };

  const exportHarmonizedCSV = () => {
    if (!commonMaterials.length) return;
    const headers = ['Common Code', 'Category', 'Standardized Description', 'Mapped CPSE Count', 'Created At'];
    const rows = commonMaterials.map((c) => [
      c.common_code,
      c.category || '',
      `"${(c.standardized_description || '').replace(/"/g, '""')}"`,
      c.mapped_count,
      c.created_at
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `ekmat_harmonized_material_master.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Sub-tab Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h2 className="text-xl font-bold text-slate-900 font-['Outfit'] flex items-center space-x-2">
            <Database className="w-5 h-5 text-blue-600" />
            <span>National Material Master Catalog</span>
          </h2>
          <p className="text-xs text-slate-500">
            Harmonized golden record repository maintaining full backward traceability to all CPSE source codes.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Sub Tab Buttons */}
          <div className="flex items-center bg-slate-100 border border-slate-200 rounded-xl p-0.5 text-xs">
            <button
              onClick={() => setActiveSubTab('harmonized')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeSubTab === 'harmonized'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Harmonized National Master
            </button>
            <button
              onClick={() => setActiveSubTab('all_materials')}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                activeSubTab === 'all_materials'
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Raw CPSE Master Records
            </button>
          </div>

          {activeSubTab === 'harmonized' && (
            <button
              onClick={exportHarmonizedCSV}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 text-xs font-semibold transition-colors shadow-xs"
              title="Export Harmonized Master to CSV"
            >
              <Download className="w-3.5 h-3.5 text-emerald-600" />
              <span className="hidden sm:inline">Export CSV</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter & Search Bar */}
      <form onSubmit={handleSearchSubmit} className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-3 text-xs">
        <div className="flex-1 min-w-[240px] relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by code, equipment description, standard, material..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-xs"
          />
        </div>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-white border border-slate-200 text-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500 font-medium"
        >
          <option value="">All Categories</option>
          <option value="VALVE">VALVE</option>
          <option value="BEARING">BEARING</option>
          <option value="PUMP">PUMP</option>
          <option value="FLANGE">FLANGE</option>
        </select>

        {activeSubTab === 'all_materials' && (
          <>
            <select
              value={cpseFilter}
              onChange={(e) => setCpseFilter(e.target.value)}
              className="bg-white border border-slate-200 text-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500 font-medium"
            >
              <option value="">All CPSEs</option>
              <option value="BHEL">BHEL</option>
              <option value="ONGC">ONGC</option>
              <option value="GAIL">GAIL</option>
              <option value="NTPC">NTPC</option>
              <option value="SAIL">SAIL</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-white border border-slate-200 text-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500 font-medium"
            >
              <option value="">All Mapping Status</option>
              <option value="MAPPED">Harmonized (Mapped)</option>
              <option value="UNMAPPED">Unmapped</option>
            </select>
          </>
        )}

        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-colors shadow-xs"
        >
          Apply Filters
        </button>
      </form>

      {/* Sub Tab 1: Harmonized National Master */}
      {activeSubTab === 'harmonized' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* List (5 cols) */}
          <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col h-[70vh]">
            <div className="p-3 border-b border-slate-200 bg-slate-50 text-xs font-semibold text-slate-600 flex justify-between">
              <span>Standardized Master Entries ({commonMaterials.length})</span>
              <span>Click to view legacy mappings</span>
            </div>

            <div className="overflow-y-auto divide-y divide-slate-100 flex-1">
              {loading ? (
                <div className="p-8 text-center text-xs text-slate-500 flex flex-col items-center space-y-2">
                  <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
                  <span>Loading Harmonized Master...</span>
                </div>
              ) : commonMaterials.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500 space-y-2">
                  <span>No approved harmonized codes yet.</span>
                  <span className="block text-[11px] text-slate-400">
                    Go to Match Review and approve candidate clusters to generate Common National Codes.
                  </span>
                </div>
              ) : (
                commonMaterials.map((c) => {
                  const isSelected = selectedCM?.id === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => loadCommonDetail(c.id)}
                      className={`p-3.5 cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-blue-50/80 border-l-4 border-blue-600 text-slate-900'
                          : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-mono font-bold text-blue-700">
                          {c.common_code}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                          {c.mapped_count} Mapped CPSEs
                        </span>
                      </div>
                      <p className="text-xs text-slate-800 line-clamp-2 mb-1.5 font-semibold">
                        {c.standardized_description}
                      </p>
                      <div className="text-[10px] text-slate-500 flex justify-between">
                        <span>Category: {c.category || 'GEN'}</span>
                        <span>{c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Panel: Detail with All Mapped CPSE Records (7 cols) */}
          <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col h-[70vh]">
            {!selectedCM ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-2">
                <Database className="w-10 h-10 stroke-1" />
                <span className="text-xs">Select a Common National Material Code to inspect legacy mappings</span>
              </div>
            ) : (
              <div className="flex flex-col h-full overflow-hidden">
                {/* Header */}
                <div className="p-5 border-b border-slate-200 bg-slate-50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-base font-mono font-bold text-blue-700 bg-white px-2.5 py-1 rounded-lg border border-blue-200 select-all shadow-xs">
                      {selectedCM.common_code}
                    </span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold flex items-center">
                      <CheckCircle className="w-3.5 h-3.5 mr-1" />
                      Active Harmonized Code
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 leading-snug">
                    {selectedCM.standardized_description}
                  </h3>

                  <div className="text-xs text-slate-500 flex items-center space-x-4 pt-1">
                    <span>Category: <strong className="text-slate-800">{selectedCM.category}</strong></span>
                    <span>Mapped Enterprises: <strong className="text-emerald-700">{selectedCM.mapped_count} CPSEs</strong></span>
                  </div>
                </div>

                {/* Table of Mapped CPSE Records */}
                <div className="p-5 overflow-y-auto space-y-4 flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center">
                      <Building className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
                      Mapped Legacy CPSE Records ({selectedCM.mappings?.length || 0})
                    </h4>
                    <span className="text-[10px] text-slate-500">
                      Cross-enterprise ERP mapping table (cpse_mappings)
                    </span>
                  </div>

                  <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-xs">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold text-[11px]">
                          <th className="py-2.5 px-3">CPSE Entity</th>
                          <th className="py-2.5 px-3">Original CPSE Code</th>
                          <th className="py-2.5 px-4">CPSE Legacy Description</th>
                          <th className="py-2.5 px-3">Unit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {selectedCM.mappings?.map((m) => (
                          <tr key={m.id} className="hover:bg-slate-50/70 transition-colors">
                            <td className="py-2.5 px-3">
                              <span className="inline-block px-1.5 py-0.5 rounded bg-slate-100 text-blue-700 font-mono text-[10px] font-bold">
                                {m.cpse_code}
                              </span>
                              <span className="text-[10px] text-slate-500 block font-medium">{m.erp_system}</span>
                            </td>
                            <td className="py-2.5 px-3 font-mono font-bold text-amber-800 select-all">
                              {m.material_code}
                            </td>
                            <td className="py-2.5 px-4 text-slate-800 font-medium">
                              {m.raw_description}
                            </td>
                            <td className="py-2.5 px-3 font-semibold text-slate-600 uppercase">
                              {m.unit_of_measure}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sub Tab 2: Raw CPSE Master Records */}
      {activeSubTab === 'all_materials' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold text-[11px]">
                  <th className="py-3 px-4">CPSE</th>
                  <th className="py-3 px-3">Original Code</th>
                  <th className="py-3 px-3">Category</th>
                  <th className="py-3 px-5">Raw Description & Specs</th>
                  <th className="py-3 px-3">Unit</th>
                  <th className="py-3 px-4">Harmonized Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rawMaterials.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-100 font-mono text-blue-700 font-bold">
                        {m.cpse_code}
                      </span>
                      <span className="text-[10px] text-slate-500 block font-medium">{m.erp_system}</span>
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-amber-800 select-all">
                      {m.original_code}
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-700">
                      {m.category}
                    </td>
                    <td className="py-3 px-5 text-slate-800">
                      <div className="font-medium">{m.raw_description}</div>
                      {m.raw_specification && (
                        <span className="text-[10px] text-slate-500 block">{m.raw_specification}</span>
                      )}
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-600 uppercase">
                      {m.unit_of_measure}
                    </td>
                    <td className="py-3 px-4">
                      {m.common_code ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {m.common_code}
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600">
                          Unmapped
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between p-4 border-t border-slate-200 text-xs text-slate-500 bg-slate-50/50">
            <span>Showing {rawMaterials.length} of {rawTotal} Total CPSE Master Items</span>
            <div className="flex items-center space-x-2">
              <button
                disabled={rawPage <= 1}
                onClick={() => setRawPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed shadow-xs"
              >
                Previous
              </button>
              <span className="font-semibold text-slate-800 px-2">Page {rawPage}</span>
              <button
                disabled={rawMaterials.length < 15}
                onClick={() => setRawPage((p) => p + 1)}
                className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed shadow-xs"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
