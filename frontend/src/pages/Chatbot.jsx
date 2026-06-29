import { useState } from "react";
import { Send, Bot, User, Sparkles } from "lucide-react";

export default function ChatPage() {
  // 1. Create states to store messages and what the user types
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello! I'm your AI. Send me 4 numbers (sepal length, width, petal length, width) to get a prediction!" }
  ]);
  const [inputText, setInputText] = useState("");

  const handleSend = async () => {
    if (!inputText.trim()) return;

    // 2. Add User Message to the screen
    const newMessages = [...messages, { role: "user", text: inputText }];
    setMessages(newMessages);
    const currentInput = inputText; // Save it before clearing
    setInputText("");

    try {
      // 3. Convert input string "5.1, 3.5, 1.4, 0.2" into numbers for your FastAPI
      const coords = currentInput.split(",").map(num => parseFloat(num.trim()));

      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sepal_length: coords[0],
          sepal_width: coords[1],
          petal_length: coords[2],
          petal_width: coords[3],
        }),
      });

      const data = await response.json();

      // 4. Add Bot Prediction to the screen
      setMessages((prev) => [...prev, { role: "bot", text: `Prediction: ${data.prediction}` }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "bot", text: "Error: Could not reach the AI server." }]);
    }
  };

  return (
    <div className="h-[calc(100vh-160px)] flex flex-col">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-6 pb-10">
        {messages.map((msg, index) => (
          <div key={index} className={`flex gap-4 ${msg.role === "user" ? "justify-end" : ""}`}>
            {msg.role === "bot" && (
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-lg shrink-0">
                <Bot size={20} />
              </div>
            )}
            <div className={`p-5 rounded-3xl max-w-[80%] shadow-sm ${
              msg.role === "user" 
                ? "bg-indigo-600 text-white rounded-tr-none" 
                : "bg-white text-slate-700 border border-slate-100 rounded-tl-none"
            }`}>
              <p className="leading-relaxed">{msg.text}</p>
            </div>
            {msg.role === "user" && (
              <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 shrink-0">
                <User size={20} />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="relative pt-4">
        <div className="absolute left-6 top-1/2 -translate-y-1/2 text-indigo-500 animate-pulse">
          <Sparkles size={20} />
        </div>
        <input 
          type="text" 
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()} // Send on Enter key
          placeholder="Enter numbers like: 5.1, 3.5, 1.4, 0.2" 
          className="w-full pl-14 pr-16 py-5 bg-white border border-slate-100 rounded-2xl shadow-2xl outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button 
          onClick={handleSend}
          className="absolute right-3 top-1/2 -translate-y-1/2 bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 transition-colors shadow-lg"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}