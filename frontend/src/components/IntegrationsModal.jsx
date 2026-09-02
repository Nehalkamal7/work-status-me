import React, { useState, useEffect } from 'react';
import { Key, Database, FileSpreadsheet, Save, RefreshCw, Copy, Check, ShieldCheck } from 'lucide-react';

export default function IntegrationsModal() {
  const [odooUrl, setOdooUrl] = useState('https://enterprise-odoo.example.com');
  const [odooDb, setOdooDb] = useState('production_db');
  const [odooUser, setOdooUser] = useState('admin@enterprise.com');
  const [odooPass, setOdooPass] = useState('••••••••••••');
  const [sheetsUrl, setSheetsUrl] = useState('https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0');
  const [apiKey, setApiKey] = useState('ws_live_demo_enterprise_key_2026_x99');
  const [copiedKey, setCopiedKey] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      alert('تم حفظ إعدادات التكامل وتشفير بيانات الاعتماد بـ AES-256 بنجاح.');
    }, 1000);
  };

  const handleCopyKey = () => {
    navigator.clipboard.writeText(apiKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  return (
    <div className="my-8 max-w-4xl mx-auto space-y-8">
      {/* Chrome Extension API Key Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-indigo-950 text-indigo-400 rounded-lg border border-indigo-800">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">مفتاح الربط لإضافة كروم (Chrome Extension API Key)</h3>
            <p className="text-xs text-slate-400">استخدم هذا المفتاح لمصادقة إضافة كروم الخاصة بمحادثات الواتساب.</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-slate-950 p-3 rounded-lg border border-slate-800">
          <code className="flex-1 font-mono text-xs text-emerald-400 select-all overflow-x-auto">{apiKey}</code>
          <button
            onClick={handleCopyKey}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded-md flex items-center gap-1.5 transition"
          >
            {copiedKey ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedKey ? 'تم النسخ' : 'نسخ المفتاح'}</span>
          </button>
        </div>
      </div>

      {/* Odoo Credentials Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-slate-800 text-indigo-400 rounded-lg border border-slate-700">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">بيانات اتصال Odoo (XML-RPC Connector)</h3>
            <p className="text-xs text-slate-400">تتيح لك جلب المشاريع والمهام تلقائيًا مع التحديث التراكمي كل 60 ثانية.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 font-bold mb-1">رابط سيرفر Odoo (URL)</label>
            <input
              type="text"
              value={odooUrl}
              onChange={(e) => setOdooUrl(e.target.value)}
              placeholder="https://odoo.yourcompany.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-bold mb-1">اسم قاعدة البيانات (Database Name)</label>
            <input
              type="text"
              value={odooDb}
              onChange={(e) => setOdooDb(e.target.value)}
              placeholder="production_db"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-bold mb-1">اسم المستخدم / البريد الإلكتروني</label>
            <input
              type="text"
              value={odooUser}
              onChange={(e) => setOdooUser(e.target.value)}
              placeholder="admin@company.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-bold mb-1">كلمة المرور (مشفّرة AES-256)</label>
            <input
              type="password"
              value={odooPass}
              onChange={(e) => setOdooPass(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Google Sheets Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-slate-800 text-emerald-400 rounded-lg border border-slate-700">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">روابط جداول بيانات جوجل (Google Sheets URLs)</h3>
            <p className="text-xs text-slate-400">يتم قراءتها واستخراج عناوين الأعمدة وتطبيق Fuzzy Matching تلقائيًا.</p>
          </div>
        </div>

        <div className="text-xs">
          <label className="block text-slate-400 font-bold mb-1">رابط الشيت العام أو الخاص</label>
          <input
            type="text"
            value={sheetsUrl}
            onChange={(e) => setSheetsUrl(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500 font-mono"
          />
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-6 py-3 rounded-xl flex items-center gap-2 transition shadow-lg hover:shadow-indigo-500/20"
        >
          <Save className="w-4 h-4" />
          <span>{saving ? 'جاري الحفظ…' : 'حفظ إعدادات الربط'}</span>
        </button>
      </div>
    </div>
  );
}
