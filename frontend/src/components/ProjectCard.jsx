import React, { useState } from 'react';
import { Copy, Check, Calendar, AlertCircle, Clock, Tag } from 'lucide-react';

export default function ProjectCard({ project }) {
  const [copied, setCopied] = useState(false);

  const metrics = project.metrics || {};
  const metadata = project.raw_metadata || {};
  
  const stageNames = {
    analysis: 'التحليل',
    design: 'التصميم',
    programming: 'البرمجة',
    testing: 'الاختبار والمراجعة',
    delivery: 'التسليم',
    maintenance: 'الصيانة'
  };

  const currentStageName = stageNames[project.status?.toLowerCase()] || project.status || 'التحليل';

  const ownershipTagClass = {
    pm: 'badge-owner-pm',
    team: 'badge-owner-team',
    client: 'badge-owner-client'
  }[metrics.ownership_tag || 'team'];

  const followupText = metrics.followup_message || (
    `السلام عليكم، نود المتابعة بخصوص مشروع «${project.name}» (${project.external_id || 'AA'}). ` +
    `نرجو التكرم بموافاتنا بالرد أو الاعتماد المطلوب حتى نتمكن من استكمال الخطوة التالية وفق الجدول. شاكرين تعاونكم.`
  );

  const handleCopy = () => {
    navigator.clipboard.writeText(followupText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Checklist items
  const checklistItems = [
    { label: "اللوجو", present: metadata.logo_present || false },
    { label: "التصميم", present: metadata.design_present || false },
    { label: "التحليل", present: metadata.analysis_present || false },
    { label: "الدومين", present: metadata.domain_present || false },
    { label: "إيميل", present: metadata.email_present || false },
    { label: "الداشبورد", present: metadata.dashboard_present || false }
  ];

  return (
    <article className={`decision-card ${metrics.is_delayed ? 'is-delayed' : ''} p-5 flex flex-col justify-between`}>
      <div>
        {/* Head: Code, Name, Stage */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <span className="text-[11px] font-mono font-bold text-slate-400 block mb-1">
              {project.external_id || `PROJ_${project.id.slice(0,6)}`}
            </span>
            <h3 className="text-base font-bold text-white leading-snug">{project.name}</h3>
          </div>
          <span className="text-xs font-bold bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700">
            {currentStageName}
          </span>
        </div>

        {/* Ownership Tag Badge */}
        <div className={`inline-block text-xs font-bold px-3 py-1 rounded-md mb-4 ${ownershipTagClass}`}>
          {metrics.ownership_text || 'مع الفريق التقني/المصمم'}
        </div>

        {/* Project Checklist */}
        <div className="flex flex-wrap gap-1.5 mb-4 text-[11px] font-medium">
          {checklistItems.map((item, idx) => (
            <span
              key={idx}
              className={`px-2 py-0.5 rounded border transition ${
                item.present
                  ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                  : 'bg-slate-900 border-slate-800 text-slate-500'
              }`}
              title={`${item.label}: ${item.present ? 'موجود' : 'غير موجود في وصف Odoo'}`}
            >
              {item.label}
            </span>
          ))}
        </div>

        {/* Stale Alert if modified long ago */}
        {metadata.stale_days && (
          <div className="bg-amber-950/30 border border-amber-900/40 text-amber-400 text-xs px-3 py-1.5 rounded-lg mb-4 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            <span>لم يُحدّث منذ {metadata.stale_days} يوم</span>
          </div>
        )}

        {/* Date Grid */}
        <div className="grid grid-cols-2 gap-2 bg-slate-900/80 p-3 rounded-lg border border-slate-800 mb-3 text-xs">
          <div>
            <span className="text-[11px] text-slate-400 block">التسليم المتوقع</span>
            <b className={`font-mono text-slate-200 ${!metadata.expected_delivery ? 'text-slate-500 font-normal' : ''}`}>
              {metadata.expected_delivery || 'غير محدد'}
            </b>
          </div>
          <div>
            <span className="text-[11px] text-slate-400 block">التاريخ الفعلي</span>
            <b className={`font-mono ${metrics.is_delayed ? 'text-rose-400 font-bold' : 'text-slate-200'}`}>
              {metadata.actual_delivery || 'غير محدد'}
            </b>
          </div>
        </div>

        {/* Health Badge */}
        <div className="mb-4">
          {metrics.is_delayed ? (
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-400 bg-rose-950/40 border border-rose-900/50 px-2.5 py-1 rounded-md">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>متأخر +{metrics.delay_days} يوم</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md">
              <span>فارق المواعيد غير محدد</span>
            </span>
          )}
        </div>

        {/* Note Timeline */}
        {metadata.latest_notes && (
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-lg mb-4 text-xs">
            <span className="text-[10px] text-indigo-400 font-bold block mb-1">آخر تحديث مسجل</span>
            <p className="text-slate-300 leading-relaxed">{metadata.latest_notes}</p>
          </div>
        )}
      </div>

      {/* Ready-to-copy client follow-up box (shown when waiting for client) */}
      {metrics.ownership_tag === 'client' && (
        <div className="mt-2 pt-3 border-t border-slate-800">
          <span className="text-[11px] font-bold text-amber-400 block mb-1">رسالة المتابعة الجاهزة للعميل</span>
          <p className="text-[11px] text-slate-300 bg-slate-900 p-2.5 rounded-lg border border-slate-800 mb-2.5 leading-relaxed font-sans select-all">
            {followupText}
          </p>
          <button
            onClick={handleCopy}
            className={`w-full flex items-center justify-center gap-2 text-xs font-bold py-2 rounded-lg transition ${
              copied
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
            }`}
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>تم نسخ الرسالة بنجاح</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>نسخ رسالة متابعة</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Source Footer */}
      <div className="mt-4 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
        <span>المصدر: {project.source || 'Odoo + Google Sheets'}</span>
      </div>
    </article>
  );
}
