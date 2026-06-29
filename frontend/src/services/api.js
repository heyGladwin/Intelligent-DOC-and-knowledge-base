// frontend/src/services/api.js

export const API_BASE = "http://127.0.0.1:5000/api";

// This is the function your App.jsx is currently looking for
export const pingBackend = async () => {
    try {
        // This hits your @app.route('/') in Flask
        const response = await fetch("http://127.0.0.1:5000/"); 
        if (!response.ok) throw new Error("Backend unreachable");
        const data = await response.json();
        console.log("Backend Status:", data.status);
        return data;
    } catch (error) {
        console.error("Ping failed:", error);
        throw error;
    }
};

// This will be used by your Chatbot.jsx page
export const sendMessage = async (message) => {
    try {
        const response = await fetch(`${API_BASE}/chat/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });
        return await response.json();
    } catch (error) {
        console.error("Chat error:", error);
        throw error;
    }
};