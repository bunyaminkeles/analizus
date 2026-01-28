"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 1. Django'dan Token İste (Giriş Yap)
      // Not: Django 8000 portunda çalışıyor olmalı
      const res = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        if (res.status === 401) {
          throw new Error('Kullanıcı adı veya şifre hatalı.');
        }
        const text = await res.text();
        console.error("Login Error:", text);
        throw new Error(`Sunucu hatası: ${res.status}`);
      }

      const data = await res.json();

      // 2. Token'ları Tarayıcıya Kaydet
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      // 3. Token ile Kullanıcı Bilgilerini (/api/me/) Çek
      const userRes = await fetch('http://127.0.0.1:8000/api/me/', {
        headers: {
          'Authorization': `Bearer ${data.access}`
        }
      });

      if (userRes.ok) {
        const userData = await userRes.json();
        localStorage.setItem('user', JSON.stringify(userData));
      }

      // 4. Anasayfaya Yönlendir
      router.push('/');
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white p-4">
      <div className="bg-slate-800 p-8 rounded-xl border border-slate-700 w-full max-w-md shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-400 mb-2">Analizus</h1>
          <p className="text-slate-400 text-sm">Hesabınıza giriş yapın</p>
        </div>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-200 p-3 rounded mb-6 text-sm flex items-center gap-2">
            <i className="bi bi-exclamation-circle"></i>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Kullanıcı Adı</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition"
              placeholder="Kullanıcı adınız"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Şifre</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition"
              placeholder="••••••••"
              required
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-bold py-3 rounded-lg transition shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-500">
          Hesabınız yok mu? <a href="/register" className="text-blue-400 hover:text-blue-300 transition">Kayıt Ol</a>
        </div>
      </div>
    </div>
  );
}