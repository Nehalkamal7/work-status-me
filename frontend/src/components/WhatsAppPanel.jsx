import React, { useState, useEffect } from 'react';
import { MessageSquare, Sparkles, AlertTriangle, CheckSquare, RefreshCw, Send } from 'lucide-react';

export default function WhatsAppPanel() {
  const [summaries, setSummaries] = useState([]);
  const [messages, setMessages] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('تطبيق سيف الفرحان');
  const [analyzing, setAnalyzing] = useState(false);
  const [simulatedMsg, setSimulatedMsg] = useState('');

  // Sample data fallback
  const demoSummaries = [
    {
      id: "1",
      group_name: "تطبيق سيف الفرحان",
      executive_summary: "تم إرسال النسخة التجريبية الأولى للتطبيق للمراجعة. العميل يتواصل بخصوص إضافة خاصية خيارات الدفع متعددة العملات.",
      extracted_action_items: [
        { task: "مراجعة ملف التعديلات والرد على العميل", owner: "نهال كمال (PM)", urgency: "High" },
        { task: "تعديل واجهة شاشة خيارات الدفع", owner: "فريق التصميم", urgency: "Normal" }
      ],
      identified_risks: [
        "تأخير اعتماد العميل للتصميم الأولي قد يؤخر تسليم المرحلة الحالية بـ 4 أيام."
      ],
      generated_at: new Date().toISOString()
    }
  ];

  const demoMessages = [
    { sender: "أحمد المصمم", message_text: "تم رفع التصاميم المحدثة على الفيجما للمراجعة.", timestamp: "11:45 AM" },
    { sender: "خالد المهندس", message_text: "نحن بانتظار موافقة العميل لنبدأ في ربط بوابة الدفع.", timestamp: "11:50 AM" },
    { sender: "نهال (PM)", message_text: "سأقوم بمتابعة العميل اليوم وإرسال رسالة التذكير.", timestamp: "12:05 PM" }
  ];

  const handleAnalyzeWithAI = async () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      alert("تمت معالجة محادثات المجموعة بالذكاء الاصطناعي بنجاح واستخراج قائمة المهام والمخاطر.");
    }, 1500);
  };

  const handleAddSimulatedMsg = (e) => {
    e.preventDefault();
    if (!simulatedMsg.trim()) return;
    setMessages(prev => [
      { sender: "PM / Admin", message_text: simulatedMsg, timestamp: "الآن" },
      ...prev
    ]);
    setSimulatedMsg('');
  };

  return (
    <div className="my-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-indigo-950 border border-indigo-800/60 rounded-xl text-indigo-400">
            <MessageSquare className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold text-indigo-400 uppercase tracking-wider">Chrome Extension Active</span>
              <span className="bg-emerald-950 text-emerald-400 text-[10px] px-2 py-0.5 rounded font-bold border border-emerald-800">CONNECTED</span>
            </div>
            <h2 className="text-xl font-bold text-white mt-0.5">مستجدات الواتساب وتحليلات الذكاء الاصطناعي</h2>
            <p className="text-xs text-slate-400">يلتقط إضافة كروم محادثات مجموعات العمل تلقائيًا ويقوم الذكاء الاصطناعي بتلخيصها واستخراج القرارات.</p>
          </div>
        </div>

        <button
          onClick={handleAnalyzeWithAI}
          disabled={analyzing}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-4 py-2.5 rounded-xl transition shadow-lg hover:shadow-indigo-500/25 active:scale-95"
        >
          <Sparkles className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
          <span>{analyzing ? 'جاري التحليل بواسطة LLM…' : 'تحليل المحادثات بالذكاء الاصطناعي'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: AI Summaries & Action Items */}
        <div className="lg:col-span-2 space-y-6">
          {demoSummaries.map((summary) => (
            <div key={summary.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <span>{summary.group_name}</span>
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">
                  تم التوليد: {new Date(summary.generated_at).toLocaleTimeString('ar-SA')}
                </span>
              </div>

              {/* Executive Summary */}
              <div className="mb-5">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  <span>الملخص التنفيذي للمحادثة</span>
                </h4>
                <p className="text-xs text-slate-200 bg-slate-950 p-3.5 rounded-lg border border-slate-800/80 leading-relaxed">
                  {summary.executive_summary}
                </p>
              </div>

              {/* Extracted Action Items */}
              <div className="mb-5">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <CheckSquare className="w-3.5 h-3.5 text-emerald-400" />
                  <span>الإجراءات والمهام المستخرجة (Action Items)</span>
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-right text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 bg-slate-950">
                        <th className="p-2.5">المهمة المطلوبة</th>
                        <th className="p-2.5">صاحب الخطوة / المسؤول</th>
                        <th className="p-2.5">الأولوية</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {summary.extracted_action_items.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-850/50">
                          <td className="p-2.5 text-slate-200 font-medium">{item.task}</td>
                          <td className="p-2.5 text-indigo-300 font-bold">{item.owner}</td>
                          <td className="p-2.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              item.urgency === 'High' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-slate-800 text-slate-300'
                            }`}>
                              {item.urgency}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Identified Risks */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                  <span>المخاطر والعوائق المحددة</span>
                </h4>
                <ul className="space-y-2">
                  {summary.identified_risks.map((risk, idx) => (
                    <li key={idx} className="text-xs text-rose-300 bg-rose-950/20 border border-rose-900/30 p-2.5 rounded-lg">
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* Right Column: Live Message Feed Simulation */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h3 className="text-sm font-bold text-white">سجل المحادثات الملتقطة المباشر</h3>
              <span className="text-[10px] bg-indigo-950 text-indigo-400 px-2 py-0.5 rounded border border-indigo-800 font-mono">LIVE FEED</span>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {(messages.length > 0 ? messages : demoMessages).map((msg, idx) => (
                <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-indigo-400">{msg.sender}</span>
                    <span className="text-[10px] text-slate-500">{msg.timestamp}</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">{msg.message_text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Test input simulation */}
          <form onSubmit={handleAddSimulatedMsg} className="mt-4 pt-3 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={simulatedMsg}
              onChange={(e) => setSimulatedMsg(e.target.value)}
              placeholder="اكتب رسالة تجريبية للاختبار…"
              className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
            />
            <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded-lg">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
