import { useState, useEffect, useRef } from 'react'
import { 
  Workflow, 
  Database, 
  UserCheck, 
  PackageCheck, 
  Settings, 
  ChevronRight, 
  CheckCircle, 
  AlertTriangle, 
  Sparkles, 
  Send, 
  User, 
  TrendingUp, 
  Search, 
  Download, 
  Cpu, 
  Eye, 
  ArrowRight,
  RefreshCw,
  Check,
  FolderOpen
} from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('architecture') // 'architecture' | 'ingest' | 'match' | 'dispense'
  const [presets, setPresets] = useState([])
  const [selectedPresetId, setSelectedPresetId] = useState('dorothy_thompson')
  const [selectedPreset, setSelectedPreset] = useState(null)
  const [dbType, setDbType] = useState('mock')
  
  // Extraction states
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractionComplete, setExtractionComplete] = useState(false)
  const [extractionSteps, setExtractionSteps] = useState([])
  const [extractedFields, setExtractedFields] = useState(null)
  
  // Matching states
  const [candidates, setCandidates] = useState([])
  const [selectedCandidateId, setSelectedCandidateId] = useState(null)
  
  // Chatbot states
  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [isChatLoading, setIsChatLoading] = useState(false)
  const chatEndRef = useRef(null)

  // Load presets
  useEffect(() => {
    fetch('/api/presets')
      .then(res => res.json())
      .then(data => {
        setPresets(data)
        if (data.length > 0) {
          loadPreset(selectedPresetId)
        }
      })
      .catch(err => console.error("Error loading presets:", err))
  }, [])

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const loadPreset = (presetId) => {
    fetch(`/api/preset/${presetId}`)
      .then(res => res.json())
      .then(data => {
        setSelectedPreset(data)
        setSelectedPresetId(presetId)
        // Reset states
        setExtractionComplete(false)
        setIsExtracting(false)
        setExtractedFields(null)
        setCandidates([])
        setSelectedCandidateId(null)
        
        // Load initial chatbot intro message
        setChatMessages([
          { sender: 'ai', text: `Connected to CloudScript AI. Ready to analyze ${data.label}. Ask me about match signals, patient history, or NPI credentials.` }
        ])
      })
      .catch(err => console.error("Error loading preset:", err))
  }

  const handleExtract = async () => {
    setIsExtracting(true)
    setExtractionSteps([
      { step: "Downloading from GCS", status: "pending" },
      { step: "Gemini 2.5 Flash - OCR", status: "pending" },
      { step: "Parsing + coercing fields", status: "pending" },
      { step: "Generating name embedding", status: "pending" },
      { step: "Inserting to Cloud SQL", status: "pending" },
      { step: "Extraction complete", status: "pending" }
    ])

    // Animate steps
    for (let i = 0; i < 6; i++) {
      await new Promise(resolve => setTimeout(resolve, 300))
      setExtractionSteps(prev => prev.map((s, idx) => 
        idx === i ? { ...s, status: "completed" } : s
      ))
    }

    // Call API
    fetch('/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset_id: selectedPresetId })
    })
      .then(res => res.json())
      .then(data => {
        setExtractedFields(data.extracted_fields)
        setExtractionComplete(true)
        setIsExtracting(false)
        
        // Prefetch candidates for Stage 2
        fetch('/api/match', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-Database-Type': dbType
          },
          body: JSON.stringify({ preset_id: selectedPresetId })
        })
          .then(res => res.json())
          .then(matchData => {
            setCandidates(matchData.candidates)
            if (matchData.candidates.length > 0) {
              setSelectedCandidateId(matchData.candidates[0].id)
            }
          })
      })
  }

  const handleSendChatMessage = () => {
    if (!chatInput.trim()) return
    const userMsg = chatInput
    setChatMessages(prev => [...prev, { sender: 'user', text: userMsg }])
    setChatInput('')
    setIsChatLoading(true)

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset_id: selectedPresetId, message: userMsg })
    })
      .then(res => res.json())
      .then(data => {
        setChatMessages(prev => [...prev, { sender: 'ai', text: data.reply }])
        setIsChatLoading(false)
      })
      .catch(() => setIsChatLoading(false))
  }

  const handleDispense = () => {
    fetch('/api/dispense', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-Database-Type': dbType
      },
      body: JSON.stringify({ preset_id: selectedPresetId })
    })
      .then(res => res.json())
      .then(data => {
        alert(data.message)
        setActiveTab('architecture')
      })
  }

  return (
    <div className="flex h-screen bg-[#f8f9fa] text-zinc-800 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-72 bg-white border-r border-zinc-200 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo Header */}
          <div className="p-6 border-b border-zinc-200">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center font-bold text-white text-lg">
                CS
              </div>
              <div>
                <h1 className="font-bold text-lg tracking-tight text-zinc-950">CloudScript</h1>
                <p className="text-xs text-zinc-450 font-semibold uppercase">Pharmacy Intelligence</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            <button
              onClick={() => setActiveTab('architecture')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'architecture'
                  ? 'bg-red-50 text-red-600 border-l-4 border-red-500'
                  : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'
              }`}
            >
              <Workflow className="w-5 h-5" />
              Architecture Overview
            </button>

            <button
              onClick={() => setActiveTab('ingest')}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'ingest'
                  ? 'bg-red-50 text-red-600 border-l-4 border-red-500'
                  : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'
              }`}
            >
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5" />
                Ingest + Extract
              </div>
              <span className="text-[10px] bg-zinc-100 px-1.5 py-0.5 rounded font-mono text-zinc-650">Stage 1</span>
            </button>

            <button
              onClick={() => setActiveTab('match')}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'match'
                  ? 'bg-red-50 text-red-600 border-l-4 border-red-500'
                  : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'
              }`}
            >
              <div className="flex items-center gap-3">
                <UserCheck className="w-5 h-5" />
                Match + Review
              </div>
              <span className="text-[10px] bg-zinc-100 px-1.5 py-0.5 rounded font-mono text-zinc-650">Stage 2</span>
            </button>

            <button
              onClick={() => setActiveTab('dispense')}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'dispense'
                  ? 'bg-red-50 text-red-600 border-l-4 border-red-500'
                  : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'
              }`}
            >
              <div className="flex items-center gap-3">
                <PackageCheck className="w-5 h-5" />
                Verify + Dispense
              </div>
              <span className="text-[10px] bg-zinc-100 px-1.5 py-0.5 rounded font-mono text-zinc-650">Stage 3</span>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-zinc-200 text-xs text-zinc-500">
          <div className="flex justify-between items-center">
            <span>Gemini 2.5 Flash connected</span>
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#f4f5f6]">
        {/* Header Bar */}
        <header className="h-16 border-b border-zinc-200 bg-white px-8 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-zinc-500 text-sm">Active Scenario:</span>
              <span className="font-semibold text-zinc-800 text-sm bg-zinc-50 px-2.5 py-1 rounded border border-zinc-200">
                {selectedPreset ? selectedPreset.label : 'Loading...'}
              </span>
            </div>
            
            <div className="flex items-center gap-2 ml-4">
              <span className="text-zinc-500 text-sm">Target Database:</span>
              <select 
                value={dbType} 
                onChange={(e) => setDbType(e.target.value)}
                className="bg-zinc-50 text-zinc-800 text-xs font-semibold px-3 py-1.5 rounded border border-zinc-200 focus:outline-none focus:border-red-500 cursor-pointer"
              >
                <option value="mock">Mock Presets (In-Memory)</option>
                <option value="cloudsql">Cloud SQL (PostgreSQL 18)</option>
                <option value="spanner">Google Cloud Spanner</option>
                <option value="alloydb">Google Cloud AlloyDB</option>
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <span>GCP Project:</span>
            <span className="font-mono text-red-650 font-semibold">pharmacy-intelligence-demo</span>
          </div>
        </header>

        {/* Tab Pages */}
        <div className="flex-1 overflow-y-auto p-8">
          
          {/* 1. Architecture Page */}
          {activeTab === 'architecture' && (
            <div className="max-w-6xl mx-auto space-y-8">
              <div>
                <span className="text-xs font-semibold text-red-650 uppercase tracking-widest">Overview</span>
                <h2 className="text-3xl font-extrabold text-zinc-950 mt-1">CloudScript Architecture</h2>
                <p className="text-zinc-650 mt-1">AI-powered prescription processing on Google Cloud — from fax to dispensed in seconds.</p>
              </div>

              {/* End-to-End Pipeline Node Flow */}
              <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
                <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider mb-6">End-to-End Ingestion Pipeline</h3>
                <div className="grid grid-cols-6 gap-2 relative">
                  {/* Step 1 */}
                  <div className="text-center p-4 bg-zinc-50/50 rounded-lg border border-zinc-200 flex flex-col justify-between h-36">
                    <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-2 text-sm font-bold">1</div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">Prescription Arrives</h4>
                      <p className="text-[10px] text-zinc-500 mt-1">Fax / Digital Upload</p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="text-center p-4 bg-zinc-50/50 rounded-lg border border-zinc-200 flex flex-col justify-between h-36">
                    <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-2 text-sm font-bold">2</div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">Gemini OCR</h4>
                      <p className="text-[10px] text-zinc-500 mt-1">Vision Extraction</p>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="text-center p-4 bg-zinc-50/50 rounded-lg border border-zinc-200 flex flex-col justify-between h-36">
                    <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-2 text-sm font-bold">3</div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">Embedding Generation</h4>
                      <p className="text-[10px] text-zinc-500 mt-1">Vertex AI text-embedding</p>
                    </div>
                  </div>

                  {/* Step 4 */}
                  <div className="text-center p-4 bg-zinc-50/50 rounded-lg border border-zinc-200 flex flex-col justify-between h-36">
                    <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-2 text-sm font-bold">4</div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">pgvector Match</h4>
                      <p className="text-[10px] text-zinc-500 mt-1">HNSW Cosine Match</p>
                    </div>
                  </div>

                  {/* Step 5 */}
                  <div className="text-center p-4 bg-zinc-50/50 rounded-lg border border-zinc-200 flex flex-col justify-between h-36">
                    <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-2 text-sm font-bold">5</div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">Multi-Signal Weighted</h4>
                      <p className="text-[10px] text-zinc-500 mt-1">8 parameters scoring</p>
                    </div>
                  </div>

                  {/* Step 6 */}
                  <div className="text-center p-4 bg-zinc-50/50 rounded-lg border border-zinc-200 flex flex-col justify-between h-36">
                    <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-2 text-sm font-bold">6</div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">Verify & Dispense</h4>
                      <p className="text-[10px] text-zinc-500 mt-1">Auto-approval or HITL</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Match Signal Weights */}
                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
                  <h3 className="text-sm font-semibold uppercase text-zinc-450 tracking-wider mb-6">Match Signal Weights</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-zinc-800 font-medium">Date of Birth (Exact / Year Proximity)</span>
                        <span className="text-red-650 font-bold font-mono">35%</span>
                      </div>
                      <div className="w-full bg-zinc-100 h-2 rounded-full overflow-hidden">
                        <div className="bg-red-500 h-2 rounded-full" style={{ width: '35%' }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-zinc-800 font-medium">Patient Name (pg_trgm + pgvector)</span>
                        <span className="text-red-650 font-bold font-mono">20%</span>
                      </div>
                      <div className="w-full bg-zinc-100 h-2 rounded-full overflow-hidden">
                        <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-zinc-800 font-medium">Insurance ID (Exact String)</span>
                        <span className="text-red-650 font-bold font-mono">20%</span>
                      </div>
                      <div className="w-full bg-zinc-100 h-2 rounded-full overflow-hidden">
                        <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-zinc-800 font-medium">NPI Prior Fill History</span>
                        <span className="text-red-650 font-bold font-mono">10%</span>
                      </div>
                      <div className="w-full bg-zinc-100 h-2 rounded-full overflow-hidden">
                        <div className="bg-red-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-zinc-800 font-medium">Drug History (TF-IDF Match)</span>
                        <span className="text-red-650 font-bold font-mono">10%</span>
                      </div>
                      <div className="w-full bg-zinc-100 h-2 rounded-full overflow-hidden">
                        <div className="bg-red-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Google Cloud Stack */}
                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
                  <h3 className="text-sm font-semibold uppercase text-zinc-450 tracking-wider mb-6">Google Cloud Stack</h3>
                  <ul className="space-y-4">
                    {dbType === "spanner" ? (
                      <li className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Database className="w-5 h-5" /></div>
                        <div>
                          <h4 className="text-xs font-semibold text-zinc-800 font-semibold">Google Cloud Spanner</h4>
                          <p className="text-[10px] text-zinc-500">Relational database with transactional patient lookups</p>
                        </div>
                      </li>
                    ) : dbType === "alloydb" ? (
                      <li className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Database className="w-5 h-5" /></div>
                        <div>
                          <h4 className="text-xs font-semibold text-zinc-800 font-semibold">Google Cloud AlloyDB</h4>
                          <p className="text-[10px] text-zinc-500">High-performance PostgreSQL with pgvector scoring</p>
                        </div>
                      </li>
                    ) : dbType === "mock" ? (
                      <li className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Database className="w-5 h-5" /></div>
                        <div>
                          <h4 className="text-xs font-semibold text-zinc-800 font-semibold">Mock Presets (In-Memory)</h4>
                          <p className="text-[10px] text-zinc-500">Local sandbox memory presets for rapid verification</p>
                        </div>
                      </li>
                    ) : (
                      <li className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Database className="w-5 h-5" /></div>
                        <div>
                          <h4 className="text-xs font-semibold text-zinc-800 font-semibold">Cloud SQL PostgreSQL 18</h4>
                          <p className="text-[10px] text-zinc-500">Storing profiles with pgvector & pg_trgm indexes</p>
                        </div>
                      </li>
                    )}
                    <li className="flex items-center gap-3">
                      <div className="p-2 bg-amber-50 text-amber-600 rounded-lg"><Sparkles className="w-5 h-5" /></div>
                      <div>
                        <h4 className="text-xs font-semibold text-zinc-800">Gemini 2.5 Flash</h4>
                        <p className="text-[10px] text-zinc-500">Structured vision extraction & reasoning model</p>
                      </div>
                    </li>
                    <li className="flex items-center gap-3">
                      <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><Cpu className="w-5 h-5" /></div>
                      <div>
                        <h4 className="text-xs font-semibold text-zinc-800">Vertex AI Embeddings</h4>
                        <p className="text-[10px] text-zinc-500">Semantic name & drug substitution mappings</p>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Demo Scenarios Grid */}
              <div>
                <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider mb-4">Select a Demo Scenario</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {presets.map(item => (
                    <button
                      key={item.id}
                      onClick={() => {
                        loadPreset(item.id)
                        setActiveTab('ingest')
                      }}
                      className={`text-left p-4 rounded-xl border transition-all ${
                        selectedPresetId === item.id 
                          ? 'bg-red-50/50 border-red-500 text-red-800' 
                          : 'bg-white border-zinc-200 hover:border-zinc-300 text-zinc-700'
                      }`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-semibold text-sm">{item.label}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold font-mono ${
                          item.status === 'EQUAL' ? 'bg-emerald-50 text-emerald-700 border border-emerald-250' :
                          item.status === 'FAIR' ? 'bg-amber-50 text-amber-700 border border-amber-250' :
                          'bg-blue-50 text-blue-700 border border-blue-250'
                        }`}>
                          {item.status}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-500 line-clamp-2">{item.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}          {/* 2. Ingest + Extract Page */}
          {activeTab === 'ingest' && selectedPreset && (
            <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Column: Prescription Scan */}
              <div className="space-y-6">
                <div>
                  <span className="text-[10px] bg-red-50 text-red-650 px-2 py-0.5 rounded border border-red-200 font-mono uppercase tracking-wider font-semibold">Stage 1 of 3</span>
                  <h2 className="text-2xl font-bold mt-2 text-zinc-950">Ingest & Extract</h2>
                  <p className="text-sm text-zinc-500 mt-1">Gemini 2.5 Flash reads the prescription image and extracts all fields into Cloud SQL.</p>
                </div>

                {/* Prescription Mock Card */}
                <div className="bg-white text-zinc-900 p-8 rounded-xl border border-zinc-200 shadow-xl max-w-md mx-auto aspect-[4/5] flex flex-col justify-between font-serif relative">
                  {/* Security watermark */}
                  <div className="absolute inset-0 opacity-[0.03] pointer-events-none flex items-center justify-center text-4xl font-extrabold uppercase border-8 border-black select-none rotate-12">
                    Secured Rx
                  </div>
                  <div>
                    <div className="border-b-2 border-zinc-900 pb-4 mb-4">
                      <h4 className="font-sans font-bold text-xl tracking-tight text-red-600">ePrescription — Electronic Rx</h4>
                      <p className="font-sans text-[10px] text-zinc-500 uppercase tracking-widest font-semibold">CloudScript Pharmacy | 1200 Main St. Houston, TX 77002</p>
                    </div>

                    <div className="space-y-3 font-sans text-xs">
                      <div>
                        <span className="text-[9px] text-zinc-500 uppercase font-semibold">Patient Name:</span>
                        <p className="font-bold border-b border-zinc-300 pb-0.5 text-zinc-900">{selectedPreset.rx_image.patient_name}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-[9px] text-zinc-500 uppercase font-semibold">Date of Birth:</span>
                          <p className="font-bold border-b border-zinc-300 pb-0.5 text-zinc-900">{selectedPreset.rx_image.dob}</p>
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-500 uppercase font-semibold">Insurance ID:</span>
                          <p className="font-bold border-b border-zinc-300 pb-0.5 text-zinc-900">{selectedPreset.rx_image.insurance_id}</p>
                        </div>
                      </div>
                      <div>
                        <span className="text-[9px] text-zinc-500 uppercase font-semibold">ZIP Code:</span>
                        <p className="font-bold border-b border-zinc-300 pb-0.5 text-zinc-900">{selectedPreset.rx_image.zip_code}</p>
                      </div>

                      <div className="border-t border-dashed border-zinc-400 my-4 pt-4">
                        <span className="text-[9px] text-zinc-500 uppercase font-semibold">Medication (Rx):</span>
                        <p className="font-serif italic font-bold text-sm border-b border-zinc-300 pb-1 mt-1 text-zinc-900">{selectedPreset.rx_image.medication}</p>
                        <div className="grid grid-cols-2 gap-4 mt-2">
                          <div>
                            <span className="text-[9px] text-zinc-500 uppercase font-semibold">Qty / Days:</span>
                            <p className="font-bold border-b border-zinc-300 pb-0.5 text-zinc-900">{selectedPreset.rx_image.qty_days}</p>
                          </div>
                          <div>
                            <span className="text-[9px] text-zinc-500 uppercase font-semibold">Refills:</span>
                            <p className="font-bold border-b border-zinc-300 pb-0.5 text-zinc-900">{selectedPreset.rx_image.refills}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-zinc-300 pt-4 flex justify-between items-end font-sans text-xs">
                    <div>
                      <span className="text-[9px] text-zinc-500 uppercase font-semibold">Prescriber:</span>
                      <p className="font-bold text-zinc-900">{selectedPreset.rx_image.prescriber}</p>
                      <p className="text-[9px] text-zinc-500 font-mono">NPI: {selectedPreset.rx_image.npi}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-[9px] text-zinc-500 uppercase font-semibold">DEA:</span>
                      <p className="font-mono text-zinc-900">{selectedPreset.rx_image.dea}</p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-center gap-3">
                  <button
                    onClick={handleExtract}
                    disabled={isExtracting}
                    className="w-full max-w-xs py-3 px-6 bg-red-650 hover:bg-red-750 disabled:bg-zinc-200 disabled:text-zinc-400 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 transition-colors cursor-pointer text-white shadow-md"
                  >
                    {isExtracting ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Extracting...
                      </>
                    ) : (
                      <>
                        <Cpu className="w-4 h-4" />
                        Extract Prescription
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Right Column: Processing logs & values */}
              <div className="space-y-6">
                {/* Pipeline Steps Logs */}
                {isExtracting || extractionComplete ? (
                  <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm space-y-4">
                    <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider">Extraction Pipeline</h3>
                    <div className="space-y-3">
                      {extractionSteps.map((step, idx) => (
                        <div key={idx} className="flex justify-between items-center text-sm text-zinc-800">
                          <span className={`${step.status === 'completed' ? 'text-zinc-900 font-medium' : 'text-zinc-450'}`}>{step.step}</span>
                          <div>
                            {step.status === 'completed' ? (
                              <CheckCircle className="w-4 h-4 text-emerald-500" />
                            ) : (
                              <div className="w-4 h-4 rounded-full border-2 border-zinc-200 border-t-red-500 animate-spin"></div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="bg-white p-8 rounded-xl border border-zinc-200 shadow-sm text-center flex flex-col justify-center items-center h-48 text-zinc-500">
                    <Eye className="w-8 h-8 text-zinc-400 mb-2" />
                    <span className="font-semibold text-zinc-800">Ready to Extract</span>
                    <p className="text-xs text-zinc-550 mt-1">Select a scenario and click 'Extract' to run the pipeline.</p>
                  </div>
                )}

                {/* Extraction Result Table */}
                {extractionComplete && extractedFields && (
                  <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider">Extracted Fields</h3>
                      <span className="text-[10px] px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded font-bold font-mono">100% Match</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                      <div className="bg-zinc-50 p-2.5 rounded border border-zinc-200">
                        <span className="text-[9px] text-zinc-500 block mb-0.5">Patient Name</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.patient_name}</span>
                      </div>
                      <div className="bg-zinc-50 p-2.5 rounded border border-zinc-200">
                        <span className="text-[9px] text-zinc-500 block mb-0.5">Date of Birth</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.dob}</span>
                      </div>
                      <div className="bg-zinc-50 p-2.5 rounded border border-zinc-200">
                        <span className="text-[9px] text-zinc-500 block mb-0.5">Insurance ID</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.insurance_id}</span>
                      </div>
                      <div className="bg-zinc-50 p-2.5 rounded border border-zinc-200">
                        <span className="text-[9px] text-zinc-500 block mb-0.5">ZIP Code</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.zip_code}</span>
                      </div>
                      <div className="bg-zinc-50 p-2.5 rounded border border-zinc-200">
                        <span className="text-[9px] text-zinc-500 block mb-0.5">Drug Name</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.drug_name}</span>
                      </div>
                      <div className="bg-zinc-50 p-2.5 rounded border border-zinc-200">
                        <span className="text-[9px] text-zinc-500 block mb-0.5">Qty / Days</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.qty_days}</span>
                      </div>
                    </div>

                    <div className="pt-4 flex justify-end">
                      <button
                        onClick={() => setActiveTab('match')}
                        className="py-2 px-4 bg-white hover:bg-zinc-50 text-zinc-700 text-xs font-semibold rounded-md border border-zinc-200 flex items-center gap-1.5 transition-colors cursor-pointer"
                      >
                        Proceed to Match & Review
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 3. Match + Review Page */}
          {activeTab === 'match' && selectedPreset && (
            <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Left Column: Query Fields */}
              <div className="space-y-6">
                <div>
                  <span className="text-[10px] bg-red-50 text-red-650 px-2 py-0.5 rounded border border-red-200 font-mono uppercase tracking-wider font-semibold">Stage 2 of 3</span>
                  <h2 className="text-2xl font-bold mt-2 text-zinc-950">Match & Review</h2>
                  <p className="text-xs text-zinc-500 mt-1">AI agent evaluates database candidates using trgm & vector matching.</p>
                </div>

                <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm space-y-4">
                  <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider">Active Query Profile</h3>
                  
                  {extractedFields ? (
                    <div className="space-y-3 text-xs">
                      <div className="flex justify-between border-b border-zinc-100 pb-2">
                        <span className="text-zinc-500">Patient:</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.patient_name}</span>
                      </div>
                      <div className="flex justify-between border-b border-zinc-100 pb-2">
                        <span className="text-zinc-500">DOB:</span>
                        <span className="font-semibold text-zinc-800 font-mono">{extractedFields.dob}</span>
                      </div>
                      <div className="flex justify-between border-b border-zinc-100 pb-2">
                        <span className="text-zinc-500">Insurance ID:</span>
                        <span className="font-semibold text-zinc-800 font-mono">{extractedFields.insurance_id}</span>
                      </div>
                      <div className="flex justify-between border-b border-zinc-100 pb-2">
                        <span className="text-zinc-500">ZIP Code:</span>
                        <span className="font-semibold text-zinc-800 font-mono">{extractedFields.zip_code}</span>
                      </div>
                      <div className="flex justify-between border-b border-zinc-100 pb-2">
                        <span className="text-zinc-500">Drug:</span>
                        <span className="font-semibold text-zinc-800">{extractedFields.drug_name}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-zinc-500 text-xs text-center py-6">
                      No query profile extracted yet. Run Stage 1 extraction first.
                    </div>
                  )}
                </div>
              </div>

              {/* Middle Column: Patient Candidates List */}
              <div className="space-y-6">
                <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider">Patient Candidates</h3>
                
                {candidates.length > 0 ? (
                  <div className="space-y-4">
                    {candidates.map((cand) => (
                      <div
                        key={cand.id}
                        onClick={() => setSelectedCandidateId(cand.id)}
                        className={`p-5 rounded-xl border transition-all cursor-pointer ${
                          selectedCandidateId === cand.id 
                            ? 'bg-red-50 border-red-550 shadow-md shadow-red-50/50' 
                            : 'bg-white border-zinc-200 hover:border-zinc-300 shadow-sm'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h4 className="font-bold text-sm text-zinc-800">{cand.name}</h4>
                            <p className="text-[10px] text-zinc-500 mt-0.5">DOB: {cand.dob} | Ins: {cand.insurance_id}</p>
                          </div>
                          <span className={`text-xs font-extrabold font-mono px-2 py-0.5 rounded ${
                            cand.score >= 75 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                            cand.score >= 40 ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                            'bg-red-50 text-red-700 border border-red-200'
                          }`}>
                            {cand.score}% Match
                          </span>
                        </div>

                        {/* Matching Signal Indicators */}
                        <div className="space-y-1.5 pt-2 border-t border-zinc-150">
                          {/* DOB Signal */}
                          <div>
                            <div className="flex justify-between text-[9px] text-zinc-500">
                              <span>Date of Birth</span>
                              <span className="font-mono text-zinc-700 font-bold">{cand.signals.dob}%</span>
                            </div>
                            <div className="w-full bg-zinc-100 h-1 rounded-full overflow-hidden mt-0.5">
                              <div className={`h-1 ${cand.signals.dob >= 75 ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${cand.signals.dob}%` }}></div>
                            </div>
                          </div>

                          {/* Patient Name (trgm/vector) */}
                          <div>
                            <div className="flex justify-between text-[9px] text-zinc-500">
                              <span>Patient Name (trgm: {cand.trgm_score}%, vector: {cand.vector_score}%)</span>
                              <span className="font-mono text-zinc-700 font-bold">{cand.signals.name}%</span>
                            </div>
                            <div className="w-full bg-zinc-100 h-1 rounded-full overflow-hidden mt-0.5">
                              <div className={`h-1 ${cand.signals.name >= 75 ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${cand.signals.name}%` }}></div>
                            </div>
                          </div>

                          {/* Insurance ID */}
                          <div>
                            <div className="flex justify-between text-[9px] text-zinc-500">
                              <span>Insurance ID</span>
                              <span className="font-mono text-zinc-700 font-bold">{cand.signals.insurance}%</span>
                            </div>
                            <div className="w-full bg-zinc-100 h-1 rounded-full overflow-hidden mt-0.5">
                              <div className={`h-1 ${cand.signals.insurance >= 75 ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${cand.signals.insurance}%` }}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-zinc-500 text-xs text-center py-12 bg-white rounded-xl border border-zinc-200 h-48 flex flex-col justify-center items-center shadow-sm">
                    <span>No Candidates loaded.</span>
                    <p className="text-zinc-650 mt-1">Complete Stage 1 to populate matching candidates.</p>
                  </div>
                )}
              </div>

              {/* Right Column: AI Chatbot Assistant */}
              <div className="bg-white border border-zinc-200 rounded-xl flex flex-col h-[550px] shadow-sm">
                {/* Chatbot Header */}
                <div className="p-4 border-b border-zinc-200 bg-zinc-50/50 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-red-55 text-red-650 rounded-lg">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-800">CloudScript AI</h4>
                      <p className="text-[9px] text-zinc-500">Gemini 2.5 Flash Assistant</p>
                    </div>
                  </div>
                  <span className="text-[9px] bg-emerald-50 text-emerald-700 border border-emerald-250 px-1.5 py-0.5 rounded font-mono uppercase font-bold">Connected</span>
                </div>

                {/* Messages List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
                  {chatMessages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-3 rounded-lg ${
                        msg.sender === 'user' 
                          ? 'bg-red-600 text-white rounded-br-none' 
                          : 'bg-zinc-50 border border-zinc-200 text-zinc-800 rounded-bl-none'
                      }`}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {isChatLoading && (
                    <div className="flex justify-start">
                      <div className="bg-zinc-50 border border-zinc-200 p-3 rounded-lg rounded-bl-none flex items-center gap-2 text-zinc-500">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        AI is typing...
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Quick Prompts */}
                <div className="p-2 border-t border-zinc-200 bg-zinc-50 flex gap-1.5 overflow-x-auto select-none shrink-0">
                  <button 
                    onClick={() => {
                      setChatInput("Why did you recommend this match?")
                    }}
                    className="shrink-0 text-[10px] bg-white hover:bg-zinc-50 border border-zinc-200 px-2 py-1 rounded text-zinc-650 font-medium shadow-sm"
                  >
                    Explain match score
                  </button>
                  <button 
                    onClick={() => {
                      setChatInput("Check drug history formulary status")
                    }}
                    className="shrink-0 text-[10px] bg-white hover:bg-zinc-50 border border-zinc-200 px-2 py-1 rounded text-zinc-650 font-medium shadow-sm"
                  >
                    Verify drug status
                  </button>
                </div>

                {/* Message Input Box */}
                <div className="p-3 border-t border-zinc-200 flex gap-2 shrink-0">
                  <input
                    type="text"
                    placeholder="Ask about candidate, warnings, database keys..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendChatMessage()}
                    className="flex-1 bg-white border border-zinc-200 rounded-lg px-3 py-2 text-xs text-zinc-800 placeholder-zinc-400 focus:outline-none focus:border-red-500"
                  />
                  <button
                    onClick={handleSendChatMessage}
                    className="p-2 bg-red-650 hover:bg-red-750 text-white rounded-lg transition-colors cursor-pointer"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Bottom Action bar */}
              <div className="lg:col-span-3 flex justify-end gap-3 pt-4 border-t border-zinc-200">
                <button
                  onClick={() => setActiveTab('dispense')}
                  className="py-3 px-6 bg-red-650 hover:bg-red-750 text-white text-sm font-semibold rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer shadow-sm"
                >
                  Proceed to Verify & Dispense
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* 4. Verify & Dispense Page */}
          {activeTab === 'dispense' && selectedPreset && (
            <div className="max-w-3xl mx-auto space-y-6">
              <div>
                <span className="text-[10px] bg-red-55 text-red-650 px-2 py-0.5 rounded border border-red-200 font-mono uppercase tracking-wider font-semibold">Stage 3 of 3</span>
                <h2 className="text-2xl font-bold mt-2 text-zinc-950">Verify & Dispense</h2>
                <p className="text-xs text-zinc-500 mt-1">Final safety checkpoints before recording the dispensed prescription in target database.</p>
              </div>

              <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden divide-y divide-zinc-150 shadow-sm">
                {/* Selected Patient */}
                <div className="p-6">
                  <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider mb-3">Selected Patient Candidate</h3>
                  <div className="flex justify-between items-center bg-zinc-50 p-4 rounded-lg border border-zinc-200">
                    <div>
                      <h4 className="font-bold text-base text-zinc-800">{selectedPreset.rx_image.patient_name}</h4>
                      <p className="text-xs text-zinc-500 mt-0.5">Date of Birth: {selectedPreset.rx_image.dob} | Address ZIP: {selectedPreset.rx_image.zip_code}</p>
                    </div>
                    <span className="text-xs bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded border border-emerald-200 font-bold uppercase tracking-wider">Verified Candidate</span>
                  </div>
                </div>

                {/* Drug Details */}
                <div className="p-6">
                  <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider mb-3">Dispense Medication Details</h3>
                  <div className="grid grid-cols-2 gap-6 text-sm">
                    <div>
                      <span className="text-[10px] text-zinc-500 block">Medication Name</span>
                      <span className="font-semibold text-zinc-800">{selectedPreset.rx_image.medication}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-zinc-500 block">Prescriber</span>
                      <span className="font-semibold text-zinc-800">{selectedPreset.rx_image.prescriber}</span>
                    </div>
                  </div>
                </div>

                {/* Warnings */}
                <div className="p-6 space-y-4">
                  <h3 className="text-xs font-semibold uppercase text-zinc-450 tracking-wider mb-1">Safety Checks</h3>
                  
                  <div className="flex gap-3 bg-amber-50/50 border border-amber-200 p-4 rounded-lg text-xs">
                    <div className="p-1 bg-amber-100 text-amber-700 rounded-lg shrink-0 h-fit">
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <div>
                      <h5 className="font-bold text-zinc-800">Patient Copay & Substitutions</h5>
                      <p className="text-zinc-650 mt-1">If brand names were substituted for generics, confirm that the patient agrees to the lisinopril/generic replacement.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Large Approve Action button */}
              <div className="flex justify-end gap-3 pt-4">
                <button
                  onClick={handleDispense}
                  className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white text-base font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg transition-colors cursor-pointer"
                >
                  <Check className="w-5 h-5" />
                  Approve & Dispense Prescription
                </button>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  )
}

export default App
