# AGENTS.md - CENG302 Data Middleware

Bu dosya, repoda calisan bir AI ajaninin ilk okumasi gereken dokumandir. Kisa, baglayicidir.

## Proje 1 cumlede

Borsa kurulusu icin, log ureten Producer ve KVKK anonimlestirme + filtreleme + zenginlestirme + rol bazli bicimlendirme yapan Middleware'den olusan, RabbitMQ uzerinden haberlesen iki Docker uygulamasi.

## Mimari (iki satir)

```
Producer (Docker)  --publish-->  RabbitMQ (broker)  --consume-->  Middleware (Docker)
Middleware pipeline:  Anonymize -> Filter -> Enrich -> Format/Route
```

Detayli akis ve tasarim kaliplari icin: `docs/SPECS.md` ve `.cursor/plans/data_middleware_plani_351ee24e.plan.md`.

## Tek dogruluk kaynaklari (oncelik sirasi)

1. **`docs/SPECS.md`** - Davranis sozlesmesi (regexler, semalar, rol->format, etiketler, filtre kurallari, pattern->dosya eslemesi). Kod yazarken **buraya** uyulur, sezgilere degil.
2. **`docs/STATE.md`** - Hangi fazdayiz, neyi bitirdik, sonraki adim. Her faz basinda/sonunda guncellenir.
3. **`docs/DECISIONS.md`** - Mimari/yorum kararlari (ADR). Yeni karar alindiginda yeni madde eklenir.
4. **Plan dosyasi** (`.cursor/plans/data_middleware_plani_351ee24e.plan.md`) - Faz kirilimlari ve gerekce.

## Sert kisitlar

- **Python 3.11+**, async kod tercih edilir (transport katmaninda zorunlu).
- **En az 3 tasarim kalibi** kullanilacak (biz 5 kullaniyoruz: Chain of Responsibility, Strategy, Decorator, Factory, Singleton). Yerleri `docs/SPECS.md`'de.
- **KVKK:** hassas veriler asla diske/cikti dosyasina **maskelenmeden** yazilmaz. Anonimlestirme pipeline'in **ilk** asamasidir.
- **"Iki Docker modulu"** ifadesi, gelistirdigimiz iki uygulama modulu (producer + middleware) olarak yorumlanir. RabbitMQ resmi image, kod yazmiyoruz; altyapidir (bkz. `docs/DECISIONS.md` D-001).
- **Cikti formatlari:** HTML / Markdown / CSV / JSON hepsi destekli; rol->format eslemesi config'ten gelir (varsayilan: sysadmin=md, developer=json, security=csv).
- **Filtre:** `info` ve `warning` seviyeleri ile sistem-disi loglar **dusurulur** (performans gostergesi).

## Calistirma

```bash
docker compose up --build           # 3 servis: producer, middleware, rabbitmq
docker compose logs -f middleware   # akisi izle
# Stres testi:
docker compose run --rm producer python -m producer.src.main --total 100000 --rate 5000 --batch 200
```

Ciktilar host'ta `./output/{sysadmin.md, developer.json, security.csv, ...}` altina yazilir. Metrikler: `http://127.0.0.1:8000/metrics`. RabbitMQ UI: `http://127.0.0.1:15672` (guest/guest). Windows'ta `localhost` yerine `127.0.0.1` tercih edilir.

## Kodlama konvansiyonlari

- Kod ne yaptigini anlatan **yorum yazma**. Yorumlar sadece "neden" / "trade-off" / "kısıt" icin.
- Tip ipuclari (`type hints`) zorunlu. Pydantic modelleri `shared/log_schema.py`.
- Hata firlatma sessiz tutulmaz; consumer'da nack(requeue=false) + sayac.
- Testler `tests/` altinda, `pytest` ile; her faz sonunda yeni test eklenir.
- Yeni hassas veri tipi / yeni rol / yeni format eklerken **once `docs/SPECS.md`** guncellenir, sonra kod.

## Faz dongusu (ajanin uyacagi ritim)

1. `docs/STATE.md`'ye bak: aktif faz nedir?
2. Plan dosyasindan faz gereklerini oku.
3. Kodla, test ekle.
4. Faz tamamlaninca `docs/STATE.md`'de kutuyu isaretle, kisa not ekle.
5. Karar aldiysan `docs/DECISIONS.md`'ye ADR maddesi ekle.
