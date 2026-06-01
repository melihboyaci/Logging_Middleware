# SPECS - Davranis Sozlesmesi

Bu dosya **tek dogruluk kaynagidir**. Kod, sezgi/yorum degil, buraya uyacak. Yeni davranis once burada tanimlanir, sonra kodlanir.

## 1. Log Semasi (`shared/log_schema.py`)

Pydantic v2 modeli:

| Alan | Tip | Aciklama |
|------|------|----------|
| `id` | UUID4 | Producer'da uretilir |
| `timestamp` | datetime (ISO8601 UTC) | Producer'da set edilir; end-to-end gecikme bundan hesaplanir |
| `level` | enum: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | |
| `type` | enum: `LOG`, `ERROR`, `TRANSACTION`, `ACCESS` | |
| `role` | enum: `sysadmin`, `developer`, `security` | Hedef rol |
| `source` | str | Olayi ureten alt sistem (`docker.*` filtreyle dusurulur) |
| `message` | str | Insan okunabilir mesaj |
| `payload` | dict[str, Any] | Tipe gore degisken alanlar (TC, IBAN, kart, vb.) |

JSON ornek:
```json
{
  "id": "8c4f...-...",
  "timestamp": "2026-06-09T12:34:56.789Z",
  "level": "ERROR",
  "type": "TRANSACTION",
  "role": "security",
  "source": "trade.api",
  "message": "3 failed login attempts",
  "payload": {"tc": "12345678901", "ip": "1.2.3.4"}
}
```

## 2. KVKK Anonimlestirme Kurallari (`middleware/src/security/`)

`message` **ve** `payload` icindeki tum string degerlerde uygulanir. Sira: TC -> Kart -> IBAN -> SWIFT -> Email.

| Tip | Tespit (regex) | Maskeleme | Ornek |
|------|----------------|-----------|--------|
| TC Kimlik | `\b\d{11}\b` (11 hane, ilki 0 degil) | Ilk 2 hane + `xxxxxxxx` + son hane | `12345678901` -> `12xxxxxxxx1` |
| Kredi Karti | `\b(?:\d[ -]?){13,19}\b` (Luhn dogrulamali) | Ilk 4 + ` xxxxxx ` + son 4 | `5235123412341234` -> `5235 xxxxxx 1234` |
| IBAN (TR) | `\bTR\d{24}\b` | Ilk 4 + `xxxxxxxxxxxxxxxxxxxx` + son 4 | `TR12...3456` -> `TR12xxxx...3456` |
| SWIFT/BIC | `\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b` | Komple `***SWIFT***` | `GARBTRIS` -> `***SWIFT***` |
| E-posta | RFC-ish basit: `[\w.+-]+@[\w-]+\.[\w.-]+` | Ilk harf + `***@` + domain | `melih@example.com` -> `m***@example.com` |

Notlar:
- Maskeleme **deterministik** ve **idempotent** (zaten maskeli icerige tekrar uygulanirsa degismez).
- Tespit kurallari `security/rules.py`'da; maskeleme `security/anonymizer.py`'da. Yeni tip eklerken bu tabloyu da guncelle.

## 3. Filtre Kurallari (`middleware/src/pipeline/filter_handler.py`)

| Kural | Aksiyon |
|-------|---------|
| `level in {DEBUG, INFO, WARNING}` | DROP |
| `source` regex `^docker\.` ile basliyor | DROP (sistem-disi/altyapi gurultusu) |
| Diger | KEEP |

Dusen her log icin `MetricsCollector.dropped += 1`. Filtre toggle config'ten (`FILTER_ENABLED`); stres testinde "filtre acik vs kapali" karsilastirmasi icin.

## 4. Zenginlestirme (Decorator zinciri, `middleware/src/enrichment/`)

Her log icin uygulanacak dekoratorler:

| Sira | Decorator | Etki |
|------|-----------|------|
| 1 | `SenderIdDecorator` | `payload.sender_id` set/uret |
| 2 | `TransactionInfoDecorator` | type=TRANSACTION ise `payload.transaction_no` ekle |
| 3 | `CriticalityDecorator` | `level`/`type` -> `payload.criticality` (`low`/`med`/`high`/`critical`) |
| 4 | `RoleTagDecorator` | Role gore `message`'i sar (asagida) |
| 5 | `DebugDecorator` | level=DEBUG (filtre kapaliysa) icin `payload.debug=True` |

