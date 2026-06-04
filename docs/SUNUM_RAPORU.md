# Sunum Raporu — Data Middleware Projesi

> **Toplam Süre:** ~15 dakika  
> **Format:** Ekran paylaşımlı video kaydı  
> **Araçlar:** Terminal, VS Code / Kod editörü, Tarayıcı (RabbitMQ arayüzü), Dosya gezgini

---

## Genel Akış

| # | Bölüm | Süre |
|---|-------|------|
| 1 | Giriş ve mimari anlatım | 1–2 dk |
| 2 | Sistemi başlatma ve canlı demo | 3–4 dk |
| 3 | 4 temel gereksinimi gösterme | 4–5 dk |
| 4 | Tasarım kalıpları — kodda gösterme | 2–3 dk |
| 5 | Performans ve stres testi | 1–2 dk |
| 6 | CI/CD (GitHub Actions) | 1 dk |
| 7 | Kapanış | 30 sn |

---

## Bölüm 1 — Giriş ve Mimari Anlatım (1–2 dk)

### Ne Söylenecek

> "Bu proje, bir borsa kurumunun log altyapısını simüle ediyor. Sistemde iki ayrı Docker modülü var: **Producer** ve **Middleware**. Producer, saniyede yüzlerce borsa log kaydı üretiyor. Middleware bu logları alıp dört aşamadan geçiriyor: önce kişisel verileri KVKK kapsamında maskeler, sonra gereksiz logları eler, ardından her loga ek bilgi ekler ve son olarak kullanıcı rolüne göre farklı formatlarda dosyaya yazar."

### Ne Gösterilecek

**→ `README.md` dosyasını aç**, "Mimari" başlığı altındaki Mermaid diyagramını göster:

> "README artık projeyi ilk kez gören biri için özet, mimari, demo komutları, çıktı dosyaları ve grafik referanslarını tek yerde topluyor. Sunum sırasında bu dosyayı ana rehber gibi kullanabiliriz."

Ardından `AGENTS.md` dosyasını aç, "Mimari" başlığı altındaki kısa ASCII diyagramı göster:

```
Producer (Docker)  --publish-->  RabbitMQ (broker)  --consume-->  Middleware (Docker)
Middleware pipeline:  Anonymize -> Filter -> Enrich -> Format/Route
```

> Bu diyagram dosyada tam olarak bu şekilde yer alıyor. Ekranda yakınlaştırarak göster.

Hemen altında `docs/SPECS.md` dosyasını aç, **Bölüm 5 (Rol → Format Eşlemesi)** tablosunu göster:

| Rol | Format | Dosya |
|-----|--------|-------|
| sysadmin | Markdown | output/sysadmin.md |
| developer | JSON | output/developer.json |
| security | CSV | output/security.csv |

> "Hangi rolün hangi formatı aldığı bu tabloda tanımlı. Kod değişmeden bu eşleştirmeyi yapılandırma dosyasından değiştirebilirsiniz."

**→ Söz arasında `docker-compose.yml` dosyasını aç**, şunu göster:

- `rabbitmq` servisi — mesaj köprüsü
- `middleware` ve `producer` servisleri — iki uygulama modülü
- `depends_on: condition: service_healthy` satırı — RabbitMQ hazır olmadan hiçbir şey başlamıyor

> "RabbitMQ sunucu, iki modül arasındaki köprü. Producer doğrudan middleware'e değil, bir kuyruğa yazıyor. Bu mimari yüksek hacimli trafikte kuyruk tamponu sağlıyor."

---

## Bölüm 2 — Sistemi Başlatma ve Canlı Demo (3–4 dk)

### Adım 2.1 — Sistemi Başlat

**Terminal 1'i aç**, proje kök dizinine git:

```bash
docker compose up --build rabbitmq middleware
```

> "Demo için önce yalnızca RabbitMQ ve Middleware'i başlatıyorum. Producer'ı ayrı terminalde kontrollü çalıştıracağız; böylece kuyruk başlangıçta boş kalıyor ve mesaj akışını net görebiliyoruz."

**→ Konsolda şu çıktıyı bekle ve göster:**

```
dm-rabbitmq   | Server startup complete
dm-middleware | INFO:     Application startup complete.
dm-middleware | INFO:     Uvicorn running on http://0.0.0.0:8000
```

