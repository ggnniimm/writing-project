import { useState, useEffect, useRef, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import axios from 'axios'
import { Search, Database, Layers, X, PlusCircle, FileText } from 'lucide-react'

// Backend URL
const API_URL = 'http://localhost:8000'

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResult, setSearchResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const fgRef = useRef()

  // Fetch Graph Data
  useEffect(() => {
    axios.get(`${API_URL}/graph`)
      .then(res => {
        setGraphData(res.data)
      })
      .catch(err => console.error("Error fetching graph:", err))
  }, [])

  // Handle Search
  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setLoading(true)
    setSearchResult(null)
    try {
      const res = await axios.post(`${API_URL}/query`, { question: searchQuery })
      setSearchResult(res.data)
      setSidebarOpen(true)
    } catch (err) {
      console.error("Search error:", err)
      setSearchResult({ answer: "Error occurred.", context: "" })
    } finally {
      setLoading(false)
    }
  }

  // Node Color Logic
  const getNodeColor = (node) => {
    switch (node.type) {
      case 'Case': return '#ef4444' // Red 500
      case 'Law': return '#3b82f6'  // Blue 500
      case 'Person': return '#eab308' // Yellow 500
      case 'Principle': return '#a855f7' // Purple 500
      case 'Ruling': return '#f97316' // Orange 500
      default: return '#10b981' // Emerald 500
    }
  }

  // On Node Click
  const handleNodeClick = useCallback(node => {
    setSelectedNode(node)
    setSidebarOpen(true)

    // Zoom to node
    fgRef.current.centerAt(node.x, node.y, 1000)
    fgRef.current.zoom(3, 2000)
  }, [fgRef])

  return (
    <div className="relative w-screen h-screen bg-background text-gray-100 overflow-hidden font-sans">

      {/* Navbar */}
      <div className="absolute top-0 left-0 w-full h-14 bg-surface border-b border-gray-800 flex items-center px-4 z-10 justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-tr from-primary to-secondary rounded-lg flex items-center justify-center">
            <Database size={18} className="text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">Oracle <span className="text-gray-500 text-sm font-normal">Legal Graph</span></span>
        </div>

        <div className="flex items-center gap-4">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-gray-800 rounded-md">
            <Layers size={20} />
          </button>
        </div>
      </div>

      {/* Main Graph Area */}
      <div className="w-full h-full pt-14">
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          backgroundColor="#09090b"
          nodeLabel="id"
          nodeColor={getNodeColor}
          nodeRelSize={6}
          linkColor={() => '#3f3f46'} // Zinc 700
          onNodeClick={handleNodeClick}
          cooldownTicks={100}
        />
      </div>

      {/* Sidebar Interface */}
      {sidebarOpen && (
        <div className="absolute top-14 right-0 w-96 h-[calc(100vh-3.5rem)] bg-surface/95 backdrop-blur-sm border-l border-gray-800 shadow-xl overflow-y-auto transition-all duration-300">

          {/* Close Button Mobile only or generally useful */}
          {/* Search Box */}
          <div className="p-4 border-b border-gray-800">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Search or Ask a question..."
                className="w-full bg-black/50 border border-gray-700 rounded-lg py-2 pl-3 pr-10 text-sm focus:outline-none focus:border-primary transition-colors"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="absolute right-2 top-2 p-0.5 hover:text-primary transition-colors">
                <Search size={16} />
              </button>
            </form>
          </div>

          {/* Content Area */}
          <div className="p-4 space-y-6">

            {/* Selected Node Details */}
            {selectedNode && !searchResult && (
              <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Node Details</h3>
                  <button onClick={() => setSelectedNode(null)}><X size={14} /></button>
                </div>
                <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-800">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: getNodeColor(selectedNode) }}></span>
                    <span className="font-bold text-lg">{selectedNode.id}</span>
                    <span className="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-400">{selectedNode.type}</span>
                  </div>
                  {selectedNode.summary && <p className="text-gray-300 text-sm leading-relaxed">{selectedNode.summary}</p>}

                  {/* Metadata */}
                  {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-800 grid gap-2">
                      {Object.entries(selectedNode.metadata).map(([k, v]) => (
                        <div key={k} className="text-xs">
                          <span className="text-gray-500">{k}:</span> <span className="text-gray-300">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Search Results (RAG Answer) */}
            {loading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            )}

            {searchResult && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-primary flex items-center gap-2">
                    <FileText size={14} />
                    AI Answer
                  </h3>
                  <button onClick={() => setSearchResult(null)}><X size={14} /></button>
                </div>

                <div className="prose prose-invert prose-sm max-w-none bg-gray-900/30 p-4 rounded-lg border border-gray-800/50">
                  <p className="whitespace-pre-wrap">{searchResult.answer}</p>
                </div>

                {/* Context Used */}
                <div className="mt-6">
                  <h4 className="text-xs font-semibold text-gray-500 mb-2 uppercase">Sources / Context</h4>
                  <div className="text-xs text-gray-400 bg-black/20 p-2 rounded overflow-x-auto max-h-40 overflow-y-auto whitespace-pre-wrap font-mono">
                    {searchResult.context}
                  </div>
                </div>
              </div>
            )}

            {/* Default State */}
            {!selectedNode && !searchResult && !loading && (
              <div className="text-center py-10 opacity-30">
                <Database size={48} className="mx-auto mb-4" />
                <p>Select a node or search to view details</p>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  )
}

export default App
