import React, { useState } from 'react';
import { Target, TrendingUp, CheckCircle, Save } from 'lucide-react';

export default function WeeklyReportPanel({ projects }) {
  const [targetPercentages, setTargetPercentages] = useState({});

  const handlePercentageChange = (id, val) => {
    setTargetPercentages(prev => ({ ...prev, [id]: val }));
  };

  const handleSaveReport = () => {
    alert('تم اعتماد وحفظ نسبة الإنجاز والهدف الأسبوعي بنجاح.');
  };

  return (
    <div className="my-8 max-w-7xl mx-auto space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">متابعة الأهداف الأسبوعية والتقدم النسبية</h2>
          <p className="text-xs text-slate-400 mt-1">تسجيل أهداف الأسبوع الحالية ومقارنتها بنسبة الإنجاز المسجلة سابقًا.</p>
        </div>
        <button
          onClick={handleSaveReport}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-5 py-2.5 rounded-xl flex items-center gap-2 transition shadow-md"
        >
          <Save className="w-4 h-4" />
          <span>حفظ التقرير الأسبوعي</span>
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-right text-xs">
          <thead>
            <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <th className="p-3.5">الكود</th>
              <th className="p-3.5">اسم المشروع</th>
              <th className="p-3.5">المرحلة</th>
              <th className="p-3.5">نسبة الإنجاز الحالية</th>
              <th className="p-3.5">الهدف الأسبوعي المطلوب (%)</th>
              <th className="p-3.5">حالة التقدم</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {projects.map((p) => (
              <tr key={p.id} className="hover:bg-slate-850/50">
                <td className="p-3.5 font-mono font-bold text-slate-400">{p.external_id || 'PROJ'}</td>
                <td className="p-3.5 font-bold text-white">{p.name}</td>
                <td className="p-3.5">
                  <span className="bg-slate-800 text-slate-300 px-2.5 py-1 rounded text-[11px]">
                    {p.status}
                  </span>
                </td>
                <td className="p-3.5">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="bg-indigo-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, p.current_progress_percentage || 45)}%` }}
                      ></div>
                    </div>
                    <span className="font-bold text-indigo-400 font-mono">{p.current_progress_percentage || 45}%</span>
                  </div>
                </td>
                <td className="p-3.5">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={targetPercentages[p.id] ?? (p.weekly_target_percentage || 60)}
                    onChange={(e) => handlePercentageChange(p.id, e.target.value)}
                    className="w-20 bg-slate-950 border border-slate-800 rounded p-1.5 text-center font-mono text-white outline-none focus:border-indigo-500"
                  />
                </td>
                <td className="p-3.5">
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>مستقر</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