> "Middleware, FastAPI web sunucusuyla ayağa kalktı. Port 8000'den sağlık ve metrik sorguları kabul ediyor."

---

### Adım 2.2 — RabbitMQ Yönetim Arayüzü

**Tarayıcıyı aç → `http://127.0.0.1:15672`** *(kullanıcı adı: guest, şifre: guest)*

> "Bu RabbitMQ'nun kendi yönetim paneli. Buradan kuyruğun anlık durumunu izleyebiliyoruz."

**→ Gösterilecekler:**

1. **Queues** sekmesi → `logs.raw` kuyruğunu tıkla
2. Şu an 0 mesaj var — sistem bekliyor
3. Sayfayı bu hâlde bırak, bir sonraki adımda mesajların dolduğunu göstereceğiz

---

### Adım 2.3 — Producer'ı Çalıştır

**Terminal 2'yi aç:**

```bash
docker compose run --build --rm producer python -m producer.src.main --total 200 --rate 50 --batch 20
```

> "Producer 200 log kaydı üretiyor, saniyede 50 tane, 20'li gruplar hâlinde gönderiyor."

**→ Terminalden şu çıktıyı göster:**

```
Publish done. published=200 elapsed=4.10s throughput=48.70 log/s
```

**→ RabbitMQ sekmesine geç**, kuyruğun dolup boşaldığını göster:

> "Mesajlar kuyruğa düştü, middleware anında tüketiyor. Kuyruk derinliği neredeyse sıfırda kalıyor — sistem akıcı çalışıyor."

---

### Adım 2.4 — Çıktı Dosyalarını Göster

**Dosya gezginini aç → `output/` klasörü**

> "Middleware, işlediği logları üç ayrı dosyaya yazdı. Her dosya farklı bir role ait."

Üç dosyayı sırayla aç ve birkaç satır göster:

| Dosya | Ne Gösterilecek |
|-------|-----------------|
| `output/sysadmin.md` | Markdown başlıklı, insan okunabilir format |
| `output/developer.json` | Her satır bir JSON objesi — makine tarafından işlenmeye uygun |
| `output/security.csv` | CSV başlığı ve satırları — tablo analizine uygun |

---

## Bölüm 3 — 4 Temel Gereksinimi Gösterme (4–5 dk)

### Gereksinim 1 — KVKK: Kişisel Veri Maskeleme

> "KVKK kapsamında hiçbir kişisel veri ham hâliyle diske yazılmamalı. Bunu kodda nasıl sağladığımıza bakalım."

**→ `middleware/src/security/rules.py` dosyasını aç**, şu satırları göster:

```python
TC_PATTERN    = re.compile(r"\b[1-9]\d{10}\b")
CARD_PATTERN  = re.compile(r"\b(?:\d[ -]?){13,19}\b")
IBAN_PATTERN  = re.compile(r"\bTR\d{24}\b")
SWIFT_PATTERN = re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
```

> "Beş tür hassas veri için düzenli ifade tanımladık: TC kimlik, kredi kartı, IBAN, SWIFT ve e-posta. Bunların tespiti ve maskelenmesi pipeline'ın ilk adımında gerçekleşiyor — sonraki hiçbir adım ham veriyle karşılaşmıyor."

**→ `output/security.csv` dosyasına dön**, maskeleme örneklerini göster:

```
Özgün veri:          12345678901
Maskelenmiş hâli:    12xxxxxxxx1

Özgün veri:          5235 1234 1234 1234
Maskelenmiş hâli:    5235 xxxxxx 1234

Özgün veri:          TR330006100519786457841326
Maskelenmiş hâli:    TR33xxxxxxxxxxxxxxxxxxxx26

Özgün veri:          melih@example.com
Maskelenmiş hâli:    m***@example.com
```

> "Hem log mesajının içinde geçen hem de ek bilgi alanındaki (payload) kişisel veriler ayrı ayrı taranıyor ve maskeleniyor. Maskeleme deterministik: aynı girdi her zaman aynı çıktıyı veriyor."

---

### Gereksinim 2 — Filtreleme: Gereksiz Logları Eleme

> "Borsa sisteminde çok sayıda gürültü log üretiliyor: INFO/WARNING seviyesindekiler ve Docker'ın kendi iç mesajları. Bunların sistemi geçmesine izin vermiyor, erken eliyoruz."

