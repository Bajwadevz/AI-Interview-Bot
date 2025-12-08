import { useEffect, useRef, useState } from "react";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function ChatBubble({ who, text, clarify }) {
  return (
    <div className={`msg ${who}`}>
      <div className="bubble" style={clarify ? { boxShadow: "0 6px 18px rgba(46, 197, 166, 0.06)", border: "1px solid rgba(46,197,166,0.12)" } : {}}>
        {clarify && <div style={{fontSize:12, color:"#9aa4b2", marginBottom:6}}>Clarify</div>}
        <div>{text}</div>
      </div>
    </div>
  );
}

export default function Home() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const [summary, setSummary] = useState(null);
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages, typing, summary]);

  async function startSession() {
    setLoading(true);
    setTyping(true);
    setSummary(null);
    try {
      const resp = await fetch(`${API_URL}/v1/conversation/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: "student", domain: "backend", difficulty: 2 })
      });
      const j = await resp.json();
      setSessionId(j.sessionId);
      setMessages(j.question && j.question.text ? [{ who: "bot", text: j.question.text }] : [{ who: "bot", text: "No question returned" }]);
    } catch (e) {
      console.error(e);
      setMessages([{ who: "bot", text: "Failed to start session" }]);
    } finally {
      await new Promise(r => setTimeout(r, 250));
      setTyping(false);
      setLoading(false);
    }
  }

  async function sendText() {
    if (!input.trim()) return;
    const text = input.trim();
    setMessages(m => [...m, { who: "user", text }]);
    setInput("");
    if (!sessionId) return alert("Start session first");
    setLoading(true);
    setTyping(true);
    try {
      const resp = await fetch(`${API_URL}/v1/conversation/${sessionId}/utter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const j = await resp.json();
      const botText = (j.nextQuestion && j.nextQuestion.text) || "No reply";
      const isClarify = !!j.clarify;
      // small delay for realism
      await new Promise(r => setTimeout(r, 300));
      setMessages(m => [...m, { who: "bot", text: botText, clarify: isClarify }]);
    } catch (e) {
      console.error(e);
      setMessages(m => [...m, { who: "bot", text: "Error contacting server" }]);
    } finally {
      setTyping(false);
      setLoading(false);
    }
  }

  async function endSession() {
    if (!sessionId) return;
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/v1/conversation/${sessionId}/end`, { method: "POST" });
      const j = await resp.json();
      setMessages(m => [...m, { who: "bot", text: "Session ended." }]);
      setSummary(j.summary || null);
      setSessionId(null);
    } catch (e) {
      console.error(e);
      alert("Failed to end session");
    } finally {
      setLoading(false);
    }
  }

  async function viewTranscript() {
    if (!sessionId) return alert("Start a session first");
    try {
      const resp = await fetch(`${API_URL}/v1/conversation/${sessionId}/transcript`);
      const j = await resp.json();
      const t = (j.transcript || []).map(x => `${x.speaker}: ${x.text}`).join("\\n");
      alert("Transcript:\\n\\n" + t);
    } catch (e) {
      console.error(e);
      alert("Failed to fetch transcript");
    }
  }

  return (
    <div className="container">
      <div className="header">
        <div className="title">HIREBRAIN</div>
      </div>

      <div className="card">
        <div ref={chatRef} className="chat">
          {messages.length === 0 ? (
            <div className="center-hirebrain">
              <img src="/logo.svg" alt="HIREBRAIN" />
              <div className="sub">Click <strong>Start session</strong> to begin your mock interview</div>
            </div>
          ) : (
            <>
              {messages.map((m, i) => <ChatBubble key={i} who={m.who} text={m.text} clarify={m.clarify} />)}
              {typing && <div className="msg bot"><div className="typing">Bot is typing...</div></div>}
            </>
          )}
          {summary && (
            <div style={{marginTop:12, padding:12, borderRadius:10, background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.03)"}}>
              <div style={{fontWeight:700}}>Session summary</div>
              <div style={{marginTop:8}}>Turns: {summary.turns}</div>
              <div>Average confidence: {summary.average_confidence ? (Math.round(summary.average_confidence*100)/100) : "N/A"}</div>
              <div style={{color:"#9aa4b2", marginTop:6}}>Started: {summary.startedAt}</div>
              <div style={{color:"#9aa4b2"}}>Finished: {summary.finishedAt}</div>
            </div>
          )}
        </div>

        <div className="input-row">
          <input className="input" placeholder="Type your answer..." value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter") sendText() }} />
          <button className="btn" onClick={sendText} disabled={loading}>Send</button>
          <button className="small" onClick={startSession} disabled={loading}>{sessionId ? "Restart" : "Start session"}</button>
          <button className="small" onClick={endSession} disabled={!sessionId || loading}>End</button>
          <button className="small" onClick={viewTranscript} disabled={!sessionId}>Transcript</button>
        </div>

        <div className="footer">Tip: make sure your backend (local or deployed) is reachable from NEXT_PUBLIC_API_URL</div>
      </div>
    </div>
  );
}
