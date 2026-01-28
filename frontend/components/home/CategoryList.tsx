// /frontend/components/home/CategoryList.tsx
import Link from 'next/link';

interface Category {
  id: number;
  title: string;
  slug: string;
  icon_class: string;
  description: string;
}

interface Section {
  id: number;
  title: string;
  categories: Category[];
}

interface CategoryListProps {
  sections: Section[];
}

export default function CategoryList({ sections }: CategoryListProps) {
  return (
    <div className="lg:col-span-2 space-y-8">
      {sections.map((section) => (
        <div key={section.id} className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden shadow-lg transition-shadow duration-300 hover:shadow-xl hover:shadow-blue-500/20">
          <div className="bg-slate-800 px-6 py-3 border-b border-slate-700 font-semibold text-blue-400 flex items-center gap-2">
            <i className="bi bi-layers"></i> {section.title}
          </div>
          <div className="divide-y divide-slate-700/50">
            {section.categories.map((cat) => (
              <Link key={cat.id} href={`/forum/${cat.slug}`} className="block p-4 hover:bg-slate-700/40 transition group">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center text-2xl text-blue-400 transition-all duration-300 group-hover:bg-blue-500/20 group-hover:scale-110`}>
                    <i className={`bi ${cat.icon_class}`}></i>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-slate-200 transition-colors duration-300 group-hover:text-blue-300 text-lg">{cat.title}</h3>
                    <p className="text-sm text-slate-500 mt-1">{cat.description}</p>
                  </div>
                  <i className="bi bi-chevron-right text-slate-600 transition-transform duration-300 group-hover:translate-x-1.5"></i>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
