# Faz 1 Detayli Rapor - Producer Cekirdegi

Tarih: 2026-06-01  
Faz Durumu: Tamamlandi

## 1) Faz Ozeti

Faz 1'de producer tarafinin cekirdegi implement edildi. Bu kapsamda:

- Konfigurasyon katmani (`config.py`)
- Hassas veri uretecleri (`sensitive_data.py`)
- Senaryo modeli ve agirlikli secim mantigi (`scenarios.py`)
- Factory tabanli log uretimi (`log_factory.py`)
- RabbitMQ publish katmani (`transport/publisher.py`)
- CLI tabanli calistirma akisi (`main.py`)

tamamlandi.

Faz sonunda birim testleri ve dry-run smoke testi calistirildi.

## 2) Yapilan Teknik Isler

### 2.1 Config Katmani

`producer/src/config.py` ile `ProducerConfig` dataclass'i eklendi.

Saglanan parametreler:

- AMQP URL
- Exchange / Routing key
- Total log adedi
- Batch boyutu
- Rate (log/sn)
- Senaryo seed
- Producer ID

Boylece CLI argumanlari + env degerleri tek noktadan yonetilebilir hale geldi.

### 2.2 Hassas Veri Uretecleri

`producer/src/generators/sensitive_data.py` icinde:

- `generate_tckn`
- `generate_credit_card`
- `generate_email`
- `generate_iban`
- `generate_swift`
- `generate_amount`

fonksiyonlari eklendi. Bunlar Faz 2+ tarafinda anonimlestirme testlerine girdi uretecek.

### 2.3 Senaryo Jeneratoru

`producer/src/generators/scenarios.py` icinde:

- `ScenarioOutput` veri modeli
- `SCENARIO_WEIGHTS` (agirlikli dagilim)
- `generate_scenario(...)`
- `weighted_scenario_name(...)`

eklendi.

SPECS'teki ana senaryolar kapsandi:

- `kvkk_transaction`
- `failed_login_burst`
- `dev_404`
- `sysadmin_datetime_mismatch`
- `noise_info_warning`
- `docker_internal_noise`
- `card_purchase`

### 2.4 Factory ile Log Uretimi

`producer/src/generators/log_factory.py` icinde `LogFactory` eklendi.

Factory:

- Senaryo agirliklarina gore secim yapiyor,
- Senaryo ciktisini `shared.log_schema.LogRecord` formatina donusturuyor,
- `payload` icine `scenario` ve `producer_id` alanlarini ekliyor.

Bu, raporda "Factory pattern" gosterimi icin dogrudan kullanilabilir.

### 2.5 RabbitMQ Publisher

`producer/src/transport/publisher.py` ile `RabbitPublisher` eklendi.

Saglanan yetenekler:

- Robust AMQP connection (`aio-pika`)
- Topic exchange declaration (`logs`)
- Durable queue declaration/bind (`logs.raw`)
- Persistent mesaj publish (`DeliveryMode.PERSISTENT`)
- Batch publish
- Rate-limited stream publish
- Basit throughput metrik donusu (`published`, `elapsed`, `throughput`)

### 2.6 CLI Akisi

`producer/src/main.py` guncellendi.

Desteklenen argumanlar:

- `--total`
- `--batch`
- `--rate`
- `--amqp-url`
- `--dry-run`

`--dry-run` modunda publish yapmadan sadece uretim akisi test ediliyor.
Onemli duzeltme: `aio-pika` bagimliligi olmayan ortamlarda dry-run calissin diye publisher importu lazy hale getirildi.

## 3) Degisen Dosyalar

- `shared/__init__.py`
- `producer/src/config.py`
- `producer/src/generators/__init__.py`
- `producer/src/generators/sensitive_data.py`
- `producer/src/generators/scenarios.py`
- `producer/src/generators/log_factory.py`
- `producer/src/transport/__init__.py`
- `producer/src/transport/publisher.py`
- `producer/src/main.py`
- `tests/test_phase1_producer.py`
- `docs/STATE.md`

## 4) Calistirilan Testler/Komutlar

1. Dry-run smoke test:

```bash
python -m producer.src.main --dry-run --total 20 --batch 5 --rate 100
```

2. Faz 1 unit testleri:

```bash
python -m pytest -q tests/test_phase1_producer.py
```

3. Lint/diagnostik kontrolu (degisen producer dosyalari):

- `producer/src/main.py`
- `producer/src/config.py`
- `producer/src/generators/*`
- `producer/src/transport/publisher.py`
- `tests/test_phase1_producer.py`

## 5) Test Sonuclari

- Dry-run smoke test: **Basarili** (`Generated 20 logs`)
- Unit testler: **3 passed**
- Lint/diagnostik: **Yeni hata yok**

## 6) Riskler / Acik Maddeler

- Publisher tarafi gercek broker ile entegre smoke test (live publish) Faz 2 ile middleware consumer gelince daha anlamli hale gelecek.
- `pytest` ve `aio-pika` lokal ortama sonradan kuruldu; CI ortaminda requirements bazli yukleme dogrulanmali.

## 7) Sonraki Faz

Faz 2 odagi:

- Middleware `config.py`
- `transport/consumer.py` (aio-pika)
- `pipeline/handler.py` ve `pipeline_builder.py`
- `security/rules.py` + `security/anonymizer.py`
- `pipeline/anonymization_handler.py`
- `api/routes.py` + `main.py` (health/metrics)
- Faz 2 testleri

## 8) Revizyon - Push Hazirlik Notu

Bu rapor, kullanici istegi uzerine push oncesi tekrar gozden gecirildi ve guncellendi.

Durum:

- Faz 1 teknik kapsaminda degisiklik yok.
- Test sonuclari degismedi (3/3 unit test geciyor).
- Bu klasorde (`d:\my-projects\yazılım-ödev-middleware`) su an `.git` dizini bulunmadigi icin dogrudan `git add/commit/push` adimlari calistirilamiyor.

Push icin gerekli kosullar:

1. Proje klasorunun git repo olarak baslatilmasi (`git init`) veya mevcut bir repo icine alinmasi.
2. Uzak repository (`origin`) tanimlanmasi.
3. Sonrasinda commit + push adimlari.
