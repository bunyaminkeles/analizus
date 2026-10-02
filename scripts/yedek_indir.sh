#!/usr/bin/env bash
# Hetzner DB yedeklerini bu bilgisayara sıkıştırarak indirir (~/yedekler/analizus/).
#
#   yedek_indir.sh           → en yeni gecelik yedeği (backup_analizus_YYYYMMDD.sql, 02:00 cron) indirir.
#                              Zaten indirildiyse hiçbir şey yapmaz → cron'da saatlik çalıştırılabilir.
#   yedek_indir.sh --simdi   → deploy öncesi ANLIK yedek: pg_dump çıktısı sunucuya yazılmadan gzip'lenip
#                              buraya akar (yedek_YYYY-MM-DD_HHMM.sql.gz) → sunucuda /root/yedek_* birikmez.
#
# Her iki türden de son YEDEK_SAKLA adet tutulur, eskiler silinir.
set -euo pipefail

SUNUCU="root@89.167.5.224"
HEDEF="${YEDEK_DIZIN:-$HOME/yedekler/analizus}"
YEDEK_SAKLA="${YEDEK_SAKLA:-14}"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=15"

SIMDI=0
case "${1:-}" in
    "") ;;
    --simdi) SIMDI=1 ;;
    *) echo "Kullanım: $0 [--simdi]" >&2; exit 2 ;;
esac

mkdir -p "$HEDEF"
exec 9>"$HEDEF/.kilit"
if [ "$SIMDI" = 1 ]; then
    flock -w 600 9 || { echo "HATA: başka bir yedek indirmesi sürüyor (10 dk beklendi)" >&2; exit 1; }
else
    flock -n 9 || exit 0   # önceki çalışma sürüyorsa çık
fi

if [ "$SIMDI" = 1 ]; then
    ad="yedek_$(date +%F_%H%M).sql.gz"
    desen="yedek_*.sql.gz"
    echo "Anlık yedek alınıyor (sunucuda pg_dump → gzip → buraya)…"
    # Uzak komut tek tırnakla aynen gider; $POSTGRES_* db container'ının içinde açılır
    uzak='cd /app && docker compose exec -T db sh -c '\''pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"'\'' | gzip -c'
else
    son=$($SSH "$SUNUCU" 'ls -t /root/backup_analizus_*.sql 2>/dev/null | head -1')
    [ -n "$son" ] || { echo "$(date '+%F %T') HATA: sunucuda yedek bulunamadı" >&2; exit 1; }
    ad="$(basename "$son").gz"
    desen="backup_analizus_*.sql.gz"
    [ -f "$HEDEF/$ad" ] && exit 0
    uzak="gzip -c '$son'"
fi

gecici="$HEDEF/.$ad.part"
$SSH "$SUNUCU" "$uzak" > "$gecici"

# Doğrulama: gzip bütünlüğü + pg_dump "dump complete" satırı (yeni pg_dump sonuna \unrestrict ekler → son 10 satır)
gzip -t "$gecici"
if ! zcat "$gecici" | tail -n 10 | grep -q "PostgreSQL database dump complete"; then
    rm -f "$gecici"
    echo "$(date '+%F %T') HATA: $ad eksik (dump tamamlanmamış)" >&2
    exit 1
fi
mv "$gecici" "$HEDEF/$ad"
echo "$(date '+%F %T') indirildi: $ad ($(du -h "$HEDEF/$ad" | cut -f1))"
[ "$SIMDI" = 1 ] && echo "Konum: $HEDEF/$ad"

ls -1t "$HEDEF"/$desen | tail -n +"$((YEDEK_SAKLA + 1))" | xargs -r rm -f
