#!/usr/bin/env bash
set -e

mkdir -p orchestrator_lambda orchestrator_lambda/tests frontend/pages frontend/styles

cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.venv/
.vscode/
.idea/
.DS_Store
node_modules
frontend/.next
frontend/.env.local
frontend/node_modules
EOF

cat > requirements.txt <<'EOF'
boto3>=1.26
python-dateutil>=2.8
pytest>=7.0
EOF

cat > README.md <<'EOF'
Module 3 — Conversational Orchestrator
This branch contains Module-3 implementation (backend orchestrator + frontend).
Local run:
- Backend: placeholder in orchestrator_lambda/
- Frontend: cd frontend && npm install && npm run dev
EOF

cat > template.yaml <<'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Module-3 Conversational Orchestrator - placeholder
Resources: {}
EOF

cat > orchestrator_lambda/app.py <<'EOF'
import json
from datetime import datetime
def _now_iso(): return datetime.utcnow().isoformat()
def lambda_response(status_code, body):
    return {"statusCode": status_code, "headers": {"Content-Type":"application/json"}, "body": json.dumps(body)}
def lambda_handler(event, context):
    return lambda_response(200, {"message":"Module-3 orchestrator placeholder","timestamp":_now_iso()})
EOF

cat > orchestrator_lambda/followup.py <<'EOF'
def choose_next_question(session, current_question, last_response):
    return {"questionId":"q-placeholder","text":"Describe your experience with backend systems."}
EOF

cat > orchestrator_lambda/tests/test_followup.py <<'EOF'
from followup import choose_next_question
def test_choose():
    r = choose_next_question({}, None, {})
    assert "questionId" in r
EOF

cat > frontend/package.json <<'EOF'
{"name":"module-3-frontend","version":"0.1.0","private":true,"scripts":{"dev":"next dev -p 3001","build":"next build","start":"next start -p 3001"},"dependencies":{"next":"13.5.6","react":"18.2.0","react-dom":"18.2.0"}}
EOF

cat > frontend/next.config.js <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true }
module.exports = nextConfig
EOF

cat > frontend/.gitignore <<'EOF'
node_modules
.next
.env.local
.DS_Store
EOF

cat > frontend/styles/globals.css <<'EOF'
body{font-family:Inter,system-ui;margin:0;background:#071126;color:#e6eef6}
.container{max-width:900px;margin:40px auto;padding:20px}
.card{background:rgba(255,255,255,0.03);padding:16px;border-radius:12px}
EOF

cat > frontend/pages/_app.js <<'EOF'
import "../styles/globals.css"
export default function App({Component,pageProps}){return <Component {...pageProps} />}
EOF

cat > frontend/pages/index.js <<'EOF'
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
EOF

echo "Scaffold created by reset_module3.sh"
