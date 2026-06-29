import { Link } from "react-router-dom";
import { TrendingUp } from "lucide-react"; // Make sure to import this

export default function DashboardCard({ title, value, trend, icon, color, path }) {
  // Mapping the color prop to professional background/text combinations
  const colorMap = {
    blue: "bg-blue-50 text-blue-600 border-blue-100",
    purple: "bg-purple-50 text-purple-600 border-purple-100",
    emerald: "bg-emerald-50 text-emerald-600 border-emerald-100",
    orange: "bg-orange-50 text-orange-600 border-orange-100",
    indigo: "bg-indigo-50 text-indigo-600 border-indigo-100",
  };

  const selectedColor = colorMap[color] || colorMap.indigo;

  return (
    <Link to={path} className="group block">
      <div className="relative bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm transition-all duration-500 hover:shadow-2xl hover:shadow-indigo-100/50 hover:-translate-y-2 overflow-hidden">
        
        {/* Top Section: Icon and Trend Badge */}
        <div className="flex items-start justify-between mb-4">
          <div className={`p-4 rounded-2xl ${selectedColor} border transition-transform duration-500 group-hover:rotate-[10deg] group-hover:scale-110`}>
            {icon}
          </div>
          
          {trend && (
            <div className="flex items-center gap-1 px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full border border-emerald-100">
              <TrendingUp size={12} strokeWidth={3} />
              <span className="text-[10px] font-black uppercase tracking-tighter">{trend}</span>
            </div>
          )}
        </div>

        {/* Bottom Section: Title and Value */}
        <div className="space-y-1">
          <h4 className="text-slate-400 font-bold text-xs uppercase tracking-[0.15em]">
            {title}
          </h4>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-black text-slate-900 tracking-tight">
              {value}
            </p>
            <span className="text-[10px] text-slate-400 font-medium italic">Updated just now</span>
          </div>
        </div>

        {/* Decorative Background Element */}
        <div className={`absolute -right-6 -bottom-6 w-24 h-24 rounded-full opacity-[0.05] transition-transform duration-700 group-hover:scale-[2] ${selectedColor.split(' ')[0]}`}></div>
      </div>
    </Link>
  );
}