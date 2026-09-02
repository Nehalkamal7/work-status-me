import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import FocusGrid from './components/FocusGrid';
import StageGroup from './components/StageGroup';
import WhatsAppPanel from './components/WhatsAppPanel';
import IntegrationsModal from './components/IntegrationsModal';
import WeeklyReportPanel from './components/WeeklyReportPanel';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [metrics, setMetrics] = useState({
    delayed_projects_count: 19,
    this_week_deliveries_count: 1,
    waiting_client_count: 1,
    pm_intervention_count: 1
  });
  const [todayFocusItems, setTodayFocusItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch projects & metrics from backend
  const fetchDashboardData = async () => {
    try {
      const projRes = await fetch('/api/v1/projects');
      if (projRes.ok) {
        const data = await projRes.json();
        setProjects(data);
      }

      const metricsRes = await fetch('/api/v1/projects/metrics-summary');
      if (metricsRes.ok) {
        const mData = await metricsRes.json();
        setMetrics(mData);
      }

      const focusRes = await fetch('/api/v1/projects/today-focus');
      if (focusRes.ok) {
        const fData = await focusRes.json();
        setTodayFocusItems(fData);
      }
    } catch (err) {
      console.warn("Backend API offline or initial fallback mode.", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // 60-second periodic dashboard auto-refresh
    const interval = setInterval(fetchDashboardData, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRefreshAll = async () => {
    setIsRefreshing(true);
    try {
      await fetch('/api/v1/sync/now', { method: 'POST' });
      await fetchDashboardData();
    } catch (e) {
      console.error("Sync error:", e);
    } finally {
      setTimeout(() => setIsRefreshing(false), 1000);
    }
  };

  // Seed default demo projects if list is empty
  const defaultProjects = projects.length > 0 ? projects : [
    {
      id: "1",
      external_id: "S01145 · AA2110",
      name: "تطبيق سيف الفرحان",
      status: "analysis",
      source: "ODOO + Google Sheets",
      metrics: {
        is_delayed: false,
        delay_days: 0,
        ownership_tag: "pm",
        ownership_text: "مطلوب تدخلي كـ PM"
      },
      raw_metadata: {
        stale_days: 13,
        latest_notes: "20 أغسطس · 11:58ص: تم إرسال ملف التحليل بعد التعديلات، والعمل متوقف حاليًا على مراجعة العميل وردّه."
      }
    },
    {
      id: "2",
      external_id: "AA60843",
      name: "تطبيق محمد أبو ثنين ومحمد الربيعان",
      status: "design",
      source: "Google Sheets",
      metrics: {
        is_delayed: true,
        delay_days: 34,
        ownership_tag: "team",
        ownership_text: "مع الفريق التقني/المصمم"
      },
      raw_metadata: {
        expected_delivery: "2026-11-27",
        actual_delivery: "2026-12-31",
        latest_notes: "اجتماع متابعة بخصوص التصميم"
      }
    },
    {
      id: "3",
      external_id: "S02665 · AA67663",
      name: "يور كاشير — مريم الجهني",
      status: "design",
      source: "ODOO + Google Sheets",
      metrics: {
        is_delayed: false,
        delay_days: 0,
        ownership_tag: "team",
        ownership_text: "مع الفريق التقني/المصمم"
      },
      raw_metadata: {
        stale_days: 13,
        latest_notes: "20 أغسطس · 12:09م: تم توثيق محضر الاجتماع الأخير."
      }
    },
    {
      id: "4",
      external_id: "AA60523",
      name: "فرج آل مطلق",
      status: "design",
      source: "Google Sheets",
      metrics: {
        is_delayed: false,
        delay_days: 0,
        ownership_tag: "client",
        ownership_text: "بانتظار العميل"
      },
      raw_metadata: {
        latest_notes: "تم إرسال التصميم وفي انتظار رد العميل"
      }
    },
    {
      id: "5",
      external_id: "S02338 · AA60265",
      name: "شركة أودال — تفاعلي",
      status: "programming",
      source: "ODOO + Google Sheets",
      metrics: {
        is_delayed: true,
        delay_days: 28,
        ownership_tag: "client",
        ownership_text: "بانتظار العميل"
      },
      raw_metadata: {
        stale_days: 13,
        expected_delivery: "2026-10-29",
        actual_delivery: "2026-11-26",
        latest_notes: "20 أغسطس · 10:36ص: تم اعتماد التصميم وبدأت مرحلة البرمجة بمدة تقديرية 70 يوم عمل."
      }
    },
    {
      id: "6",
      external_id: "AA63801",
      name: "تطبيق Wash Up",
      status: "programming",
      source: "Google Sheets",
      metrics: {
        is_delayed: true,
        delay_days: 32,
        ownership_tag: "team",
        ownership_text: "مع الفريق التقني/المصمم"
      },
      raw_metadata: {
        expected_delivery: "2026-09-03",
        actual_delivery: "2026-10-05",
        latest_notes: "التواصل والمتابعة على البريد"
      }
    },
    {
      id: "7",
      external_id: "S02288 · AA57068",
      name: "ReValue — تطبيق",
      status: "programming",
      source: "ODOO + Google Sheets",
      metrics: {
        is_delayed: true,
        delay_days: 36,
        ownership_tag: "team",
        ownership_text: "مع الفريق التقني/المصمم"
      },
      raw_metadata: {
        stale_days: 15,
        expected_delivery: "2026-09-27",
        actual_delivery: "2026-11-02",
        latest_notes: "18 أغسطس · 3:09م: تم إعداد بريد العمل وبيئة الاستضافة وإبلاغ الفريق."
      }
    },
    {
      id: "8",
      external_id: "2107",
      name: "تطبيق - نقلي",
      status: "programming",
      source: "Google Sheets",
      metrics: {
        is_delayed: true,
        delay_days: 88,
        ownership_tag: "team",
        ownership_text: "مع الفريق التقني/المصمم"
      },
      raw_metadata: {
        expected_delivery: "2026-09-23",
        actual_delivery: "2026-12-20",
        latest_notes: "المشروع مستقر ولا توجد ملاحظة عاجلة مسجلة في الشيت."
      }
    },
    {
      id: "9",
      external_id: "AA58377",
      name: "تطبيق أنعام مكة",
      status: "programming",
      source: "Google Sheets",
      metrics: {
        is_delayed: true,
        delay_days: 18,
        ownership_tag: "client",
        ownership_text: "بانتظار العميل"
      },
      raw_metadata: {
        expected_delivery: "2026-08-30",
        actual_delivery: "2026-09-17",
        latest_notes: "تم اعتماد التصميم وبدء البرمجة"
      }
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header & Metric Navigation */}
      <Header
        metrics={metrics}
        isRefreshing={isRefreshing}
        onRefreshAll={handleRefreshAll}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 py-6">
        {activeTab === 'dashboard' && (
          <>
            <FocusGrid
              items={todayFocusItems}
              onSelectProject={(item) => setSearchQuery(item.name)}
            />
            <StageGroup
              projects={defaultProjects}
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              activeFilter={activeFilter}
              setActiveFilter={setActiveFilter}
            />
          </>
        )}

        {activeTab === 'whatsapp' && <WhatsAppPanel />}

        {activeTab === 'weekly' && <WeeklyReportPanel projects={defaultProjects} />}

        {activeTab === 'settings' && <IntegrationsModal />}
      </main>

      {/* Corporate Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-2">
          <span>لوحة قرارات وتكامن المشروعات المؤسسية © 2026 Enterprise Intelligence Platform</span>
          <span className="font-mono text-[11px] text-slate-600">FastAPI Async + LiteLLM + Manifest V3</span>
        </div>
      </footer>
    </div>
  );
}
