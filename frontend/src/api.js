const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

async function request(path, options = {}) {
  const token = localStorage.getItem("ayu_token");
  const headers = { ...(options.body instanceof FormData ? {} : {"Content-Type":"application/json"}), ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.message || `Request failed (${res.status})`);
  return data;
}

export const api = {
  register: (body) => request("/auth/register", {method:"POST", body:JSON.stringify(body)}),
  login: (body) => request("/auth/login-json", {method:"POST", body:JSON.stringify(body)}),
  innovations: () => request("/innovations"),
  createInnovation: (body) => request("/innovations", {method:"POST", body:JSON.stringify(body)}),
  innovation: (id) => request(`/innovations/${id}`),
  analyze: (id) => request(`/innovations/${id}/analyze`, {method:"POST"}),
  analysis: (id) => request(`/analyses/${id}`),
  evidence: (id) => request(`/analyses/${id}/evidence`),
  risks: (id) => request(`/analyses/${id}/risks`),
  roadmap: (id) => request(`/analyses/${id}/roadmap`),
  passport: (id) => request(`/passport/${id}`),
  passportGenerate: async (id) => { const token = localStorage.getItem("ayu_token"); const res = await fetch(`${API}/passport/${id}/generate`, {method:"POST", headers: token ? {Authorization:`Bearer ${token}`} : {}}); if(!res.ok){const data=await res.json().catch(()=>({})); throw new Error(data.detail||data.message||`Request failed (${res.status})`);} return await res.blob(); },
  chat: (question, jurisdiction="India") => request("/chat", {method:"POST", body:JSON.stringify({question,jurisdiction})}),
  sources: (q) => request(`/sources/search?q=${encodeURIComponent(q)}`),
  market: (country) => request(`/markets/${encodeURIComponent(country)}`),
  upload: (file) => {
    const form = new FormData(); form.append("file", file);
    return request("/documents/upload", {method:"POST", body:form});
  },
  health: () => request("/health")
};