// Dosya: /home/bunyamin/Documents/analizdestek/frontend/app/register/page.tsx
"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Şifreler eşleşmiyor.');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Kayıt işlemi başarısız.');
      }

      // Başarılı kayıt sonrası login sayfasına yönlendir
      router.push('/login?registered=true');
      
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
          <p className="text-slate-400 text-sm">Aramıza katılın</p>
        </div>
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-200 p-3 rounded mb-6 text-sm flex items-center gap-2">
            <i className="bi bi-exclamation-circle"></i>
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Kullanıcı Adı</label>
            <input 
              type="text" name="username" required
              value={formData.username} onChange={handleChange}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">E-posta</label>
            <input 
              type="email" name="email" required
              value={formData.email} onChange={handleChange}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Şifre</label>
            <input 
              type="password" name="password" required
              value={formData.password} onChange={handleChange}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Şifre Tekrar</label>
            <input 
              type="password" name="confirmPassword" required
              value={formData.confirmPassword} onChange={handleChange}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-white focus:border-blue-500 outline-none"
            />
          </div>

          <button 
            type="submit" disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition mt-2"
          >
            {loading ? 'Kaydediliyor...' : 'Kayıt Ol'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-500">
          Zaten hesabınız var mı? <Link href="/login" className="text-blue-400 hover:text-blue-300 transition">Giriş Yap</Link>
        </div>
      </div>
    </div>
  );
}
