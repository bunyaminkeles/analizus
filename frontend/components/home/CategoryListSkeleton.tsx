// /frontend/components/home/CategoryListSkeleton.tsx

export default function CategoryListSkeleton() {
  return (
    <div className="lg:col-span-2 space-y-8">
      {[...Array(2)].map((_, i) => (
        <div key={i} className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden shadow-lg">
          <div className="bg-slate-800 px-6 py-3 border-b border-slate-700">
            <div className="h-6 bg-slate-700 rounded-md w-1/3 animate-pulse"></div>
          </div>
          <div className="divide-y divide-slate-700/50">
            {[...Array(3)].map((_, j) => (
              <div key={j} className="p-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-lg bg-slate-700 animate-pulse"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-5 bg-slate-700 rounded-md w-3/4 animate-pulse"></div>
                    <div className="h-4 bg-slate-700 rounded-md w-1/2 animate-pulse"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
