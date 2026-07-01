import { useState, useEffect } from 'react'
import { Sun, Moon, TrendingUp, TrendingDown, AlertTriangle, Users, DollarSign, BarChart2 } from 'lucide-react'

function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [persona, setPersona] = useState('sales') // 'sales' | 'ce'
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  useEffect(() => {
    fetch('/api/revenue')
      .then(res => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      })
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const formatCurrency = (val) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(1)}K`;
    return `$${val}`;
  }

  const totalRevenue = data.reduce((sum, row) => sum + row.db_rev_ytd_current_year, 0);
  const topCustomer = data.length > 0 ? data[0].account_name : 'N/A';
  const topProduct = data.length > 0 ? data[0].product_name : 'N/A';

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-[#09090b] text-zinc-950 dark:text-zinc-50 transition-colors duration-300">
      <div className="max-w-[1600px] mx-auto p-6">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight">Vector Reporting</h1>
            <p className="text-zinc-500 dark:text-zinc-400">NorthAM Database Team | Strategic Resource Orchestrator</p>
          </div>
          <div className="flex items-center gap-4">
            {/* Segmented Control for Persona */}
            <div className="bg-zinc-100 dark:bg-[#0c0c0f] p-1 rounded-[8px] flex border border-zinc-200 dark:border-zinc-800">
              <button
                onClick={() => setPersona('sales')}
                className={`px-4 py-1.5 rounded-[6px] text-sm font-medium transition-all ${
                  persona === 'sales'
                    ? 'bg-white dark:bg-zinc-800 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
                }`}
              >
                Sales Leader
              </button>
              <button
                onClick={() => setPersona('ce')}
                className={`px-4 py-1.5 rounded-[6px] text-sm font-medium transition-all ${
                  persona === 'ce'
                    ? 'bg-white dark:bg-zinc-800 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
                }`}
              >
                CE Manager
              </button>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-full bg-zinc-100 dark:bg-[#0c0c0f] border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors"
              aria-label="Toggle theme"
            >
              {darkMode ? <Sun className="w-5 h-5 text-yellow-500" /> : <Moon className="w-5 h-5 text-zinc-600" />}
            </button>
          </div>
        </header>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Card 1 */}
          <div className="bg-white dark:bg-[#0c0c0f] p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Total YTD Revenue</h3>
            <p className="text-2xl font-bold font-mono">{formatCurrency(totalRevenue)}</p>
          </div>

          {/* Card 2 */}
          <div className="bg-white dark:bg-[#0c0c0f] p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
                <BarChart2 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Top Product</h3>
            <p className="text-xl font-bold truncate">{topProduct}</p>
          </div>

          {/* Card 3 */}
          <div className="bg-white dark:bg-[#0c0c0f] p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-amber-50 dark:bg-amber-900/30 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Top Customer</h3>
            <p className="text-xl font-bold truncate">{topCustomer}</p>
          </div>

          {/* Card 4 */}
          <div className="bg-white dark:bg-[#0c0c0f] p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg">
                <Users className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-1">Total Customers</h3>
            <p className="text-2xl font-bold font-mono">{data.length}</p>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex gap-6">
          {/* Primary Data Table */}
          <div className="w-full bg-white dark:bg-[#0c0c0f] rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden transition-all">
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex justify-between items-center">
              <h2 className="text-lg font-semibold">
                {persona === 'sales' ? 'Workload Revenue Forecast' : 'Workload Resource Allocation'}
              </h2>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 text-sm border border-zinc-200 dark:border-zinc-700 rounded-md hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors">
                  Filter
                </button>
                <button className="px-3 py-1.5 text-sm bg-emerald-600 hover:bg-emerald-700 text-white rounded-md transition-colors">
                  Export
                </button>
              </div>
            </div>
            <div className="overflow-x-auto">
              {loading ? (
                <div className="p-6 text-center text-zinc-500">Loading revenue data...</div>
              ) : error ? (
                <div className="p-6 text-center text-rose-500">Error: {error}</div>
              ) : (
                <table className="w-full text-left text-sm">
                  <thead className="bg-zinc-50 dark:bg-zinc-900/50 text-zinc-500 dark:text-zinc-400 text-xs uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-3 font-medium">Account Name</th>
                      <th className="px-6 py-3 font-medium">Product</th>
                      <th className="px-6 py-3 font-medium">Region</th>
                      <th className="px-6 py-3 font-medium">Industry</th>
                      <th className="px-6 py-3 font-medium">Revenue (YTD)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                    {data.map((row, index) => (
                      <tr key={index} className="hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors cursor-pointer">
                        <td className="px-6 py-4 font-medium">{row.account_name}</td>
                        <td className="px-6 py-4">{row.product_name}</td>
                        <td className="px-6 py-4">{row.sub_region}</td>
                        <td className="px-6 py-4">{row.industry}</td>
                        <td className="px-6 py-4 font-mono">${row.db_rev_ytd_current_year.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
