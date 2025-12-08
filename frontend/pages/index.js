import {useEffect, useRef, useState} from "react";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home(){
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  useEffect(()=>{ if(chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight }, [messages]);

  async function startSession(){
    setLoading(true);
    try{
      const resp = await fetch(`${API_URL}/v1/conversation/start`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ userId: "student", domain: "backend", difficulty: 2 })
      });
      const j = await resp.json();
      setSessionId(j.sessionId);
      if(j.question && j.question.text){
        setMessages([{who:"bot", text: j.question.text}]);
      } else {
        setMessages([{who:"bot", text: "No question returned"}]);
      }
    }catch(e){ console.error(e); alert("Start failed"); }
    setLoading(false);
  }

  async function sendText(){
    if(!input.trim()) return;
    const text = input.trim();
    setMessages(m=>[...m, {who:"user", text}]);
    setInput("");
    if(!sessionId){ alert("Start session first"); return; }
    setLoading(true);
    try{
      const resp = await fetch(`${API_URL}/v1/conversation/${sessionId}/utter`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ text })
      });
      const j = await resp.json();
      const botText = (j.nextQuestion && j.nextQuestion.text) || "No reply";
      setMessages(m=>[...m, {who:"bot", text: botText}]);
    }catch(e){
      console.error(e);
      setMessages(m=>[...m, {who:"bot", text: "Error contacting server"}]);
    }
    setLoading(false);
  }

  async function endSession(){
    if(!sessionId) return alert("No active session");
    setLoading(true);
    try{
      await fetch(`${API_URL}/v1/conversation/${sessionId}/end`, { method: "POST" });
      setMessages(m=>[...m, {who:"bot", text: "Session ended."}]);
      setSessionId(null);
    }catch(e){ console.error(e); alert("End failed"); }
    setLoading(false);
  }

  async function viewTranscript(){
    if(!sessionId) return alert("Start a session and then click View Transcript");
    try{
      const resp = await fetch(`${API_URL}/v1/conversation/${sessionId}/transcript`);
      const j = await resp.json();
      const t = (j.transcript || []).map(x => `${x.speaker}: ${x.text}`).join("\n");
      alert("Transcript:\\n\\n" + t);
    }catch(e){ console.error(e); alert("Failed to fetch transcript"); }
  }

  return (
    <div style={{maxWidth:820, margin:"24px auto", fontFamily:"Inter,system-ui"}}>
      <div style={{padding:16, borderRadius:12, background:"#071126", color:"#e6eef6"}}>
        <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
          <h2 style={{margin:0}}>Module 3 — Interview practice</h2>
          <div>
            <button onClick={startSession} disabled={loading} style={{marginRight:8}}>{sessionId ? "Restart" : "Start session"}</button>
            <button onClick={endSession} disabled={loading || !sessionId}>End</button>
          </div>
        </div>

        <div ref={chatRef} style={{height: "55vh", overflow:"auto", marginTop:12, padding:12, borderRadius:8, background:"#061426"}}>
          {messages.length===0 && <div style={{color:"#9aa4b2"}}>No messages yet. Start session to receive first question.</div>}
          {messages.map((m,i)=>(
            <div key={i} style={{margin:"10px 0", display:"flex", justifyContent: m.who==="user" ? "flex-end" : "flex-start"}}>
              <div style={{background: m.who==="user" ? "rgba(56,189,248,0.12)" : "rgba(255,255,255,0.03)", padding:10, borderRadius:8, maxWidth:"75%"}}>
                <div style={{fontSize:14}}>{m.text}</div>
              </div>
            </div>
          ))}
        </div>

        <div style={{display:"flex", gap:8, marginTop:12}}>
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter") sendText()}} style={{flex:1,padding:10, borderRadius:8}} placeholder="Type your answer..." />
          <button onClick={sendText} disabled={loading}>Send</button>
          <button onClick={viewTranscript} disabled={!sessionId}>View Transcript</button>
        </div>

        <div style={{marginTop:8, color:"#9aa4b2", fontSize:13}}>
          Tip: set NEXT_PUBLIC_API_URL in frontend/.env.local to point to the backend (default localhost:8000).
        </div>
      </div>
    </div>
  );
}
