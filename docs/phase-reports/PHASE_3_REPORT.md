# Faz 3 Raporu — Filtreleme ve Zenginleştirme

**Tarih:** 2026-06-01  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Faz 2'de kurulan işleme hattı yalnızca kişisel verileri maskeliyordu. Bu fazda hatta iki yeni adım eklendi:

1. **Filtreleme** — Önemsiz logları sistemden elemek (performans gereksinimi)
2. **Zenginleştirme** — Geçen loglara anlamlı ek bilgiler eklemek

Faz sonunda işleme hattı şu sıraya ulaştı:

```
Anonimleştirme → Filtreleme → Zenginleştirme → Sonlandırma
```

---

## 2. Yapılan Çalışmalar

### 2.1 Filtreleme Adımı

`FilterHandler` sınıfı, işleme hattına giren logları iki kurala göre eliyor:

**Elinen loglar:**
- Önem seviyesi DEBUG, INFO veya WARNING olan loglar — bunlar düşük önceliklidir, çok sayıda üretilir ve anlamlı bir şey söylemezler
- Kaynağı `docker.` ile başlayan loglar — bunlar sistemin kendi altyapısına ait iç mesajlardır, borsa uygulamasıyla ilgisi yoktur

**Geçen loglar:**
- Yalnızca ERROR ve CRITICAL seviyesindeki gerçek uygulama logları

Bu kural projenin performans gereksinimi: gereksiz logları mümkün olduğunca erken elemek, sistemin geri kalanının yükünü azaltır.

### 2.2 Zenginleştirme Adımı (Decorator Tasarım Kalıbı)

Filtrelemeyi geçen her loga ek bilgiler ekleniyor. Bu işlem **Decorator** (Süsleme) tasarım kalıbıyla yapılandırıldı: her "süsleyici" logu alıp üzerine bir şeyler ekliyor ve değiştirilmiş logu döndürüyor.

Kullanılan süsleyiciler sırayla şunlar:

| Süsleyici | Eklediği Bilgi |
|-----------|----------------|
| `SenderIdDecorator` | Logu gönderen üreticinin kimliği |
| `TransactionInfoDecorator` | İşlem numarası (borsa işlemi takibi için) |
| `CriticalityDecorator` | Logun kritiklik derecesi (1-5 arası) |
| `RoleTagDecorator` | Hedef kitleye göre etiket (sysadmin, developer, security) |
| `DebugDecorator` | Geliştirme sırasında ek hata ayıklama bilgisi |

Bu yapı sayesinde yeni bir bilgi türü eklemek istediğimizde mevcut kodu değiştirmek gerekmez; sadece yeni bir süsleyici eklenir.

### 2.3 Pipeline Güncellenmesi

`pipeline_builder.py` dosyası güncellenerek işleme hattına yeni adımlar eklendi:

```
Önceki:  Anonimleştirme → Sonlandırma
Yeni:    Anonimleştirme → Filtreleme → Zenginleştirme → Sonlandırma
```

---

## 3. Değişen / Oluşturulan Dosyalar

- `middleware/src/enrichment/enrichers.py` (yeni)
- `middleware/src/pipeline/filter_handler.py` (yeni)
- `middleware/src/pipeline/enrichment_handler.py` (yeni)
- `middleware/src/pipeline/pipeline_builder.py` (güncellendi)
- `tests/test_phase3_pipeline.py` (yeni)

---

## 4. Çalıştırılan Testler

| Komut | Sonuç |
|-------|-------|
| `pytest test_phase1 test_phase2 test_phase3` | **9/9 test geçti** |
| Linter kontrolü | Yeni hata yok |

Test kapsamı: filtreleme kurallarının doğru çalışması (doğru loglar elenip doğruları geçiyor mu?), her süsleyicinin beklenen alanları eklemesi.

---

## 5. Açık Maddeler

- Zenginleştirilmiş loglar henüz dosyaya yazılmıyor; bu Faz 4'ün konusu. Şu an loglar son adımda sayılıp bırakılıyor.
- `DebugDecorator` yalnızca geliştirme ortamında etkin olmalı; bu ayrım Faz 5'te yapılandırmaya bağlanacak.

---

## 6. Sonraki Faz

Faz 4'te loglar dosyaya yazılmaya başlayacak. Her rol için farklı bir format kullanılacak:

- Sistem yöneticisi → Markdown
- Geliştirici → JSON
- Güvenlik ekibi → CSV

Bu biçimlendirme **Strategy** (Strateji) tasarım kalıbıyla yapılacak; hangi formatın kullanılacağını belirleyen bir fabrika fonksiyonu rol bilgisine bakarak otomatik seçecek.
