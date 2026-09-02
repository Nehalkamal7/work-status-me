import React from 'react';
import { ArrowLeft, Target, AlertCircle } from 'lucide-react';

export default function FocusGrid({ items, onSelectProject }) {
  const displayItems = items && items.length > 0 ? items : [
    { rank: 1, name: "شركة أودال — تفاعلي", ownership_text: "بانتظار العميل", is_delayed: true, delay_days: 28 },
    { rank: 2, name: "تطبيق Wash Up", ownership_text: "مع الفريق التقني/المصمم", is_delayed: true, delay_days: 32 },
    { rank: 3, name: "شركة ازدهار الأفق — تطبيق", ownership_text: "اختبار ومراجعة داخلي", is_delayed: true, delay_days: 15 },
    { rank: 4, name: "SAST — تطبيق وموقع", ownership_text: "مع الفريق التقني/المصمم", is_delayed: true, delay_days: 20 },
    { rank: 5, name: "ReValue — تطبيق", ownership_text: "مع الفريق التقني/المصمم", is_delayed: true, delay_days: 36 }
  ];

  return (
    <section className="my-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-[11px] font-extrabold text-indigo-400 tracking-wider uppercase bg-indigo-950/80 border border-indigo-800/50 px-2.5 py-0.5 rounded">
            تركيز اليوم
          </span>
          <h2 className="text-xl font-bold text-white mt-1">أهم 5 مشروعات تحتاج قرارًا</h2>
        </div>
        <span className="text-xs text-slate-400">مرتبة بالتأخير والعوائق وفترة التوقف</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {displayItems.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectProject && onSelectProject(item)}
            className="bg-slate-900 border border-slate-800 hover:border-indigo-600/80 p-3.5 rounded-xl text-right flex items-center justify-between group transition duration-200 shadow-sm hover:shadow-indigo-500/10"
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <span className="w-7 h-7 flex-shrink-0 flex items-center justify-center bg-slate-800 group-hover:bg-indigo-600 text-slate-300 group-hover:text-white font-bold text-xs rounded-lg transition">
                {item.rank || idx + 1}
              </span>
              <div className="truncate">
                <h3 className="text-xs font-bold text-slate-100 group-hover:text-indigo-300 truncate transition">
                  {item.name}
                </h3>
                <p className="text-[11px] text-slate-400 truncate mt-0.5">
                  {item.ownership_text} {item.is_delayed ? '· متأخر' : ''}
                </p>
              </div>
            </div>
            <ArrowLeft className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 group-hover:-translate-x-1 transition flex-shrink-0 mr-1" />
          </button>
        ))}
      </div>
    </section>
  );
}
