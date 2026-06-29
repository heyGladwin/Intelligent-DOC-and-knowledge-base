import { Link, NavLink } from "react-router-dom";


export default function Navbar() {
return (
<nav className="bg-white/80 backdrop-blur shadow-sm sticky top-0 z-50">
<div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
<h1 className="font-extrabold text-2xl tracking-tight">📘 IntelliDocs</h1>
<div className="flex gap-6 text-sm font-medium">
{["/", "/upload", "/docs", "/search", "/chat"].map((path, i) => (
<NavLink
key={i}
to={path}
className={({ isActive }) =>
isActive
? "text-blue-600"
: "text-gray-600 hover:text-blue-600"
}
>
{["Dashboard", "Upload", "Docs", "Search", "Chat"][i]}
</NavLink>
))}
</div>
</div>
</nav>
);
}