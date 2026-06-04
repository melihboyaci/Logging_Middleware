# CENG302 Veri Middleware Projesi — Proje Raporu

| | |
|---|---|
| Ders | CENG302 — Yazılım Mühendisliği |
| Proje | Borsa Kurumu Log Ara Katmanı (Data Middleware) |
| Öğrenci | Melih Boyacı |
| Öğrenci No | 22253073 |
| Tarih | 4 Haziran 2026 |

---

## Özet

Bu ödevde borsa ortamındaki log akışını simüle eden **iki Docker modülü** geliştirdik: **Producer** (veri üretici) ve **Middleware** (ara katman). Modüller **RabbitMQ** üzerinden asenkron ve gevşek bağlı (decoupled) haberleşir; yüksek trafikte kuyruk tampon görevi görür.

Middleware tarafında her log **pipeline** (işleme hattı) üzerinden geçer: KVKK anonimleştirme → gürültü filtresi → Decorator ile zenginleştirme → Strategy ile rol bazlı biçimlendirme. Çıktılar Markdown, JSON (JSONL) ve CSV olarak ayrı dosyalara yazılır.

Ödev metninde “en az iki tasarım kalıbı” geçse de değerlendirmede **en az üç** beklenir; projede **beş** kalıp uygulandı: Chain of Responsibility, Strategy, Decorator, Factory, Singleton.

Doğrulama: **21 pytest** testi, Docker tabanlı uçtan uca (E2E) deneme. Son E2E koşusunda `consumed_total=300`, `processed_total=183`, `dropped_total=117` (%39 filtre), pipeline gecikmesi **p50 ≈ 1,49 ms**.

---

## 1. Giriş

### 1.1 Problem

Mikroservis mimarisinde log hacmi yüksektir; kayıtlar TC, kart, IBAN, e-posta gibi PII (kişisel veri) içerebilir. KVKK gereği bu veriler ham hâliyle saklanmamalıdır. Aynı anda sistem yöneticisi, güvenlik ve geliştirme ekipleri farklı format (insan okunur metin, tablo, makine JSON) ister. Ara katman bu ihtiyaçları tek noktada toplar.

### 1.2 Kapsam

| Dahil | Hariç |
|-------|--------|
| Producer + Middleware (Docker), RabbitMQ broker | Gerçek borsa entegrasyonu |
| Maskeleme, filtre, zenginleştirme, rol çıktıları | Kalıcı veritabanı |
| `/health`, `/metrics`, stres testi | Çok bölgeli dağıtım |

### 1.3 Ödev maddeleri

| Ödev | Karşılık |
|------|----------|
| İki Docker modülü | Producer + Middleware |
| Anonimleştirme | Pipeline ilk handler; regex tabanlı maskeleme |
| Zenginleştirme | Decorator zinciri (sender_id, transaction_no, criticality, rol etiketi, debug) |
| Filtreleme (performans) | DEBUG/INFO/WARNING + `docker.*` kaynak drop |
| Rol bazlı biçim | Strategy: sysadmin→MD, developer→JSONL, security→CSV; HTML destekli |
| ≥3 tasarım kalıbı | 5 kalıp (Bölüm 5) |
| Tüm senaryolar | 7 ağırlıklı senaryo |
| Performans aralığı | Metrik endpoint + stres CLI |

Ödevdeki *system admin*, *cybersec*, *web dev* rolleri sırasıyla `sysadmin`, `security`, `developer` enum değerlerine eşlendi.

---

## 2. Geliştirme Süreci (Faz 0–9)

| Faz | Teknik çıktı |
|-----|----------------|
| 0 | Docker Compose, Pydantic `LogRecord` şeması |
| 1 | LogFactory, senaryo motoru, AMQP publisher |
| 2 | Async consumer, FastAPI, CoR + KVKK handler |
| 3 | FilterHandler, enrichment Decorator’ları |
| 4 | Strategy formatter’lar, RoleRouter |
| 5 | MetricsCollector (p50/p95/p99), load_runner |
| 6 | Dokümantasyon |
| 7 | E2E smoke otomasyonu |
| 8 | GitHub Actions CI |
| 9 | Kuyruk derinliği örnekleme, performans grafikleri |

