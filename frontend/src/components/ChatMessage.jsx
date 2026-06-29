export default function ChatMessage({ text, from }) {
return (
<div className={`flex ${from === "user" ? "justify-end" : "justify-start"}`}>
<div
className={`max-w-sm px-4 py-2 rounded-xl text-sm mb-2 ${
from === "user"
? "bg-slate-900 text-white"
: "bg-white border border-slate-200 text-slate-700"
}`}
>
{text}
</div>
</div>
);
}