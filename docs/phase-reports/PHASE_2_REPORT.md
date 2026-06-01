# Faz 2 Detayli Rapor - Middleware Iskeleti ve Guvenlik

Tarih: 2026-06-01  
Faz Durumu: Tamamlandi

## 1) Faz Ozeti

Faz 2'de middleware tarafinin temel omurgasi kuruldu:

- RabbitMQ consumer iskeleti
- FastAPI `health` ve `metrics` endpointleri
- Chain of Responsibility tabani
- KVKK anonimlestirme kurallari ve handler'i
- Basit metrik toplayici

Bu faz ile producer'dan gelen `LogRecord` mesajlarini middleware tarafinda parse edip pipeline'a sokabilecek altyapi tamamlandi.

## 2) Yapilan Teknik Isler

### 2.1 Konfigurasyon ve Metrik Katmani

- `middleware/src/config.py` ile `MiddlewareConfig` tanimlandi.
  - AMQP URL
  - Exchange / queue
  - Prefetch
  - API host/port
- `middleware/src/metrics/collector.py` ile faz 2 icin temel sayaclar eklendi:
  - `consumed_total`
  - `processed_total`
  - `dropped_total`
  - `errors_total`

### 2.2 CoR Taban ve Pipeline Kurulumu

- `middleware/src/pipeline/handler.py` ile `AbstractHandler` eklendi.
- `middleware/src/pipeline/pipeline_builder.py` ile ilk zincir kuruldu:
  - `AnonymizationHandler -> TerminalHandler`
- `middleware/src/pipeline/terminal_handler.py` faz 2 icin gecici son adim olarak `processed_total` sayacini artiriyor.

Bu yapi Faz 3'te filtre ve zenginlestirme handler'lari eklenerek genisletilecek.

### 2.3 KVKK Kurallari ve Anonimlestirme

- `middleware/src/security/rules.py`:
  - TC, kart, IBAN, SWIFT, email regex desenleri
- `middleware/src/security/anonymizer.py`:
  - `anonymize_text`
  - `anonymize_payload`
  - Sira: TC -> Kart -> IBAN -> SWIFT -> Email

`AnonymizationHandler` (`middleware/src/pipeline/anonymization_handler.py`) log mesaji ve payload string alanlarini maskeliyor.

### 2.4 RabbitMQ Consumer

`middleware/src/transport/consumer.py`:

- `aio-pika` ile robust baglanti
- Topic exchange declaration
- Queue declaration + bind
- `prefetch_count` ayari
- Mesaj validasyonu (`LogRecord.model_validate_json`)
- Pipeline'a iletme
- Metrik artirimlari (`consumed`, `dropped`, `errors`)
- `message.process(requeue=False)` ile hata davranisi

### 2.5 API ve Uygulama Yasam Dongusu

- `middleware/src/api/routes.py`:
  - `GET /health` -> `{\"status\": \"ok\"}`
  - `GET /metrics` -> metrics snapshot
- `middleware/src/main.py`:
  - FastAPI lifespan icinde consumer start/stop
  - `create_app()` factory
  - `uvicorn` calistirma giris noktasi

## 3) Degisen / Eklenen Dosyalar

- `middleware/src/config.py`
- `middleware/src/metrics/__init__.py`
- `middleware/src/metrics/collector.py`
- `middleware/src/pipeline/__init__.py`
- `middleware/src/pipeline/handler.py`
- `middleware/src/pipeline/anonymization_handler.py`
- `middleware/src/pipeline/terminal_handler.py`
- `middleware/src/pipeline/pipeline_builder.py`
- `middleware/src/security/__init__.py`
- `middleware/src/security/rules.py`
- `middleware/src/security/anonymizer.py`
- `middleware/src/transport/__init__.py`
- `middleware/src/transport/consumer.py`
- `middleware/src/api/__init__.py`
- `middleware/src/api/routes.py`
- `middleware/src/main.py` (faz 0 scaffold'dan faz 2 app yapisina gecirildi)
- `tests/test_phase2_middleware.py`
- `docs/STATE.md`

## 4) Calistirilan Testler/Komutlar

1. Faz 1 + Faz 2 testleri:

```bash
python -m pytest -q tests/test_phase1_producer.py tests/test_phase2_middleware.py
```

2. Compose dogrulamasi:

```bash
docker compose -f d:\my-projects\yazılım-ödev-middleware\docker-compose.yml config
```

3. Lint/diagnostik kontrolu:

- `middleware/src/**`
- `tests/test_phase2_middleware.py`

## 5) Test Sonuclari

- Pytest: **6 passed**
- Compose config: **Basarili**
- Lint: **Yeni hata yok**

## 6) Riskler / Acik Maddeler

- Faz 2'de pipeline sadece anonimlestirme + terminal adimindan olusuyor; filtre/zenginlestirme Faz 3'te eklenecek.
- `metrics` endpoint su an temel sayac snapshot'u donuyor; histogram/p95/p99 Faz 5 hedefinde.
- Live end-to-end (producer publish -> middleware consume -> cikti dosyalari) formatlama ve sink asamalari Faz 4'te tamamlaninca daha anlamli hale gelecek.

## 7) Sonraki Faz

Faz 3 odagi:

- `filter_handler.py` ile INFO/WARNING ve `docker.*` loglarini dusurme
- `enrichment_handler.py` + `enrichers.py` ile role tag ve ek alanlar
- Pipeline zincirini genisletme
- Faz 3 testleri ve raporu
