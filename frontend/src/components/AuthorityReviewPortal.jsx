import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ArrowRight, CheckCircle2, ClipboardCheck, ExternalLink, FileSearch, LoaderCircle, ShieldCheck, UserCheck, XCircle, LockKeyhole, LogOut } from 'lucide-react';
import { apiUrl } from '../lib/api';

const CLAIMS = [
  ['no_prechecked_addons', 'No pre-selected optional add-ons'],
  ['transparent_pricing', 'All mandatory pricing disclosed upfront'],
  ['neutral_choices', 'Neutral decline and cancellation choices'],
  ['easy_cancellation', 'Cancellation is as easy as sign-up'],
  ['no_false_urgency', 'No fabricated urgency or scarcity']
];

const STATUS = {
  queued: ['Audit queued', 'text-[#6798ff] bg-[#6798ff]/10 border-[#6798ff]/25'],
  submitted: ['Submitted', 'text-[#a7a7a7] bg-[#a7a7a7]/10 border-[#a7a7a7]/25'],
  scanning: ['Evidence collection', 'text-[#6798ff] bg-[#6798ff]/10 border-[#6798ff]/25'],
  evidence_ready: ['Ready for review', 'text-[#51cf66] bg-[#51cf66]/10 border-[#51cf66]/25'],
  human_review_required: ['Human review required', 'text-[#ffa94d] bg-[#ffa94d]/10 border-[#ffa94d]/25'],
  decision_recorded: ['Decision recorded', 'text-white bg-white/10 border-white/20']
};

const api = async (path, options = {}, token = '') => {
  const response = await fetch(apiUrl(path), { headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) }, ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || body.error || `Request failed (${response.status})`);
  return body;
};

