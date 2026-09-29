#!/usr/bin/env bash
# Hetzner'deki en yeni gecelik DB yedeğini (backup_analizus_YYYYMMDD.sql, 02:00 cron) bu bilgisayara
# sıkıştırarak indirir. Zaten indirildiyse hiçbir şey yapmaz → cron'da saatlik çalıştırılabilir.
# Son YEDEK_SAKLA adet yedek tutulur, eskiler silinir.
set -euo pipefail

SUNUCU="root@89.167.5.224"
HEDEF="${YEDEK_DIZIN:-$HOME/yedekler/analizus}"
YEDEK_SAKLA="${YEDEK_SAKLA:-14}"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=15"

mkdir -p "$HEDEF"
exec 9>"$HEDEF/.kilit"
flock -n 9 || exit 0   # önceki çalışma sürüyorsa çık

son=$($SSH "$SUNUCU" 'ls -t /root/backup_analizus_*.sql 2>/dev/null | head -1')
[ -n "$son" ] || { echo "$(date '+%F %T') HATA: sunucuda yedek bulunamadı" >&2; exit 1; }
ad="$(basename "$son").gz"
[ -f "$HEDEF/$ad" ] && exit 0

gecici="$HEDEF/.$ad.part"
$SSH "$SUNUCU" "gzip -c '$son'" > "$gecici"

# Doğrulama: gzip bütünlüğü + pg_dump "dump complete" satırı (yeni pg_dump sonuna \unrestrict ekler → son 10 satır)
gzip -t "$gecici"
if ! zcat "$gecici" | tail -n 10 | grep -q "PostgreSQL database dump complete"; then
    rm -f "$gecici"
    echo "$(date '+%F %T') HATA: $ad eksik (dump tamamlanmamış)" >&2
    exit 1
fi
mv "$gecici" "$HEDEF/$ad"
echo "$(date '+%F %T') indirildi: $ad ($(du -h "$HEDEF/$ad" | cut -f1))"

ls -1t "$HEDEF"/backup_analizus_*.sql.gz | tail -n +"$((YEDEK_SAKLA + 1))" | xargs -r rm -f
