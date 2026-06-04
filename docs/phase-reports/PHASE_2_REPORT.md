# Faz 2 Raporu — Middleware İskeleti ve Güvenlik

**Tarih:** 2026-06-01  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Bu fazda middleware modülünün temel omurgası kuruldu. Producer'dan gelen log kayıtları artık RabbitMQ'dan okunup bir işleme hattına (pipeline) sokulmaya hazır. Bu fazın sonunda middleware şunları yapabiliyor:

- RabbitMQ kuyruğundan log mesajlarını okumak
- Mesaj içindeki kişisel verileri (KVKK) maskelemek
- Sağlık durumu ve anlık istatistikleri dışarıya sunmak (`/health`, `/metrics`)

---

## 2. Yapılan Çalışmalar

### 2.1 Yapılandırma ve Temel Sayaçlar

Middleware'in davranışını kontrol eden ayarlar `config.py` dosyasında toplandı: RabbitMQ adresi, hangi kuyruğu dinleyeceği, kaç mesajı aynı anda işleyeceği, API sunucusunun hangi portta çalışacağı.

İşlem sırasında kaç mesaj alındı, kaçı işlendi, kaçı hata verdi — bunları takip eden basit sayaçlar `MetricsCollector` sınıfında tanımlandı.

### 2.2 İşleme Hattı (Chain of Responsibility Tasarım Kalıbı)

Middleware, logları sıralı adımlardan geçiren bir "işleme hattı" kullanıyor. Bu yapı **Chain of Responsibility** (Sorumluluk Zinciri) tasarım kalıbına dayanıyor: her adım kendi işini yapıp logu bir sonraki adıma iletiyor.

Bu fazda zincir iki adımdan oluşuyor:

```
Anonimleştirme → Son Adım (sayaç arttırma)
```

İlerideki fazlarda bu zincire filtreleme ve zenginleştirme adımları eklenecek.

### 2.3 KVKK Anonimleştirmesi

KVKK kapsamında maskelenmesi gereken kişisel veri türleri `security/rules.py` dosyasında düzenli ifadeler (regex) olarak tanımlandı. Maskeleme sırası şöyle:

1. TC kimlik numarası
2. Kredi kartı numarası
3. IBAN
4. SWIFT/BIC kodu
5. E-posta adresi

Hem log mesajının içindeki metin hem de ek bilgiler (`payload`) ayrı ayrı taranıyor ve hassas veriler `***` ile değiştiriliyor. Bu işlem pipeline'ın **ilk** adımında yapılıyor; hiçbir hassas veri sonraki aşamalara ulaşmıyor.

### 2.4 RabbitMQ Dinleyicisi (Consumer)

`consumer.py` dosyası middleware'in RabbitMQ'dan mesaj okuduğu katmanı oluşturuyor:

- Kuyruk bağlantısı kurulduğunda otomatik olarak `logs.raw` kuyruğu bildirilip abone olunuyor
- Her gelen mesaj `LogRecord` veri modeline dönüştürülüyor
- Dönüştürme başarılıysa pipeline'a gönderiliyor
- Hatalı mesajlar kuyruğa geri konmadan siliniyor ve hata sayacı artırılıyor

### 2.5 Web Arayüzü (FastAPI)

Middleware çalışırken dışarıdan durumunu sorgulamak mümkün:

- `GET /health` → `{"status": "ok"}` — middleware ayakta mı?
- `GET /metrics` → anlık sayaçlar — kaç mesaj işlendi, kaçı düşürüldü?

FastAPI uygulaması başlarken RabbitMQ dinleyicisini de devreye alıyor; kapanırken temiz şekilde bağlantıyı kapatıyor.

---

## 3. Değişen / Oluşturulan Dosyalar

- `middleware/src/config.py`
- `middleware/src/metrics/collector.py`
- `middleware/src/pipeline/handler.py` (temel sınıf)
- `middleware/src/pipeline/anonymization_handler.py`
- `middleware/src/pipeline/terminal_handler.py`
- `middleware/src/pipeline/pipeline_builder.py`
- `middleware/src/security/rules.py`
- `middleware/src/security/anonymizer.py`
- `middleware/src/transport/consumer.py`
- `middleware/src/api/routes.py`
- `middleware/src/main.py`
- `tests/test_phase2_middleware.py`

---

## 4. Çalıştırılan Testler

| Komut | Sonuç |
|-------|-------|
| `pytest test_phase1_producer.py test_phase2_middleware.py` | **6/6 test geçti** |
| `docker compose config` | Başarılı |
| Linter kontrolü | Yeni hata yok |

Test kapsamı: KVKK anonimleştirme kuralları, `/health` ve `/metrics` endpoint'lerinin doğru yanıt vermesi.

---

## 5. Açık Maddeler

- Pipeline henüz yalnızca anonimleştirme adımından oluşuyor; filtreleme ve zenginleştirme Faz 3'te eklenecek.
- Gecikme (latency) ölçümü ve p95/p99 istatistikleri Faz 5'te ekleneceğinden `/metrics` şimdilik yalnızca temel sayaçları gösteriyor.
- Üçten fazla servis birlikte çalışmadan tam uçtan uca test anlamlı olmuyor; bu Faz 4 sonrasında yapılacak.

---

## 6. Sonraki Faz

Faz 3'te pipeline iki yeni adımla genişletilecek:

- **Filtreleme:** INFO/WARNING seviyesindeki ve Docker'ın kendi iç logları çıkarılacak (bu loglar sistemle ilgisiz olduğundan önemsiz kabul ediliyor).
- **Zenginleştirme:** Her loga hedef kitlesine göre ek etiketler, işlem numarası ve kritiklik bilgisi eklenecek.
