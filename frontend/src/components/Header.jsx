import React from 'react';
import { RefreshCw, Clock, AlertTriangle, CheckCircle, UserCheck, Layers, Database, ShieldAlert, Cpu } from 'lucide-react';

export default function Header({ metrics, isRefreshing, onRefreshAll, activeTab, setActiveTab }) {
  return (
    <header className="hero-gradient border-b border-slate-800 pb-6 pt-6 px-4 sm:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Top Eyebrow & Nav Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-2 text-xs font-semibold tracking-wider text-indigo-400 uppercase bg-indigo-950/60 px-3 py-1 rounded-full border border-indigo-800/50">
            <Cpu className="w-3.5 h-3.5" />
            <span>Action-Driven · Google Sheets + Odoo + WhatsApp مباشر</span>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3 py-1.5 rounded-md font-medium transition ${activeTab === 'dashboard' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
            >
              لوحة المشاريع والقرارات
            </button>
            <button
              onClick={() => setActiveTab('whatsapp')}
              className={`px-3 py-1.5 rounded-md font-medium transition ${activeTab === 'whatsapp' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
            >
              مستجدات الواتساب والذكاء الاصطناعي
            </button>
            <button
              onClick={() => setActiveTab('weekly')}
              className={`px-3 py-1.5 rounded-md font-medium transition ${activeTab === 'weekly' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
            >
              التقرير الأسبوعي
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`px-3 py-1.5 rounded-md font-medium transition ${activeTab === 'settings' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
            >
              إعدادات الربط والرخص
            </button>
          </div>
        </div>

        {/* Title & Live Status */}
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">لوحة قرارات مشروعات نهال</h1>
            <p className="text-sm text-slate-400 mt-1">ما يحتاج إجراء اليوم أولًا، مع تحديد صاحب الخطوة وصحة المواعيد تلقائيًا.</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-900/80 text-emerald-400 border border-emerald-900/40 px-3 py-1.5 rounded-lg text-xs font-medium">
            <span className="pulse-dot"></span>
            <span>تحديث تلقائي كل دقيقة</span>
          </div>
        </div>

        {/* Unified Sync Action Bar */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 mb-6 flex flex-wrap items-center justify-between gap-4 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-950/70 border border-indigo-800/50 rounded-lg text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">اتصال مباشر موحّد</span>
                <span className="text-[10px] bg-emerald-950 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-800/40 font-mono">LIVE</span>
              </div>
              <h2 className="text-sm font-bold text-slate-100">Odoo + Google Sheets + WhatsApp</h2>
              <p className="text-xs text-slate-400">المصادر الثلاثة مباشرة — تحديث تلقائي كل 60 ثانية</p>
            </div>
          </div>

          <button
            onClick={onRefreshAll}
            disabled={isRefreshing}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-950 disabled:text-slate-500 text-white text-xs font-bold px-4 py-2.5 rounded-lg transition shadow-md hover:shadow-indigo-500/20 active:scale-95"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'جاري تحديث المصادر…' : 'تحديث الكل الآن'}</span>
          </button>
        </div>

        {/* Action Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-slate-700 transition">
            <span className="text-xs font-semibold text-slate-400">المشاريع المتأخرة</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-2xl font-black text-rose-400">{metrics.delayed_projects_count || 19}</span>
              <AlertTriangle className="w-4 h-4 text-rose-500/80" />
            </div>
            <span className="text-[11px] text-slate-500 mt-1">تجاوزت التاريخ المتوقع</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-slate-700 transition">
            <span className="text-xs font-semibold text-slate-400">تسليمات هذا الأسبوع</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-2xl font-black text-emerald-400">{metrics.this_week_deliveries_count || 1}</span>
              <CheckCircle className="w-4 h-4 text-emerald-500/80" />
            </div>
            <span className="text-[11px] text-slate-500 mt-1">خلال 7 أيام</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex flex-col justify-between hover:border-slate-700 transition">
            <span className="text-xs font-semibold text-slate-400">انتظار العميل +5 أيام</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-2xl font-black text-amber-400">{metrics.waiting_client_count || 1}</span>
              <UserCheck className="w-4 h-4 text-amber-500/80" />
            </div>
            <span className="text-[11px] text-slate-500 mt-1">تحتاج تذكير متابعة</span>
          </div>

          <div className="bg-rose-950/20 border border-rose-900/40 p-4 rounded-xl flex flex-col justify-between hover:border-rose-800/60 transition">
            <span className="text-xs font-semibold text-rose-300">مطلوب تدخلي كـ PM</span>
            <div className="flex items-baseline justify-between mt-2">
              <span className="text-2xl font-black text-rose-400">{metrics.pm_intervention_count || 1}</span>
              <ShieldAlert className="w-4 h-4 text-rose-400" />
            </div>
            <span className="text-[11px] text-rose-400/80 mt-1">إجراء مباشر مطلوب</span>
          </div>
        </div>
      </div>
    </header>
  );
}
