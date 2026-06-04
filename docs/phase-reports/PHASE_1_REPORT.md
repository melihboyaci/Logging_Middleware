# Faz 1 Raporu — Veri Üretici (Producer)

**Tarih:** 2026-06-01  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Bu fazda sisteme gerçekçi borsa logları üreten ve bunları RabbitMQ kuyruğuna gönderen **producer** modülü yazıldı. Producer; TC kimlik numarası, kredi kartı, IBAN gibi kişisel veriler içeren simüle edilmiş log kayıtları üretir. Bu veriler middleware'de KVKK kapsamında anonimleştirilecek.

---

## 2. Yapılan Çalışmalar

### 2.1 Yapılandırma Katmanı

Producer'ın davranışını belirleyen tüm ayarlar tek bir yapılandırma dosyasında toplandı (`config.py`). Kaç log üretileceği, ne hızda gönderileceği, RabbitMQ adresinin ne olduğu gibi parametreler hem komut satırı argümanlarından hem de ortam değişkenlerinden okunabiliyor.

### 2.2 Hassas Veri Üreticileri

KVKK anonimleştirmesini test edebilmek için gerçekçi görünümlü sahte veriler üreten fonksiyonlar yazıldı:

- TC kimlik numarası
- Kredi kartı numarası
- E-posta adresi
- IBAN (TR formatında)
- SWIFT/BIC kodu
- İşlem tutarı

Bu veriler gerçek kişilere ait değil; yalnızca sistemin anonimleştirme kurallarını test etmek için üretiliyor.

### 2.3 Senaryo Sistemi

Sistemin farklı durumları test edebilmesi için yedi senaryo tanımlandı. Her senaryo farklı bir log türüne karşılık geliyor:

| Senaryo | Ne Simüle Eder |
|---------|----------------|
| `kvkk_transaction` | TC kimlik ve IBAN içeren şüpheli transfer |
| `failed_login_burst` | Aynı IP'den art arda hatalı giriş denemeleri |
| `dev_404` | Geliştirici tarafından tetiklenen 404 hatası |
| `sysadmin_datetime_mismatch` | Sunucular arası saat uyumsuzluğu |
| `noise_info_warning` | Önemsiz bilgi logları (filtrelenerek elenecek) |
| `docker_internal_noise` | Docker'ın kendi iç logları (sisteme ait olmayan, elenecek) |
| `card_purchase` | Kredi kartı ile şüpheli ödeme işlemi |

Her senaryo belirli bir ağırlıkla seçiliyor; örneğin gürültü logları daha sık üretiliyor çünkü gerçek sistemlerde önemsiz loglar çoğunluktadır.

### 2.4 Factory Tasarım Kalıbı ile Log Üretimi

Log üretimi **Factory** tasarım kalıbıyla yapılandırıldı. `LogFactory` sınıfı şunları yapıyor:

1. Ağırlıklara göre rastgele bir senaryo seçiyor
2. Senaryoya uygun hassas veri üretiyor
3. Bunu projenin ortak log şemasına (`LogRecord`) dönüştürüyor
4. Log kaydına üretici kimliği ve senaryo adını ekliyor

Bu yapı sayesinde log üretme mantığı tek bir yerden yönetiliyor; yeni senaryo eklemek çok kolay.

### 2.5 RabbitMQ'ya Gönderim

Üretilen loglar `publisher.py` aracılığıyla RabbitMQ'ya gönderiliyor. Gönderim sırasında şunlar garanti altına alındı:

- Loglar toplu olarak gönderiliyor (tek tek değil), bu daha verimli
- Her mesaj "kalıcı" olarak işaretleniyor; RabbitMQ yeniden başlasa bile kaybolmuyor
- Gönderim hızı saniye başına kaç log olacağı şeklinde ayarlanabiliyor
- Kaç log gönderildiği, ne kadar sürdüğü ve saniyedeki log sayısı raporlanıyor

### 2.6 Komut Satırı Arayüzü

`main.py` dosyası aşağıdaki parametreleri destekliyor:

| Parametre | Açıklama |
|-----------|----------|
| `--total` | Toplam kaç log üretileceği |
| `--batch` | Tek seferde kaç log gönderileceği |
| `--rate` | Saniyede kaç log gönderileceği |
| `--amqp-url` | RabbitMQ adresi |
| `--dry-run` | Gönderim yapmadan sadece üretimi test etmek için |

`--dry-run` modu sayesinde RabbitMQ'ya bağlanmadan üretim akışı test edilebiliyor. Bu özellikle geliştirme ve CI ortamlarında yararlı.

---

## 3. Değişen / Oluşturulan Dosyalar

- `producer/src/config.py`
- `producer/src/generators/sensitive_data.py`
- `producer/src/generators/scenarios.py`
- `producer/src/generators/log_factory.py`
- `producer/src/transport/publisher.py`
- `producer/src/main.py`
- `tests/test_phase1_producer.py`

---

## 4. Çalıştırılan Testler

| Komut | Sonuç |
|-------|-------|
| `python -m producer.src.main --dry-run --total 20` | 20 log üretildi, başarılı |
| `pytest tests/test_phase1_producer.py` | **3/3 test geçti** |
| Linter kontrolü | Yeni hata yok |

Test içerikleri: hassas veri formatlarının doğruluğu, tüm senaryoların çalışması ve üretilen log kaydının doğru alanları taşıması.

---

## 5. Açık Maddeler

- RabbitMQ'ya canlı gönderim testi, Faz 2'de middleware tüketicisi hazır olunca anlamlı hale gelecek.
- Yerel geliştirme ortamında `pytest` ve `aio-pika` elle kuruldu; CI ortamında bu işlem `requirements.txt` üzerinden otomatik yapılıyor.

---

## 6. Sonraki Faz

Faz 2'de middleware'in temel yapısı kurulacak. Producer'ın gönderdiği loglar RabbitMQ'dan okunup işlenmeye başlayacak; ilk adım olarak KVKK kapsamındaki kişisel verilerin maskelenmesi gerçekleştirilecek.
