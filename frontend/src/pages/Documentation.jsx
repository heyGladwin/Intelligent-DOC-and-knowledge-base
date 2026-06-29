import { FileText, Download, Trash2, Clock, ShieldCheck, Search, Filter } from "lucide-react";

export default function Documentation() {
  // This array will eventually be replaced by your MongoDB data
  const docs = [
    { id: 1, name: "Technical_Specs_v1.pdf", size: "1.2 MB", type: "PDF", status: "Indexed", date: "Jan 30, 2026" },
    { id: 2, name: "Knowledge_Base_Export.csv", size: "4.5 MB", type: "CSV", status: "Processing", date: "Feb 01, 2026" },
    { id: 3, name: "AI_Training_Guidelines.docx", size: "890 KB", type: "DOCX", status: "Indexed", date: "Jan 28, 2026" },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* 1. Header & Quick Search */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Documentation</h1>
          <p className="text-slate-500 font-medium">Manage your indexed knowledge and document library.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input 
              type="text" 
              placeholder="Filter docs..." 
              className="pl-11 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl shadow-sm focus:ring-2 focus:ring-indigo-500 outline-none w-64"
            />
          </div>
          <button className="p-2.5 bg-white border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors">
            <Filter size={20} />
          </button>
        </div>
      </div>

      {/* 2. Top Stats - The "Appealing" Mini-Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-indigo-600 to-blue-700 p-6 rounded-[2rem] text-white shadow-xl flex items-center justify-between">
          <div>
            <p className="text-indigo-100 text-xs font-bold uppercase tracking-wider mb-1">Vault Security</p>
            <h3 className="text-2xl font-black italic">ENCRYPTED</h3>
          </div>
          <ShieldCheck size={40} className="text-white/20" />
        </div>
        
        <div className="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-2xl flex items-center justify-center">
            <FileText size={24} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-tighter">Live Docs</p>
            <h3 className="text-2xl font-black text-slate-800">{docs.length}</h3>
          </div>
        </div>

        <div className="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 bg-amber-50 text-amber-600 rounded-2xl flex items-center justify-center animate-pulse">
            <Clock size={24} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-tighter">Last Update</p>
            <h3 className="text-2xl font-black text-slate-800 italic">Feb 1</h3>
          </div>
        </div>
      </div>

      {/* 3. The Professional Table */}
      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50/50 border-b border-slate-100">
              <tr>
                <th className="px-8 py-5 text-xs font-bold text-slate-400 uppercase tracking-widest">Filename</th>
                <th className="px-8 py-5 text-xs font-bold text-slate-400 uppercase tracking-widest text-center">Status</th>
                <th className="px-8 py-5 text-xs font-bold text-slate-400 uppercase tracking-widest">Size</th>
                <th className="px-8 py-5 text-xs font-bold text-slate-400 uppercase tracking-widest">Date Added</th>
                <th className="px-8 py-5 text-xs font-bold text-slate-400 uppercase tracking-widest text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {docs.map((doc) => (
                <tr key={doc.id} className="group hover:bg-indigo-50/30 transition-all duration-300">
                  <td className="px-8 py-5">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center font-bold text-[10px] group-hover:scale-110 transition-transform">
                        {doc.type}
                      </div>
                      <span className="font-bold text-slate-700">{doc.name}</span>
                    </div>
                  </td>
                  <td className="px-8 py-5 text-center">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                      doc.status === 'Indexed' 
                      ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                      : 'bg-amber-100 text-amber-700 border border-amber-200 animate-pulse'
                    }`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-8 py-5 text-slate-500 font-medium text-sm">{doc.size}</td>
                  <td className="px-8 py-5 text-slate-500 font-medium text-sm">{doc.date}</td>
                  <td className="px-8 py-5 text-right">
                    <div className="flex justify-end gap-2">
                      <button className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-white rounded-lg transition-all shadow-sm border border-transparent hover:border-slate-100">
                        <Download size={18} />
                      </button>
                      <button className="p-2 text-slate-400 hover:text-red-500 hover:bg-white rounded-lg transition-all shadow-sm border border-transparent hover:border-slate-100">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}