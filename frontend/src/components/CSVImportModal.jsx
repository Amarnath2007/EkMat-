import React, { useState } from 'react';
import { X, UploadCloud, FileSpreadsheet, CheckCircle, AlertTriangle, AlertCircle, RefreshCw } from 'lucide-react';
import { importMaterialsCSV } from '../api/client';

export default function CSVImportModal({ isOpen, onClose, onImportSuccess }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (!selected.name.endsWith('.csv')) {
        setError('Only .csv files are supported.');
        setFile(null);
      } else {
        setFile(selected);
        setError(null);
        setResult(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file to upload.');
      return;
    }

    setIsUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await importMaterialsCSV(formData);
      setResult(res);
      if (onImportSuccess) {
        onImportSuccess(res);
      }
    } catch (err) {
      setError(err.message || 'Failed to import CSV.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg border border-blue-200">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 font-['Outfit']">Import CPSE Material Master CSV</h3>
              <p className="text-xs text-slate-500">Row-level validation: duplicate detection, attribute extraction, and vector embedding</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* File Picker Zone */}
          {!result && (
            <div className="space-y-4">
              <label
                htmlFor="csv-dropzone"
                className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl p-8 cursor-pointer bg-slate-50/50 hover:bg-blue-50/20 transition-all group"
              >
                <FileSpreadsheet className="w-12 h-12 text-slate-400 group-hover:text-blue-600 transition-colors mb-3" />
                <span className="text-sm font-semibold text-slate-700">
                  {file ? file.name : 'Click to select or drag and drop CPSE Master CSV'}
                </span>
                <span className="text-xs text-slate-500 mt-1">
                  Required columns: <code className="text-slate-700 bg-slate-100 px-1 py-0.5 rounded font-mono">cpse, material_code, description, category</code>
                </span>
                <input
                  id="csv-dropzone"
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>

              {file && (
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                  <div className="flex items-center space-x-2">
                    <FileSpreadsheet className="w-4 h-4 text-blue-600" />
                    <span className="text-slate-800 font-semibold">{file.name}</span>
                    <span className="text-slate-500">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <button onClick={handleReset} className="text-rose-600 hover:text-rose-700 font-semibold">
                    Remove
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start space-x-3 text-xs text-rose-800">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Validation Error</span>
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Upload Results Summary */}
          {result && (
            <div className="space-y-4 animate-fadeIn">
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-center">
                  <span className="text-xs text-slate-500 block">Total Processed</span>
                  <span className="text-2xl font-bold text-slate-900">{result.total_rows_processed}</span>
                </div>
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-center">
                  <span className="text-xs text-emerald-700 block font-medium">Accepted & Ingested</span>
                  <span className="text-2xl font-bold text-emerald-700">{result.accepted_count}</span>
                </div>
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-center">
                  <span className="text-xs text-rose-700 block font-medium">Rejected / Invalid</span>
                  <span className="text-2xl font-bold text-rose-700">{result.rejected_count}</span>
                </div>
              </div>

              {result.rejected_rows && result.rejected_rows.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mr-1.5" />
                    Row-Level Validation Rejections ({result.rejected_rows.length})
                  </h4>
                  <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-xl bg-slate-50 divide-y divide-slate-200">
                    {result.rejected_rows.map((rej, idx) => (
                      <div key={idx} className="p-2.5 text-xs flex items-start justify-between">
                        <div>
                          <span className="font-semibold text-slate-800 mr-2">Row #{rej.row_number}</span>
                          <span className="text-slate-600 font-mono">[{rej.cpse || 'N/A'}] {rej.material_code || 'Empty Code'}</span>
                        </div>
                        <span className="text-rose-600 text-right ml-4 font-medium">{rej.error}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={handleReset}
                className="w-full py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
              >
                Upload Another CSV
              </button>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end space-x-3 px-6 py-4 border-t border-slate-200 bg-slate-50">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
          >
            Close
          </button>
          {!result && (
            <button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className={`flex items-center space-x-2 px-5 py-2 rounded-xl text-xs font-bold text-white transition-all ${
                !file || isUploading
                  ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-sm shadow-blue-500/20 active:scale-95'
              }`}
            >
              {isUploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Validating & Embedding...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Validate & Ingest</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
