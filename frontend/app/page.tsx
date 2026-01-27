"use client";
import { useEffect, useState } from 'react';
import Link from 'next/link';

// --- Veri Tipleri (Interfaces) ---
interface Category {
  id: number;
  title: string;
  slug: string;
  icon_class: string;
  description: string;
}

interface Section {
  id: number;
  title: string;
  categories: Category[];
}

interface User {
  username: string;
  profile?: {
    avatar?: string;
  };
}

interface Topic {
  id: number;
  subject: string;
  views: number;
  replies_count: number;
  starter: User;
  category: Category;
}

interface HomeData {
  stats: {
    total_topics: number;
    total_posts: number;
    total_users: number;
    completed_jobs: number;
  };
  sections: Section[];
  popular_topics: Topic[];
  daily_tip: { content: string } | null;
}

// --- Ana Bileşen ---
export default function Home() {
  const [data, setData] = useState<HomeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Django API'den verileri çek
    fetch('http://127.0.0.1:8000/api/home/')
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("API Hatası:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-slate-400 gap-4">
        <i className="bi bi-exclamation-triangle text-4xl text-yellow-500"></i>
        <p>Veriler yüklenemedi. Django sunucusu (port 8000) çalışıyor mu?</p>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-4 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        
        {/* Header / Karşılama */}
        <header className="mb-10 text-center py-10">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600 mb-4">
            Analizus Forum
          </h1>
          <p className="text-slate-400 text-lg">Veri Analizi, İstatistik ve Yazılım Topluluğu</p>
        </header>

        {/* İstatistik Kartları */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <StatCard title="Konular" value={data.stats.total_topics} icon="bi-chat-text" color="text-blue-400" />
          <StatCard title="Mesajlar" value={data.stats.total_posts} icon="bi-chat-quote" color="text-green-400" />
          <StatCard title="Üyeler" value={data.stats.total_users} icon="bi-people" color="text-purple-400" />
          <StatCard title="Tamamlanan İş" value={data.stats.completed_jobs} icon="bi-check-circle" color="text-orange-400" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* SOL KOLON: Kategoriler */}
          <div className="lg:col-span-2 space-y-8">
            {data.sections.map((section) => (
              <div key={section.id} className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden shadow-lg">
                <div className="bg-slate-800 px-6 py-3 border-b border-slate-700 font-semibold text-blue-400 flex items-center gap-2">
                  <i className="bi bi-layers"></i> {section.title}
                </div>
                <div className="divide-y divide-slate-700/50">
                  {section.categories.map((cat) => (
                    <Link key={cat.id} href={`/forum/${cat.slug}`} className="block p-4 hover:bg-slate-700/30 transition group">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center text-2xl group-hover:bg-blue-500/20 group-hover:text-blue-400 transition ${cat.icon_class}`}>
                          <i className={`bi ${cat.icon_class}`}></i>
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-slate-200 group-hover:text-blue-300 transition text-lg">{cat.title}</h3>
                          <p className="text-sm text-slate-500 mt-1">{cat.description}</p>
                        </div>
                        <i className="bi bi-chevron-right text-slate-600 group-hover:translate-x-1 transition-transform"></i>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* SAĞ KOLON: Widgetlar */}
          <div className="space-y-6">
            
            {/* Popüler Konular */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5 shadow-lg">
              <h3 className="font-bold text-orange-400 mb-4 flex items-center gap-2 border-b border-slate-700 pb-2">
                <i className="bi bi-fire"></i> Popüler Konular
              </h3>
              <ul className="space-y-4">
                {data.popular_topics.map((topic, index) => (
                  <li key={topic.id} className="flex gap-3 items-start group">
                    <span className="bg-orange-500/10 text-orange-500 w-6 h-6 flex items-center justify-center rounded text-xs font-bold shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    <div>
                      <Link href={`/topic/${topic.id}`} className="text-sm font-medium text-slate-300 group-hover:text-orange-400 transition line-clamp-2">
                        {topic.subject}
                      </Link>
                      <div className="text-xs text-slate-500 flex items-center gap-3 mt-1">
                        <span className="flex items-center gap-1"><i className="bi bi-eye"></i> {topic.views}</span>
                        <span className="flex items-center gap-1"><i className="bi bi-chat"></i> {topic.replies_count}</span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            {/* Günün İpucu */}
            {data.daily_tip && (
              <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-xl border border-blue-500/30 p-5 shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 -mt-2 -mr-2 w-16 h-16 bg-blue-500/20 rounded-full blur-xl"></div>
                <h3 className="font-bold text-blue-300 mb-2 flex items-center gap-2 relative z-10">
                  <i className="bi bi-lightbulb-fill text-yellow-400"></i> Günün İpucu
                </h3>
                <p className="text-sm text-slate-300 italic relative z-10 leading-relaxed">
                  "{data.daily_tip.content}"
                </p>
              </div>
            )}

          </div>
        </div>
      </div>
    </main>
  );
}

// Yardımcı Bileşen: İstatistik Kartı
function StatCard({ title, value, icon, color }: { title: string, value: number, icon: string, color: string }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl flex items-center gap-4 hover:bg-slate-800 transition shadow-md">
      <div className={`text-3xl ${color} bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center`}>
        <i className={`bi ${icon}`}></i>
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">{title}</div>
      </div>
    </div>
  );
}
