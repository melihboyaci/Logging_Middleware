# Faz 5 Raporu — Performans Ölçümü ve Stres Altyapısı

**Tarih:** 2026-06-01  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Sistemin ne kadar hızlı çalıştığını sayılarla ortaya koymak gerekiyor. Bu fazda iki şey yapıldı:

1. **Middleware tarafında:** Her log kaydının ne kadar sürede işlendiği ölçüldü; istatistiksel özet (medyan, %95, %99 yüzdelikler) üretildi.
2. **Producer tarafında:** Sistemi farklı yük profillerinde zorlayan bir stres testi altyapısı eklendi.

---

## 2. Yapılan Çalışmalar

### 2.1 Gecikme Ölçümü

`MetricsCollector` sınıfı yeni yetenekler kazandı:

- Her log işlenirken başlangıç ve bitiş zamanı kaydediliyor
- Tüm bu süreler bir listede biriktiriliyor
- `/metrics` isteğine cevap verilirken bu listeden şu istatistikler hesaplanıyor:
  - **p50 (medyan):** Logların yarısı bu süreden daha hızlı işleniyor
  - **p95:** Logların %95'i bu süreden daha hızlı işleniyor
  - **p99:** En yavaş %1 için eşik değer

Bu üç ölçüm, sistemin gerçek yük altındaki davranışını anlamak için endüstri standardı.

### 2.2 Anlık Durum Raporu

`MetricsReporter` sınıfı eklendi. Bu sınıf tek bir iş yapıyor: o anki tüm metrikleri (kaç log işlendi, gecikme istatistikleri vb.) zaman damgalı bir JSON dosyası olarak `reports/` klasörüne kaydediyor. Bu dosyalar sonraki fazda grafiklere dönüştürülecek.

### 2.3 Stres Testi — Yük Koşucusu

`load_runner.py` iki farklı yük profili sunuyor:

| Profil | Açıklama |
|--------|----------|
| **Ramp (Kademeli Artış)** | Yavaş başlayıp giderek artan yük — sistemin ne zaman "gerilmeye" başladığını gösterir |
| **Burst (Ani Yük)** | Kısa sürede çok sayıda mesaj — ani trafik artışlarına karşı dayanıklılığı ölçer |

Her stres testi sonucunda `reports/load_profile_<profil>.json` dosyası oluşuyor: kaç log gönderildi, ne kadar sürdü, saniyede kaç log işlendiği.

---

## 3. Değişen / Oluşturulan Dosyalar

- `middleware/src/metrics/collector.py` (gecikme ölçümü eklendi)
- `middleware/src/metrics/reporter.py` (yeni)
- `middleware/src/transport/consumer.py` (her mesajda süre ölçümü eklendi)
- `producer/src/stress/load_runner.py` (yeni)
- `tests/test_phase5_metrics_and_stress.py` (yeni)

Örnek çıktı dosyaları:

- `reports/load_profile_ramp.json`
- `reports/phase5_metrics_*.json`

---

## 4. Çalıştırılan Testler

| Komut | Sonuç |
|-------|-------|
| `pytest` (tüm fazlar) | **14/14 test geçti** |
| Stres testi — ramp profil | Başarılı, JSON raporu oluştu |
| Gecikme raporu üretimi | Başarılı |
| Linter kontrolü | Yeni hata yok |

---

## 5. Açık Maddeler

- Kuyruk derinliği (RabbitMQ'da ne kadar mesaj bekliyor) şu an ölçülmüyor; bu Faz 9'da eklenecek.
- Stres testi şu an bağımsız çalışıyor; ileride E2E smoke testi ile entegre edilebilir.

---

## 6. Sonraki Faz

Faz 6'da proje teslim aşamasına hazırlanıyor:

- Projeyi açıklayan kapsamlı bir README
- Ödev raporu için hazır şablon
- Demo video için adım adım anlatım senaryosu
- Tüm testlerin son bir toplu koşusu
