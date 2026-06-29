import { API_BASE } from "./api";


export const uploadDocuments = async (files) => {
const formData = new FormData();
files.forEach((file) => formData.append("files", file));
const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
return res.json();
};