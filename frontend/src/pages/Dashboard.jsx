import { Activity, Upload, Database, MessageSquare, TrendingUp, Users } from "lucide-react";
import DashboardCard from "../components/DashboardCard";

export default function Dashboard() {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* SECTION 1: Welcome & Global Stats */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">System Overview</h1>
          <p className="text-slate-500 mt-1">Manage your knowledge base and AI interactions.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-semibold transition-all shadow-lg shadow-indigo-200">
            <Upload size={18} /> New Upload
          </button>
        </div>
      </div>

      {/* SECTION 2: The Core Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <DashboardCard 
          title="Total Documents" 
          value="1,284" 
          trend="+12% this week" 
          icon={<Database className="text-blue-600" />} 
          color="blue"
        />
        <DashboardCard 
          title="AI Queries" 
          value="850" 
          trend="+5.4%" 
          icon={<MessageSquare className="text-purple-600" />} 
          color="purple"
        />
        <DashboardCard 
          title="User Activity" 
          value="92" 
          trend="Active Now" 
          icon={<Users className="text-emerald-600" />} 
          color="emerald"
        />
        <DashboardCard 
          title="System Load" 
          value="24%" 
          trend="Optimal" 
          icon={<Activity className="text-orange-600" />} 
          color="orange"
        />
      </div>

      {/* SECTION 3: Main Dashboard Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Recent Activity */}
        <div className="lg:col-span-2 bg-white rounded-[2rem] border border-slate-100 shadow-sm p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-slate-800">Knowledge Base Health</h3>
            <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full uppercase tracking-wider">Live</span>
          </div>
          {/* Placeholder for a Chart or detailed list */}
          <div className="h-64 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="mx-auto text-slate-300 mb-2" size={40} />
              <p className="text-slate-400 font-medium">Activity Analytics Visualization</p>
            </div>
          </div>
        </div>

        {/* Right Column: Quick Tips / Status */}
        <div className="bg-indigo-900 rounded-[2rem] p-8 text-white shadow-xl relative overflow-hidden">
          <h3 className="text-xl font-bold mb-4 relative z-10">AI Insights</h3>
          <p className="text-indigo-100 text-sm leading-relaxed mb-6 relative z-10">
            Based on recent uploads, your knowledge base has grown by 20%. Consider optimizing your vector embeddings for faster retrieval.
          </p>
          <button className="w-full bg-white text-indigo-900 py-3 rounded-xl font-bold hover:bg-indigo-50 transition-colors relative z-10">
            View Reports
          </button>
          {/* Decorative Circle */}
          <div className="absolute bottom-[-20px] right-[-20px] w-32 h-32 bg-indigo-500/20 rounded-full blur-2xl"></div>
        </div>
      </div>
    </div>
  );
}