**→ `middleware/src/pipeline/filter_handler.py` dosyasını aç:**

```python
if log.level in {LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING}:
    return None          # pipeline'ı burada kesiyor

if DOCKER_SOURCE_RE.match(log.source):
    return None
```

> "Handler `None` döndürdüğünde log pipeline'dan çıkar. Filtre kararı burada veriliyor."

**→ `middleware/src/transport/consumer.py` dosyasını aç**, metrik sayacının arttığı yeri göster:

```python
result = self._process_log(log)
if result is None:
    METRICS.dropped_total += 1
```

> "Sayaç artışı consumer tarafında tutuluyor. Böylece pipeline yalnızca karar veriyor, metrik toplama ise mesaj tüketim katmanında merkezî kalıyor."

**→ Tarayıcıda `http://127.0.0.1:8000/metrics` adresini aç:**

```json
{
  "consumed_total": 200,
  "processed_total": 87,
  "dropped_total": 113,
  "errors_total": 0
}
```

> "200 log geldi, 113'ü filtre aşamasında elendi. Bu logların büyük kısmı INFO/WARNING veya Docker kaynağından gelen gürültü. Sadece 87 anlamlı log ileriye geçti."

---

### Gereksinim 3 — Zenginleştirme: Loglara Ek Bilgi Ekleme

> "Filtreyi geçen her log zenginleştirme adımından geçiyor. Burada her loga anlamlı bağlam bilgileri ekleniyor."

**→ `middleware/src/enrichment/enrichers.py` dosyasını aç**, şu sınıfları göster:

**`SenderIdDecorator`** — Kaynağın kimliği:
```python
payload.setdefault("sender_id", payload.get("producer_id", "unknown-sender"))
```

**`TransactionInfoDecorator`** — İşlem numarası (yalnızca TRANSACTION tipindeki loglara):
```python
payload.setdefault("transaction_no", f"txn-{uuid4().hex[:12]}")
```

**`CriticalityDecorator`** — Kritiklik derecesi:
```python
if log.level == LogLevel.CRITICAL:   criticality = "critical"
elif log.level == LogLevel.ERROR:    criticality = "high"
```

**`RoleTagDecorator`** — Role göre mesaj etiketi:
```python
if log.role == UserRole.security:    message = f"<{log.message}>"
elif log.role == UserRole.developer: message = f"{{{log.message}}}"
else:                                message = f"{{~{log.message}~}}"
```

> "Her dekoratör logu alıp üzerine bir şey ekleyerek döndürüyor. Zincir hâlinde çalışıyorlar — biri biter, diğeri başlar. Bu Decorator tasarım kalıbı."

**→ `output/security.csv` veya `output/developer.json` dosyasından** gerçek bir satır göster, şu alanların varlığını işaret et:

- `sender_id`
- `transaction_no` (TRANSACTION tipindekilerde)
- `criticality`
- Mesaj başı/sonu etiketleri (`<...>`, `{...}`, `{~...~}`)

---

### Gereksinim 4 — Rol Bazlı Biçimlendirme

> "Her kullanıcı grubunun ihtiyacı farklı. Sistem yöneticisi okunabilir bir rapor istiyor, geliştirici makine tarafından işlenebilir JSON istiyor, güvenlik ekibi ise Excel'e alabilmek için CSV istiyor."

**→ `middleware/src/formatting/formatter_factory.py` dosyasını aç:**

```python
def formatter_for_role(role: UserRole) -> Formatter:
    target = ROLE_FORMAT_MAP.get(role.value, "json")
    if target == "markdown":   return MarkdownFormatter()
    if target == "csv":        return CsvFormatter()
    if target == "html":       return HtmlFormatter()
    return JsonFormatter()
```

> "Fabrika fonksiyonu role bakıyor ve doğru biçimlendiriciyi seçiyor. Eşleşme tablosu yapılandırma dosyasında — kodu değiştirmeden hangi rolün hangi formatı alacağını değiştirebiliriz."

**→ Üç dosyayı yan yana aç:**

`output/sysadmin.md`:
```markdown
## ERROR | trade.api | 2026-06-02T...
**Message:** {~datetime mismatch between nodes~}
**Criticality:** high
```

`output/developer.json`:
```json
{"level": "ERROR", "source": "auth.service", "message": "{404 GET /users/42}", "payload": {"sender_id": "prod-1", "criticality": "high"}}
```

