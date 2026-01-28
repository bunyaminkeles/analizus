// /frontend/app/error.tsx
'use client'; // Error components must be Client Components

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-slate-400 gap-4">
      <i className="bi bi-exclamation-triangle text-5xl text-red-500"></i>
      <h2 className="text-2xl font-bold text-white">Bir şeyler ters gitti!</h2>
      <p className="text-slate-500">Verileri yüklerken beklenmedik bir hata oluştu.</p>
      <button
        onClick={() => reset()}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
      >
        Tekrar Dene
      </button>
    </div>
  );
}
