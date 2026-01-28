// /frontend/lib/api.ts

export interface Category {
  id: number;
  title: string;
  slug: string;
  icon_class: string;
  description: string;
}

export interface Section {
  id: number;
  title: string;
  categories: Category[];
}

export interface Topic {
  id: number;
  subject: string;
  views: number;
  replies_count: number;
  starter: { username: string };
  category: Category;
}

export interface HomeData {
  stats: {
    total_topics: number;
    total_posts: number;
    total_users: number;
    completed_jobs: number;
  };
  sections: Section[];
  popular_topics: Topic[];
  daily_tip: { content: string } | null;
}

export async function getHomeData(): Promise<HomeData | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/home/`, { cache: 'no-store' });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error(`API Hatası (HTTP ${res.status}):`, errorText);
      return null;
    }
    
    const data = await res.json();
    return data;
  } catch (err) {
    console.error("Fetch Hatası:", err);
    return null;
  }
}