Rol etiketi sarmalayicilari (`RoleTagDecorator`):

| Rol | Sarmalayici | Ornek |
|------|------------|-------|
| `security` | `<...>` | `<3 failed login attempts>` |
| `developer` | `{...}` | `{404 GET /users/42}` |
| `sysadmin` | `{~...~}` | `{~datetime mismatch~}` |

## 5. Rol -> Format Eslemesi (`middleware/src/formatting/`)

Strategy arayuzu: `Formatter.format(log: LogRecord) -> bytes`. Factory `FormatterFactory.for_role(role)` config'e bakar.

| Rol | Format | Dosya |
|-----|--------|------|
| `sysadmin` | Markdown | `output/sysadmin.md` |
| `developer` | JSON (JSONL: satir basina bir obje) | `output/developer.json` |
| `security` | CSV | `output/security.csv` |

Tum formatlar implementli (HTML/MD/CSV/JSON); eslemeyi degistirmek icin `middleware/src/config.py` -> `ROLE_FORMAT_MAP`.

## 6. Transport (RabbitMQ)

| Ogel | Deger |
|------|------|
| URL | `amqp://guest:guest@rabbitmq:5672/` (env: `AMQP_URL`) |
| Exchange | `logs` (topic, durable) |
| Routing key (publish) | `logs.raw` |
| Queue | `logs.raw` (durable, autoDelete=false) |
| Mesaj | `delivery_mode=2` (persistent), `content_type=application/json` |
| Tuketim | `prefetch_count` config'ten (varsayilan 50); `process()` ile auto-ack on success |
| Hata | nack(requeue=false); opsiyonel DLQ -> `logs.dlq` |

## 7. Tasarim Kalibi -> Dosya Eslemesi

| Kalip | Yer | Rol |
|-------|-----|-----|
| Chain of Responsibility | `middleware/src/pipeline/` (`handler.py`, `*_handler.py`, `pipeline_builder.py`) | Cekirdek isleme hatti |
| Strategy | `middleware/src/formatting/` (`formatter.py`, `*_formatter.py`) | Format secimi |
| Decorator | `middleware/src/enrichment/enrichers.py` | Zenginlestirme |
| Factory | `producer/src/generators/log_factory.py` + `middleware/src/formatting/formatter_factory.py` | Log/Formatter uretimi |
| Singleton | `middleware/src/metrics/collector.py` + `middleware/src/config.py` | Metrik/konfig ortak ornek |

## 8. Metrikler (`/metrics` endpoint)

- `published_total` (producer tarafindan publish edilen - opsiyonel)
- `consumed_total`
- `processed_total`
- `dropped_total` (filtre)
- `errors_total`
- `processing_latency_seconds` (pipeline icindeki gecikme; histogram, p50/p95/p99)
- `e2e_latency_seconds` (log.timestamp -> processed; histogram)
- `queue_depth` (RabbitMQ mgmt API'sinden cekilir, `reports/` icin)

## 9. Senaryo Setleri (`producer/src/generators/scenarios.py`)

| Senaryo | Tip / Level / Rol | Tetikledigi gereksinim |
|---------|-------------------|------------------------|
| `kvkk_transaction` | TRANSACTION / ERROR / security | KVKK (TC + IBAN + miktar) + zenginlestirme |
| `failed_login_burst` | ACCESS / ERROR / security | Zenginlestirme `<3 failed login>` |
| `dev_404` | ACCESS / ERROR / developer | Zenginlestirme `{404 GET ...}` |
| `sysadmin_datetime_mismatch` | LOG / CRITICAL / sysadmin | Zenginlestirme `{~datetime~}` |
| `noise_info_warning` | LOG / INFO veya WARNING | Filtre dususu (performans kaniti) |
| `docker_internal_noise` | LOG / source=docker.* | Filtre dususu (sistem-disi) |
| `card_purchase` | TRANSACTION / ERROR / security | Kart maskelemesi + miktar |

Producer her senaryoyu agirlikli rastgele uretir; agirliklar `producer/src/config.py`'da.
