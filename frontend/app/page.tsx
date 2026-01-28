// /frontend/app/page.tsx
import Header from '@/components/home/Header';
import Stats from '@/components/home/Stats';
import CategoryList from '@/components/home/CategoryList';
import PopularTopics from '@/components/home/PopularTopics';
import DailyTip from '@/components/home/DailyTip';
import { getHomeData } from '@/lib/api';

// Ana Sayfa Bileşeni
export default async function Home() {
  const data = await getHomeData();

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-slate-400 gap-4">
        <i className="bi bi-exclamation-triangle text-4xl text-yellow-500"></i>
        <p>Veriler yüklenemedi.</p>
        <p className="text-sm text-slate-500">API sunucusunun çalıştığından ve ulaşılabilir olduğundan emin olun.</p>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-4 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <Header />
        <Stats stats={data.stats} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <CategoryList sections={data.sections} />
          <div className="space-y-6">
            <PopularTopics topics={data.popular_topics} />
            <DailyTip tip={data.daily_tip} />
          </div>
        </div>
      </div>
    </main>
  );
}