```
Faz0 → Faz1(Producer) → Faz2(CoR+KVKK) → Faz3(Filter+Decorator)
     → Faz4(Strategy) → Faz5(Metrik) → Faz7(E2E) → Faz8(CI) → Faz9(Grafik)
```

---

## 3. Mimari

### 3.1 Dağıtık akış

```
Producer (Docker) --AMQP publish--> [exchange: logs] --> [queue: logs.raw]
                                              |
                                              v
                                    Middleware (Docker)
                                              |
                         +--------------------+--------------------+
                         v                    v                    v
                   sysadmin.md        developer.json       security.csv
                   /health            /metrics
```

Producer ve Middleware birbirini doğrudan çağırmaz; mesajlar kalıcı (`delivery_mode=2`) JSON olarak kuyrukta tutulur. İki geliştirilen modül ödev kapsamındaki “iki Docker modülü”dür; RabbitMQ altyapı bileşenidir.

### 3.2 Pipeline (Chain of Responsibility)

Sıra sabittir; KVKK ihlali olmaması için maskeleme her zaman önceliklidir.

```
AnonymizationHandler → FilterHandler → EnrichmentHandler → TerminalHandler
        |                    |                  |                  |
     maskeler            drop?              Decorator         Strategy +
     TC/kart/...        None ise STOP       zinciri           dosyaya yaz
```

Zincir kurulumu (mantık):

```python
anonymizer.set_next(filter_handler).set_next(enrichment).set_next(terminal)
```

`AbstractHandler.handle`: `process()` sonucu `None` ise zincir kesilir (filtre); aksi halde `_next.handle()` çağrılır.

### 3.3 Ortak veri modeli

Tüm modüller aynı **Pydantic v2** `LogRecord` yapısını kullanır:

| Alan | Tip / değerler |
|------|----------------|
| id | UUID4 |
| timestamp | ISO8601 UTC |
| level | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| type | LOG, ERROR, TRANSACTION, ACCESS |
| role | sysadmin, developer, security |
| source | Üreten bileşen adı |
| message | Metin |
| payload | Esnek sözlük (TC, IBAN, vb.) |

### 3.4 Teknoloji

| Katman | Seçim |
|--------|--------|
| Dil | Python 3.11+, type hints |
| Mesajlaşma | RabbitMQ topic exchange, `aio-pika`, prefetch_count=50 |
| API | FastAPI — sağlık ve metrik |
| Çıktı | Append modunda rol dosyaları |

---

## 4. Gereksinimler

### 4.1 Güvenlik (KVKK)

Maskeleme **message** ve **payload** içindeki tüm string değerlere uygulanır. Kurallar deterministik ve **idempotent** (zaten maskeli metin tekrar bozulmaz).

| Tip | Tespit | Örnek maske |
|-----|--------|-------------|
| TC | 11 hane, ilk hane 0 değil | `12xxxxxxxx1` |
| Kart | 13–19 hane (Luhn) | `5235 xxxxxx 1234` |
| IBAN TR | `TR` + 24 hane | Baş/son korunur |
| SWIFT | BIC formatı | `***SWIFT***` |
| E-posta | Basit RFC deseni | `m***@domain` |

Pipeline’da bu adım **AnonymizationHandler** ile ilk halkadır; disk yazımından önce tamamlanır.

Örnek maskeli çıktı: `tc=49xxxxxxxx4`, `swift=***SWIFT***`, mesaj `<Şüpheli transfer...>`.

### 4.2 Zenginleştirme (Decorator)

`EnrichmentHandler` içinde beş Decorator sırayla çalışır:

| # | Decorator | Etki |
|---|-----------|------|
| 1 | SenderId | `payload.sender_id` |
| 2 | TransactionInfo | type=TRANSACTION → `transaction_no` |
| 3 | Criticality | level/type → low/med/high/critical |
| 4 | RoleTag | security `<m>`, developer `{m}`, sysadmin `{~m~}` |
| 5 | Debug | level=DEBUG → `debug=true` |

```python
for decorator in decorators:
    log = decorator.apply(log)
```

### 4.3 Filtreleme (performans)

Erken drop ile CPU ve I/O tasarrufu hedeflenir.

| Koşul | Aksiyon |
|-------|---------|
| `level ∈ {DEBUG, INFO, WARNING}` | DROP (`process` → `None`) |
| `source` regex `^docker\.` | DROP |
| Diğer | KEEP |

