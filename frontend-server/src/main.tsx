import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ApiClient, type Employee, type Audit, type Run } from "./api";
import "./style.css";

const api = new ApiClient();
type Tab = "Funcionários"|"Configurações"|"Execuções"|"Auditoria";
function App() {
  const [signed, setSigned] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [tab, setTab] = useState<Tab>("Funcionários");
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [mode, setMode] = useState("deepseek_only");
  const [name, setName] = useState("");
  const [role, setRole] = useState("worker");
  const [provider, setProvider] = useState<"grok"|"deepseek">("deepseek");
  const [model, setModel] = useState("");
  async function refresh() {
    try {
      const [next, nextMode, nextRuns, nextAudit] = await Promise.all([api.listAgents(),api.getMode(),api.listRuns(),api.audit()]);
      setEmployees(next);setMode(nextMode.mode);setRuns(nextRuns);setAudit(nextAudit);
    } catch (e) { setError(String(e)); }
  }
  useEffect(() => { if (signed) void refresh(); }, [signed]);
  async function login(e: React.FormEvent) {
    e.preventDefault();setError("");
    try { await api.login(password);setPassword("");setSigned(true); }
    catch(e) {setError(String(e));}
  }
  async function create(e: React.FormEvent) {
    e.preventDefault();setError("");
    try {await api.createAgent({name,role,provider,model});setName("");setModel("");await refresh();}
    catch(e){setError(String(e));}
  }
  if (!signed) return <main className="login"><h1>MultAgent Server</h1><p>Administração remota autenticada</p><form onSubmit={e=>void login(e)}><label>Senha administrativa<input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} minLength={12} required /></label><button>Entrar</button></form>{error&&<p role="alert">{error}</p>}</main>;
  return <div className="shell"><aside><h1>MultAgent</h1><p>Server edition</p><nav>{(["Funcionários","Configurações","Execuções","Auditoria"] as Tab[]).map(t=><button className={tab===t?"selected":""} key={t} onClick={()=>setTab(t)}>{t}</button>)}</nav><button onClick={()=>void api.logout().then(()=>{setSigned(false);setError("");})}>Sair</button></aside><main><header><h2>{tab}</h2><button onClick={()=>void refresh()}>Atualizar</button></header>{error&&<p role="alert">{error}</p>}{tab==="Funcionários"&&<><section><h3>Novo funcionário</h3><form onSubmit={e=>void create(e)} className="grid"><label>Nome<input required value={name} onChange={e=>setName(e.target.value)}/></label><label>Cargo<input required value={role} onChange={e=>setRole(e.target.value)}/></label><label>Provedor<select value={provider} onChange={e=>setProvider(e.target.value as "grok"|"deepseek")}><option value="deepseek">DeepSeek</option><option value="grok">Grok/xAI</option></select></label><label>Modelo<input required value={model} onChange={e=>setModel(e.target.value)} /></label><button>Cadastrar</button></form></section><section><h3>Funcionários cadastrados</h3><table><thead><tr><th>Nome</th><th>Função</th><th>Provedor</th><th>Modelo</th><th></th></tr></thead><tbody>{employees.map(a=><tr key={a.id}><td>{a.name}</td><td>{a.role}</td><td>{a.provider}</td><td>{a.model}</td><td><button onClick={()=>{if(confirm("Excluir funcionário?"))void api.deleteAgent(a.id).then(refresh).catch(e=>setError(String(e)));}}>Excluir</button></td></tr>)}</tbody></table></section></>}{tab==="Configurações"&&<section><h3>Roteamento global</h3><p>Provedores desabilitados não são usados. Não há fallback oculto.</p><select value={mode} onChange={e=>setMode(e.target.value)}><option value="deepseek_only">Somente DeepSeek</option><option value="grok_only">Somente Grok</option><option value="hybrid">Híbrido</option></select><button onClick={()=>void api.setMode(mode).then(refresh).catch(e=>setError(String(e)))}>Salvar</button></section>}{tab==="Execuções"&&<section><h3>Histórico</h3><p>O Server não inicia chamadas pagas ou ferramentas automaticamente neste marco.</p>{runs.map(r=><p key={r.id}>{r.id} — {r.state}</p>)}</section>}{tab==="Auditoria"&&<section><h3>Eventos registrados</h3>{audit.map((a,i)=><p key={i}>{a.occurred_at} | {a.principal_id} | {a.action}</p>)}</section>}</main></div>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
