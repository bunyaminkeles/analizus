// /frontend/components/home/PopularTopics.tsx
import Link from 'next/link';

interface Topic {
  id: number;
  subject: string;
  views: number;
  replies_count: number;
}

interface PopularTopicsProps {
  topics: Topic[];
}

export default function PopularTopics({ topics }: PopularTopicsProps) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5 shadow-lg transition-shadow duration-300 hover:shadow-xl hover:shadow-orange-500/20">
      <h3 className="font-bold text-orange-400 mb-4 flex items-center gap-2 border-b border-slate-700 pb-2">
        <i className="bi bi-fire"></i> Popüler Konular
      </h3>
      <ul className="space-y-4">
        {topics.map((topic, index) => (
          <li key={topic.id} className="flex gap-3 items-start group">
            <span className="bg-orange-500/10 text-orange-400 w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold shrink-0 mt-0.5 transition-colors duration-300 group-hover:bg-orange-500 group-hover:text-white">
              {index + 1}
            </span>
            <div>
              <Link href={`/topic/${topic.id}`} className="text-sm font-medium text-slate-300 transition-colors duration-300 hover:text-orange-400 line-clamp-2">
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
  );
}
