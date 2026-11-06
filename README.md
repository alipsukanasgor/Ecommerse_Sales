# E-Commerce Sales Performance Dashboard

**UTS Visualisasi Data — Sample Superstore**

## Menjalankan secara Steamlit
https://ecommersesales-n964bcsbdpepnuinkcd37t.streamlit.app/

## Deskripsi
Dashboard interaktif untuk menganalisis performa penjualan, profit, pesanan, kuantitas, kategori produk, wilayah, segmen pelanggan, serta hubungan diskon dan profit.

## Dataset
- Nama: Sample Superstore
- File: `data/superstore_clean.csv`
- Jumlah: 9.994 baris dan 21 kolom
- Periode transaksi: 3 Januari 2014 – 30 Desember 2017
- Sumber Kaggle: https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

## Fitur
- KPI: Total Sales, Total Profit, Unique Orders, Units Sold, Profit Margin
- Filter: rentang tanggal, kategori produk, wilayah, segmen pelanggan
- Grafik: tren penjualan, penjualan per wilayah, penjualan per kategori, diskon vs profit, profit per subkategori, sales & profit per segmen
- Key insights yang menyesuaikan filter
- Tabel transaksi dan unduh CSV hasil filter

## Menjalankan secara lokal
1. Pastikan Python 3.10+ sudah terpasang.
2. Buka terminal pada folder proyek.
3. Buat virtual environment (opsional tetapi disarankan):
   ```bash
   python -m venv .venv
   ```
4. Aktifkan:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
5. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
6. Jalankan:
   ```bash
   streamlit run app.py
   ```

## Struktur
```text
Ecommerce_Sales_Dashboard/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── superstore_clean.csv
```

## Catatan
Angka KPI dan insight pada dashboard dihitung langsung dari data sesuai filter yang dipilih. Dataset ini merupakan data historis 2014–2017.
