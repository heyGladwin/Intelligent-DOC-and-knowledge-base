import { useState } from "react";
import { uploadDocuments } from "../services/documentService";


export default function FileUpload() {
const [files, setFiles] = useState([]);


const handleSubmit = async () => {
if (files.length === 0) return;
await uploadDocuments(files);
};


return (
<div className="space-y-4">
<input type="file" multiple onChange={(e) => setFiles(Array.from(e.target.files))} />
<button onClick={handleSubmit} className="bg-blue-600 text-white px-4 py-2 rounded">
Generate Documentation
</button>
</div>
);
}