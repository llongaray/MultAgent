export interface Employee { id: string; name: string; role: string; provider: "grok"|"deepseek"; model: string; supervisor_id: string|null; enabled: boolean; }
export interface Audit { principal_id: string; resource_id: string; action: string; occurred_at: string; }
export interface Run { id: string; state: string; agent_id?: string; }

export class ApiClient {
  csrf = "";
  async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch("/api" + path, {
      ...init,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...(this.csrf ? { "X-CSRF-Token": this.csrf } : {}), ...init.headers }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.status === 401 ? "Faça login novamente" : "Operação não autorizada ou indisponível"}`);
    return await response.json() as T;
  }
  async login(password: string): Promise<void> {
    const response = await this.request<{csrf_token:string}>("/login", { method:"POST", body: JSON.stringify({password}) });
    this.csrf = response.csrf_token;
  }
  async logout(): Promise<void> {
    await this.request("/logout", { method:"POST" });
    this.csrf = "";
  }
  listAgents(): Promise<Employee[]> { return this.request("/agents"); }
  createAgent(input: {name:string;role:string;provider:"grok"|"deepseek";model:string}): Promise<{id:string}> {
    return this.request("/agents", {method:"POST",body:JSON.stringify(input)});
  }
  deleteAgent(id: string): Promise<void> { return this.request("/agents/" + encodeURIComponent(id), {method:"DELETE"}); }
  getMode(): Promise<{mode:string}> {return this.request("/mode");}
  setMode(mode: string): Promise<{mode:string}> {return this.request("/mode", {method:"POST",body:JSON.stringify({mode})});}
  listRuns(): Promise<Run[]> {return this.request("/runs");}
  audit(): Promise<Audit[]> {return this.request("/audit");}
}