export default function AuthorityReviewPortal({ onOpenScan }) {
  const [token, setToken] = useState(() => localStorage.getItem('pattern_guard_authority_token') || '');
  const [reviewer, setReviewer] = useState(() => localStorage.getItem('pattern_guard_authority_reviewer') || '');
  const [login, setLogin] = useState({ email: 'authority@ccpa.gov.in', password: 'PatternGuardDemo2026!' });
  const [submissions, setSubmissions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    company_name: '', contact_email: '', target_url: 'http://127.0.0.1:8000/mock/shopsneak',
    flow_type: 'checkout', declaration_text: 'We confirm that optional add-ons are not pre-selected and all mandatory costs are disclosed before checkout.',
    declared_claims: ['no_prechecked_addons', 'transparent_pricing']
  });
  const [decision, setDecision] = useState({ reviewer_name: 'Demo Reviewer', reviewer_notes: '', decision: 'changes_requested' });

  const load = async (focusId) => {
    setLoading(true);
    try {
      const data = await api('/api/submissions', {}, token);
      setSubmissions(data.submissions || []);
      const next = data.submissions?.find(item => item.id === focusId) || data.submissions?.find(item => item.id === selected?.id) || data.submissions?.[0] || null;
      setSelected(next);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    api('/api/authority/me', {}, token)
      .then(data => { setReviewer(data.reviewer); localStorage.setItem('pattern_guard_authority_reviewer', data.reviewer); load(); })
      .catch(() => { localStorage.removeItem('pattern_guard_authority_token'); setToken(''); setLoading(false); });
  }, [token]);

  const handleLogin = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    try {
      const data = await api('/api/authority/login', { method: 'POST', body: JSON.stringify(login) });
      localStorage.setItem('pattern_guard_authority_token', data.access_token);
      setToken(data.access_token);
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  };

  const logout = () => {
    localStorage.removeItem('pattern_guard_authority_token'); localStorage.removeItem('pattern_guard_authority_reviewer');
    setToken(''); setReviewer(''); setSelected(null); setSubmissions([]);
  };

  const counts = useMemo(() => ({
    total: submissions.length,
    ready: submissions.filter(item => item.status === 'evidence_ready').length,
    blocked: submissions.filter(item => item.status === 'human_review_required').length,
    decided: submissions.filter(item => item.status === 'decision_recorded').length
  }), [submissions]);

  const createSubmission = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    try {
      const created = await api('/api/submissions', { method: 'POST', body: JSON.stringify(form) });
      setShowForm(false); await load(created.id);
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  };

  const runScan = async () => {
    if (!selected) return;
    setSaving(true); setError('');
    try { const updated = await api(`/api/submissions/${selected.id}/scan`, { method: 'POST' }, token); await load(updated.id); }
    catch (err) { setError(err.message); await load(selected.id); }
    finally { setSaving(false); }
  };

  const recordDecision = async (event) => {
    event.preventDefault(); if (!selected) return;
    setSaving(true); setError('');
    try { const updated = await api(`/api/submissions/${selected.id}/decision`, { method: 'PATCH', body: JSON.stringify(decision) }, token); await load(updated.id); }
    catch (err) { setError(err.message); }
    finally { setSaving(false); }
  };

  const toggleClaim = (claim) => setForm(current => ({ ...current, declared_claims: current.declared_claims.includes(claim) ? current.declared_claims.filter(item => item !== claim) : [...current.declared_claims, claim] }));
  const recommendation = selected?.ai_recommendation?.replaceAll('_', ' ') || 'pending';

  if (!token) return <div className="min-h-[calc(100vh-56px)] bg-[#0a0a0a] px-6 py-16 text-white"><form onSubmit={handleLogin} className="mx-auto max-w-md rounded-xl border border-[#303030] bg-[#121212] p-7 shadow-2xl"><div className="mb-6 flex h-11 w-11 items-center justify-center rounded-lg bg-[#6798ff]/15 text-[#6798ff]"><LockKeyhole className="h-5 w-5" /></div><div className="font-mono text-[11px] uppercase tracking-[.16em] text-[#6798ff]">Restricted workspace</div><h1 className="mt-2 text-2xl font-medium">Authority Review Sign In</h1><p className="mt-2 text-sm leading-6 text-[#a7a7a7]">Authorized officers can inspect company compliance requests, evidence reports, and AI recommendations.</p>{error && <div className="mt-4 rounded border border-[#ff6b6b]/30 bg-[#ff6b6b]/10 p-3 text-xs text-[#ffb0b0]">{error}</div>}<label className="mt-6 block text-xs text-[#a7a7a7]">Authorized email<input type="email" required value={login.email} onChange={e => setLogin({...login, email: e.target.value})} className="mt-1.5 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2.5 text-sm text-white outline-none focus:border-[#6798ff]" /></label><label className="mt-4 block text-xs text-[#a7a7a7]">Password<input type="password" required value={login.password} onChange={e => setLogin({...login, password: e.target.value})} className="mt-1.5 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2.5 text-sm text-white outline-none focus:border-[#6798ff]" /></label><button disabled={saving} className="mt-6 w-full rounded bg-white px-4 py-2.5 text-sm font-medium text-black disabled:opacity-50">{saving ? 'Signing in…' : 'Enter Authority Review'}</button><p className="mt-4 text-[11px] leading-5 text-[#666]">Demo credentials are configured locally. Production deployments must use authority identity management and environment secrets.</p></form></div>;

  return <div className="min-h-[calc(100vh-56px)] bg-[#0a0a0a] px-6 py-10 text-white">
    <div className="mx-auto max-w-[1400px] space-y-7">
      <div className="flex flex-col justify-between gap-5 border-b border-[#1e1e1e] pb-7 md:flex-row md:items-end">
        <div>
          <div className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[.14em] text-[#6798ff]"><ShieldCheck className="h-3.5 w-3.5" /> Authority review prototype</div>
          <h1 className="text-3xl font-medium tracking-tight sm:text-4xl">Compliance Submission Desk</h1>
          <p className="mt-2 max-w-3xl text-sm text-[#a7a7a7]">AI-assisted evidence triage. Pattern Guard makes a recommendation; an authorized reviewer records the decision.</p>
        </div>
        <div className="flex items-center gap-3"><span className="hidden text-xs text-[#777] md:block">Signed in: {reviewer}</span><button onClick={() => setShowForm(!showForm)} className="rounded-md border border-[#303030] bg-[#171717] px-3 py-2 text-xs text-[#d4d4d4] transition hover:bg-[#242424]">{showForm ? 'Close demo intake' : 'Simulate company request'}</button><button onClick={logout} className="inline-flex items-center gap-1 rounded-md bg-white px-3 py-2 text-xs font-medium text-black"><LogOut className="h-3.5 w-3.5" />Sign out</button></div>
      </div>

      {error && <div className="flex items-center gap-2 rounded-md border border-[#ff6b6b]/30 bg-[#ff6b6b]/10 px-4 py-3 text-sm text-[#ff9a9a]"><AlertTriangle className="h-4 w-4" />{error}</div>}

      {showForm && <form onSubmit={createSubmission} className="grid gap-5 rounded-lg border border-[#6798ff]/30 bg-[#111827] p-6 lg:grid-cols-2"><div className="lg:col-span-2 text-sm text-[#b9ccff]">Demo intake only: this simulates a company request arriving in the authority queue. The audit starts automatically after submission.</div>
        <div className="space-y-4"><label className="block text-xs text-[#a7a7a7]">Company name<input required value={form.company_name} onChange={e => setForm({...form, company_name: e.target.value})} className="mt-1.5 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]" placeholder="Company legal name" /></label>
          <label className="block text-xs text-[#a7a7a7]">Compliance contact email<input required type="email" value={form.contact_email} onChange={e => setForm({...form, contact_email: e.target.value})} className="mt-1.5 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]" placeholder="compliance@company.example" /></label>
          <label className="block text-xs text-[#a7a7a7]">Public or staging URL<input required type="url" value={form.target_url} onChange={e => setForm({...form, target_url: e.target.value})} className="mt-1.5 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]" /></label>
          <label className="block text-xs text-[#a7a7a7]">Audit flow<select value={form.flow_type} onChange={e => setForm({...form, flow_type: e.target.value})} className="mt-1.5 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]"><option value="checkout">Checkout & upsell</option><option value="cancellation">Cancellation</option><option value="signup">Sign-up</option><option value="general">General scan</option></select></label></div>
        <div className="space-y-4"><label className="block text-xs text-[#a7a7a7]">Company compliance declaration<textarea required minLength="20" value={form.declaration_text} onChange={e => setForm({...form, declaration_text: e.target.value})} className="mt-1.5 h-24 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]" /></label>
          <div><div className="mb-2 text-xs text-[#a7a7a7]">Claims to verify</div><div className="grid gap-2 sm:grid-cols-2">{CLAIMS.map(([id, label]) => <label key={id} className="flex cursor-pointer items-start gap-2 rounded border border-[#303030] bg-[#0a0a0a] p-2 text-xs text-[#d4d4d4]"><input type="checkbox" checked={form.declared_claims.includes(id)} onChange={() => toggleClaim(id)} className="mt-0.5" />{label}</label>)}</div></div>
          <button disabled={saving} className="inline-flex items-center gap-2 rounded bg-[#6798ff] px-4 py-2 text-sm font-medium text-black disabled:opacity-50"><ClipboardCheck className="h-4 w-4" />Create submission</button></div>
      </form>}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{[[counts.total, 'Total cases'], [counts.ready, 'Ready for review'], [counts.blocked, 'Human intervention'], [counts.decided, 'Decisions recorded']].map(([value, label]) => <div key={label} className="rounded-lg border border-[#252525] bg-[#121212] px-5 py-4"><div className="font-mono text-2xl text-white">{value}</div><div className="mt-1 text-xs uppercase tracking-wider text-[#777]">{label}</div></div>)}</div>

      <div className="grid gap-6 xl:grid-cols-[.85fr_1.4fr]">
        <section className="overflow-hidden rounded-lg border border-[#252525] bg-[#121212]"><div className="border-b border-[#252525] px-5 py-4 text-xs font-mono uppercase tracking-wider text-[#a7a7a7]">Submission queue</div>{loading ? <div className="p-8 text-sm text-[#777]">Loading cases…</div> : submissions.length === 0 ? <div className="p-8 text-sm text-[#777]">No submissions yet. Create one to begin.</div> : <div className="divide-y divide-[#252525]">{submissions.map(item => <button key={item.id} onClick={() => setSelected(item)} className={`w-full p-5 text-left transition hover:bg-white/[.03] ${selected?.id === item.id ? 'bg-[#6798ff]/[.08]' : ''}`}><div className="flex items-start justify-between gap-3"><div><div className="font-medium">{item.company_name}</div><div className="mt-1 font-mono text-[11px] text-[#777]">{item.reference_code}</div></div><span className={`rounded border px-2 py-1 text-[10px] font-mono uppercase ${STATUS[item.status]?.[1] || STATUS.submitted[1]}`}>{STATUS[item.status]?.[0] || item.status}</span></div><div className="mt-3 truncate text-xs text-[#a7a7a7]">{item.target_url}</div></button>)}</div>}</section>

        <section className="rounded-lg border border-[#252525] bg-[#121212]">{selected ? <div className="p-6"><div className="flex flex-col justify-between gap-4 border-b border-[#252525] pb-5 md:flex-row"><div><div className="font-mono text-[11px] text-[#6798ff]">CASE {selected.reference_code}</div><h2 className="mt-1 text-xl font-medium">{selected.company_name}</h2><a href={selected.target_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex items-center gap-1 text-xs text-[#a7a7a7] hover:text-white">Open submitted URL <ExternalLink className="h-3 w-3" /></a></div><div className="text-left md:text-right"><div className="text-[11px] uppercase tracking-wider text-[#777]">AI recommendation</div><div className="mt-1 font-mono text-sm capitalize text-[#ffa94d]">{recommendation}</div></div></div>
          <div className="mt-5 grid gap-5 lg:grid-cols-2"><div><h3 className="mb-2 text-xs font-mono uppercase tracking-wider text-[#a7a7a7]">Company compliance report</h3><p className="rounded border border-[#252525] bg-[#0a0a0a] p-4 text-sm leading-6 text-[#d4d4d4]">{selected.declaration_text}</p></div><div><h3 className="mb-2 text-xs font-mono uppercase tracking-wider text-[#a7a7a7]">Pattern Guard evidence report</h3>{selected.scan ? <div className="rounded border border-[#252525] bg-[#0a0a0a] p-4"><div className="flex items-end justify-between"><div><div className="text-2xl font-medium">{selected.scan.audit_status === 'human_review_required' ? 'N/A' : selected.scan.score_summary?.manipulation_index ?? 0}<span className="text-sm text-[#777]">{selected.scan.audit_status === 'human_review_required' ? '' : '/100'}</span></div><div className="text-xs text-[#777]">{selected.scan.audit_status === 'human_review_required' ? 'Protected boundary' : 'Manipulation index'}</div></div><div className="text-right text-xs text-[#a7a7a7]">{selected.scan.score_summary?.total_findings || 0} findings<br />{selected.scan.total_steps || 0} steps</div></div><button onClick={() => onOpenScan(selected.scan)} className="mt-3 inline-flex items-center gap-1 text-xs text-[#6798ff] hover:text-white">Inspect original evidence <ArrowRight className="h-3 w-3" /></button></div> : <div className="rounded border border-[#252525] bg-[#0a0a0a] p-4 text-sm text-[#a7a7a7]">{selected.status === 'queued' || selected.status === 'scanning' ? 'Pattern Guard is automatically collecting evidence for this request…' : 'No audit record is available.'}</div>}</div></div>
          {selected.human_review_reason && <div className="mt-5 flex gap-3 rounded border border-[#ffa94d]/30 bg-[#ffa94d]/10 p-4 text-sm text-[#ffd0a3]"><UserCheck className="mt-0.5 h-4 w-4 shrink-0" />{selected.human_review_reason}</div>}
          {selected.reconciliation?.length > 0 && <div className="mt-5"><h3 className="mb-2 text-xs font-mono uppercase tracking-wider text-[#a7a7a7]">Declaration ↔ evidence reconciliation</h3><div className="space-y-2">{selected.reconciliation.map(item => <div key={item.claim_id} className="flex gap-3 rounded border border-[#252525] bg-[#0a0a0a] p-3 text-sm"><span className={item.outcome === 'contradicted' ? 'text-[#ff6b6b]' : 'text-[#51cf66]'}>{item.outcome === 'contradicted' ? <XCircle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}</span><div><div>{item.claim}</div><div className="mt-1 text-xs text-[#777]">{item.evidence_summary}</div></div></div>)}</div></div>}
          {selected.final_conclusion && <div className="mt-5 rounded border border-[#6798ff]/30 bg-[#6798ff]/[.07] p-4"><div className="font-mono text-[11px] uppercase tracking-wider text-[#6798ff]">Final comparison conclusion</div><div className="mt-2 text-sm font-medium">{(() => { try { return JSON.parse(selected.final_conclusion).conclusion; } catch { return selected.final_conclusion; } })()}</div><p className="mt-2 text-sm leading-6 text-[#b8c2d8]">{(() => { try { const result = JSON.parse(selected.final_conclusion); return `${result.source}: ${result.rationale}`; } catch { return ''; } })()}</p></div>}
          {(selected.status === 'evidence_ready' || selected.status === 'human_review_required') && <form onSubmit={recordDecision} className="mt-6 border-t border-[#252525] pt-5"><h3 className="text-xs font-mono uppercase tracking-wider text-[#a7a7a7]">Authorized reviewer decision</h3><div className="mt-3 grid gap-3 md:grid-cols-[1fr_1fr]"><input required value={decision.reviewer_name} onChange={e => setDecision({...decision, reviewer_name: e.target.value})} className="rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]" placeholder="Reviewer name" /><select value={decision.decision} onChange={e => setDecision({...decision, decision: e.target.value})} className="rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]"><option value="approved">Approve compliance</option><option value="changes_requested">Request changes</option><option value="rejected">Reject submission</option><option value="human_review_required">Require human evidence</option></select></div><textarea required minLength="4" value={decision.reviewer_notes} onChange={e => setDecision({...decision, reviewer_notes: e.target.value})} className="mt-3 h-20 w-full rounded border border-[#303030] bg-[#0a0a0a] px-3 py-2 text-sm outline-none focus:border-[#6798ff]" placeholder="Decision rationale and next steps" /><button disabled={saving} className="mt-3 rounded bg-[#6798ff] px-4 py-2 text-sm font-medium text-black disabled:opacity-50">Record human decision</button></form>}
          {selected.events?.length > 0 && <div className="mt-6 border-t border-[#252525] pt-5"><h3 className="mb-3 text-xs font-mono uppercase tracking-wider text-[#a7a7a7]">Case audit trail</h3><div className="space-y-3">{selected.events.map(event => <div key={event.id} className="flex gap-3 text-xs"><div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#6798ff]" /><div><span className="font-mono text-[#a7a7a7]">{event.event_type.replaceAll('_', ' ')}</span><span className="text-[#555]"> · {event.actor}</span><p className="mt-0.5 text-[#d4d4d4]">{event.detail}</p></div></div>)}</div></div>}
        </div> : <div className="p-8 text-sm text-[#777]">Select a case to inspect it.</div>}</section>
      </div>
    </div>
  </div>;
}
