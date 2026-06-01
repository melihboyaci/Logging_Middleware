# Video Anlatim Akisi (<= 15 dk)

## 0) Giris (30-45 sn)

- Odev hedefi: Data Middleware
- Mimariyi bir cumleyle anlat
- Neleri yaptigini net listele

## 1) Sistem Canli Demo (4-5 dk)

1. `docker compose up --build`
2. Producer log uretimi
3. Middleware isleme akisi
4. `output/` altindaki role bazli dosyalari goster

## 2) 4 Gereksinim Demo (4-5 dk)

### Guvenlik
- TC / kredi karti / email / IBAN maskelenmis cikti goster

### Filtreleme
- INFO/WARNING ve `docker.*` loglarin elendigini goster

### Zenginlestirme
- sender_id, transaction_no, criticality, role tag ornekleri

### Bicimlendirme
- sysadmin md, developer json, security csv dosyalarini goster

## 3) Tasarim Kaliplari (2-3 dk)

- CoR: pipeline zinciri
- Strategy: formatter secimi
- Decorator: enrichment katmani
- Factory: log/formatter uretimi
- Singleton: metrics collector

## 4) Performans / Stres (2 dk)

- load profile dosyasi
- reports metrics snapshot
- filtre acik/kapali yorum

## 5) Kapanis (30 sn)

- Yapilanlar/eksikler acikca soylenir
- Repo + rapor + video linkleri belirtilir
