// /frontend/components/home/DailyTip.tsx

interface DailyTipProps {
  tip: {
    content: string;
  } | null;
}

export default function DailyTip({ tip }: DailyTipProps) {
  if (!tip) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-xl border border-blue-500/30 p-5 shadow-lg relative overflow-hidden">
      <div className="absolute top-0 right-0 -mt-2 -mr-2 w-16 h-16 bg-blue-500/20 rounded-full blur-xl"></div>
      <h3 className="font-bold text-blue-300 mb-2 flex items-center gap-2 relative z-10">
        <i className="bi bi-lightbulb-fill text-yellow-400"></i> Günün İpucu
      </h3>
      <p className="text-sm text-slate-300 italic relative z-10 leading-relaxed">
        "{tip.content}"
      </p>
    </div>
  );
}
