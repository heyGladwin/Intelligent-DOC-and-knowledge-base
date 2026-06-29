import { UploadCloud, File, X, CheckCircle } from "lucide-react";
import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState(null);

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Upload Documents</h1>
        <p className="text-slate-500">Add PDFs or Text files to your AI Knowledge Base.</p>
      </div>

      <div className="bg-white p-12 rounded-[2.5rem] border-2 border-dashed border-slate-200 hover:border-indigo-400 transition-colors flex flex-col items-center justify-center group">
        <div className="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-3xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
          <UploadCloud size={40} />
        </div>
        <h3 className="text-xl font-bold text-slate-800 mb-2">Drag and drop your files here</h3>
        <p className="text-slate-400 mb-8 text-center">Support for PDF, TXT, and DOCX up to 25MB</p>
        
        <label className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-xl font-bold cursor-pointer transition-all shadow-lg shadow-indigo-200">
          Browse Files
          <input type="file" className="hidden" onChange={(e) => setFile(e.target.files[0])} />
        </label>
      </div>

      {file && (
        <div className="mt-8 bg-white p-6 rounded-2xl border border-slate-100 flex items-center justify-between animate-in zoom-in-95">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl"><File /></div>
            <div>
              <p className="font-bold text-slate-800">{file.name}</p>
              <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(2)} KB</p>
            </div>
          </div>
          <button onClick={() => setFile(null)} className="text-slate-300 hover:text-red-500"><X /></button>
        </div>
      )}
    </div>
  );
}