Filtre kararı **FilterHandler**’da; `dropped_total` sayacı **consumer**’da artırılır (sorumluluk ayrımı).

E2E: 117/300 ≈ **%39** drop — `noise_info_warning` ve `docker_internal_noise` senaryoları doğrulandı.

### 4.4 Biçimlendirme (Strategy + Factory)

**Strategy:** `Formatter.format(log) -> str` — JSON, CSV, Markdown, HTML somut sınıfları.

**Factory:** `formatter_for_role(role)` rol haritasına göre somut Strategy döndürür.

| Rol | Varsayılan format | Kullanım |
|-----|-------------------|----------|
| sysadmin | Markdown | Operasyonel okuma |
| developer | JSONL | Otomasyon / parse |
| security | CSV | Tablo analizi |

HTML Strategy mevcuttur; rol–format eşlemesi yapılandırma ile değiştirilebilir (ödevde HTML/CSV/JSON isteği).

---

## 5. Tasarım Kalıpları

| Kalıp | Rol |
|-------|-----|
| Chain of Responsibility | Pipeline handler zinciri |
| Strategy | Format algoritmaları |
| Decorator | Zenginleştirme |
| Factory | Log + formatter üretimi |
| Singleton | `METRICS` tek örnek |

```
Producer: LogFactory (Factory)
    → AMQP → Middleware: CoR → Decorator → Strategy+Factory → dosya
                              ↘ Singleton (METRICS)
```

### 5.1 Chain of Responsibility

İstek sırayla handler’lardan geçer; filtre `None` ile zinciri keser. Open/Closed: yeni handler = yeni halka, mevcut kod minimal değişir.

### 5.2 Strategy

Biçimlendirme algoritması çalışma anında değişir; `Formatter` arayüzü yeni format eklemeyi kolaylaştırır (Liskov: tüm formatter’lar aynı `LogRecord` girdisini kabul eder).

### 5.3 Decorator

Log nesnesine davranış ekleme; inheritance yerine kompozisyon. Her Decorator tek sorumluluk (SRP).

### 5.4 Factory

`LogFactory.create_log()`: ağırlıklı senaryo seçimi + `LogRecord` üretimi gizlenir. `formatter_for_role()`: rol → Strategy eşlemesi tek noktada.

### 5.5 Singleton

`METRICS = MetricsCollector()` — `consumed_total`, `processed_total`, `dropped_total`, `errors_total`, gecikme listesi. `/metrics` JSON snapshot (p50/p95/p99 dahil).

### 5.6 Bütünleşik akış

Factory (üret) → kuyruk → CoR (maskele, filtre, zenginleştir) → Strategy (biçim) → append dosya; boyunca Singleton güncellenir.

---

## 6. Senaryolar

Ağırlıklı rastgele seçim (`SCENARIO_WEIGHTS`); ödev davranışlarının tamamı:

| Senaryo | level / type / role | Test ettiği özellik |
|---------|---------------------|---------------------|
| kvkk_transaction | ERROR, TRANSACTION, security | TC, IBAN, SWIFT maskesi |
| failed_login_burst | ERROR, ACCESS, security | `<...>` etiket |
| dev_404 | ERROR, ACCESS, developer | `{...}` etiket |
| sysadmin_datetime_mismatch | CRITICAL, LOG, sysadmin | `{~...~}`, criticality |
| noise_info_warning | INFO/WARNING | Filtre drop |
| docker_internal_noise | INFO, source docker.* | Filtre drop |
| card_purchase | ERROR, TRANSACTION, security | Kart maskesi |

**Demo:** ~200 log, 50 log/s, batch 20.  
**Stres:** 100.000 log, 5000 log/s, batch 200; ek ramp/burst profilleri.

---

## 7. Test ve Doğrulama

| Grup | Adet | Kapsam |
|------|------|--------|
| Producer | 3 | PII şekilleri, 7 senaryo, LogRecord alanları |
| Middleware güvenlik | 4 | Maskeleme, idempotency, /health, /metrics |
| Pipeline | 3 | Filtre, enrichment, transaction_no |
| Formatting | 2 | Rol dosyaları, JSON serileştirme |
| Metrik/stres | 3 | Quantile snapshot, reporter, load profile |
| E2E betik | 2 | Smoke, burst |
| CI | 1 | Workflow jobs |
| Performans raporu | 5 | Grafik üretimi |
| **Toplam** | **21** | `pytest -q` |