`output/security.csv`:
```
id,timestamp,level,type,role,source,message,...
...,ERROR,TRANSACTION,security,trade.api,"<Suspicious transfer: amount=47832.50>",...
```

> "Aynı sistem, aynı veri, üç farklı format. Biçimlendirme seçimi tamamen otomatik."

---

## Bölüm 4 — Tasarım Kalıpları (2–3 dk)

> "Ödev en az üç tasarım kalıbı gerektiriyor. Biz beş tane kullandık. Hepsini kısaca gösteriyorum."

### Kalıp 1 — Chain of Responsibility (Sorumluluk Zinciri)

**→ `middleware/src/pipeline/pipeline_builder.py` dosyasını aç:**

```python
def build_pipeline() -> AbstractHandler:
    anonymizer = AnonymizationHandler()
    filter_handler = FilterHandler()
    enrichment = EnrichmentHandler()
    terminal = TerminalHandler()
    anonymizer.set_next(filter_handler).set_next(enrichment).set_next(terminal)
    return anonymizer
```

**→ `middleware/src/pipeline/handler.py` dosyasını aç:**

```python
def handle(self, log: LogRecord) -> LogRecord | None:
    current = self.process(log)
    if current is None:
        return None     # elendi, zincirsonu
    if self._next is None:
        return current  # son adım
    return self._next.handle(current)
```

> "Her handler sadece kendi işini yapıyor, sonra bir sonrakine iletiyor. `None` döndürürse zincir kırılıyor. Yeni bir adım eklemek için sadece `.set_next()` ile zincire bağlamak yeterli."

---

### Kalıp 2 — Strategy (Strateji)

**→ `middleware/src/formatting/formatter.py` dosyasını aç:**

```python
class Formatter(ABC):
    @abstractmethod
    def format(self, log: LogRecord) -> str:
        raise NotImplementedError
```

> "Soyut `Formatter` sınıfı sözleşmeyi tanımlıyor. JSON, CSV, Markdown, HTML biçimlendiricilerin hepsi bu sözleşmeyi uygular. `RoleRouter` hangi biçimlendiriciyle çalıştığını bilmek zorunda değil — sadece `.format()` çağırıyor. Çalışma anında strateji değişebiliyor."

---

### Kalıp 3 — Decorator (Süsleme)

**→ `middleware/src/enrichment/enrichers.py` dosyasını aç, `apply_enrichment` fonksiyonunu göster:**

```python
def apply_enrichment(log: LogRecord) -> LogRecord:
    decorators = [
        SenderIdDecorator(),
        TransactionInfoDecorator(),
        CriticalityDecorator(),
        RoleTagDecorator(),
        DebugDecorator(),
    ]
    current = log
    for decorator in decorators:
        current = decorator.apply(current)
    return current
```

> "Her dekoratör logu alıp zenginleştirilmiş bir kopyasını döndürüyor. Orijinal log değişmiyor. Yeni bir bilgi türü eklemek istediğimizde mevcut kodu değiştirmiyoruz, sadece listeye yeni bir dekoratör ekliyoruz."

---

### Kalıp 4 — Factory (Fabrika)

**→ `producer/src/generators/log_factory.py` dosyasını aç:**

```python
class LogFactory:
    def create_log(self) -> LogRecord:
        scenario_name = weighted_scenario_name(self._rng)
        scenario = generate_scenario(scenario_name, self._rng)
        ...
        return LogRecord(...)
```

> "Producer, `LogFactory` üzerinden log üretiyor. Hangi senaryonun seçileceğini, ne tür veri içereceğini fabrika biliyor. Dışarıdan sadece `create_log()` çağrılıyor. Aynı kalıp middleware tarafında `formatter_factory.py`'da da var — role bakıp doğru formatter'ı üretiyor."

---

### Kalıp 5 — Singleton (Tekil Örnek)

**→ `middleware/src/metrics/collector.py` dosyasını aç, son satırı göster:**

```python
METRICS = MetricsCollector()
```

> "Tüm modüller bu tek `METRICS` nesnesini import ediyor. Uygulama boyunca tek bir örnek var — hem consumer hem de API endpoint'i aynı sayaçlara bakıyor. Bu Singleton kalıbı."

---

## Bölüm 5 — Performans ve Stres Testi (1–2 dk)

