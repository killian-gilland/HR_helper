import React, { useState, useEffect } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

const API_BASE_URL = "http://localhost:8000";

export default function TalentAIApp() {
  // === ÉTATS GLOBAUX ===
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [currentPage, setCurrentPage] = useState('pool');
  const [lang, setLang] = useState('fr');
  const [offerMode, setOfferMode] = useState('new');
  
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  
  const [offers, setOffers] = useState([]);
  const [selectedOfferId, setSelectedOfferId] = useState('');
  const [candidates, setCandidates] = useState([]);
  
  const [sortBy, setSortBy] = useState('desc');
  const [topN, setTopN] = useState(10);
  const [selectedCandidates, setSelectedCandidates] = useState(new Set());
  const [candidateModal, setCandidateModal] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // === DICTIONNAIRE ===
  const t = {
    fr: {
      scan: "Nouveau Scan", pool: "Vivier Candidats", newOffer: "Nouvelle offre", oldOffer: "Offre existante",
      title: "Titre du poste", desc: "Description du poste", browse: "Parcourir les PDF", launch: "Lancer l'Analyse",
      sortBy: "Trier par", sortDesc: "Meilleurs scores", sortAsc: "Scores faibles", sortAlpha: "A-Z",
      display: "Affichage", selectCamp: "Sélectionnez une campagne", total: "Profils",
      export: "Export Excel", genInt: "Générer Entretiens", delete: "Supprimer", details: "Détails",
      scannedOn: "Scanné le", emptyCamp: "-- Aucune campagne --", strength: "Force", risk: "Risque"
    },
    en: {
      scan: "New Scan", pool: "Candidate Pool", newOffer: "New offer", oldOffer: "Existing offer",
      title: "Job Title", desc: "Job Description", browse: "Browse PDFs", launch: "Start Analysis",
      sortBy: "Sort by", sortDesc: "Highest scores", sortAsc: "Lowest scores", sortAlpha: "A-Z",
      display: "Display", selectCamp: "Select a campaign", total: "Profiles",
      export: "Excel Export", genInt: "Generate Interviews", delete: "Delete", details: "Details",
      scannedOn: "Scanned on", emptyCamp: "-- No campaign --", strength: "Strength", risk: "Risk"
    }
  }[lang];

  // === APPELS API ===
  const handleAuth = async () => {
    const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register';
    const payload = isLoginMode ? { username, password } : { username, password, company };
    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        if (isLoginMode) {
          setUser({ id: data.user_id, company: data.company_name, username });
          setIsLoggedIn(true);
          fetchOffers(data.user_id);
        } else {
          alert("Compte créé avec succès !");
          setIsLoginMode(true);
        }
      } else alert(data.detail);
    } catch (e) { alert("Erreur de connexion au serveur."); }
  };

  const fetchOffers = async (userId) => {
    const res = await fetch(`${API_BASE_URL}/api/offers/${userId}`);
    const data = await res.json();
    setOffers(data);
    if (data.length > 0) setSelectedOfferId(data[0].id);
  };

  useEffect(() => {
    if (selectedOfferId) {
      fetch(`${API_BASE_URL}/api/candidates/${selectedOfferId}`)
        .then(res => res.json())
        .then(data => { setCandidates(data); setSelectedCandidates(new Set()); })
        .catch(err => console.error(err));
    }
  }, [selectedOfferId]);

  // === LOGIQUE ===
  let displayedCandidates = [...candidates].sort((a, b) => {
    const scoreA = a.score_final || 0, scoreB = b.score_final || 0;
    const nameA = a.nom || "", nameB = b.nom || "";
    if (sortBy === 'desc') return scoreB - scoreA;
    if (sortBy === 'asc') return scoreA - scoreB;
    return nameA.localeCompare(nameB);
  }).slice(0, topN);

  const toggleCandidateSelection = (id) => {
    const newSet = new Set(selectedCandidates);
    if (newSet.has(id)) newSet.delete(id); else newSet.add(id);
    setSelectedCandidates(newSet);
  };

  const toggleAll = () => {
    if (selectedCandidates.size === displayedCandidates.length) setSelectedCandidates(new Set());
    else setSelectedCandidates(new Set(displayedCandidates.map(c => c.id)));
  };

  const parseAnalyse = (jsonStr) => {
    try { return typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr || {}; } 
    catch { return {}; }
  };

  const getRadarData = (analyse) => [
    { subject: 'Hard Skills', A: Math.min((analyse.n_hard_skills_coeur || 0) * (100/65), 100) },
    { subject: 'Outils', A: Math.min((analyse.n_outils_metier || 0) * 10, 100) },
    { subject: 'Impact', A: Math.min((analyse.n_business_impact || 0) * 10, 100) },
    { subject: 'Séniorité', A: Math.min((analyse.n_seniorite || 0) * 20, 100) },
    { subject: 'Soft Skills', A: Math.min((analyse.n_soft_skills || 0) * 20, 100) },
    { subject: 'Storytelling', A: Math.min((analyse.n_storytelling || 0) * 20, 100) }
  ];

  const exportToExcel = () => {
    if (selectedCandidates.size === 0) return;
    const selected = displayedCandidates.filter(c => selectedCandidates.has(c.id));
    const headers = ["Candidat", "Score IA", "Point Fort", "Risque", "Conclusion"];
    const csvRows = [headers.join(";")]; 

    selected.forEach(c => {
      const analyse = parseAnalyse(c.analyse_json);
      const cleanString = (str) => `"${(str || '').replace(/"/g, '""').replace(/\n/g, ' ')}"`;
      const row = [cleanString(c.nom || c.filename), cleanString(`${c.score_final}/100`), cleanString(analyse.strength), cleanString(analyse.risk), cleanString(analyse.reasoning)];
      csvRows.push(row.join(";"));
    });

    const csvString = csvRows.join("\n");
    const blob = new Blob(["\uFEFF" + csvString], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const offerName = offers.find(o => o.id === parseInt(selectedOfferId))?.title || "Campagne";
    link.setAttribute("href", url);
    link.setAttribute("download", `Export_TalentAI_${offerName.replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // ==========================================
  // BACKGROUND MESH GRADIENT (Le secret du look)
  // ==========================================
  const MeshBackground = () => (
    <div className="fixed inset-0 z-[-1] overflow-hidden bg-[#F8FAFC]">
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-purple-300/40 blur-[120px] pointer-events-none mix-blend-multiply" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[60%] h-[60%] rounded-full bg-blue-300/40 blur-[140px] pointer-events-none mix-blend-multiply" />
      <div className="absolute top-[20%] right-[20%] w-[40%] h-[40%] rounded-full bg-emerald-200/30 blur-[100px] pointer-events-none mix-blend-multiply" />
    </div>
  );

  // === ÉCRAN DE CONNEXION (GLASSMORPHISM) ===
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 relative">
        <MeshBackground />
        
        <div className="absolute top-6 right-6 flex gap-2 z-10">
          <button onClick={() => setLang('fr')} className={`text-4xl hover:scale-110 transition-transform ${lang === 'fr' ? 'opacity-100' : 'opacity-40 grayscale blur-[1px]'}`}>🇫🇷</button>
          <button onClick={() => setLang('en')} className={`text-4xl hover:scale-110 transition-transform ${lang === 'en' ? 'opacity-100' : 'opacity-40 grayscale blur-[1px]'}`}>🇬🇧</button>
        </div>

        <h1 className="text-6xl font-black text-slate-800 mb-10 tracking-tighter drop-shadow-sm">TALENT<span className="text-blue-600">.AI</span></h1>
        
        <div className="w-full max-w-md bg-white/60 backdrop-blur-2xl p-10 rounded-[2rem] shadow-[0_8px_32px_rgba(0,0,0,0.04)] border border-white/60">
          <div className="flex gap-6 mb-8 border-b border-slate-200/50">
            <button onClick={() => setIsLoginMode(true)} className={`pb-3 text-sm font-bold transition-all ${isLoginMode ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-400 hover:text-slate-600'}`}>Connexion</button>
            <button onClick={() => setIsLoginMode(false)} className={`pb-3 text-sm font-bold transition-all ${!isLoginMode ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-400 hover:text-slate-600'}`}>Créer un compte</button>
          </div>
          <div className="flex flex-col gap-5">
            {!isLoginMode && <input type="text" placeholder="Nom de l'entreprise" value={company} onChange={e => setCompany(e.target.value)} className="w-full p-4 bg-white/50 backdrop-blur-sm border border-white/60 rounded-2xl focus:bg-white focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-slate-700 placeholder-slate-400" />}
            <input type="text" placeholder="Identifiant" value={username} onChange={e => setUsername(e.target.value)} className="w-full p-4 bg-white/50 backdrop-blur-sm border border-white/60 rounded-2xl focus:bg-white focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-slate-700 placeholder-slate-400" />
            <input type="password" placeholder="Mot de passe" value={password} onChange={e => setPassword(e.target.value)} className="w-full p-4 bg-white/50 backdrop-blur-sm border border-white/60 rounded-2xl focus:bg-white focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-slate-700 placeholder-slate-400" />
            <button onClick={handleAuth} className="w-full mt-2 py-4 bg-blue-600/90 backdrop-blur-md text-white font-bold rounded-2xl hover:bg-blue-600 shadow-[0_8px_20px_rgba(37,99,235,0.2)] transition-all hover:-translate-y-0.5 active:translate-y-0">
              {isLoginMode ? "Accéder à mon espace" : "Créer mon espace"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // === ÉCRAN PRINCIPAL (APPLE VISION PRO STYLE) ===
  return (
    <div className="flex min-h-screen font-sans text-slate-800 relative">
      <MeshBackground />
      
      {/* SIDEBAR EN VERRE DÉPOLI */}
      <div className="w-80 bg-white/30 backdrop-blur-2xl border-r border-white/50 flex flex-col p-8 z-10 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        <h2 className="text-4xl font-black text-slate-800 mb-2 tracking-tighter">TALENT<span className="text-blue-600">.AI</span></h2>
        <div className="inline-flex items-center px-3 py-1.5 bg-white/50 border border-white/60 text-slate-600 text-xs font-bold rounded-full w-fit mb-10 shadow-sm backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 mr-2 shadow-[0_0_8px_rgba(52,211,153,0.8)] animate-pulse"></span>
          ESPACE {user?.company?.toUpperCase() || 'PRO'}
        </div>

        <div className="space-y-6 flex-1">
          <div>
            <p className="text-slate-500 text-xs font-bold tracking-widest uppercase mb-4 mix-blend-multiply">1. Configuration</p>
            <div className="flex flex-col gap-3 mb-5">
              <label className="flex items-center gap-3 cursor-pointer group">
                <input type="radio" checked={offerMode === 'new'} onChange={() => setOfferMode('new')} className="w-4 h-4 text-blue-500 border-white/60 bg-white/50 focus:ring-blue-500 cursor-pointer" />
                <span className={`text-sm font-semibold transition-colors ${offerMode === 'new' ? 'text-slate-800' : 'text-slate-500 group-hover:text-slate-700'}`}>{t.newOffer}</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer group">
                <input type="radio" checked={offerMode === 'existing'} onChange={() => setOfferMode('existing')} className="w-4 h-4 text-blue-500 border-white/60 bg-white/50 focus:ring-blue-500 cursor-pointer" />
                <span className={`text-sm font-semibold transition-colors ${offerMode === 'existing' ? 'text-slate-800' : 'text-slate-500 group-hover:text-slate-700'}`}>{t.oldOffer}</span>
              </label>
            </div>

            {offerMode === 'new' ? (
              <>
                <input type="text" placeholder={t.title} className="w-full p-3 bg-white/50 backdrop-blur-md border border-white/60 rounded-xl text-slate-800 text-sm outline-none focus:border-blue-400 focus:bg-white/80 transition-all mb-3 placeholder-slate-400 shadow-sm" />
                <textarea placeholder={t.desc} rows={6} className="w-full p-3 bg-white/50 backdrop-blur-md border border-white/60 rounded-xl text-slate-800 text-sm outline-none resize-none focus:border-blue-400 focus:bg-white/80 transition-all placeholder-slate-400 shadow-sm"></textarea>
              </>
            ) : (
              <select className="w-full p-3 bg-white/50 backdrop-blur-md border border-white/60 rounded-xl text-slate-800 font-medium text-sm outline-none focus:border-blue-400 transition-all cursor-pointer shadow-sm">
                {offers.length === 0 && <option>{t.emptyCamp}</option>}
                {offers.map(o => <option key={o.id} value={o.id}>{o.title}</option>)}
              </select>
            )}
          </div>

          <div>
            <p className="text-slate-500 text-xs font-bold tracking-widest uppercase mb-4 mix-blend-multiply">2. Importation</p>
            <div className="w-full p-6 border-2 border-dashed border-slate-300/50 bg-white/30 backdrop-blur-md rounded-2xl flex flex-col items-center justify-center text-center hover:border-blue-400 transition-colors cursor-pointer group">
               <div className="w-10 h-10 mb-3 rounded-full bg-white/60 border border-white/80 flex items-center justify-center group-hover:bg-blue-50 group-hover:text-blue-500 transition-colors shadow-sm">📄</div>
               <label className="text-sm font-semibold text-slate-700 cursor-pointer group-hover:text-blue-600 transition-colors">
                 {t.browse} <input type="file" multiple className="hidden" accept=".pdf" />
               </label>
            </div>
          </div>
        </div>

        <button className="w-full py-4 mt-8 bg-blue-600/90 backdrop-blur-md text-white font-bold rounded-2xl hover:bg-blue-600 shadow-[0_8px_20px_rgba(37,99,235,0.2)] transition-all hover:-translate-y-0.5">{t.launch}</button>
      </div>

      {/* CONTENU CENTRAL TRANSLUCIDE */}
      <div className="flex-1 flex flex-col h-screen overflow-y-auto px-12 py-10 relative z-0">
        
        {/* HEADER & LANGUE */}
        <div className="flex justify-between items-center mb-10">
          <div className="flex bg-white/40 backdrop-blur-xl p-1.5 rounded-2xl w-fit shadow-sm border border-white/50">
            <button onClick={() => setCurrentPage('scan')} className={`px-8 py-2.5 rounded-xl text-sm font-bold transition-all ${currentPage === 'scan' ? 'bg-white text-slate-800 shadow-[0_2px_10px_rgba(0,0,0,0.04)]' : 'text-slate-500 hover:text-slate-700'}`}>{t.scan}</button>
            <button onClick={() => setCurrentPage('pool')} className={`px-8 py-2.5 rounded-xl text-sm font-bold transition-all ${currentPage === 'pool' ? 'bg-white text-slate-800 shadow-[0_2px_10px_rgba(0,0,0,0.04)]' : 'text-slate-500 hover:text-slate-700'}`}>{t.pool}</button>
          </div>
          <div className="flex gap-2 bg-white/30 backdrop-blur-md p-1.5 rounded-2xl border border-white/50 shadow-sm">
            <button onClick={() => setLang('fr')} className={`text-2xl px-2 hover:scale-110 transition-transform ${lang === 'fr' ? 'opacity-100' : 'opacity-40 grayscale blur-[0.5px]'}`}>🇫🇷</button>
            <button onClick={() => setLang('en')} className={`text-2xl px-2 hover:scale-110 transition-transform ${lang === 'en' ? 'opacity-100' : 'opacity-40 grayscale blur-[0.5px]'}`}>🇬🇧</button>
          </div>
        </div>

        {currentPage === 'pool' && (
          <div className="max-w-6xl w-full mx-auto pb-20">
            
            {/* SELECTEUR DE CAMPAGNE (GLASS) */}
            <div className="relative w-full max-w-2xl mb-10">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 block mix-blend-multiply">{t.selectCamp}</label>
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="w-full p-5 bg-white/60 backdrop-blur-2xl border border-white/70 rounded-[2rem] shadow-[0_8px_30px_rgba(0,0,0,0.04)] flex items-center justify-between hover:bg-white/80 transition-all focus:outline-none group"
              >
                <span className="text-2xl font-black text-slate-800 tracking-tight">
                  {selectedOfferId && offers.length > 0 
                    ? offers.find(o => o.id === parseInt(selectedOfferId))?.title 
                    : "Sélectionner une campagne..."}
                </span>
                <div className="w-10 h-10 rounded-full bg-white border border-slate-100 flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
                  <svg className={`w-5 h-5 text-slate-600 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M19 9l-7 7-7-7" /></svg>
                </div>
              </button>

              {isDropdownOpen && (
                <div className="absolute top-[105%] left-0 right-0 bg-white/80 backdrop-blur-3xl border border-white/60 rounded-[2rem] shadow-[0_20px_40px_rgba(0,0,0,0.08)] z-50 overflow-hidden p-2">
                  {offers.length === 0 ? (
                    <div className="p-4 text-slate-500 font-medium text-center">Aucune campagne</div>
                  ) : (
                    offers.map(o => (
                      <div 
                        key={o.id} onClick={() => { setSelectedOfferId(o.id); setIsDropdownOpen(false); }}
                        className={`p-4 rounded-2xl cursor-pointer transition-all flex justify-between items-center ${parseInt(selectedOfferId) === o.id ? 'bg-blue-50 border border-blue-100/50' : 'hover:bg-white/60'}`}
                      >
                        <span className={`font-bold text-lg ${parseInt(selectedOfferId) === o.id ? 'text-blue-700' : 'text-slate-700'}`}>{o.title}</span>
                        <span className="text-xs font-bold text-slate-400 bg-slate-100/50 border border-slate-200/50 px-3 py-1.5 rounded-full">
                          {o.created_at ? new Date(o.created_at).toLocaleDateString() : 'Date inconnue'}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* FILTRES & BARRE D'ACTIONS FLOTTANTE */}
            <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
              <div className="flex gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest pl-1">{t.sortBy}</label>
                  <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="px-5 py-3 bg-white/50 backdrop-blur-xl border border-white/60 rounded-2xl text-sm font-bold text-slate-700 outline-none cursor-pointer shadow-sm focus:bg-white/80 transition-colors">
                    <option value="desc">{t.sortDesc}</option>
                    <option value="asc">{t.sortAsc}</option>
                    <option value="alpha">{t.sortAlpha}</option>
                  </select>
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest pl-1">{t.display}</label>
                  <select value={topN} onChange={(e) => setTopN(e.target.value)} className="px-5 py-3 bg-white/50 backdrop-blur-xl border border-white/60 rounded-2xl text-sm font-bold text-slate-700 outline-none cursor-pointer shadow-sm focus:bg-white/80 transition-colors">
                    <option value={5}>Top 5</option>
                    <option value={10}>Top 10</option>
                    <option value={50}>Tous</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-white/40 backdrop-blur-xl p-2 rounded-2xl border border-white/50 shadow-sm">
                <span className="px-4 text-sm font-black text-slate-600">{candidates.length} {t.total}</span>
                {selectedCandidates.size > 0 && (
                  <>
                    <button onClick={exportToExcel} className="px-5 py-2.5 bg-white/80 border border-white shadow-sm text-slate-700 rounded-xl text-sm font-bold hover:bg-white transition-colors flex items-center gap-2">
                      <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                      {t.export} ({selectedCandidates.size})
                    </button>
                    <button className="px-5 py-2.5 bg-slate-800 text-white shadow-md rounded-xl text-sm font-bold hover:bg-slate-900 transition-colors">
                      {t.genInt}
                    </button>
                    <button className="px-5 py-2.5 bg-rose-50 border border-rose-100 text-rose-600 rounded-xl text-sm font-bold hover:bg-rose-100 transition-colors">
                      {t.delete}
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* LISTING SPATIAL (SMART ROWS EN VERRE) */}
            <div className="flex flex-col gap-4 relative z-0">
              <div className="flex items-center px-6 py-1">
                <input type="checkbox" onChange={toggleAll} checked={displayedCandidates.length > 0 && selectedCandidates.size === displayedCandidates.length} className="w-5 h-5 rounded border-white text-blue-500 focus:ring-blue-400 cursor-pointer accent-blue-500 mr-5 shadow-sm" />
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mix-blend-multiply">Tout sélectionner</span>
              </div>

              {displayedCandidates.map(c => {
                const analyse = parseAnalyse(c.analyse_json);
                const isSelected = selectedCandidates.has(c.id);

                return (
                  <div 
                    key={c.id} 
                    onClick={() => setCandidateModal(c)}
                    className={`group flex items-center justify-between p-5 backdrop-blur-xl rounded-[2rem] transition-all duration-300 cursor-pointer border shadow-[0_8px_30px_rgba(0,0,0,0.03)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.08)] hover:-translate-y-1 ${isSelected ? 'bg-white/80 border-blue-300/50 ring-4 ring-blue-500/10' : 'bg-white/40 border-white/60 hover:bg-white/60 hover:border-white/80'}`}
                  >
                    {/* Colonne Gauche */}
                    <div className="flex items-center gap-5 w-1/3 min-w-[280px]">
                      <div onClick={e => e.stopPropagation()}>
                        <input type="checkbox" checked={isSelected} onChange={() => toggleCandidateSelection(c.id)} className="w-6 h-6 rounded border-white text-blue-500 focus:ring-blue-400 cursor-pointer accent-blue-500 shadow-sm" />
                      </div>
                      <div className="w-14 h-14 rounded-full bg-white border border-white/80 shadow-sm flex items-center justify-center font-black text-slate-400 text-xl shrink-0 group-hover:text-blue-500 group-hover:bg-blue-50/50 transition-colors">
                        {c.nom ? c.nom.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div className="flex flex-col truncate">
                        <span className="text-base font-bold text-slate-800 truncate leading-tight mb-0.5">{c.nom || c.filename}</span>
                        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{t.scannedOn} {c.date_scan || 'Inconnue'}</span>
                      </div>
                    </div>

                    {/* Colonne Milieu (Insights Rapides) */}
                    <div className="hidden md:flex flex-col gap-2 w-1/3 px-4 truncate">
                      <div className="flex items-center gap-3 text-sm text-slate-600 truncate bg-white/30 px-3 py-1.5 rounded-lg border border-white/40">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0 shadow-[0_0_8px_rgba(52,211,153,0.5)]"></span>
                        <span className="truncate font-medium"><strong className="text-slate-700">{t.strength}:</strong> {analyse.strength || '-'}</span>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-slate-600 truncate bg-white/30 px-3 py-1.5 rounded-lg border border-white/40">
                        <span className="w-2.5 h-2.5 rounded-full bg-rose-400 shrink-0 shadow-[0_0_8px_rgba(251,113,133,0.5)]"></span>
                        <span className="truncate font-medium"><strong className="text-slate-700">{t.risk}:</strong> {analyse.risk || '-'}</span>
                      </div>
                    </div>

                    {/* Colonne Droite (Score & Action) */}
                    <div className="flex items-center justify-end gap-6 w-1/4">
                      <div className={`px-5 py-2 rounded-2xl border font-black text-lg shadow-sm backdrop-blur-md ${c.score_final >= 75 ? 'bg-emerald-50/80 text-emerald-600 border-emerald-200/50' : c.score_final >= 50 ? 'bg-amber-50/80 text-amber-600 border-amber-200/50' : 'bg-rose-50/80 text-rose-600 border-rose-200/50'}`}>
                        {c.score_final}<span className="text-xs opacity-50">/100</span>
                      </div>
                      <div className="w-12 h-12 rounded-full bg-white border border-slate-100 flex items-center justify-center shadow-sm opacity-0 group-hover:opacity-100 transition-all -translate-x-4 group-hover:translate-x-0">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" /></svg>
                      </div>
                    </div>

                  </div>
                );
              })}
            </div>

            {/* ======================================================== */}
            {/* FENÊTRE MODALE DÉTAILS (FROSTED GLASS EXTRÊME) */}
            {/* ======================================================== */}
            {candidateModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-slate-900/30 backdrop-blur-md">
                <div className="bg-white/80 backdrop-blur-2xl rounded-[3rem] shadow-[0_20px_60px_rgba(0,0,0,0.1)] border border-white/60 w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                  
                  {/* Header Modale */}
                  <div className="px-10 py-6 border-b border-white/40 flex justify-between items-center bg-white/40">
                    <div className="flex items-center gap-6">
                      <div className="w-16 h-16 rounded-full bg-white shadow-sm flex items-center justify-center font-black text-slate-800 text-2xl">
                        {candidateModal.nom ? candidateModal.nom.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div>
                        <h2 className="text-3xl font-black text-slate-800 tracking-tight">{candidateModal.nom || candidateModal.filename}</h2>
                        <span className="text-sm font-bold text-slate-500 uppercase tracking-wider">Score Global : <span className="text-blue-600">{candidateModal.score_final}/100</span></span>
                      </div>
                    </div>
                    <button onClick={() => setCandidateModal(null)} className="w-12 h-12 bg-white rounded-full flex items-center justify-center hover:bg-slate-100 transition-colors shadow-sm border border-slate-100">
                      <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  </div>

                  {/* Corps Modale */}
                  <div className="flex-1 overflow-y-auto p-10">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                      
                      {/* Colonne 1 : Insights */}
                      <div className="space-y-6">
                        <div className="bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-white shadow-sm">
                          <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-3">Preuve d'ingénierie</h4>
                          <p className="text-slate-800 font-medium leading-relaxed text-lg">{parseAnalyse(candidateModal.analyse_json).preuve_ingenierie || 'Non disponible.'}</p>
                        </div>
                        
                        <div className="flex gap-6">
                          <div className="flex-1 bg-emerald-50/80 backdrop-blur-xl p-6 rounded-3xl border border-emerald-100 shadow-sm">
                            <h4 className="text-[11px] font-black text-emerald-600 uppercase tracking-widest mb-2">Point Fort Principal</h4>
                            <p className="text-emerald-950 font-bold text-lg leading-tight">{parseAnalyse(candidateModal.analyse_json).strength || '-'}</p>
                          </div>
                          <div className="flex-1 bg-rose-50/80 backdrop-blur-xl p-6 rounded-3xl border border-rose-100 shadow-sm">
                            <h4 className="text-[11px] font-black text-rose-600 uppercase tracking-widest mb-2">Point de Vigilance</h4>
                            <p className="text-rose-950 font-bold text-lg leading-tight">{parseAnalyse(candidateModal.analyse_json).risk || '-'}</p>
                          </div>
                        </div>

                        <div className="bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-white shadow-sm">
                          <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-3">Conclusion de l'IA</h4>
                          <p className="text-slate-600 italic font-medium leading-relaxed text-lg">{parseAnalyse(candidateModal.analyse_json).reasoning || '-'}</p>
                        </div>
                      </div>

                      {/* Colonne 2 : Radar & Questions */}
                      <div className="flex flex-col gap-6">
                        <div className="bg-white/60 backdrop-blur-xl p-8 rounded-3xl border border-white shadow-sm h-80">
                          <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest mb-4 text-center">Empreinte de Compétences</h4>
                          <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={getRadarData(parseAnalyse(candidateModal.analyse_json))}>
                              <PolarGrid stroke="#CBD5E1" />
                              <PolarAngleAxis dataKey="subject" tick={{fontSize: 12, fill: '#475569', fontWeight: 800}} />
                              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                              <Radar name="Score" dataKey="A" stroke="#3B82F6" strokeWidth={3} fill="#3B82F6" fillOpacity={0.2} />
                            </RadarChart>
                          </ResponsiveContainer>
                        </div>

                        {parseAnalyse(candidateModal.analyse_json).interview_questions && (
                          <div className="bg-slate-900/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-700">
                            <h4 className="font-bold text-white mb-6 flex items-center gap-3 text-lg">
                              <span className="p-2 bg-indigo-500/20 rounded-lg">🎯</span> Plan d'entretien
                            </h4>
                            <div className="space-y-4">
                              {['q1_force', 'q2_risque', 'q3_situation'].map((qKey, i) => parseAnalyse(candidateModal.analyse_json).interview_questions[qKey] && (
                                <div key={qKey} className="bg-white/5 p-5 rounded-2xl border border-white/10">
                                  <p className="text-xs font-black text-indigo-400 tracking-wider mb-2 uppercase">Q{i+1}. {parseAnalyse(candidateModal.analyse_json).interview_questions[qKey].titre}</p>
                                  <p className="text-base font-medium text-white italic leading-relaxed">« {parseAnalyse(candidateModal.analyse_json).interview_questions[qKey].question} »</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
}