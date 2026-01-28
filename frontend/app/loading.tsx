// /frontend/app/loading.tsx
import Header from '@/components/home/Header';
import StatsSkeleton from '@/components/home/StatsSkeleton';
import CategoryListSkeleton from '@/components/home/CategoryListSkeleton';
import PopularTopicsSkeleton from '@/components/home/PopularTopicsSkeleton';

export default function Loading() {
  return (
    <main className="min-h-screen p-4 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <Header />
        <StatsSkeleton />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <CategoryListSkeleton />
          <div className="space-y-6">
            <PopularTopicsSkeleton />
          </div>
        </div>
      </div>
    </main>
  );
}
