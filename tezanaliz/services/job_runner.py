"""
Tez Analizi iş yürütücüsü.
Daemon thread içinde fetch → analyze → PDF → S3 → email akışını yönetir.
"""
import gc
import threading
import logging

from django.core.mail import EmailMessage
from django.conf import settings

logger = logging.getLogger(__name__)


def run_tezanaliz_job(job_id: str) -> None:
    """Tez analizi işini arka planda başlat."""

    def _run():
        from tezanaliz.models import TezAnaliz
        from tezanaliz.services.fetcher import fetch_all
        from tezanaliz.services.analyzer import run_all_analyses, compute_similar_theses
        from tezanaliz.services.pdf_builder import build_pdf
        from forum.s3_utils import upload_bytes_to_s3

        try:
            job = TezAnaliz.objects.get(id=job_id)
            job.mark_running()

            # 1. Tüm tezleri çek
            records = fetch_all(
                tez_ad=job.tez_ad,
                yazar=job.yazar,
                universite=job.universite,
                tur=job.tur or '0',
                yil_baslangic=job.yil_baslangic,
                yil_bitis=job.yil_bitis,
                metin=job.metin,
            )

            if not records:
                job.mark_failed('Tez verisi çekilemedi. Arama kriterlerini genişletin.')
                return

            if len(records) < 5:
                job.mark_failed(
                    f'Analiz için en az 5 kayıt gereklidir (bulunan: {len(records)}). '
                    'Arama kriterlerini genişletin.'
                )
                return

            # 2. Kayıtları kaydet (benzer tezler için)
            job.records = records
            job.save(update_fields=['records'])

            # 3. Benzer tezler hesapla
            query_text = ' '.join(filter(None, [job.tez_ad, job.metin]))
            similar = compute_similar_theses(records, query_text, top_n=10)
            job.analysis_data = {'similar': similar}
            job.save(update_fields=['analysis_data'])

            # 4. Analizler
            figures = run_all_analyses(records)
            if not figures:
                job.mark_failed('Analizler üretilemedi. Veri yetersiz olabilir.')
                return

            # 5. PDF oluştur
            pdf_bytes = build_pdf(
                figures,
                total_records=len(records),
                query_summary=job.get_query_summary(),
            )

            # 6. Figürleri serbest bırak
            n_figures = len(figures)
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except Exception:
                pass
            del figures
            gc.collect()

            # 7. S3'e yükle
            s3_key = f'tezanaliz/pdf/{job.id}.pdf'
            pdf_url = upload_bytes_to_s3(pdf_bytes, s3_key, 'application/pdf')

            # 8. Job'ı tamamla
            job.mark_completed(total_records=len(records), pdf_url=pdf_url or '')

            logger.info(
                f'[tezanaliz] Job {job_id} tamamlandı. '
                f'{len(records)} kayıt, {n_figures} analiz.'
            )

            # 9. Email gönder
            send_completion_email_async(str(job.id), pdf_url)

        except TezAnaliz.DoesNotExist:
            logger.error(f'[tezanaliz] Job bulunamadı: {job_id}')
        except Exception as e:
            logger.error(f'[tezanaliz] Job hatası [{job_id}]: {e}', exc_info=True)
            try:
                from tezanaliz.models import TezAnaliz
                TezAnaliz.objects.get(id=job_id).mark_failed(str(e))
            except Exception:
                pass

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def send_completion_email_async(job_id: str, pdf_url: str = '') -> None:
    """Analiz tamamlandığında PDF URL'si ile email gönder."""

    def _run():
        from tezanaliz.models import TezAnaliz
        try:
            job = TezAnaliz.objects.get(id=job_id)
            user = job.user
            site_url = getattr(settings, 'SITE_URL', 'https://analizus.com')
            result_url = f'{site_url}/tezanaliz/sonuc/{job.id}/'

            subject = f'Tez & Makale Analizi Tamamlandı — {job.get_query_summary()[:50]}'
            body_lines = [
                f'Merhaba {user.first_name or user.username},',
                '',
                f'"{job.get_query_summary()}" sorgunuz için tez analizi tamamlandı.',
                '',
                f'Toplam Analiz Edilen Tez: {job.total_records}',
                '',
                'Analiz sonuçlarınızı ve PDF raporunuzu görüntülemek için:',
                f'  {result_url}',
                '',
            ]
            if pdf_url:
                body_lines += [
                    'PDF raporunuzu doğrudan indirmek için:',
                    f'  {pdf_url}',
                    '',
                    'Not: İndirme linki 3 gün geçerlidir.',
                    '',
                ]
            body_lines += [
                '---',
                'Bu bir otomatik bildirimdir.',
                'Analizus — Akademik Veri Üssü  |  analizus.com',
            ]

            email = EmailMessage(
                subject=subject,
                body='\n'.join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.send()
            logger.info(f'[tezanaliz] Tamamlanma emaili gönderildi: {user.email}')

        except Exception as e:
            logger.error(f'[tezanaliz] Email hatası [{job_id}]: {e}', exc_info=True)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
