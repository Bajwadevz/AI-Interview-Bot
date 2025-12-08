import {useState,useRef,useEffect} from "react"
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"
export default function Home(){
  const [sessionId,setSessionId]=useState(null), [messages,setMessages]=useState([]), [input,setInput]=useState(""), [loading,setLoading]=useState(false)
  const chatRef=useRef(null)
  useEffect(()=>{ if(chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight },[messages])
  async function startSession(){
    setLoading(true)
    try{
      const r=await fetch(`${API_URL}/v1/conversation/start`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({userId:"student",domain:"backend",difficulty:2})})
      const j=await r.json()
      setSessionId(j.sessionId)
      if(j.question && j.question.text) setMessages(m=>[...m,{who:"bot",text:j.question.text}])
    }catch(e){console.error(e);alert("start failed")}finally{setLoading(false)}
  }
  async function sendText(){
    if(!input.trim()) return
    setMessages(m=>[...m,{who:"user",text:input}])
    const text=input; setInput("")
    if(!sessionId){alert("Start session");return}
    setLoading(true)
    try{
      const r=await fetch(`${API_URL}/v1/conversation/${sessionId}/utter`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})})
      const j=await r.json()
      const botText = (j.nextQuestion && j.nextQuestion.text) || "No reply"
      setMessages(m=>[...m,{who:"bot",text:botText}])
    }catch(e){setMessages(m=>[...m,{who:"bot",text:"Error contacting server"}])}finally{setLoading(false)}
  }
  return (
    <div className="container">
      <div className="card">
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <h2>Module 3 — Interview practice</h2>
          <button onClick={startSession} disabled={loading}>{sessionId?"Restart":"Start session"}</button>
        </div>
        <div ref={chatRef} style={{height:"60vh",overflow:"auto",padding:12,borderRadius:8,background:"rgba(255,255,255,0.02)"}}>
          {messages.map((m,i)=><div key={i} style={{margin:"8px 0"}}><b>{m.who}:</b> {m.text}</div>)}
        </div>
        <div style={{display:"flex",gap:8,marginTop:12}}>
          <input value={input} onChange={e=>setInput(e.target.value)} style={{flex:1,padding:10}} onKeyDown={e=>{if(e.key==="Enter") sendText()}}/>
          <button onClick={sendText} disabled={loading}>Send</button>
        </div>
      </div>
    </div>
  )
}
