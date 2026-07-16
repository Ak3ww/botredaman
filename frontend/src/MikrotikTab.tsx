import { useEffect, useState } from 'react';
import axios from 'axios';
import { Server, Activity, WifiOff, RefreshCw, CheckCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

function Card({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={`bg-slate-900/40 backdrop-blur-sm rounded-xl border border-slate-800/80 shadow-md transition-all duration-200 hover:border-slate-700/60 ${className}`}>
      {children}
    </div>
  );
}

function CardContent({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  return <div className={`p-6 pt-0 ${className}`}>{children}</div>;
}

export default function MikrotikTab() {
  const [mikrotikData, setMikrotikData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchMikrotikNonActive = () => {
    setLoading(true);
    axios.get(`${API_BASE}/mikrotik/non-active`)
      .then(res => {
        setMikrotikData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMikrotikNonActive();
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center tracking-tight">
            <WifiOff className="w-6 h-6 mr-3 text-indigo-400" />
            Mikrotik Non-Active Connections
          </h2>
          <p className="text-slate-400 mt-1">Daftar pelanggan (PPP Secrets) yang sedang terputus / offline dari Mikrotik</p>
        </div>
        <button
          onClick={fetchMikrotikNonActive}
          disabled={loading}
          className={`flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition-colors ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading && !mikrotikData ? (
        <Card>
          <CardContent className="py-20 flex flex-col items-center justify-center">
            <div className="w-10 h-10 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
            <p className="text-slate-400 text-lg">Mengambil data live dari Mikrotik API...</p>
          </CardContent>
        </Card>
      ) : mikrotikData ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-gradient-to-br from-slate-900 to-slate-900 border-l-4 border-l-indigo-500">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">Total Secrets</p>
                    <h3 className="text-3xl font-bold text-white mt-2">{mikrotikData.total_secrets}</h3>
                  </div>
                  <div className="p-3 bg-indigo-500/10 rounded-xl">
                    <Server className="w-8 h-8 text-indigo-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900 to-slate-900 border-l-4 border-l-emerald-500">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">Active Connections</p>
                    <h3 className="text-3xl font-bold text-white mt-2">{mikrotikData.total_active}</h3>
                  </div>
                  <div className="p-3 bg-emerald-500/10 rounded-xl">
                    <Activity className="w-8 h-8 text-emerald-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-900 to-slate-900 border-l-4 border-l-rose-500">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">Non-Active (Offline)</p>
                    <h3 className="text-3xl font-bold text-rose-400 mt-2">{mikrotikData.total_non_active}</h3>
                  </div>
                  <div className="p-3 bg-rose-500/10 rounded-xl">
                    <WifiOff className="w-8 h-8 text-rose-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <div className="overflow-x-auto rounded-xl">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-slate-900/80 text-slate-300 font-semibold uppercase tracking-wider text-xs border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Username PPP</th>
                    <th className="px-6 py-4">Profile</th>
                    <th className="px-6 py-4">Nama Pelanggan (Comment)</th>
                    <th className="px-6 py-4">Last Disconnect</th>
                    <th className="px-6 py-4">Last Logged Out</th>
                    <th className="px-6 py-4">Last MAC</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {mikrotikData.non_active_list.map((item: any) => {
                    let realName = item.comment;
                    if (realName && realName.includes('Pelanggan:')) {
                        realName = realName.split('Pelanggan:')[1].trim();
                    }
                    return (
                      <tr key={item.id} className={`hover:bg-slate-800/50 transition-colors ${item.disabled ? 'opacity-50' : ''}`}>
                        <td className="px-6 py-4 font-medium text-slate-200">
                          {item.name}
                          {item.disabled && <span className="ml-2 text-xs bg-rose-500/20 text-rose-400 px-2 py-0.5 rounded">DISABLED</span>}
                        </td>
                        <td className="px-6 py-4 text-slate-400">{item.profile}</td>
                        <td className="px-6 py-4 text-emerald-400 font-medium">{realName}</td>
                        <td className="px-6 py-4 text-rose-300">{item.last_disconnect_reason}</td>
                        <td className="px-6 py-4 text-slate-400">{item.last_logged_out}</td>
                        <td className="px-6 py-4 text-slate-500 font-mono text-xs">{item.last_caller_id}</td>
                      </tr>
                    );
                  })}
                  
                  {mikrotikData.non_active_list.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                        <div className="flex flex-col items-center justify-center">
                          <CheckCircle className="w-12 h-12 text-emerald-500/50 mb-3" />
                          <p className="text-lg font-medium text-slate-300">Semua Pelanggan Aktif!</p>
                          <p className="text-sm mt-1">Tidak ada PPP Secret yang putus koneksi.</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
