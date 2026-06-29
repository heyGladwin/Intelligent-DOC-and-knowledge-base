import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Documentation from "./pages/Documentation";
import SearchKB from "./pages/SearchKB";
import Chatbot from "./pages/Chatbot";
import { useEffect } from "react"; // 1. Add this import
// ... your other imports ...
import { pingBackend } from './services/api';

export default function App() {

  // 2. This runs when the app starts
  useEffect(() => {
    pingBackend();
  }, []);
return (
<MainLayout>
<Routes>
<Route path="/" element={<Dashboard />} />
<Route path="/upload" element={<Upload />} />
<Route path="/docs" element={<Documentation />} />
<Route path="/search" element={<SearchKB />} />
<Route path="/chat" element={<Chatbot />} />
</Routes>
</MainLayout>
);
}