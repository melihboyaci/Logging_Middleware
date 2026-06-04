# Faz 0 Raporu — Proje İskeleti ve Altyapı

**Tarih:** 2026-06-01  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Projenin "boş bir kağıt" üzerinde başlamaması için önce sağlam bir iskelet kurulması gerekiyordu. Bu fazda herhangi bir iş mantığı yazmadan sadece şunlar yapıldı:

- Proje klasör yapısının belirlenmesi ve oluşturulması
- Üç Docker servisinin (RabbitMQ, Producer, Middleware) birlikte çalışacağı ortamın kurulması
- İki uygulama modülünün de kullanacağı ortak log veri modelinin tanımlanması
- Her iki modül için temel Docker yapılandırma dosyalarının hazırlanması

---

## 2. Yapılan Çalışmalar

### 2.1 Klasör Yapısı

Projenin ilerleyen fazlarında karışıklık yaşanmaması için tüm ana klasörler en baştan oluşturuldu:

- `producer/` — log üreten uygulama
- `middleware/` — logları işleyen uygulama
- `shared/` — her iki uygulama tarafından ortak kullanılan kod
- `tests/` — testler
- `output/` — işlenmiş logların yazıldığı yer
- `reports/` — performans ve stres testi çıktıları

Middleware içindeki alt klasörler de (güvenlik, filtreleme, biçimlendirme vb.) şimdiden açıldı; bu sayede sonraki fazlarda dosyalar doğru yerlerine eklenebildi.

### 2.2 Docker Orkestrasyon Dosyası

`docker-compose.yml` dosyası oluşturuldu. Bu dosya üç servisi tanımlıyor:

1. **RabbitMQ** — logların producer'dan middleware'e taşındığı mesaj kuyruğu
2. **Middleware** — logları tüketen ve işleyen servis
3. **Producer** — log üreten servis

Önemli bir detay: RabbitMQ tamamen hazır olmadan producer ve middleware başlatılmıyor. Bunu sağlamak için `depends_on: condition: service_healthy` yapılandırması kullanıldı. Böylece servis başlangıç sırası güvence altına alındı.

### 2.3 Ortak Log Veri Modeli

`shared/log_schema.py` dosyasında projenin temel veri yapısı tanımlandı. Her log kaydı şu bilgileri taşıyor:

| Alan | Açıklama |
|------|----------|
| `id` | Her log için otomatik üretilen benzersiz kimlik |
| `timestamp` | Logun üretildiği an (UTC) |
| `level` | Önem seviyesi: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `type` | Log türü: LOG, ERROR, TRANSACTION, ACCESS |
| `role` | Hedef kitle: sysadmin, developer, security |
| `source` | Logu üreten sistem bileşeni |
| `message` | İnsan tarafından okunabilir mesaj |
| `payload` | Ek bilgiler (TC kimlik, IBAN, kart numarası vb.) |

Bu model projenin tüm fazlarında değişmeden kullanıldı; hem producer hem middleware bu yapıya göre çalıştı.

### 2.4 Başlangıç Uygulama Dosyaları

Her iki modül için Python paket tanımlama dosyaları (`__init__.py`) ve en basit hâliyle çalışan `main.py` giriş noktaları eklendi. Bu sayede Faz 0'ın gerçekten çalıştığı doğrulanabildi.

### 2.5 Docker Yapılandırma Dosyaları

Her iki uygulama için ayrı `Dockerfile` oluşturuldu. İkisi de aynı mantığı izliyor: hafif bir Python 3.11 imajı üzerine gerekli bağımlılıklar kurulup uygulama kodu kopyalanıyor.

- Producer bağımlılıkları: `aio-pika` (RabbitMQ iletişimi), `pydantic` (veri doğrulama)
- Middleware bağımlılıkları: `aio-pika`, `pydantic`, `fastapi`, `uvicorn` (web sunucusu)

---

## 3. Değişen / Oluşturulan Dosyalar

- `.gitignore` — gereksiz dosyaların Git'e eklenmesini engelleyen kural listesi
- `docker-compose.yml` — üç servisli Docker ortamı
- `shared/log_schema.py` — ortak log veri modeli
- `producer/Dockerfile`, `producer/requirements.txt`, başlangıç Python dosyaları
- `middleware/Dockerfile`, `middleware/requirements.txt`, başlangıç Python dosyaları
- `docs/STATE.md` — faz ilerlemesi takip dosyası güncellendi

---

## 4. Çalıştırılan Testler

| Komut | Beklenen Sonuç |
|-------|----------------|
| `docker compose config` | Yapılandırma hatası yok |
| `python -m producer.src.main` | Uygulama sorunsuz çalışıyor |
| `python -m middleware.src.main` | Uygulama sorunsuz çalışıyor |
| Linter kontrolü | Yeni hata yok |

---

## 5. Sonuçlar

Tüm doğrulama adımları başarılı geçti. Faz 0 kriterleri sağlandı.

---

## 6. Açık Maddeler

Bu fazda yalnızca iskelet kurulduğundan henüz gerçek bir log akışı yok. Producer log üretmiyor, middleware herhangi bir şeyi işlemiyor. Bunlar kasıtlı olarak boş bırakıldı; gerçek iş mantığı Faz 1 ve Faz 2'de eklenecek.

---

## 7. Sonraki Faz

Faz 1'de producer'ın çekirdeği yazılacak: gerçekçi borsa logları üretmek, hassas verileri (TC kimlik, kredi kartı vb.) simüle etmek ve üretilen logları RabbitMQ'ya göndermek.
