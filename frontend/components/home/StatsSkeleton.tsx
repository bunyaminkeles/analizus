// /frontend/components/home/StatsSkeleton.tsx

export default function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-slate-700 animate-pulse"></div>
          <div className="flex-1 space-y-2">
            <div className="h-6 bg-slate-700 rounded-md w-3/4 animate-pulse"></div>
            <div className="h-4 bg-slate-700 rounded-md w-1/2 animate-pulse"></div>
          </div>
        </div>
      ))}
    </div>
  );
}
