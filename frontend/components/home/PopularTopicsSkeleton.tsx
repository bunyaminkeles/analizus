// /frontend/components/home/PopularTopicsSkeleton.tsx

export default function PopularTopicsSkeleton() {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5 shadow-lg">
      <div className="h-6 bg-slate-700 rounded-md w-2/3 mb-4 animate-pulse"></div>
      <ul className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <li key={i} className="flex gap-3 items-start">
            <div className="w-6 h-6 rounded-full bg-slate-700 shrink-0 mt-0.5 animate-pulse"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-slate-700 rounded-md w-full animate-pulse"></div>
              <div className="h-3 bg-slate-700 rounded-md w-1/2 animate-pulse"></div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
