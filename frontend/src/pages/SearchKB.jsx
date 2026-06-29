import { Search, Filter, ArrowRight } from "lucide-react";

export default function SearchPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="relative">
        <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400" size={24} />
        <input 
          type="text" 
          placeholder="Search through your knowledge base..." 
          className="w-full pl-16 pr-6 py-6 bg-white border border-slate-100 rounded-[2rem] shadow-xl focus:ring-4 focus:ring-indigo-100 outline-none text-xl font-medium"
        />
      </div>

      <div className="grid grid-cols-1 gap-4">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest px-4">Recent Findings</h3>
        {[1, 2, 3].map((item) => (
          <div key={item} className="bg-white p-6 rounded-3xl border border-slate-100 hover:shadow-md transition-shadow flex items-center justify-between group">
            <div className="flex flex-col gap-1">
              <span className="text-xs font-bold text-indigo-500">Document Fragment #{item}</span>
              <p className="text-slate-700 font-semibold italic">"The project completion date is set for December 2026..."</p>
            </div>
            <ArrowRight className="text-slate-300 group-hover:text-indigo-500 group-hover:translate-x-2 transition-all" />
          </div>
        ))}
      </div>
    </div>
  );
}