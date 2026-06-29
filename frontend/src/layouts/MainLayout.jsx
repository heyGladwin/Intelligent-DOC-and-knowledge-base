import Navbar from "../components/Navbar";

export default function MainLayout({ children }) {
  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col font-sans selection:bg-indigo-100 selection:text-indigo-700">
      
      {/* 1. Fixed Professional Navbar Container */}
      <div className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/60">
        <Navbar />
      </div>

      {/* 2. Main Content Stage */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        
        {/* Decorative Background Glows (Subtle, not "plain") */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] pointer-events-none overflow-hidden z-0">
          <div className="absolute -top-[10%] left-[10%] w-[40%] h-[40%] bg-indigo-200/20 blur-[120px] rounded-full"></div>
          <div className="absolute top-[5%] right-[5%] w-[30%] h-[30%] bg-purple-200/20 blur-[100px] rounded-full"></div>
        </div>

        {/* The Content Wrapper */}
        <div className="relative z-10">
          {children}
        </div>
      </main>

      {/* 3. Subtle Footer or Status Bar */}
      <footer className="py-6 border-t border-slate-200/60 bg-white/50">
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center text-slate-400 text-xs font-bold uppercase tracking-widest">
          <span>&copy; 2026 IntelDoc AI</span>
          <div className="flex gap-4">
            <span className="flex items-center gap-1.5 text-emerald-500">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
              Systems Nominal
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}