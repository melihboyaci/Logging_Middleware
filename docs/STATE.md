# STATE - Faz Ilerlemesi

Bu dosya her faz basinda/sonunda guncellenir. Yeni bir oturum, "nerede kaldik?" sorusunu **once buradan** cevaplar.

## Aktif Faz

**Faz 2 - Hazir baslangic.** Faz 1 tamamlandi (producer cekirdegi + testler).

## Faz Tablosu

- [x] **Faz 0** - Iskelet ve Altyapi (repo yapisi, `shared/log_schema.py`, iki `Dockerfile`, `docker-compose.yml` [producer + middleware + rabbitmq healthcheck], `.gitignore`)
- [x] **Faz 1** - Producer (LogFactory, hassas veri ureticileri, senaryolar, `aio-pika` publisher, CLI)
- [ ] **Faz 2** - Middleware iskeleti + Guvenlik (consumer + FastAPI metrics/health, CoR taban, KVKK AnonymizationHandler)
- [ ] **Faz 3** - Filtre + Zenginlestirme (FilterHandler + Decorator zinciri)
- [ ] **Faz 4** - Bicimlendirme + Yonlendirme (Strategy formatlayicilar + FormatterFactory + role_router)
- [ ] **Faz 5** - Metrikler + Stres Testi (Singleton MetricsCollector + load_runner + queue-depth + matplotlib raporlari)
- [ ] **Faz 6** - Testler + README + Rapor + Video senaryosu

## Bitirilen isler (kronolojik)

- Faz 0 tamamlandi: temel klasor iskeleti, RabbitMQ tabanli `docker-compose.yml`, iki uygulama `Dockerfile`, ortak `shared/log_schema.py` ve baslangic package dosyalari olusturuldu.
- Faz 0 dogrulamasi: `docker compose ... config`, `python -m producer.src.main`, `python -m middleware.src.main` komutlari basariyla calisti.
- Faz 1 tamamlandi: producer icin `config`, `LogFactory`, hassas veri ureticileri, senaryo jenerasyonu, `aio-pika` publisher ve CLI parametreleri eklendi.
- Faz 1 testleri: `python -m producer.src.main --dry-run --total 20 --batch 5 --rate 100` ve `python -m pytest -q tests/test_phase1_producer.py` basariyla calisti (3/3).

## Sonraki adim

Faz 2: Middleware iskeleti (`transport/consumer.py`, `api/routes.py`, `config.py`, `main.py`) + CoR tabani ve KVKK anonimlestirme handler'i.

## Bloklayicilar / Notlar

(yok)

## Faz tamamlandi nasil belirlenir

Bir fazi "tamamlandi" isaretlemeden once:
1. Ilgili kod yazildi, manuel olarak `docker compose up` ile akista hata yok.
2. O fazin yeni testleri yazildi ve `pytest -q` yesil.
3. Yeni davranis/kural eklendiyse `docs/SPECS.md` guncellendi.
4. Bu dosyada kutu isaretlendi + kisa not (1-2 cumle) eklendi.

## Faz Sonu Rapor Formati (zorunlu)

Her faz tamamlandiginda kullaniciya su basliklarla rapor verilir:

1. **Faz Ozeti**
2. **Degisen Dosyalar**
3. **Calistirilan Testler/Komutlar**
4. **Test Sonuclari**
5. **Riskler/Acik Maddeler**
6. **Sonraki Faz**
