# Analizus Deploy Cheatsheet

## Lokal (geliştirme sonrası)

```bash
# Değişiklikleri commit et ve push et
git add <dosyalar>
git commit -m "feat/fix: açıklama"
git push origin dev

# dev → main merge
git checkout main && git merge dev --no-ff -m "merge: açıklama" && git push origin main && git checkout dev
```

---

## Hetzner (production güncelleme)

```bash
cd /app

# Kodu çek
git pull origin main

# Sadece kod değişikliği (JS/CSS/template/Python) — image rebuild yok, saniyeler içinde
docker compose restart web

# requirements.txt veya Dockerfile değiştiyse — rebuild gerekli
docker compose up -d --build web

# Container çakışma hatası alırsan (Conflict: container name already in use)
docker compose down && docker compose up -d --build
```

---

## Hetzner (sorun giderme)

```bash
# Logları izle
docker compose logs web --tail=50
docker compose logs web -f          # canlı

# Container durumları
docker compose ps

# Site yanıt veriyor mu?
curl -o /dev/null -w '%{http_code}' http://localhost:8000/

# Servis yeniden başlat
docker compose restart web
docker compose restart db
docker compose restart nginx

# Tüm servisleri yeniden başlat (çakışma durumunda)
docker compose down && docker compose up -d
```

---

## Hetzner (veritabanı)

```bash
# Backup al
docker exec app-db-1 pg_dump -U bunyamin analizus > /root/backup_$(date +%Y%m%d).sql

# Backup restore et
docker compose stop web
docker exec -i app-db-1 psql -U bunyamin -d postgres -c 'DROP DATABASE analizus; CREATE DATABASE analizus OWNER bunyamin;'
docker exec -i app-db-1 psql -U bunyamin -d analizus < /root/backup_YYYYMMDD.sql
docker compose up -d web

# Migration çalıştır (manuel)
docker compose exec web python manage.py migrate
```

---

## Hetzner (statik dosyalar)

```bash
# Collectstatic manuel çalıştır (deploy.sh zaten otomatik çalıştırır)
docker compose exec web python manage.py collectstatic --noinput
```

---

## Notlar

- **Bind mount aktif**: `/app` dizini host'tan mount edilir. `restart web` sonrası yeni kod otomatik görünür.
- **Sadece `requirements.txt` değişince `--build` gerekir.**
- `deploy.sh` her container başlangıcında migrate + collectstatic çalıştırır.
- DB container adı: `app-db-1`, web: `app-web-1`, nginx: `app-nginx-1`
