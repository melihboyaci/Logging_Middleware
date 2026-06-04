# Faz 4 Raporu — Biçimlendirme ve Dosyaya Yazma

**Tarih:** 2026-06-01  
**Durum:** Tamamlandı

---

## 1. Bu Fazın Amacı

Önceki fazlarda loglar işleniyor ancak hiçbir yere yazılmıyordu. Bu fazda işleme hattının son adımı tamamlandı: işlenmiş loglar artık kullanıcının rolüne göre farklı formatlarda dosyaya yazılıyor.

Bu fazın sonunda sistem çalışır hâle geldi. Bir log mesajı alındığında:

1. Kişisel veriler maskeleniyor
2. Gereksiz loglar eliniyor
3. Log zenginleştiriliyor
4. Rolüne göre biçimlendiriliyor ve `output/` klasörüne kaydediliyor

---

## 2. Yapılan Çalışmalar

### 2.1 Biçimlendirme Katmanı (Strategy Tasarım Kalıbı)

Her rol için ayrı bir biçimlendirici sınıf yazıldı. Hepsi aynı sözleşmeyi (`Formatter` arayüzü) uygular; yani tümüne aynı şekilde "bu logu biçimlendir" denilebilir.

| Biçimlendirici | Rol | Çıktı |
|----------------|-----|-------|
| `MarkdownFormatter` | Sistem yöneticisi | Okunması kolay, başlıklı metin |
| `JsonFormatter` | Geliştirici | Programatik işlemeye uygun JSON |
| `CsvFormatter` | Güvenlik ekibi | Excel/tablo analizi için CSV |
| `HtmlFormatter` | (İsteğe bağlı) | Tarayıcıda görüntülenebilir HTML |

Bu yapı **Strategy** (Strateji) tasarım kalıbıdır: algoritma (biçimlendirme) çalışma anında değiştirilebilir; yeni bir format eklemek için sadece yeni bir sınıf yazmak yeterlidir.

### 2.2 Format Seçimi (Factory Tasarım Kalıbı)

`formatter_factory.py` dosyasındaki `formatter_for_role()` fonksiyonu rol bilgisine bakarak otomatik olarak doğru biçimlendiriciyi döndürüyor:

- `sysadmin` → Markdown
- `developer` → JSON
- `security` → CSV

Bu eşleşme kod içinde sabit değil; yapılandırma dosyasından okunuyor. Eşleştirmeyi değiştirmek için kodu düzenlemek gerekmiyor.

### 2.3 Dosyaya Yazma (RoleRouter)

`RoleRouter` sınıfı şunları yapıyor:

1. Logun rolüne bakarak doğru biçimlendiriciyi seçiyor
2. Logu biçimlendiriyor
3. Çıktıyı `output/` klasöründeki uygun dosyaya ekliyor

Sonuç olarak `output/` klasöründe üç dosya oluşuyor:

- `output/sysadmin.md` — Markdown formatında sistem logları
- `output/developer.json` — JSON formatında geliştirici logları
- `output/security.csv` — CSV formatında güvenlik logları

### 2.4 Yapılandırma Genişletmesi

Middleware yapılandırma dosyasına (`config.py`) üç ek ayar eklendi:

- Rol → format eşleşme tablosu
- Her format için dosya uzantısı
- Çıktı klasörü yolu

Böylece çıktı davranışı tamamen yapılandırma dosyasından yönetilir hâle geldi.

---

## 3. Değişen / Oluşturulan Dosyalar

- `middleware/src/formatting/formatter.py` (temel sınıf)
- `middleware/src/formatting/json_formatter.py`
- `middleware/src/formatting/csv_formatter.py`
- `middleware/src/formatting/markdown_formatter.py`
- `middleware/src/formatting/html_formatter.py`
- `middleware/src/formatting/formatter_factory.py`
- `middleware/src/sinks/role_router.py`
- `middleware/src/config.py` (güncellendi)
- `middleware/src/pipeline/terminal_handler.py` (güncellendi)
- `tests/test_phase4_formatting.py`

---

## 4. Çalıştırılan Testler

| Komut | Sonuç |
|-------|-------|
| `pytest test_phase1 test_phase2 test_phase3 test_phase4` | **11/11 test geçti** |
| Linter kontrolü | Yeni hata yok |

Test kapsamı: her biçimlendiricinin doğru formatta çıktı üretmesi, `RoleRouter`'ın doğru dosyaya yazması, yanlış rol için varsayılan biçimlendirme davranışı.

---

## 5. Açık Maddeler

- CSV biçimlendirici sütun başlığını ilk satırda yazıyor. Birden fazla sürecin aynı dosyaya yazması durumunda başlık birden çok kez tekrarlanabilir. Bu küçük tutarsızlık ileride düzeltilebilir.
- Çıktı dosyaları her yeni loga ekleme yaparak büyüyor (append modu). Çok yüksek hacimli trafikte dosya boyutları hızla artabilir; gerekirse dönemsel döndürme (rotation) mekanizması eklenebilir.

---

## 6. Sonraki Faz

Faz 5'te sisteme performans ölçümü ekleniyor:

- Her logun işlenme süresi ölçülecek (p50/p95/p99 gecikme istatistikleri)
- Producer yüksek yük profilleriyle çalıştırılıp sistemin ne kadar dayanabildiği test edilecek
- Ölçüm sonuçları `reports/` klasörüne otomatik olarak kaydedilecek