E2E: Docker Compose up → Producer ~300 publish → çıktı dosyaları + metrik doğrulama → kuyruk örnekleme. CI: her push’ta unit test + isteğe bağlı E2E job.

---

## 8. Performans

### 8.1 Ölçüm koşulları

| Alan | Değer |
|------|-------|
| Tarih | 4 Haziran 2026 |
| Deneme türü | Otomatik uçtan uca (E2E) |
| Gönderilen log sayısı | ~300 |
| Ortam | Docker (Producer + Middleware + RabbitMQ) |

### 8.2 Pipeline sayaçları

| Metrik | Değer | Açıklama |
|--------|-------|----------|
| consumed_total | 300 | Kuyruktan okunan toplam mesaj |
| processed_total | 183 | Filtre sonrası dosyaya yazılan |
| dropped_total | 117 | Filtreyle elenen (%39) |
| errors_total | 0 | İşleme hatası |

| Türetilmiş oran | Hesap | Sonuç |
|-----------------|-------|--------|
| Filtre oranı | 117 ÷ 300 | %39 |
| İşleme oranı | 183 ÷ 300 | %61 |

### 8.3 İşleme gecikmesi (pipeline içi)

| Yüzdelik | Saniye | Milisaniye (yaklaşık) | Yorum |
|----------|--------|------------------------|--------|
| p50 (medyan) | 0,00149 | ~1,5 ms | Tipik kayıt süresi |
| p95 | 0,00906 | ~9,1 ms | Kayıtların %95’i bu sürenin altında |
| p99 | 0,01562 | ~15,6 ms | En yavaş %1 için üst sınır |

### 8.4 Kuyruk derinliği (8 saniye örnekleme)

| Zaman (sn) | Kuyruktaki mesaj (depth) |
|------------|--------------------------|
| 0,0 | 0 |
| 1,0 | 1 |
| 2,0 | 1 |
| 3,0 | 1 |
| 4,0 | 1 |
| 5,0 | 1 |
| 6,0 | 1 |
| 7,0 | 0 |

| Özet | Değer |
|------|-------|
| Minimum derinlik | 0 |
| Maksimum derinlik | 1 |
| Gözlem | Kuyruk birikmedi; tüketim yayına yetişti |

### 8.5 Performans özeti (tek tablo)

| Kriter | Sonuç | Değerlendirme |
|--------|-------|----------------|
| Throughput / tıkanma | Derinlik 0–1 | Darboğaz yok |
| Filtre etkisi | %39 drop | Gürültü senaryoları elendi |
| Tipik gecikme (p50) | ~1,5 ms | Düşük pipeline gecikmesi |
| Hata oranı | 0 | Kararlı koşum |

### 8.6 Ek ölçüm senaryoları (referans)

| Senaryo | Parametre (örnek) | Amaç |
|---------|-------------------|------|
| Stres | 100.000 log, 5000 log/s, batch 200 | Üst sınır throughput |
| Ramp profili | Kademeli artan yük | Ne zaman gerilme başlar |
| Burst profili | Ani yük | Kısa süreli spike dayanımı |
| Filtre karşılaştırması | FILTER_ENABLED açık / kapalı | Drop oranı farkı |

---

## 9. Yapay Zeka Kullanımı

| Araç | Amaç | Doğrulama |
|------|------|-----------|
| Cursor / LLM | Kod taslağı, test, rapor iskeleti | 21 pytest + E2E + manuel kural kontrolü |

Rapor metni ve kod taslaklarında AI kullanıldı; metrikler ve maskeli çıktı örnekleri gerçek koşumdan alındı.

---

## 10. Sonuç

- İki modül + RabbitMQ tampon mimarisi kuruldu.  
- Dört ödev görevi (güvenlik, zenginleştirme, filtre, biçim) pipeline ile karşılandı.  
- Beş tasarım kalıbı gerekçeli uygulandı (5 ≥ 3).  
- 21 test + E2E + CI ile doğrulandı.  
- Performans: %39 filtre, p50 ~1,5 ms, kuyruk stabil.

**Sınırlar:** Tek host Docker; Singleton tek süreç; DLQ opsiyonel.

**Gelecek:** Kafka, OpenTelemetry, dağıtık metrik store.

---

*Rapor sonu.*
