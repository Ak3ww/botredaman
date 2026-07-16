import { useEffect, useState } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { 
  Server, 
  AlertTriangle, 
  CheckCircle, 
  Search, 
  Menu, 
  ChevronLeft, 
  ChevronRight, 
  RefreshCw,
  TrendingDown,
  Radio,
  LayoutDashboard,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  BarChart3,
  Activity
} from 'lucide-react';

import MikrotikTab from './MikrotikTab';

const API_BASE = 'http://localhost:8000/api';
const COLORS = {
  NORMAL: '#10b981',   // Emerald 500
  WARNING: '#f59e0b',  // Amber 500
  CRITICAL: '#ef4444', // Red 500
  OFFLINE: '#64748b'   // Slate 500
};

// --- Custom Modular Components mimicking Shadcn UI structure ---

function Card({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`bg-slate-900/40 backdrop-blur-sm rounded-xl border border-slate-800/80 shadow-md transition-all duration-200 hover:border-slate-700/60 ${className}`}>
      {children}
    </div>
  );
}

function CardHeader({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>{children}</div>;
}

function CardTitle({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return <h3 className={`font-semibold tracking-tight text-slate-100 ${className}`}>{children}</h3>;
}

function CardDescription({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return <p className={`text-xs text-slate-400 ${className}`}>{children}</p>;
}

function CardContent({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return <div className={`p-6 pt-0 ${className}`}>{children}</div>;
}

function Badge({ children, status }: { children: React.ReactNode, status: 'NORMAL' | 'WARNING' | 'CRITICAL' | 'OFFLINE' }) {
  let styles = '';
  switch (status) {
    case 'NORMAL':
      styles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      break;
    case 'WARNING':
      styles = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      break;
    case 'CRITICAL':
      styles = 'bg-red-500/10 text-red-400 border-red-500/20 animate-pulse-slow';
      break;
    case 'OFFLINE':
      styles = 'bg-slate-500/10 text-slate-400 border-slate-500/20';
      break;
  }
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold tracking-wide transition-colors ${styles}`}>
      {children}
    </span>
  );
}

// ----------------------------------------------------------------

export default function App() {
  const [olts, setOlts] = useState<any[]>([]);
  const [attenuations, setAttenuations] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'CRITICAL' | 'WARNING' | 'NORMAL' | 'OFFLINE'>('ALL');
  const [selectedOlt, setSelectedOlt] = useState<string>('ALL');
  const [sortField, setSortField] = useState<string>('timestamp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [separateOffline, setSeparateOffline] = useState<boolean>(true);
  const [selectedOnu, setSelectedOnu] = useState<any | null>(null);
  const [selectedOnuHistory, setSelectedOnuHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'DATABASE' | 'STATS' | 'MIKROTIK'>('OVERVIEW');
  const [trafficStats, setTrafficStats] = useState<any>({
    today: { total_download: 0, total_upload: 0 },
    top_spenders: []
  });
  const [flappingStats, setFlappingStats] = useState<any[]>([]);
  const [eventLogs, setEventLogs] = useState<any[]>([]);
  const itemsPerPage = 10;

  // Initialize filters from URL parameters on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const filterParam = params.get('filter');
    const onuIdParam = params.get('onu_id');
    
    if (filterParam) {
      const upper = filterParam.toUpperCase();
      if (['ALL', 'CRITICAL', 'WARNING', 'NORMAL', 'OFFLINE'].includes(upper)) {
        setFilterStatus(upper as any);
      }
    }
    
    if (onuIdParam) {
      setActiveTab('DATABASE'); // open database view to show selected ONU table row
    }
  }, []);

  useEffect(() => {
    fetchData();
    let interval: any;
    if (autoRefresh) {
      interval = setInterval(fetchData, 10000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const selectedOnuId = selectedOnu?.onu_id;
  const selectedOltId = selectedOnu?.olt_id;

  useEffect(() => {
    if (selectedOnuId) {
      fetchOnuHistory(selectedOnuId, selectedOltId);
    }
  }, [selectedOnuId, selectedOltId]);

  // Refetch history for currently selected ONU periodically if autoRefresh is active
  useEffect(() => {
    let interval: any;
    if (selectedOnuId && autoRefresh) {
      interval = setInterval(() => {
        fetchOnuHistory(selectedOnuId, selectedOltId);
      }, 10000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [selectedOnuId, selectedOltId, autoRefresh]);

  const fetchStats = async () => {
    try {
      const resTraffic = await axios.get(`${API_BASE}/stats/traffic`);
      setTrafficStats(resTraffic.data);
      
      const resFlapping = await axios.get(`${API_BASE}/stats/flapping`);
      setFlappingStats(resFlapping.data);
      
      const resEvents = await axios.get(`${API_BASE}/stats/events`);
      setEventLogs(resEvents.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const fetchData = async () => {
    try {
      const resOlts = await axios.get(`${API_BASE}/olts`);
      setOlts(resOlts.data);
      
      const resAtt = await axios.get(`${API_BASE}/attenuations`);
      setAttenuations(resAtt.data);

      fetchStats();

      // Check if there is a deep link for a specific ONU ID
      const params = new URLSearchParams(window.location.search);
      const onuIdParam = params.get('onu_id');
      const oltIdParam = params.get('olt_id');
      if (onuIdParam) {
        let found;
        if (oltIdParam) {
            found = resAtt.data.find((a: any) => String(a.onu_id) === String(onuIdParam) && String(a.olt_id) === String(oltIdParam));
        } else {
            found = resAtt.data.find((a: any) => String(a.onu_id) === String(onuIdParam));
        }
        if (found) {
          setSelectedOnu(found);
        }
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const fetchOnuHistory = async (onuId: string, oltId?: string | number) => {
    setLoadingHistory(true);
    try {
      let url = `${API_BASE}/chart_data?onu_id=${onuId}`;
      if (oltId) url += `&olt_id=${oltId}`;
      const res = await axios.get(url);
      setSelectedOnuHistory(res.data);
    } catch (error) {
      console.error("Error fetching ONU history:", error);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Helper to categorize power levels
  const getPowerCategory = (power: number | null) => {
    if (power === null) return 'OFFLINE';
    if (power > -23.0) return 'NORMAL';
    if (power >= -26.0) return 'WARNING';
    return 'CRITICAL';
  };

  // Helper to format bytes
  const formatBytes = (bytes: number) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const normalCount = attenuations.filter(a => getPowerCategory(a.rx_power) === 'NORMAL').length;
  const warningCount = attenuations.filter(a => getPowerCategory(a.rx_power) === 'WARNING').length;
  const criticalCount = attenuations.filter(a => getPowerCategory(a.rx_power) === 'CRITICAL').length;
  const offlineCount = attenuations.filter(a => getPowerCategory(a.rx_power) === 'OFFLINE').length;
  const totalCount = attenuations.length;

  // Pie chart data
  const pieData = [
    { name: 'Normal', value: normalCount, color: COLORS.NORMAL },
    { name: 'Warning', value: warningCount, color: COLORS.WARNING },
    { name: 'Critical', value: criticalCount, color: COLORS.CRITICAL },
    { name: 'Offline', value: offlineCount, color: COLORS.OFFLINE }
  ].filter(d => d.value > 0);

  // Filtered data for table
  const filteredData = attenuations.filter(a => {
    const matchesSearch = 
      a.customer_name?.toLowerCase().includes(search.toLowerCase()) || 
      a.onu_id?.toLowerCase().includes(search.toLowerCase()) ||
      a.olt_name?.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;

    // Filter by OLT
    const matchesOlt = selectedOlt === 'ALL' || a.olt_name === selectedOlt;
    if (!matchesOlt) return false;

    const category = getPowerCategory(a.rx_power);
    if (filterStatus === 'ALL') return true;
    return category === filterStatus;
  });

  // Reset pagination when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [filterStatus, search, selectedOlt]);

  // Handle Sort Toggle
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Render Sort Icon Indicator
  const renderSortIcon = (field: string) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3.5 h-3.5 text-slate-600 opacity-60" />;
    }
    if (sortDirection === 'asc') {
      return <ArrowUp className="w-3.5 h-3.5 text-indigo-400" />;
    }
    return <ArrowDown className="w-3.5 h-3.5 text-indigo-400" />;
  };

  // Sorted data for table
  const sortedData = [...filteredData].sort((a, b) => {
    // 1. Separate offline if enabled
    if (separateOffline) {
      const aOffline = getPowerCategory(a.rx_power) === 'OFFLINE';
      const bOffline = getPowerCategory(b.rx_power) === 'OFFLINE';
      if (aOffline !== bOffline) {
        return aOffline ? 1 : -1; // offline goes to the end
      }
    }

    // 2. Column-based sort
    let aVal = a[sortField];
    let bVal = b[sortField];

    if (sortField === 'rx_power') {
      const aPower = aVal !== null ? parseFloat(aVal) : -999;
      const bPower = bVal !== null ? parseFloat(bVal) : -999;
      return sortDirection === 'asc' ? aPower - bPower : bPower - aPower;
    }

    if (aVal === null || aVal === undefined) aVal = '';
    if (bVal === null || bVal === undefined) bVal = '';

    if (typeof aVal === 'string') {
      return sortDirection === 'asc' 
        ? aVal.localeCompare(bVal) 
        : bVal.localeCompare(aVal);
    } else {
      return sortDirection === 'asc'
        ? (aVal > bVal ? 1 : -1)
        : (bVal > aVal ? 1 : -1);
    }
  });

  // Pagination calculation
  const totalPages = Math.ceil(sortedData.length / itemsPerPage) || 1;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = sortedData.slice(startIndex, startIndex + itemsPerPage);

  // Format history data for chart
  const formattedHistory = selectedOnuHistory.map(h => ({
    time: h.timestamp ? h.timestamp.split(' ')[1] : '',
    dbm: h.rx_power
  }));

  // Handle setting status filter (with URL sync)
  const handleFilterStatus = (status: 'ALL' | 'CRITICAL' | 'WARNING' | 'NORMAL' | 'OFFLINE') => {
    setFilterStatus(status);
    const url = new URL(window.location.href);
    if (status === 'ALL') {
      url.searchParams.delete('filter');
    } else {
      url.searchParams.set('filter', status.toLowerCase());
    }
    window.history.pushState({}, '', url.toString());
  };

  // Handle selecting an ONU (with URL sync)
  const handleSelectOnu = (onu: any) => {
    setSelectedOnu(onu);
    const url = new URL(window.location.href);
    url.searchParams.set('onu_id', onu.onu_id);
    window.history.pushState({}, '', url.toString());
  };

  // Handle closing drawer (with URL sync)
  const handleCloseDrawer = () => {
    setSelectedOnu(null);
    setSelectedOnuHistory([]);
    const url = new URL(window.location.href);
    url.searchParams.delete('onu_id');
    window.history.pushState({}, '', url.toString());
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row antialiased font-sans selection:bg-indigo-500 selection:text-white">
      
      {/* Clean Sidebar - Shadcn Visual Style */}
      <aside className="w-full md:w-64 bg-slate-900 border-b md:border-b-0 md:border-r border-slate-800/80 flex flex-col shrink-0">
        <div className="h-16 flex items-center px-6 border-b border-slate-800/85 shrink-0 gap-3">
          <div className="p-1.5 bg-indigo-600 rounded-lg text-white">
            <Radio className="w-4 h-4" />
          </div>
          <span className="font-bold text-sm tracking-widest text-slate-100 uppercase">
            NOC PORTAL
          </span>
        </div>
        
        <nav className="flex-1 py-6 px-4 space-y-4">
          <div className="space-y-1">
            <div className="px-3 py-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
              Menu Utama
            </div>
            
            <button 
              onClick={() => setActiveTab('OVERVIEW')} 
              className={`w-full flex items-center px-3 py-2 rounded-lg font-medium text-xs uppercase tracking-wider transition-all duration-150 ${
                activeTab === 'OVERVIEW' 
                  ? 'bg-slate-800 text-slate-100 shadow-sm border border-slate-700/60' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <LayoutDashboard className="w-4 h-4 mr-2.5 text-indigo-400" /> Ringkasan NOC
            </button>
            
            <button 
              onClick={() => setActiveTab('DATABASE')} 
              className={`w-full flex items-center px-3 py-2 rounded-lg font-medium text-xs uppercase tracking-wider transition-all duration-150 ${
                activeTab === 'DATABASE' 
                  ? 'bg-slate-800 text-slate-100 shadow-sm border border-slate-700/60' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Server className="w-4 h-4 mr-2.5 text-indigo-400" /> Live Data ONU
            </button>

            <button 
              onClick={() => setActiveTab('STATS')} 
              className={`w-full flex items-center px-3 py-2 rounded-lg font-medium text-xs uppercase tracking-wider transition-all duration-150 ${
                activeTab === 'STATS' 
                  ? 'bg-slate-800 text-slate-100 shadow-sm border border-slate-700/60' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <BarChart3 className="w-4 h-4 mr-2.5 text-indigo-400" /> Analisis & Statistik
            </button>
            
            <button 
              onClick={() => setActiveTab('MIKROTIK')} 
              className={`w-full flex items-center px-3 py-2 rounded-lg font-medium text-xs uppercase tracking-wider transition-all duration-150 ${
                activeTab === 'MIKROTIK' 
                  ? 'bg-slate-800 text-slate-100 shadow-sm border border-slate-700/60' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Activity className="w-4 h-4 mr-2.5 text-indigo-400" /> Mikrotik Offline
            </button>
          </div>

          <div className="space-y-1">
            <div className="px-3 py-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
              Quick Filter
            </div>
            
            <button 
              onClick={() => { handleFilterStatus('ALL'); setActiveTab('DATABASE'); }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                filterStatus === 'ALL' && activeTab === 'DATABASE' ? 'bg-slate-800 text-slate-100' : 'text-slate-450 hover:bg-slate-850/50'
              }`}
            >
              <span>🌐 Tampilkan Semua</span>
              <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded-md text-slate-400">{totalCount}</span>
            </button>

            <button 
              onClick={() => { handleFilterStatus('CRITICAL'); setActiveTab('DATABASE'); }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                filterStatus === 'CRITICAL' && activeTab === 'DATABASE' ? 'bg-red-500/10 text-red-400 border border-red-500/25' : 'text-slate-450 hover:bg-slate-850/50 hover:text-red-400'
              }`}
            >
              <span className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-red-500 mr-2.5 animate-pulse"></span>
                🔴 Kritis (Severe)
              </span>
              <span className="text-[10px] bg-red-500/10 px-2 py-0.5 rounded-md font-bold">{criticalCount}</span>
            </button>

            <button 
              onClick={() => { handleFilterStatus('WARNING'); setActiveTab('DATABASE'); }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                filterStatus === 'WARNING' && activeTab === 'DATABASE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/25' : 'text-slate-450 hover:bg-slate-850/50 hover:text-amber-400'
              }`}
            >
              <span className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-amber-500 mr-2.5"></span>
                🟡 Warning (Light)
              </span>
              <span className="text-[10px] bg-amber-500/10 px-2 py-0.5 rounded-md font-bold">{warningCount}</span>
            </button>
          </div>
        </nav>

        <div className="p-4 border-t border-slate-800 bg-slate-900/50 shrink-0">
          <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
            <span>REFRESH 10 DETIK</span>
            <button 
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-2 py-0.5 rounded text-[10px] font-bold ${autoRefresh ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-450'}`}
            >
              {autoRefresh ? 'AKTIF' : 'MATI'}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-hidden">
        
        {/* Header - Shadcn Clean style */}
        <header className="h-16 border-b border-slate-800/80 flex items-center justify-between px-6 md:px-8 bg-slate-900/10 shrink-0">
          <div className="flex items-center text-slate-400">
            <Menu className="w-5 h-5 mr-4 cursor-pointer md:hidden text-slate-200" />
            <h1 className="text-xs font-black tracking-widest text-slate-400 uppercase">
              {activeTab === 'OVERVIEW' ? 'Ringkasan Ekosistem NOC' : activeTab === 'DATABASE' ? 'Live Database Log' : activeTab === 'MIKROTIK' ? 'Mikrotik Monitor' : 'Analisis & Statistik NOC'}
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" />
              <input 
                type="text" 
                placeholder="Cari ONU ID, Nama..." 
                className="pl-9 pr-4 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:bg-slate-900 focus:border-indigo-500 outline-none w-48 md:w-64 transition-all duration-200 focus:ring-1 focus:ring-indigo-500"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <button 
              onClick={fetchData}
              className="p-2 bg-slate-900 border border-slate-850 rounded-lg text-slate-400 hover:text-white transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Dashboard Area */}
        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
          
          <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8">
            
            {/* Top Metric Cards */}
            <section className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">Total OLT</CardTitle>
                  <Server className="h-4 w-4 text-slate-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-slate-100">{olts.length}</div>
                  <p className="text-[10px] text-slate-500 mt-0.5">Suku cadang aktif terdaftar</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">Kritis (Severe)</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-red-500 animate-pulse" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-500">{criticalCount}</div>
                  <p className="text-[10px] text-red-500/60 mt-0.5">Redaman &lt; -26.0 dBm</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">Warning (Light)</CardTitle>
                  <TrendingDown className="h-4 w-4 text-amber-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-amber-500">{warningCount}</div>
                  <p className="text-[10px] text-amber-500/60 mt-0.5">Redaman -23.0 s/d -26.0 dBm</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs font-medium uppercase tracking-wider text-slate-400">Total ONU</CardTitle>
                  <CheckCircle className="h-4 w-4 text-emerald-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-emerald-500">{totalCount}</div>
                  <p className="text-[10px] text-slate-500 mt-0.5">Aktif terdeteksi SNMP</p>
                </CardContent>
              </Card>
            </section>

            {/* Render View based on Tab selected / ONU selected */}
            {selectedOnu ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <button 
                    onClick={handleCloseDrawer} 
                    className="flex items-center text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-wider bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg"
                  >
                    <ChevronLeft className="w-4 h-4 mr-1.5" /> Kembali ke Daftar
                  </button>
                  <Badge status={getPowerCategory(selectedOnu.rx_power)}>
                    {getPowerCategory(selectedOnu.rx_power)}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Identitas & Perangkat</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-lg font-extrabold text-slate-100 truncate">{selectedOnu.customer_name || 'Tanpa Nama'}</div>
                      {selectedOnu.sn && (
                        <div className="text-xs font-mono text-indigo-300 mt-2">SN: {selectedOnu.sn}</div>
                      )}
                      {selectedOnu.firmware_version && (
                        <div className="text-[10px] font-mono text-slate-400">Ver: {selectedOnu.firmware_version}</div>
                      )}
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Koneksi & Index</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-md font-bold text-indigo-400 truncate">{selectedOnu.olt_name}</div>
                      <p className="text-[10px] text-slate-500 mt-1 font-mono">{selectedOnu.onu_id}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Daya Sinyal Rx</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={`text-xl font-black ${getPowerCategory(selectedOnu.rx_power) === 'CRITICAL' ? 'text-red-500' : getPowerCategory(selectedOnu.rx_power) === 'WARNING' ? 'text-amber-500' : getPowerCategory(selectedOnu.rx_power) === 'OFFLINE' ? 'text-slate-500' : 'text-emerald-500'}`}>
                        {selectedOnu.rx_power === null ? 'Offline' : `${selectedOnu.rx_power} dBm`}
                      </div>
                      <p className="text-[10px] text-slate-500 mt-1">Status: {getPowerCategory(selectedOnu.rx_power)}</p>
                      {selectedOnu.last_offline_reason && getPowerCategory(selectedOnu.rx_power) === 'OFFLINE' && (
                        <p className="text-[11px] text-red-400 mt-2 font-semibold">Alasan Offline: {selectedOnu.last_offline_reason}</p>
                      )}
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Status Registrasi & Uptime</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-1">
                      {selectedOnu.alive_time && selectedOnu.alive_time !== '-' && (
                        <div className="text-xs text-slate-300">
                          Durasi Aktif: <span className="font-mono text-emerald-400 font-bold">{selectedOnu.alive_time}</span>
                        </div>
                      )}
                      {selectedOnu.last_up_time && selectedOnu.last_up_time !== '-' && (
                        <div className="text-[11px] text-slate-400 mt-1">
                          Last Up: <span className="font-mono text-slate-200">{selectedOnu.last_up_time}</span>
                        </div>
                      )}
                      {selectedOnu.last_down_time && selectedOnu.last_down_time !== '-' && (
                        <div className="text-[11px] text-slate-400">
                          Last Down: <span className="font-mono text-rose-400">{selectedOnu.last_down_time}</span>
                        </div>
                      )}
                      {!((selectedOnu.alive_time && selectedOnu.alive_time !== '-') || (selectedOnu.last_up_time && selectedOnu.last_up_time !== '-') || (selectedOnu.last_down_time && selectedOnu.last_down_time !== '-')) && (
                        <div className="text-xs text-slate-500 italic">Data tidak tersedia</div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Big Dedicated Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs uppercase tracking-widest text-slate-400 flex items-center justify-between">
                      <span>Grafik Analisis Trendline Redaman (50 Data Terakhir)</span>
                      {loadingHistory && <span className="text-indigo-400 text-[10px] lowercase animate-pulse">loading...</span>}
                    </CardTitle>
                    <CardDescription>Grafik historis fluktuasi sinyal optik (dBm) untuk ONU ini.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {formattedHistory.length > 0 ? (
                      <div className="h-80 w-full bg-slate-950/40 p-4 rounded-xl border border-slate-900/80">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={formattedHistory}>
                            <defs>
                              <linearGradient id="colorRxDetails" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                            <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} dy={10} />
                            <YAxis domain={['dataMin - 1', 'dataMax + 1']} axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 10}} dx={-10} />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #334155' }}
                              labelStyle={{ fontWeight: 'bold', color: '#f8fafc', fontSize: 11 }}
                              itemStyle={{ color: '#818cf8', fontSize: 11 }}
                            />
                            <Area type="monotone" dataKey="dbm" stroke="#6366f1" fillOpacity={1} fill="url(#colorRxDetails)" strokeWidth={2.5} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    ) : (
                      <div className="h-60 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
                        {loadingHistory ? 'Mengambil data...' : 'Tidak ada data riwayat.'}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Log Raw Table for this ONU */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs uppercase tracking-widest text-slate-400">Log Pengukuran Riwayat</CardTitle>
                    <CardDescription>Daftar log data redaman historis untuk pemantauan detail.</CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b border-slate-800 bg-slate-900/30">
                            <th className="px-6 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Waktu Pengecekan</th>
                            <th className="px-6 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Rx Power (dBm)</th>
                            <th className="px-6 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/40">
                          {selectedOnuHistory.slice().reverse().map((h, i) => (
                            <tr key={i} className="hover:bg-slate-900/20">
                              <td className="px-6 py-3 text-xs text-slate-300">{h.timestamp}</td>
                              <td className="px-6 py-3 text-xs font-semibold text-slate-100">{h.rx_power === null ? 'Offline' : `${h.rx_power} dBm`}</td>
                              <td className="px-6 py-3 text-xs">
                                <Badge status={getPowerCategory(h.rx_power)}>
                                  {getPowerCategory(h.rx_power)}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : activeTab === 'OVERVIEW' ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Ratio Status Donut/Pie Chart */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-xs uppercase tracking-widest text-slate-400">Status Kesehatan Sinyal</CardTitle>
                    <CardDescription>Rasio persentase status ONU yang terpantau pada jaringan saat ini.</CardDescription>
                  </CardHeader>
                  <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
                    <div className="h-48 flex justify-center">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={3}
                            dataKey="value"
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#090d16', border: '1px solid #1e293b', borderRadius: '8px' }}
                            itemStyle={{ fontSize: 12, color: '#e2e8f0' }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                          <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
                          Normal
                        </div>
                        <span className="text-xl font-extrabold text-slate-200">
                          {normalCount} <span className="text-[10px] text-slate-500 font-normal">({totalCount ? Math.round((normalCount/totalCount)*100) : 0}%)</span>
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                          <span className="w-2 h-2 rounded-full bg-amber-500 mr-2"></span>
                          Warning
                        </div>
                        <span className="text-xl font-extrabold text-slate-200">
                          {warningCount} <span className="text-[10px] text-slate-500 font-normal">({totalCount ? Math.round((warningCount/totalCount)*100) : 0}%)</span>
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                          <span className="w-2 h-2 rounded-full bg-red-500 mr-2 animate-pulse"></span>
                          Kritis
                        </div>
                        <span className="text-xl font-extrabold text-slate-200">
                          {criticalCount} <span className="text-[10px] text-slate-500 font-normal">({totalCount ? Math.round((criticalCount/totalCount)*100) : 0}%)</span>
                        </span>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                          <span className="w-2 h-2 rounded-full bg-slate-500 mr-2"></span>
                          Offline
                        </div>
                        <span className="text-xl font-extrabold text-slate-200">
                          {offlineCount} <span className="text-[10px] text-slate-500 font-normal">({totalCount ? Math.round((offlineCount/totalCount)*100) : 0}%)</span>
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* OLT Status List */}
                <Card className="flex flex-col justify-between">
                  <CardHeader>
                    <CardTitle className="text-xs uppercase tracking-widest text-slate-400">Metrik OLT Aktif</CardTitle>
                    <CardDescription>Beban total & jumlah issue pada setiap OLT.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4 max-h-[190px] overflow-y-auto pr-1 flex-1">
                    {olts.map((olt, idx) => {
                      const oltOnus = attenuations.filter(a => a.olt_name === olt.name);
                      const oltIssues = oltOnus.filter(a => getPowerCategory(a.rx_power) === 'CRITICAL' || getPowerCategory(a.rx_power) === 'WARNING').length;
                      
                      return (
                        <div key={idx} className="flex items-center justify-between border-b border-slate-800/60 pb-2.5">
                          <div className="space-y-0.5">
                            <span className="text-xs font-bold text-slate-100 block">{olt.name}</span>
                            <span className="text-[9px] font-bold text-slate-500 uppercase">{olt.brand} · {olt.ip_port}</span>
                          </div>
                          <div className="text-right">
                            <span className={`text-xs font-bold ${oltIssues > 0 ? 'text-amber-500' : 'text-emerald-500'}`}>
                              {oltIssues} Bermasalah
                            </span>
                            <span className="text-[9px] text-slate-500 block font-medium">dari {oltOnus.length} ONU</span>
                          </div>
                        </div>
                      );
                    })}
                  </CardContent>
                  <div className="px-6 py-4 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500 font-bold uppercase tracking-wider shrink-0">
                    <span>SNMP Version: <b>v1 & v2c</b></span>
                    <span>NOC Patrol: <b>Aktif</b></span>
                  </div>
                </Card>
                
              </div>
            ) : activeTab === 'DATABASE' ? (
              /* Live Database View */
              <Card className="overflow-hidden">
                <CardHeader className="bg-slate-900/10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <CardTitle className="text-xs uppercase tracking-widest text-slate-400">Database Log Attenuation</CardTitle>
                    <CardDescription>
                      Menampilkan data log dari patroli SNMP. Klik pada baris untuk menganalisis grafik riwayat.
                    </CardDescription>
                  </div>
                  
                  {/* Filter & Sort Controls */}
                  <div className="flex flex-wrap items-center gap-3">
                    {/* OLT Filter Dropdown */}
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">OLT:</span>
                      <select 
                        value={selectedOlt} 
                        onChange={e => setSelectedOlt(e.target.value)}
                        className="bg-slate-950 border border-slate-800 rounded-lg text-xs px-2.5 py-1.5 text-slate-350 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none cursor-pointer"
                      >
                        <option value="ALL">Semua OLT</option>
                        {olts.map((olt) => (
                          <option key={olt.id} value={olt.name}>{olt.name}</option>
                        ))}
                      </select>
                    </div>

                    {/* Separate Offline Toggle */}
                    <button 
                      onClick={() => setSeparateOffline(!separateOffline)}
                      className={`flex items-center gap-2 text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition-all ${
                        separateOffline 
                          ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20 shadow-sm' 
                          : 'bg-slate-950 text-slate-500 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${separateOffline ? 'bg-indigo-400' : 'bg-slate-650'}`}></span>
                      Pisahkan Offline ke Bawah
                    </button>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 bg-slate-900/30">
                          <th 
                            onClick={() => handleSort('olt_name')}
                            className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer select-none hover:text-slate-200 transition-colors"
                          >
                            <div className="flex items-center gap-1.5">
                              OLT
                              {renderSortIcon('olt_name')}
                            </div>
                          </th>
                          <th 
                            onClick={() => handleSort('onu_id')}
                            className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer select-none hover:text-slate-200 transition-colors"
                          >
                            <div className="flex items-center gap-1.5">
                              ONU ID
                              {renderSortIcon('onu_id')}
                            </div>
                          </th>
                          <th 
                            onClick={() => handleSort('customer_name')}
                            className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer select-none hover:text-slate-200 transition-colors"
                          >
                            <div className="flex items-center gap-1.5">
                              Nama Pelanggan
                              {renderSortIcon('customer_name')}
                            </div>
                          </th>
                          <th 
                            onClick={() => handleSort('rx_power')}
                            className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer select-none hover:text-slate-200 transition-colors"
                          >
                            <div className="flex items-center gap-1.5">
                              Rx Power
                              {renderSortIcon('rx_power')}
                            </div>
                          </th>
                          <th 
                            onClick={() => handleSort('timestamp')}
                            className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer select-none hover:text-slate-200 transition-colors"
                          >
                            <div className="flex items-center gap-1.5">
                              Waktu Update
                              {renderSortIcon('timestamp')}
                            </div>
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/40">
                        {paginatedData.map((row, idx) => {
                          const status = getPowerCategory(row.rx_power);
                          const isSelected = selectedOnu && selectedOnu.onu_id === row.onu_id;

                          return (
                            <tr 
                              key={idx} 
                              onClick={() => handleSelectOnu(row)}
                              className={`cursor-pointer hover:bg-slate-900/40 transition-colors duration-150 ${
                                isSelected ? 'bg-indigo-600/10 border-l-2 border-l-indigo-500 bg-slate-900/60' : ''
                              }`}
                            >
                              <td className="px-6 py-3.5 text-xs font-semibold text-slate-300">
                                {row.olt_name}
                              </td>
                              <td className="px-6 py-3.5 text-xs text-slate-450 font-mono">
                                {row.onu_id}
                              </td>
                              <td className="px-6 py-3.5 text-xs font-bold text-slate-100">
                                <div className="truncate max-w-[150px] sm:max-w-[200px]" title={row.customer_name || 'Tanpa Nama'}>
                                  {row.customer_name || <span className="text-slate-650 font-normal italic">Tanpa Nama</span>}
                                </div>
                                {(row.sn || row.firmware_version) && (
                                  <div className="text-[9px] font-mono font-normal text-slate-500 mt-0.5 truncate max-w-[150px]">
                                    {row.sn && <span>{row.sn}</span>} {row.firmware_version && <span className="opacity-70">| {row.firmware_version}</span>}
                                  </div>
                                )}
                              </td>
                              <td className="px-6 py-3.5 text-xs">
                                <Badge status={status}>
                                  {row.rx_power === null ? 'Offline' : `${row.rx_power} dBm`}
                                </Badge>
                                {row.last_offline_reason && status === 'OFFLINE' && (
                                  <div className="text-[10px] text-red-400 mt-1 truncate max-w-[150px]" title={row.last_offline_reason}>
                                    {row.last_offline_reason}
                                  </div>
                                )}
                              </td>
                              <td className="px-6 py-3.5 text-xs text-slate-500">
                                {row.timestamp}
                              </td>
                            </tr>
                          );
                        })}

                        {filteredData.length === 0 && (
                          <tr>
                            <td colSpan={5} className="px-6 py-12 text-center text-slate-500 text-xs">
                              Tidak ada data yang sesuai filter / pencarian.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination Footer */}
                  <div className="px-6 py-4 border-t border-slate-800 bg-slate-900/10 flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      Menampilkan <b className="text-slate-300">{startIndex + 1}</b> - <b className="text-slate-300">{Math.min(startIndex + itemsPerPage, filteredData.length)}</b> dari <b className="text-slate-300">{filteredData.length}</b> pelanggan
                    </span>
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        disabled={currentPage === 1}
                        className="p-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-white disabled:opacity-40 transition-all"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <span className="text-xs font-bold text-slate-400">
                        {currentPage} / {totalPages}
                      </span>
                      <button 
                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                        disabled={currentPage === totalPages}
                        className="p-1.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-white disabled:opacity-40 transition-all"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : activeTab === 'STATS' ? (
              /* STATS Tab: Analisis & Statistik NOC */
              <div className="space-y-8 animate-in fade-in duration-200">
                {/* Traffic Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Total Unduhan Hari Ini</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-black text-indigo-400">
                        {formatBytes(trafficStats.today?.total_download || 0)}
                      </div>
                      <p className="text-[10px] text-slate-500 mt-1">Konsumsi bandwidth download hari ini</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Total Unggahan Hari Ini</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-black text-emerald-400">
                        {formatBytes(trafficStats.today?.total_upload || 0)}
                      </div>
                      <p className="text-[10px] text-slate-500 mt-1">Konsumsi bandwidth upload hari ini</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-xs uppercase tracking-wider text-slate-400">Kasus Flapping (24 Jam)</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-black text-rose-500">
                        {flappingStats.length} <span className="text-xs font-normal text-slate-500">pelanggan</span>
                      </div>
                      <p className="text-[10px] text-rose-500/60 mt-1">Mengalami pemutusan koneksi berulang</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Side-by-Side Statistics Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Top 10 Spenders list */}
                  <Card className="flex flex-col">
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-widest text-slate-400 flex items-center justify-between">
                        <span>Top 10 Bandwidth Spenders (7 Hari)</span>
                        <TrendingDown className="w-4 h-4 text-indigo-400" />
                      </CardTitle>
                      <CardDescription>Peringkat pelanggan dengan total download terbakar tertinggi.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 space-y-4 max-h-[350px] overflow-y-auto pr-1">
                      {trafficStats.top_spenders?.length > 0 ? (
                        trafficStats.top_spenders.map((user: any, idx: number) => {
                          const maxDownload = trafficStats.top_spenders[0]?.total_download || 1;
                          const percent = Math.round((user.total_download / maxDownload) * 100) || 1;
                          return (
                            <div key={idx} className="space-y-1.5 border-b border-slate-900 pb-3 last:border-0 last:pb-0">
                              <div className="flex justify-between items-center text-xs">
                                <span className="font-bold text-slate-100 truncate max-w-[200px]">
                                  {idx + 1}. {user.customer_name}
                                </span>
                                <span className="font-mono text-indigo-300 font-semibold">
                                  {formatBytes(user.total_download)}
                                </span>
                              </div>
                              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                                <span>Secret: {user.pppoe_username}</span>
                                <span>Upload: {formatBytes(user.total_upload)}</span>
                              </div>
                              <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-900/50 mt-1">
                                <div 
                                  className="bg-gradient-to-r from-indigo-600 to-indigo-400 h-full rounded-full transition-all duration-300"
                                  style={{ width: `${percent}%` }}
                                ></div>
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className="h-full flex items-center justify-center text-xs text-slate-500 italic py-12">
                          Belum ada data penggunaan bandwidth terkumpul.
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Flapping Users list */}
                  <Card className="flex flex-col">
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-widest text-slate-400 flex items-center justify-between">
                        <span>Daftar Pelanggan Flapping (24 Jam)</span>
                        <AlertTriangle className="w-4 h-4 text-rose-500 animate-pulse" />
                      </CardTitle>
                      <CardDescription>Pelanggan dengan tingkat diskoneksi tertinggi (flapping).</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 p-0 overflow-hidden">
                      <div className="overflow-x-auto max-h-[350px] overflow-y-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="border-b border-slate-800 bg-slate-900/30">
                              <th className="px-4 py-2.5 text-[9px] font-bold text-slate-400 uppercase tracking-widest">Pelanggan</th>
                              <th className="px-4 py-2.5 text-[9px] font-bold text-slate-400 uppercase tracking-widest">OLT</th>
                              <th className="px-4 py-2.5 text-[9px] font-bold text-slate-400 uppercase tracking-widest text-right">Disconnects</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-900/50">
                            {flappingStats.length > 0 ? (
                              flappingStats.map((row: any, idx: number) => (
                                <tr key={idx} className="hover:bg-slate-900/20">
                                  <td className="px-4 py-2.5 text-xs">
                                    <div className="font-bold text-slate-200">{row.customer_name}</div>
                                    <div className="text-[10px] text-slate-500 font-mono">{row.pppoe_username}</div>
                                  </td>
                                  <td className="px-4 py-2.5 text-[10px] text-slate-400 font-mono">
                                    {row.olt_name} ({row.onu_id})
                                  </td>
                                  <td className="px-4 py-2.5 text-xs text-right">
                                    <span className={`px-2 py-0.5 rounded-full font-mono font-bold text-[10px] ${
                                      row.disconnect_count > 5 
                                        ? 'bg-red-500/10 text-red-400 border border-red-500/20 animate-pulse' 
                                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                    }`}>
                                      {row.disconnect_count} Drop
                                    </span>
                                  </td>
                                </tr>
                              ))
                            ) : (
                              <tr>
                                <td colSpan={3} className="px-4 py-12 text-center text-slate-500 text-xs italic">
                                  Tidak ada kejadian flapping terdeteksi dalam 24 jam terakhir. Kestabilan 100%!
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Connection Events Log Table */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xs uppercase tracking-widest text-slate-400 flex items-center justify-between">
                      <span>Log Riwayat Kejadian Koneksi Terpadu (Kombinasi Mikrotik & OLT)</span>
                      <Activity className="w-4 h-4 text-indigo-400" />
                    </CardTitle>
                    <CardDescription>Riwayat instan real-time deteksi pemutusan & pemulihan koneksi.</CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto max-h-[350px] overflow-y-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b border-slate-800 bg-slate-900/30">
                            <th className="px-6 py-3 text-[9px] font-bold text-slate-400 uppercase tracking-widest">Waktu Kejadian</th>
                            <th className="px-6 py-3 text-[9px] font-bold text-slate-400 uppercase tracking-widest">Pelanggan / Secret</th>
                            <th className="px-6 py-3 text-[9px] font-bold text-slate-400 uppercase tracking-widest">OLT / ONU</th>
                            <th className="px-6 py-3 text-[9px] font-bold text-slate-400 uppercase tracking-widest">Tipe Event</th>
                            <th className="px-6 py-3 text-[9px] font-bold text-slate-400 uppercase tracking-widest">Alasan / Detail OLT</th>
                            <th className="px-6 py-3 text-[9px] font-bold text-slate-400 uppercase tracking-widest text-right">Redaman</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/40">
                          {eventLogs.length > 0 ? (
                            eventLogs.map((log: any) => (
                              <tr key={log.id} className="hover:bg-slate-900/10 text-xs">
                                <td className="px-6 py-3 text-slate-450 font-mono">{log.timestamp}</td>
                                <td className="px-6 py-3">
                                  <div className="font-bold text-slate-200">{log.customer_name}</div>
                                  <div className="text-[10px] text-slate-500 font-mono">{log.pppoe_username}</div>
                                </td>
                                <td className="px-6 py-3 text-slate-400 font-mono">
                                  {log.olt_name} ({log.onu_id})
                                </td>
                                <td className="px-6 py-3">
                                  <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-bold ${
                                    log.event_type === 'CONNECT'
                                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                      : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                  }`}>
                                    {log.event_type === 'CONNECT' ? '🟢 CONNECT' : '🔴 DISCONNECT'}
                                  </span>
                                </td>
                                <td className="px-6 py-3 font-semibold text-slate-300">{log.reason}</td>
                                <td className="px-6 py-3 text-right font-mono font-bold">
                                  {log.rx_power !== null ? (
                                    <span className={log.rx_power < -26 ? 'text-red-400' : log.rx_power < -23 ? 'text-amber-400' : 'text-emerald-400'}>
                                      {log.rx_power} dBm
                                    </span>
                                  ) : (
                                    <span className="text-slate-600">-</span>
                                  )}
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan={6} className="px-6 py-12 text-center text-slate-500 text-xs">
                                Belum ada log kejadian koneksi tercatat.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : activeTab === 'MIKROTIK' ? (
              <MikrotikTab />
            ) : null}

          </div>

          {/* Detailed ONU Analysis is now rendered inside the main content area */}

        </div>
      </main>
    </div>
  );
}
