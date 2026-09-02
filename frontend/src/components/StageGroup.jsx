import React from 'react';
import ProjectCard from './ProjectCard';
import { Search } from 'lucide-react';

export default function StageGroup({
  projects,
  searchQuery,
  setSearchQuery,
  activeFilter,
  setActiveFilter
}) {
  const filterPills = [
    { id: 'all', label: 'الكل' },
    { id: 'delayed', label: 'المتأخرة فقط' },
    { id: 'client', label: 'بانتظار العميل' },
    { id: 'programming', label: 'مرحلة البرمجة' },
    { id: 'design', label: 'مرحلة التصميم' },
    { id: 'analysis', label: 'مرحلة التحليل' }
  ];

  const stages = [
    { id: 'analysis', name: 'التحليل' },
    { id: 'design', name: 'التصميم' },
    { id: 'programming', name: 'البرمجة' },
    { id: 'testing', name: 'الاختبار والمراجعة' },
    { id: 'delivery', name: 'التسليم' }
  ];

  // Filter project list
  const filteredProjects = projects.filter(p => {
    const metrics = p.metrics || {};
    
    // Search query match
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const nameMatch = p.name.toLowerCase().includes(q);
      const codeMatch = p.external_id && p.external_id.toLowerCase().includes(q);
      if (!nameMatch && !codeMatch) return false;
    }

    // Filter pill match
    if (activeFilter === 'delayed') return metrics.is_delayed;
    if (activeFilter === 'client') return metrics.ownership_tag === 'client';
    if (activeFilter === 'programming') return p.status?.toLowerCase() === 'programming';
    if (activeFilter === 'design') return p.status?.toLowerCase() === 'design';
    if (activeFilter === 'analysis') return p.status?.toLowerCase() === 'analysis';

    return true;
  });

  return (
    <section id="project-list" className="mt-8">
      {/* Section Head: Search & Title */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <span className="text-[11px] font-extrabold text-indigo-400 tracking-wider uppercase bg-indigo-950/80 border border-indigo-800/50 px-2.5 py-0.5 rounded">
            اتخاذ القرار
          </span>
          <h2 className="text-xl font-bold text-white mt-1">كل المشروعات</h2>
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute right-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="ابحث بالكود AA… أو باسم المشروع"
            className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 text-slate-100 placeholder-slate-500 pr-9 pl-4 py-2 rounded-xl text-xs outline-none transition"
          />
        </div>
      </div>

      {/* Filter Pills */}
      <div className="flex flex-wrap gap-2 mb-8">
        {filterPills.map(pill => (
          <button
            key={pill.id}
            onClick={() => setActiveFilter(pill.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition border ${
              activeFilter === pill.id
                ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
            }`}
          >
            {pill.label}
          </button>
        ))}
      </div>

      {/* Group Projects by Stages */}
      {stages.map(stage => {
        const stageProjects = filteredProjects.filter(
          p => (p.status?.toLowerCase() || 'analysis') === stage.id
        );

        if (stageProjects.length === 0 && activeFilter !== 'all') {
          return null;
        }

        return (
          <div key={stage.id} className="mb-10">
            {/* Stage Heading */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-5">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500/50"></span>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block">مرحلة العمل</span>
                  <h3 className="text-lg font-extrabold text-slate-100">{stage.name}</h3>
                </div>
              </div>
              <span className="text-xs font-bold bg-slate-900 text-indigo-400 px-3 py-1 rounded-full border border-slate-800">
                {stageProjects.length} مشروع
              </span>
            </div>

            {/* Project Grid */}
            {stageProjects.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {stageProjects.map(proj => (
                  <ProjectCard key={proj.id} project={proj} />
                ))}
              </div>
            ) : (
              <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-6 text-center text-xs text-slate-500">
                لا توجد مشاريع في مرحلة {stage.name} مطابقة للبحث أو التصفية الحالية.
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}
