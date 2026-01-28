// /frontend/components/home/Stats.tsx
import StatCard from './StatCard';

interface StatsProps {
  stats: {
    total_topics: number;
    total_posts: number;
    total_users: number;
    completed_jobs: number;
  };
}

export default function Stats({ stats }: StatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
      <StatCard title="Konular" value={stats.total_topics} icon="bi-chat-text" color="text-blue-400" />
      <StatCard title="Mesajlar" value={stats.total_posts} icon="bi-chat-quote" color="text-green-400" />
      <StatCard title="Üyeler" value={stats.total_users} icon="bi-people" color="text-purple-400" />
      <StatCard title="Tamamlanan İş" value={stats.completed_jobs} icon="bi-check-circle" color="text-orange-400" />
    </div>
  );
}
