"use client";
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  // Sayfa yüklendiğinde tarayıcı hafızasından (localStorage) kullanıcıyı çek
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    // Çıkış yapınca her şeyi sil
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    router.push('/login');
  };

  return (
    <nav className="bg-slate-800 border-b border-slate-700 text-white sticky top-0 z-50 shadow-lg">
      <div className="max-w-6xl mx-auto px-4 h-16 flex justify-between items-center">
        {/* Logo */}
        <Link href="/" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent hover:opacity-80 transition">
          Analizus
        </Link>

        {/* Sağ Taraf: Kullanıcı Menüsü */}
        <div className="flex items-center gap-4">
          {user ? (
            // --- GİRİŞ YAPMIŞ KULLANICI ---
            <div className="flex items-center gap-3 bg-slate-700/50 py-1 px-3 rounded-full border border-slate-600">
              {user.profile?.avatar ? (
                 <img src={user.profile.avatar} alt={user.username} className="w-8 h-8 rounded-full object-cover border border-slate-500" />
              ) : (
                <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-slate-300">
                  <i className="bi bi-person-fill"></i>
                </div>
              )}
              <div className="hidden md:block text-sm font-medium text-slate-200">
                {user.username}
              </div>
              <button 
                onClick={handleLogout}
                className="ml-2 text-slate-400 hover:text-red-400 transition"
                title="Çıkış Yap"
              >
                <i className="bi bi-box-arrow-right text-lg"></i>
              </button>
            </div>
          ) : (
            // --- MİSAFİR KULLANICI ---
            <div className="flex items-center gap-3 text-sm">
              <Link href="/login" className="text-slate-300 hover:text-white transition font-medium">Giriş Yap</Link>
              <Link href="/register" className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition font-medium shadow-lg shadow-blue-500/20">Kayıt Ol</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}