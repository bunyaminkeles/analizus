// /frontend/components/home/StatCard.tsx

interface StatCardProps {
  title: string;
  value: number;
  icon: string;
  color: string;
}

export default function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <div className={`bg-slate-800/50 border border-slate-700 p-4 rounded-xl flex items-center gap-4 transition-all duration-300 group hover:bg-slate-800 hover:scale-105 hover:border-${color.split('-')[2]}-400 shadow-lg`}>
      <div className={`text-3xl ${color} bg-slate-700/50 w-12 h-12 rounded-lg flex items-center justify-center transition-all duration-300 group-hover:bg-${color.split('-')[2]}-500/20`}>
        <i className={`bi ${icon}`}></i>
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">{title}</div>
      </div>
    </div>
  );
}