> Bu bölümde gösterilecek grafikler için video çekiminden önce `python scripts/e2e_smoke.py` ve ardından `python scripts/performance_report.py --reports-dir reports --skip-queue-fetch` çalıştırılmış olmalı. Bu hazırlık `reports/e2e_metrics.json`, `reports/queue_samples.jsonl` ve `reports/plots/` altındaki PNG dosyalarını üretir.

### Adım 5.1 — Stres Testi Çalıştır

**Terminal 2'de:**

```bash
docker compose run --rm producer python -m producer.src.main --total 5000 --rate 2000 --batch 200
```

> "Şimdi saniyede 2000 log gönderiyoruz. RabbitMQ panelini izleyelim."

**→ `http://127.0.0.1:15672` → Queues → `logs.raw`**

> "Kuyruk derinliği dalgalanıyor ama birikmiyor — middleware yetişiyor. Gerçek sistemde middleware daha yavaş olsaydı kuyruk büyürdü, bu da ölçeklendirme ihtiyacına işaret ederdi."

---

### Adım 5.2 — Metrik Grafiklerini Göster

**→ `reports/plots/` klasörünü aç**

> "Bu grafikler E2E smoke ve performance report scriptleriyle otomatik üretildi. Ham metrik snapshot'ı `reports/e2e_metrics.json`, kuyruk örnekleri ise `reports/queue_samples.jsonl` dosyasında tutuluyor."

**`pipeline_counts.png`** — Ekran paylaşımında aç:

> "İşlenen, elenen ve hata veren log sayıları. Elenen logların oranı yüksek — bu beklenen: INFO/WARNING çoğunlukta."

**`latency_percentiles.png`:**

> "p50, p95 ve p99 işleme süresi. Medyan çok düşük, p99 biraz daha yüksek — bu normal dağılım. Sistemin neredeyse tüm logları milisaniye seviyesinde işlediğini görüyoruz."

**`queue_depth.png`** *(varsa)*:

> "E2E test sırasında kaydedilen kuyruk derinliği. Yük bitince kuyruk sıfıra iniyor."

**→ `reports/performance_summary.md` dosyasını aç:**

> "Tüm bu rakamlar otomatik olarak bir özet Markdown dosyasına da yazılıyor. Raporlama altyapısı tamamen otomatik."

---

### Adım 5.3 — Metrik API'sini Göster

**Tarayıcıda: `http://127.0.0.1:8000/metrics`**

```json
{
  "consumed_total": 5000,
  "processed_total": 2143,
  "dropped_total": 2857,
  "errors_total": 0,
  "processing_latency_seconds": {
    "p50": 0.00031,
    "p95": 0.00089,
    "p99": 0.00142
  }
}
```

> "Bu endpoint'i izleme araçlarına (Prometheus, Grafana gibi) doğrudan bağlayabiliriz. p50 gecikme 0.31 ms — son derece hızlı."

---

## Bölüm 6 — CI/CD: Otomatik Test Altyapısı (1 dk)

**→ Tarayıcıda GitHub deposunu aç → Actions sekmesi**

> "Projeye CI/CD pipeline'ı da ekledik. Her `git push`'ta GitHub'ın sunucuları otomatik olarak şunları yapıyor:"

**→ Son başarılı workflow'u tıkla**, iki işi göster:

**`tests` işi:**
- Python bağımlılıkları kurulumu
- `pytest -q` → tüm testler
- `docker compose config` → yapılandırma doğrulama

**`e2e-smoke` işi:**
- Gerçek bir Docker ortamı ayağa kaldırıyor
- Producer log gönderiyor
- Çıktı dosyaları ve `/metrics` doğrulanıyor
- Oluşan `output/` ve `reports/` dosyaları artifact olarak arşivleniyor

**→ Artifacts bölümünü göster** — "output" ve "reports" indirilebilir hâlde.

> "Her push'ta test suite otomatik koşuyor. Yeşil işaret görüyorsak Python testleri, Docker Compose doğrulaması ve E2E smoke akışı sağlıklı."

---

## Bölüm 7 — Kapanış (30 sn)

**→ Terminalde sistemi kapat:**

```bash
docker compose down
```

> "Sistem temiz bir şekilde kapandı."

**Söylenecekler:**

