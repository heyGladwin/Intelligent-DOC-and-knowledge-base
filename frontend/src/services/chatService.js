import { API_BASE } from "./api";


export const askQuestion = async (question) => {
const res = await fetch(`${API_BASE}/chat`, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ question })
});
return res.json();
};