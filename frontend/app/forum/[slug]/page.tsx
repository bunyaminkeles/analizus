import Link from 'next/link';
import { notFound } from 'next/navigation';

interface Category {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon_class: string;
}

interface User {
  username: string;
  profile?: {
    avatar?: string;
    rank?: string;
  };
}

interface Topic {
  id: number;
  subject: string;
  views: number;
  replies_count: number;
  created_at: string;
  starter: User;
  is_pinned: boolean;
  is_closed: boolean;
}

interface CategoryData {
  category: Category;
  topics: Topic[];
}

async function getCategoryData(slug: string): Promise<CategoryData> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  const res = await fetch(`${baseUrl}/api/forum/${slug}/`, { cache: 'no-store' });

  if (!res.ok) {
    if (res.status === 404) {
      notFound();
    }
    throw new Error(`Failed to fetch category data: ${res.status}`);
  }

  return res.json();
}


export default async function CategoryPage({ params }: { params: { slug: string } }) {
  const resolvedParams = await params;
  const data = await getCategoryData(resolvedParams.slug);

  return (
    <div className="min-h-screen p-4 md:p-8 font-sans pb-20">
      <div className="max-w-6xl mx-auto">
        
        {/* Kategori Başlığı */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-8 mb-8 border border-slate-700 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>
            
            <div className="flex items-center gap-6 relative z-10">
                <div className="w-20 h-20 bg-slate-700/50 rounded-2xl flex items-center justify-center text-4xl text-blue-400 shadow-inner border border-slate-600">
                    <i className={`bi ${data.category.icon_class}`}></i>
                </div>
                <div>
                    <div className="flex items-center gap-2 text-sm text-slate-400 mb-1">
                        <Link href="/" className="hover:text-white transition">Forum</Link>
                        <i className="bi bi-chevron-right text-xs"></i>
                        <span>Kategori</span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">{data.category.title}</h1>
                    <p className="text-slate-400 text-lg max-w-2xl">{data.category.description}</p>
                </div>
            </div>
        </div>

        {/* Konu Listesi */}
        <div className="bg-slate-800/30 rounded-xl border border-slate-700/50 overflow-hidden backdrop-blur-sm">
            <div className="px-6 py-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/50">
                <h2 className="font-semibold text-slate-200">Konular</h2>
                <span className="text-sm text-slate-500">{data.topics.length} konu bulundu</span>
            </div>
            
            <div className="divide-y divide-slate-700/50">
                {data.topics.length === 0 ? (
                    <div className="p-8 text-center text-slate-500">
                        Bu kategoride henüz konu açılmamış.
                    </div>
                ) : (
                    data.topics.map((topic) => (
                        <div key={topic.id} className="p-4 md:p-5 hover:bg-slate-700/30 transition group flex items-start gap-4">
                            {/* Sol İkon/Avatar */}
                            <div className="shrink-0 pt-1">
                                {topic.starter.profile?.avatar ? (
                                    <img src={`${process.env.NEXT_PUBLIC_API_URL}${topic.starter.profile.avatar}`} className="w-10 h-10 rounded-full object-cover border border-slate-600" alt={topic.starter.username} />
                                ) : (
                                    <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-400 font-bold border border-slate-600">
                                        {topic.starter.username[0].toUpperCase()}
                                    </div>
                                )}
                            </div>

                            {/* İçerik */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    {topic.is_pinned && <span className="bg-orange-500/10 text-orange-400 text-[10px] px-2 py-0.5 rounded border border-orange-500/20 font-medium"><i className="bi bi-pin-angle-fill mr-1"></i>Sabit</span>}
                                    {topic.is_closed && <span className="bg-red-500/10 text-red-400 text-[10px] px-2 py-0.5 rounded border border-red-500/20 font-medium"><i className="bi bi-lock-fill mr-1"></i>Kilitli</span>}
                                    <Link href={`/topic/${topic.id}`} className="text-lg font-semibold text-slate-200 group-hover:text-blue-400 transition truncate block">
                                        {topic.subject}
                                    </Link>
                                </div>
                                <div className="flex items-center gap-4 text-xs text-slate-500">
                                    <span className="flex items-center gap-1"><i className="bi bi-person"></i> {topic.starter.username}</span>
                                    <span className="flex items-center gap-1"><i className="bi bi-clock"></i> {new Date(topic.created_at).toLocaleDateString('tr-TR')}</span>
                                </div>
                            </div>

                            {/* İstatistikler (Sağ Taraf) */}
                            <div className="hidden md:flex items-center gap-6 text-slate-400 shrink-0 px-4">
                                <div className="text-center min-w-[60px]">
                                    <div className="text-lg font-bold text-slate-300">{topic.replies_count}</div>
                                    <div className="text-[10px] uppercase tracking-wider">Cevap</div>
                                </div>
                                <div className="text-center min-w-[60px]">
                                    <div className="text-lg font-bold text-slate-300">{topic.views}</div>
                                    <div className="text-[10px] uppercase tracking-wider">Gör.</div>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
      </div>
    </div>
  );
}