> "Bu projede beş tasarım kalıbı, KVKK uyumlu veri maskeleme, rol bazlı çıktı biçimlendirme, stres testi altyapısı ve otomatik CI/CD pipeline'ı uyguladık. Kod GitHub'da açık, her push'ta testler otomatik çalışıyor."

**→ Ekranda göster:**

- GitHub repo bağlantısı
- `README.md` → Projenin özet sayfası
- `docs/SUNUM_RAPORU.md` → Bu video akışı

---

## Hazırlık Kontrol Listesi

Video çekiminden önce aşağıdakilerin hazır olduğundan emin ol:

- [ ] `docker compose up --build rabbitmq middleware` sorunsuz tamamlanıyor
- [ ] Ayrı terminalde `docker compose run --build --rm producer python -m producer.src.main --total 200 --rate 50 --batch 20` çalışıyor
- [ ] `http://127.0.0.1:15672` RabbitMQ paneli açılıyor (guest/guest)
- [ ] `http://127.0.0.1:8000/health` → `{"status": "ok"}` dönüyor
- [ ] `output/` klasöründe üç dosya oluşuyor (`sysadmin.md`, `developer.json`, `security.csv`)
- [ ] `python scripts/e2e_smoke.py` ve `python scripts/performance_report.py --reports-dir reports --skip-queue-fetch` en az bir kez çalıştırıldı
- [ ] `reports/e2e_metrics.json` ve `reports/queue_samples.jsonl` oluştu
- [ ] `reports/plots/` klasöründe üç dolu grafik dosyası var
- [ ] GitHub Actions'ta son çalıştırma yeşil
- [ ] Kod editörü açık ve ilgili dosyalar sekmede hazır
- [ ] Ekran çözünürlüğü yeterince büyük (1920×1080 önerilir)

---

## Önceden Açık Tutulacak Sekmeler / Dosyalar

### Tarayıcı sekmeleri

1. `http://127.0.0.1:15672` — RabbitMQ Yönetim Paneli
2. `http://127.0.0.1:8000/metrics` — Middleware Metrikleri
3. GitHub repo → Actions sekmesi

### Editörde açık dosyalar

1. `README.md`
2. `docker-compose.yml`
3. `middleware/src/pipeline/pipeline_builder.py`
4. `middleware/src/pipeline/handler.py`
5. `middleware/src/security/rules.py`
6. `middleware/src/pipeline/filter_handler.py`
7. `middleware/src/transport/consumer.py`
8. `middleware/src/enrichment/enrichers.py`
9. `middleware/src/formatting/formatter.py`
10. `middleware/src/formatting/formatter_factory.py`
11. `producer/src/generators/log_factory.py`
12. `middleware/src/metrics/collector.py`

### Dosya gezgini klasörleri

- `output/` — canlı çıktılar
- `reports/plots/` — performans grafikleri

---

## Olası Sorular ve Yanıtlar

**"Neden HTTP REST değil de RabbitMQ kullandınız?"**
> "HTTP REST'te middleware cevap veremediğinde producer hata alır. RabbitMQ'da middleware yavaş olsa bile mesajlar kuyrukta bekler, kaybolmaz. Yüksek hacimli borsa trafiğinde bu fark kritik."

**"KVKK maskelemesi geri döndürülebilir mi?"**
> "Hayır. Maskeleme tek yönlü — orijinal veri, çıktı dosyalarına hiç yazılmıyor. Maskeleme pipeline'ın ilk adımı, sonraki hiçbir kod ham veriyle temas etmiyor."

**"Neden beş tasarım kalıbı?"**
> "Her biri farklı bir sorunu çözdü: Chain of Responsibility işleme hattını genişletilebilir yaptı, Strategy biçimlendiriciyi değiştirilebilir kıldı, Decorator zenginleştirmeyi modüler hâle getirdi, Factory nesne üretimini merkezileştirdi, Singleton metrik tutarlılığını sağladı."

**"Testler ne kadar kapsama sağlıyor?"**
> "21 birim ve entegrasyon testi var. Her faz için ayrı test dosyası yazıldı. CI'da her push'ta otomatik koşuyor."

**"Docker olmadan çalışabilir mi?"**
> "Producer `--dry-run` modu ile RabbitMQ'ya bağlanmadan test edilebilir. Testler de Docker gerektirmiyor — sadece Python bağımlılıkları yeterli."
