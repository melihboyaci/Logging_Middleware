# Faz 9 Raporu — Performans Grafiklerinin Otomatize Edilmesi

**Tarih:** 2026-06-02  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Sistemin performansını rakamlarla göstermek yeterli değil; görseller çok daha etkili anlatıyor. Bu fazda performans verilerinden otomatik olarak grafikler üretildi ve bu grafikler CI pipeline'ına entegre edildi.

Artık E2E test koştuktan sonra şu üç grafik ve bir özet metin dosyası otomatik olarak oluşuyor:

- İşleme hattı istatistikleri (kaç log işlendi, elenidi, hata verdi)
- Gecikme yüzdelikleri (p50, p95, p99)
- Kuyruk derinliği (RabbitMQ'da bekleyen mesaj sayısının zaman içindeki değişimi)

---

## 2. Yapılan Çalışmalar

### 2.1 Kuyruk Derinliği İzleme

RabbitMQ'nun yönetim arayüzü, kuyrukların anlık durumunu bir API üzerinden sunuyor. `queue_monitor.py` modülü bu API'ye bağlanıp `logs.raw` kuyruğunda kaç mesaj beklediğini okuyor.

Bu ölçüm şunu gösteriyor: üretici çok hızlı mesaj gönderirse kuyruk birikir ve sistem gecikmesi artar. Grafik bu dinamiği görünür kılıyor.

### 2.2 Performans Raporu Scripti

`scripts/performance_report.py` scripti şu adımları otomatik gerçekleştiriyor:

1. `reports/` klasöründen en son metrik JSON dosyasını yüklüyor
2. Varsa `queue_samples.jsonl` dosyasından kuyruk derinliği verisini okuyor
3. Üç ayrı grafik PNG dosyası olarak kaydediyor (`reports/plots/`)
4. `reports/performance_summary.md` adında okunabilir bir özet rapor oluşturuyor

Script, `--skip-queue-fetch` parametresiyle CI ortamında güvenli modda da çalışabiliyor: RabbitMQ'ya bağlanmaya çalışmıyor, yalnızca kaydedilmiş verileri kullanıyor.

### 2.3 E2E Testine Kuyruk Örneklemesi Eklenmesi

`e2e_smoke.py` scripti güncellendi. Artık producer log gönderirken arka planda düzenli aralıklarla kuyruk derinliği ölçülüp `reports/queue_samples.jsonl` dosyasına yazılıyor. Bu veri daha sonra grafik scriptinin kullandığı ham veri kaynağı.

### 2.4 CI Entegrasyonu

GitHub Actions iş akışına iki güncelleme yapıldı:

- `requirements-dev.txt` (grafik kütüphanesi `matplotlib` içeriyor) test işine eklendi
- E2E testinden sonra performans raporu scripti otomatik koşuyor; üretilen grafikler artifact olarak yükleniyor

Bu sayede her CI çalışmasında performans grafikleri GitHub arayüzünden indirilebiliyor.

### 2.5 Yeni Bağımlılık

- `requirements-dev.txt` → `matplotlib>=3.8` (grafik çizim kütüphanesi)

Grafik çizimi, ekran gerektirmeden arka planda çalışan `Agg` arka ucunu kullandığı için sunucu ve CI ortamlarında sorunsuz çalışıyor.

---

## 3. Değişen / Oluşturulan Dosyalar

- `middleware/src/metrics/queue_monitor.py` (yeni)
- `scripts/performance_report.py` (yeni)
- `scripts/e2e_smoke.py` (kuyruk örneklemesi eklendi)
- `requirements-dev.txt` (yeni)
- `tests/test_phase9_performance_report.py` (yeni)
- `.github/workflows/ci.yml` (güncellendi)
- `README.md` (güncellendi)

---

## 4. Çalıştırılan Testler

| Komut | Sonuç |
|-------|-------|
| `pip install -r requirements-dev.txt` | Başarılı |
| `pytest -q` (tüm testler) | **21/21 test geçti** |
| `python scripts/performance_report.py --skip-queue-fetch` | 3 grafik + özet rapor oluştu |

---

## 5. Açık Maddeler

- Kuyruk derinliği canlı çekimi (`--skip-queue-fetch` olmadan) yalnızca çalışan Docker ortamında anlamlı; CI'da her zaman `--skip-queue-fetch` kullanılmalı.
- Grafik kütüphanesi (`matplotlib`) yalnızca geliştirici bağımlılıkları arasında; production imajlarına dahil edilmiyor.

---

## 6. Sonraki Adım

Tüm fazlar tamamlandı. Bundan sonra yapılacaklar:

- Demo videosu çekimi (`docs/video-script.md` rehber olarak kullanılabilir)
- `docs/report-template.md` şablonu kullanılarak ödev raporunun yazılması

---

## Ek — Commit Bilgisi

- Commit: `fc64b29`
- Mesaj: `Add phase 9 performance reporting with queue monitoring and plots.`
- Push: `main → origin/main` başarılı
