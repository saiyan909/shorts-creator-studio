#!/usr/bin/env python3
"""
Adhi Studio - Master Teleprompter & Project Script Sync
Menghasilkan naskah lengkap 5-adegan untuk SEMUA 43 PROYEK (Project 22 s/d 64),
memperbarui project.json di setiap folder, dan menghasilkan file NASKAH_TELEPROMPTER_SIAP_REKAM.md
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

ALL_43_SCRIPTS = [
    # 1. Project 22
    {
        "num": 1,
        "id": "22_kenapa_bau_kentut_sendiri_biasa_aja",
        "title": "Kenapa Bau Kentut Sendiri Biasa Aja tapi Orang Lain Bikin Emosi?",
        "audio": "22_kentut.mp3",
        "scenes": [
            "Kenapa kalau kita buang angin sendiri baunya biasa aja, tapi giliran orang lain yang kentut baunya langsung bikin emosi dan mual setengah mati?",
            "Padahal secara kimiawi, gas sulfur hidrogen yang keluar dari perut semua manusia itu sama-sama menyengat dan beracun!",
            "Ternyata ini mekanisme cerdas adaptasi sensori olfaktori dan self-serving bias otak kita! Otak sudah mengantisipasi aroma bakteri tubuh sendiri sejak lahir.",
            "Sementara bau tubuh orang asing dianggap oleh insting purba sebagai potensi ancaman penyakit atau racun berbahaya!",
            "Jadi kamu gak salah kalau emosi, hidungmu cuma lagi ngejalanin protokol pertahanan hidup! Siapa temenmu yang kentutnya paling mematikan? Tag di komentar ya!"
        ]
    },
    # 2. Project 23
    {
        "num": 2,
        "id": "23_kenapa_kucing_zoomies_jam_3_pagi",
        "title": "Kenapa Kucing Tiba-Tiba Lari Kesurupan Jam 3 Pagi (Zoomies)?",
        "audio": "23_zoomies.mp3",
        "scenes": [
            "Kenapa kucing yang seharian tidur manis tiba-tiba lari kesurupan keliling rumah jam tiga pagi sambil lompat-lompat nabrak tembok?",
            "Banyak yang ngira kucing lagi ngeliat hantu atau diganggu jin, padahal ini murni fenomena biologi bernama Frenetic Random Activity Periods atau Zoomies!",
            "Sebagai predator nokturnal alami, kucing secara biologis diprogram untuk berburu mangsa di waktu fajar dan tengah malam.",
            "Karena kucing peliharaan tidur enam belas jam dan gak perlu berburu tikus, tumpukan energi di ototnya meledak sekaligus dalam hitungan menit!",
            "Jadi tenang aja, kucingmu bukan kesurupan tapi cuma lagi ngabisin kuota baterai predatornya! Kucing kamu kalau zoomies jam berapa nih? Spill di komentar ya!"
        ]
    },
    # 3. Project 24
    {
        "num": 3,
        "id": "24_kenapa_tumbuh_tahi_lalat_baru",
        "title": "Kenapa Orang Bisa Nambah Punya Tahi Lalat Baru di Tubuhnya?",
        "audio": "24_tahilalat.mp3",
        "scenes": [
            "Kenapa pas lagi ngaca tiba-tiba ada tahi lalat baru di tangan atau wajah, padahal perasaan waktu kecil gak ada sama sekali?",
            "Banyak yang langsung overthinking takut tumor ganas, padahal sebagian besar tahi lalat baru adalah hal yang sangat normal!",
            "Tahi lalat terjadi saat sel penghasil pigmen bernama melanosit berkembang biak secara bergerombol di satu titik kulit, bukan menyebar merata.",
            "Pemicu utamanya adalah paparan radiasi sinar ultraviolet matahari dan perubahan lonjakan hormon saat usia dewasa atau kehamilan.",
            "Tapi ingat aturan ABCDE: kalau bentuknya asimetris, tepinya bergerigi, atau cepat membesar, wajib periksa ke dokter ya! Coba cek ada tahi lalat baru gak di tanganmu? Spill di komentar!"
        ]
    },
    # 4. Project 25
    {
        "num": 4,
        "id": "25_kenapa_gak_bisa_geli_gelitik_sendiri",
        "title": "Kenapa Kita Gak Bisa Geli Kalau Ngegelitik Diri Sendiri?",
        "audio": "25_gelitik.mp3",
        "scenes": [
            "Kenapa pas orang lain nyolek pinggang kita langsung geli setengah mati sampai teriak, tapi pas tangan sendiri yang ngegelitik rasanya hambar banget?",
            "Padahal saraf peraba di kulit telapak tangan dan pinggangmu itu adalah reseptor sentuhan yang sama persis!",
            "Kuncinya ada di otak kecil bernama cerebellum! Cerebellum bertugas memprediksi konsekuensi sensorik dari semua gerakan yang kita rencanakan sendiri.",
            "Begitu tanganmu bergerak mau menggelitik, cerebellum langsung membatalkan sensasi geli sebelum sinyalnya sempat bikin kamu tertawa!",
            "Otak kita sengaja memblokirnya biar kita bisa fokus mendeteksi ancaman sentuhan asing seperti serangga berbisa! Coba gelitik pinggangmu sekarang, geli gak? Tulis di komentar ya!"
        ]
    },
    # 5. Project 26
    {
        "num": 5,
        "id": "26_kenapa_bapak2_ngetik_hp_satu_jari",
        "title": "Kenapa Bapak-Bapak Kalau Ngetik HP Cuma Pakai Satu Jari Telunjuk?",
        "audio": "26_ketik1jari.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau ngetik pesan di HP gayanya selalu khas banget: tangan kiri megang erat HP, terus tangan kanan ngetik pakai satu jari telunjuk?",
            "Anak muda sering ngetawain gaya mengetik lambat ini, padahal ada alasan medis dan sejarah teknologi yang sangat masuk akal di baliknya!",
            "Pertama, penurunan daya akomodasi lensa mata alias presbiopi! Bapak-bapak butuh jarak fokus lebih jauh agar tulisan di layar terbaca jelas.",
            "Kedua, memori otot mesin tik mekanik jadul! Dulu tuts mesin tik butuh ditekan keras satu per satu, bukan disentuh ringan pakai jempol.",
            "Jadi itu bukan gaptek, tapi kebiasaan legendaris yang membuktikan jam terbang hidup bapakmu! Bapak kamu kalau ngetik pakai jari telunjuk juga gak nih? Spill di komentar ya!"
        ]
    },
    # 6. Project 27
    {
        "num": 6,
        "id": "27_kenapa_baterai_hp_1_persen_tahan_lama",
        "title": "Kenapa Baterai HP Pas 1 Persen Tahan Lebih Lama daripada 100 ke 99 Persen?",
        "audio": "27_baterai1persen.mp3",
        "scenes": [
            "Kenapa pas baterai HP tinggal satu persen rasanya kayak punya nyawa cadangan dan bisa tahan sampai belasan menit?",
            "Sementara waktu baterai penuh seratus persen, baru dicabut semenit dari charger langsung drop ke sembilan puluh sembilan persen?",
            "Ternyata persentase baterai di layar itu bukan takaran air di ember, tapi estimasi algoritma fuel gauge berdasarkan voltase kimia litium!",
            "Produsen sengaja menaruh buffer voltase cadangan di angka satu persen agar sistem operasi sempat menyimpan data penting sebelum mati total.",
            "Jadi satu persen itu sebenarnya penyelamat darurat dari pabrik biar HP-mu gak rusak mendadak! Rekor HP kamu pas 1 persen tahan berapa lama? Spill di komentar ya!"
        ]
    },
    # 7. Project 28
    {
        "num": 7,
        "id": "28_kenapa_siku_kepentok_kesetrum_ngilu",
        "title": "Kenapa Siku Kepentok Rasanya Kesetrum Ngilu Banget?",
        "audio": "28_siku.mp3",
        "scenes": [
            "Kenapa kalau siku tangan gak sengaja kepentok ujung meja, rasanya bukan memar biasa tapi kesetrum ngilu sampai ke ujung kelingking?",
            "Banyak yang mengira tulang siku kita yang patah, padahal tulang siku sama sekali gak punya sensor listrik seperti itu!",
            "Biang keladinya adalah saraf ulnaris! Saraf utama pengendali tangan ini melewati terowongan sempit di siku tanpa bantalan daging atau lemak.",
            "Begitu siku kepentok, saraf ulnaris langsung terjepit telak di antara tulang keras dan meja, mengirimkan ledakan sinyal listrik ke otak!",
            "Sensasi aneh ini dijuluki orang barat sebagai Funny Bone, padahal gak ada lucu-lucunya sama sekali! Kamu terakhir kepentok siku kapan nih? Sakit banget kan? Komen ya!"
        ]
    },
    # 8. Project 29
    {
        "num": 8,
        "id": "29_kenapa_bapak2_telepon_kenceng_orasi",
        "title": "Kenapa Bapak-Bapak Kalau Telepon Suaranya Kenceng Kayak Orasi?",
        "audio": "29_teleponorasi.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau lagi ngobrol di telepon suaranya kenceng banget sampai seisi rumah atau tetangga sebelah bisa denger?",
            "Anak-anaknya sering malu dan nyuruh ngecilin suara, padahal bapak-bapak gak sadar kalau suara mereka lagi sekeras mikrofon orasi demo!",
            "Secara sains, ini adalah fenomena biologis bernama Lombard Effect, yaitu refleks otomatis manusia menaikkan volume suara saat mendengar suara bising di sekitar.",
            "Ditambah lagi memori era telepon kabel jadul dan wartel, di mana sinyal suara analog butuh teriakan kencang agar terdengar jelas di seberang sana.",
            "Bapakmu cuma pengen memastikan pesan pentingnya sampai tanpa miskomunikasi! Bapak kamu kalau telepon suaranya santai atau mode toa masjid nih? Komen di bawah ya!"
        ]
    },
    # 9. Project 30
    {
        "num": 9,
        "id": "30_kenapa_kucing_dorong_barang_jatuh",
        "title": "Kenapa Kucing Suka Dorong Barang dari Meja Sampai Jatuh?",
        "audio": "30_kucingdorong.mp3",
        "scenes": [
            "Kenapa kucing suka banget natap mata kita sambil pelan-pelan dorong gelas, pulpen, atau HP dari atas meja sampai jatuh ke lantai?",
            "Banyak pemilik kucing yang mikir kucing mereka punya dendam pribadi atau sifat jahat, padahal ini murni insting pemburu!",
            "Kucing punya bantalan cakar yang sangat sensitif. Saat menowel benda mati, insting predatornya sedang menguji apakah benda itu hidup, lari, atau melawan.",
            "Faktor kedua adalah rasa bosan dan mencari perhatian. Kucing belajar bahwa suara pecahan barang adalah tombol otomatis yang bikin pemiliknya langsung mendekat!",
            "Jadi gelasmu bukan dijatuhin karena jahat, tapi kamu yang kena manipulasi psikologi kucing! Barang apa yang pernah dijatuhin kucingmu? Spill di komentar ya!"
        ]
    },
    # 10. Project 31
    {
        "num": 10,
        "id": "31_kenapa_remot_tv_digetok_nyala",
        "title": "Kenapa Remot TV Mau Abis Baterai Digetok Beneran Bisa Nyala Lagi?",
        "audio": "31_remotgetok.mp3",
        "scenes": [
            "Kenapa remot TV yang udah gak bisa mencet saluran, begitu digetok-getok ke telapak tangan atau digigit baterainya mendadak bisa nyala lagi?",
            "Trik ajaib turun-temurun ini sering dianggap kebetulan konyol, padahal ada penjelasan fisika dan kimia elektrokimia nyata di baliknya!",
            "Seiring waktu, kutub terminal baterai dan per tembaga remot mengalami oksidasi mikro yang menciptakan lapisan isolator penghambat arus listrik.",
            "Saat remot digetok atau baterai diputar, gesekan mekanik itu mengikis lapisan karat oksida dan memadatkan elektrolit sisa voltase nol koma satu volt!",
            "Metode kearifan lokal ini valid secara sains buat keadaan darurat! Kamu sendiri tim yang suka ngetok remot atau langsung ganti baterai baru nih? Komen ya!"
        ]
    },
    # 11. Project 32
    {
        "num": 11,
        "id": "32_kenapa_lagu_nyebelin_nempel_di_kepala",
        "title": "Kenapa Lagu Nyebelin Malah Nempel di Kepala Seharian (Earworm)?",
        "audio": "32_earworm.mp3",
        "scenes": [
            "Kenapa lagu jingle iklan receh atau potongan lagu yang kita benci malah muter terus berulang-ulang di dalam kepala seharian gak mau berhenti?",
            "Fenomena menjengkelkan ini punya nama ilmiah Earworm atau sindrom cacing telinga, dan dialami oleh sembilan puluh delapan persen manusia!",
            "Penyebab utamanya adalah Zeigarnik Effect! Otak manusia secara alami benci hal yang belum tuntas atau menggantung.",
            "Karena kamu cuma ingat sebagian reff lagu tanpa tahu lirik akhirnya, otakmu terus-menerus memutar potongan nada itu untuk mencari penutupnya!",
            "Trik ampuh menghentikannya: dengerin lagu itu sampai selesai atau kunyah permen karet! Lagu apa yang lagi nempel di kepalamu hari ini? Spill di komentar ya!"
        ]
    },
    # 12. Project 33
    {
        "num": 12,
        "id": "33_kenapa_restart_obat_ampuh_hp_lemot",
        "title": "Kenapa Restart Jadi Obat Paling Ampuh Buat HP dan PC Lemot?",
        "audio": "33_restart.mp3",
        "scenes": [
            "Kenapa setiap kali HP lemot, laptop hang, atau koneksi Wi-Fi macet, jurus andalan teknisi komputer cuma satu: coba di-restart dulu ya!",
            "Kelihatannya seperti solusi malas dan sepele, padahal restart adalah operasi pembersihan sistem paling canggih di dunia teknologi!",
            "Saat perangkat menyala berhari-hari, puluhan aplikasi meninggalkan residu kode sampah dan kebocoran memori alias memory leak di dalam RAM.",
            "Begitu kamu restart, pasokan listrik ke RAM terputus total, menghapus seluruh proses liar, me-reset register CPU, dan memuat ulang kernel dari nol!",
            "Dalam hitungan detik, perangkatmu kembali segar seperti baru keluar dari pabrik! Terakhir kali kamu restart HP kapan nih? Jangan-jangan udah sebulan gak dimatiin? Komen ya!"
        ]
    },
    # 13. Project 34
    {
        "num": 13,
        "id": "34_kenapa_lalat_susah_ditepok",
        "title": "Kenapa Lalat Susah Banget Ditepok Pakai Tangan Kosong?",
        "audio": "34_lalat.mp3",
        "scenes": [
            "Kenapa mau secepat apa pun tangan kita bergerak menepok lalat, serangga kecil ini selalu berhasil kabur dalam sepersekian detik?",
            "Apakah lalat punya insting cenayang yang bisa meramal masa depan, atau gerakan tangan kita yang sebenarnya terlalu lambat?",
            "Jawabannya ada pada kecepatan pemrosesan visual mata majemuk lalat! Manusia memproses sekitar enam puluh frame gambar per detik.",
            "Sementara lalat memproses hingga dua ratus lima puluh frame per detik! Di mata lalat, gerakan tanganmu yang super cepat itu terlihat seperti gerak lambat alias slow motion!",
            "Ditambah sensor hembusan udara di punggungnya yang bikin lalat langsung lepas landas! Kamu pernah sukses nangkep lalat pakai tangan kosong gak? Cerita di komentar ya!"
        ]
    },
    # 14. Project 35
    {
        "num": 14,
        "id": "35_kenapa_bapak2_suka_casing_hp_dompet",
        "title": "Kenapa Bapak-Bapak Suka Casing HP Dompet Kulit yang Nutup Layar?",
        "audio": "35_casingdompet.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau beli casing HP pilihannya hampir selalu seragam: casing model dompet kulit tebal yang punya penutup layar lipat?",
            "Anak muda sering menganggap model ini kuno dan ribet, tapi bagi bapak-bapak, casing dompet adalah mahakarya efisiensi hidup!",
            "Pertama, prinsip all-in-one! Bapak-bapak bisa menyelipkan KTP, SIM, STNK motor, dan beberapa lembar uang darurat tanpa perlu bawa dompet tebal terpisah.",
            "Kedua, proteksi tangki baja tiga ratus enam puluh derajat! Layar kaca terlindungi aman dari benturan kunci obeng di saku atau aspal jalanan.",
            "Desain ini bukti bapakmu orang yang praktis dan gak suka ribet! Coba cek HP bapak kamu sekarang, pakai casing dompet kulit juga gak nih? Komen ya!"
        ]
    },
    # 15. Project 36
    {
        "num": 15,
        "id": "36_kenapa_ada_ruang_kedua_perut_manis",
        "title": "Kenapa Selalu Ada 'Ruang Kedua di Perut' Buat Makanan Manis?",
        "audio": "36_perutmanis.mp3",
        "scenes": [
            "Kenapa pas makan nasi padang perut rasanya udah begah mau meledak, tapi begitu ditawari es krim atau martabak manis mendadak ada ruang kosong di perut?",
            "Banyak yang bercanda manusia punya dua lambung khusus makanan manis, padahal fenomena ilmiah ini bernama Sensory-Specific Satiety!",
            "Saat kita mengonsumsi makanan asin atau gurih terus-menerus, sensor rasa di lidah dan otak mengalami kejenuhan sensorik lokal.",
            "Begitu aroma dan rasa manis gula muncul, otak memprogram ulang sinyal kepuasan dan melepaskan hormon dopamin baru yang merelaksasi dinding lambung!",
            "Secara harfiah perutmu memang membesar karena rasa kenyang itu dikendalikan otak, bukan volume lambung! Makanan manis apa yang gak pernah bisa kamu tolak? Komen ya!"
        ]
    },
    # 16. Project 37
    {
        "num": 16,
        "id": "37_kenapa_flashdisk_64gb_kebaca_59gb",
        "title": "Kenapa Flashdisk 64 GB Dicolok Cuma Kebaca 59 GB?",
        "audio": "37_flashdisk59gb.mp3",
        "scenes": [
            "Kenapa setiap kali kita beli flashdisk atau hardisk baru bertuliskan enam puluh empat giga, pas dicolok ke laptop isinya cuma kebaca lima puluh sembilan giga?",
            "Banyak pembeli yang emosi dan ngira pabriknya nipu atau disunat lima giga, padahal ini murni perbedaan rumus hitungan matematika!",
            "Pabrik pembuat storage menggunakan sistem desimal kelipatan seribu. Bagi mereka, satu kilobyte adalah seribu byte.",
            "Tapi sistem operasi komputer Windows dan Android bekerja dengan sistem biner kelipatan seribu dua puluh empat! Akibatnya terjadi selisih konversi sekitar tujuh persen.",
            "Giga kamu gak hilang kemana-mana, cuma beda bahasa hitungan antara manusia dan mesin! Pernah mikir flashdisk-mu palsu gak gara-gara ini? Komen di bawah ya!"
        ]
    },
    # 17. Project 38
    {
        "num": 17,
        "id": "38_kenapa_nyamuk_dengungin_kuping",
        "title": "Kenapa Nyamuk Suka Dengungin Kuping Pas Mau Tidur?",
        "audio": "38_nyamuk.mp3",
        "scenes": [
            "Kenapa pas lampu kamar udah mati dan kita baru mau merem, tiba-tiba ada suara nyamuk dengung kencang tepat di samping liang telinga?",
            "Seakan-akan nyamuk sengaja ngejek dan nyari masalah, padahal telinga adalah area navigasi paling strategis bagi serangga penghisap darah!",
            "Nyamuk betina melacak mangsa menggunakan sensor gas karbon dioksida. Hidung dan mulut manusia mengeluarkan konsentrasi gas buang paling pekat!",
            "Saat terbang mendekati sumber nafas di wajah, suara kepakan sayap enam ratus kali per detik otomatis terdengar paling nyaring di daun telingamu.",
            "Ditambah lagi suhu hangat dan kelenjar keringat di kepala yang jadi magnet empuk! Kamu tipe yang langsung bangun nyalain lampu atau pasrah diselimutin nih? Komen ya!"
        ]
    },
    # 18. Project 39
    {
        "num": 18,
        "id": "39_kenapa_bapak2_nonton_reels_full_vol",
        "title": "Kenapa Bapak-Bapak Nonton Reels Volumenya Full Tanpa Headset?",
        "audio": "39_reelsfullvol.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau lagi asyik scroll TikTok atau nonton reels di ruang tamu, volumenya selalu disetel maksimal sampai suaranya menggema seisi rumah?",
            "Anak-anaknya sering pusing denger suara tawa rekaman dan backsound jedag-jedug, tapi bapak-bapak santai aja gak ngerasa berisik!",
            "Secara medis, ini berkaitan dengan presbikusis alias penurunan alami sensitivitas saraf pendengaran terhadap frekuensi suara tinggi di usia empat puluh tahun ke atas.",
            "Suara yang terdengar terlalu keras bagi telinga muda anak-anak, justru terdengar pas dan nyaman di telinga bapakmu agar dialognya jelas.",
            "Ditambah kebiasaan era TV tabung keluarga tempat suara ditonton ramai-ramai! Bapak kamu kalau nonton reels volumenya berapa persen nih? Spill di komentar ya!"
        ]
    },
    # 19. Project 40
    {
        "num": 19,
        "id": "40_kenapa_liat_orang_nguap_ikutan",
        "title": "Kenapa Liat Orang Nguap Bikin Kita Ikutan Nguap?",
        "audio": "40_nguap.mp3",
        "scenes": [
            "Kenapa pas kita ngeliat teman, orang asing di kereta, atau bahkan kucing di video lagi nguap, mulut kita otomatis ikut mangap lebar dan ikutan nguap?",
            "Banyak yang bercanda ini tanda kurang tidur barengan, padahal menguap menular adalah tes empati sosial paling mutakhir di otak kita!",
            "Penyebab utamanya adalah sel saraf khusus bernama Mirror Neurons! Sel ini bertugas mencerminkan tindakan dan emosi orang lain di dalam pikiran kita.",
            "Di zaman manusia purba primata, menguap serentak adalah kode non-verbal untuk menyelaraskan kewaspadaan kelompok dan mendinginkan suhu otak bersama-sama.",
            "Studi membuktikan makin dekat hubungan emosionalmu dengan seseorang, makin cepat kamu tertular nguapnya! Barusan kamu ikutan nguap gak baca ini? Ngaku di komentar ya!"
        ]
    },
    # 20. Project 41
    {
        "num": 20,
        "id": "41_kenapa_bapak2_kacak_pinggang_depan_rumah",
        "title": "Kenapa Bapak-Bapak Berdiri Berkacak Pinggang Depan Rumah?",
        "audio": "41_kacakpinggang.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau lagi berdiri di depan pagar rumah pas pagi atau sore hari, kedua tangannya hampir wajib nempel berkacak pinggang sambil mandang jalan?",
            "Pose legendaris ini sering jadi meme komedi, tapi dari kacamata fisiologi tulang dan insting manusia, ada manfaat besar di baliknya!",
            "Secara biomekanik, menaruh kedua tangan di atas tulang panggul membantu mendistribusikan beban tubuh atas dan meluruskan kurva lordosis tulang punggung bawah.",
            "Pose ini meredakan ketegangan otot pinggang setelah seharian duduk bekerja, sekaligus memperluas rongga dada agar nafas lebih lega.",
            "Ditambah lagi insting teritorial purba kepala keluarga untuk memantau keamanan wilayah rumahnya! Bapak kamu kalau pagi sering berkacak pinggang di depan rumah juga gak? Komen ya!"
        ]
    },
    # 21. Project 42
    {
        "num": 21,
        "id": "42_kenapa_bau_bensin_buku_baru_enak",
        "title": "Kenapa Bau Bensin dan Buku Baru Terasa Enak Bagi Sebagian Orang?",
        "audio": "42_baubensin.mp3",
        "scenes": [
            "Kenapa pas lagi isi bensin di SPBU atau baru buka segel buku novel baru, aromanya terasa wangi banget dan bikin kita pengen hirup dalam-dalam?",
            "Banyak yang merasa aneh sendiri dan takut dianggap kelainan, padahal ini respons neurobiologis yang dialami jutaan orang di dunia!",
            "Bensin mengandung senyawa hidrokarbon bernama benzena yang memiliki efek menekan sistem saraf pusat sementara dan memicu euforia ringan mirip obat bius.",
            "Aroma kimia ini langsung menyambar sistem limbik dan amigdala otak, yaitu pusat pengendali memori emosional masa kecil dan nostalgia perjalanan mobil keluarga.",
            "Sementara bau buku baru berasal dari degradasi senyawa lignin dan vanilin kertas yang mirip wangi vanila! Tapi awas jangan dihirup sengaja ya karena benzena beracun! Kamu tim suka bau bensin atau buku baru nih? Komen ya!"
        ]
    },
    # 22. Project 43
    {
        "num": 22,
        "id": "43_kenapa_kaca_mobil_helm_berembun",
        "title": "Kenapa Kaca Mobil dan Helm Berembun Tebal Pas Hujan?",
        "audio": "43_kacaembun.mp3",
        "scenes": [
            "Kenapa pas hujan deras turun, kaca mobil bagian dalam dan visor helm motor tiba-tiba buram tertutup kabut embun putih yang bikin gak kelihatan jalan?",
            "Banyak pemotor yang panik dan ngira kacanya kotor, padahal ini murni hukum termodinamika fisika tentang titik embun alias dew point!",
            "Saat hujan, udara di luar kabin atau helm suhunya dingin, sedangkan udara di dalam ruangan hangat karena hembusan nafas dan panas tubuh kita.",
            "Udara hangat yang sarat uap air nafas menabrak permukaan kaca yang dingin, membuat uap air mendadak kehilangan energi dan mengalami kondensasi!",
            "Milyaran tetesan air mikroskopis menempel dan membiaskan cahaya ke segala arah! Trik ampuhnya: lapisi sabun cair atau nyalakan AC mobil ke arah kaca! Komen pengalamanmu pas helm berembun ya!"
        ]
    },
    # 23. Project 44
    {
        "num": 23,
        "id": "44_kenapa_semut_papasan_salaman",
        "title": "Kenapa Semut Kalau Papasan di Jalan Selalu Salaman?",
        "audio": "44_semut.mp3",
        "scenes": [
            "Kenapa semut-semut kecil yang lagi jalan berbaris di dinding, setiap kali papasan selalu berhenti sepersekian detik dan saling nempelin kepala kayak lagi salaman?",
            "Banyak yang bercanda semut adalah hewan paling ramah dan sopan di dunia, padahal mereka lagi melakukan interogasi kimia tingkat tinggi!",
            "Semut memiliki indera penglihatan yang sangat buruk, sehingga mereka bergantung penuh pada antena di kepala untuk membaca senyawa feromon hidrokarbon kutikula.",
            "Saat saling menyentuhkan antena, semut sedang memeriksa KTP bau kimia rekannya: apakah dia teman satu sarang, atau penyusup dari koloni musuh!",
            "Selain itu, mereka juga melakukan trofalaksis, yaitu bertukar sampel sari makanan untuk mengabarkan arah sumber gula terdekat! Keren banget kan sistem radar semut? Komen di bawah ya!"
        ]
    },
    # 24. Project 45
    {
        "num": 24,
        "id": "45_kenapa_wasabi_nusuk_hidung",
        "title": "Kenapa Wasabi Gak Pedas di Lidah tapi Nusuk ke Hidung?",
        "audio": "45_wasabi.mp3",
        "scenes": [
            "Kenapa kalau kita makan pasta hijau wasabi pas makan sushi, lidah kita gak ngerasa kepedasan membakar kayak makan cabe rawit, tapi hidung dan kepala langsung berasa ditusuk jarum es?",
            "Sensasi kaget ini bikin banyak orang langsung megap-megap sambil megang batang hidung, padahal di baliknya ada perbedaan kimiawi yang luar biasa!",
            "Rasa pedas cabe berasal dari senyawa kapsaisin yang berbentuk minyak berat dan menempel erat pada reseptor panas TRPV1 di permukaan lidah.",
            "Sementara wasabi mengandung senyawa alil isotiosianat yang berbobot sangat ringan dan mudah menguap alias volatil!",
            "Saat dikunyah di mulut, uap kimianya langsung terbang naik ke rongga nasofaring hidung dan membakar reseptor saraf trigeminal pernapasan atas! Kamu kuat makan wasabi berapa banyak nih? Komen ya!"
        ]
    },
    # 25. Project 46
    {
        "num": 25,
        "id": "46_kenapa_merinding_pas_pipis",
        "title": "Kenapa Kita Suka Merinding Pas Lagi Pipis di Toilet?",
        "audio": "46_merindingpipis.mp3",
        "scenes": [
            "Kenapa di detik-detik terakhir pas kita buang air kecil di toilet, tiba-tiba seluruh tubuh kita bergidik menggigil dan bulu kuduk merinding sesaat?",
            "Sensasi misterius yang sering dialami kaum pria ini punya nama ilmiah resmi: Post-Micturition Convulsion Syndrome alias Pee Shivers!",
            "Penyebab pertamanya adalah pelepasan panas tubuh! Cairan urin bersuhu hangat sekitar tiga puluh tujuh derajat celsius keluar mendadak dalam volume besar.",
            "Penyebab keduanya adalah benturan sinyal saraf otonom! Saat kandung kemih kosong, sistem saraf parasimpatis mendadak turun dan saraf simpatis langsung melepaskan hormon katekolamin.",
            "Perubahan tekanan darah dan suhu mendadak itulah yang bikin ototmu bergetar refleks sesaat untuk menaikkan kembali suhu tubuh! Kamu sering ngalamin pee shivers juga gak? Komen di bawah ya!"
        ]
    },
    # 26. Project 47
    {
        "num": 26,
        "id": "47_kenapa_bulu_kaki_gak_panjang_kayak_rambut",
        "title": "Kenapa Bulu Kaki Gak Bisa Tumbuh Panjang Kayak Rambut?",
        "audio": "47_bulukaki.mp3",
        "scenes": [
            "Kenapa rambut di kepala kita kalau dibiarin gak dipotong bisa tumbuh panjang sampai sepunggung, tapi bulu kaki, kumis, dan alis berhenti di panjang segitu-gitu aja?",
            "Padahal mereka sama-sama tumbuh dari folikel kulit dan terbuat dari bahan protein keratin yang sama persis!",
            "Rahasianya ada pada durasi fase pertumbuhan rambut yang disebut Fase Anagen! Setiap helai rambut di tubuhmu punya jam biologis bawaan.",
            "Fase anagen rambut kepala berlangsung sangat lama, antara tiga sampai tujuh tahun sebelum rontok dan berganti baru.",
            "Sementara fase anagen bulu kaki dan tangan cuma berlangsung satu sampai dua bulan, sehingga folikelnya sudah keburu istirahat dan rontok sebelum sempat memanjang! Bayangin kalau bulu kaki bisa sepanjang rambut kepala, serem kan? Komen ya!"
        ]
    },
    # 27. Project 48
    {
        "num": 27,
        "id": "48_kenapa_cicak_bunyi_cekcek_malam",
        "title": "Kenapa Cicak Suka Bunyi 'Cek-Cek-Cek' di Dinding Pas Malam?",
        "audio": "48_cicak.mp3",
        "scenes": [
            "Kenapa cicak di dinding rumah suka tiba-tiba ngeluarin suara decakan cek-cek-cek yang nyaring pas tengah malam di saat ruangan lagi hening-heningnya?",
            "Orang tua zaman dulu sering bilang cicak lagi ngejek omongan kita atau ada makhluk halus lewat, padahal ini murni bahasa percintaan dunia reptil!",
            "Suara cek-cek-cek dihasilkan oleh cicak jantan dengan cara mengklik lidah dan langit-langit mulutnya secara berulang-ulang.",
            "Suara ini berfungsi sebagai panggilan kawin nokturnal untuk memikat cicak betina, sekaligus deklarasi batas wilayah kekuasaan terhadap cicak jantan saingannya.",
            "Selain itu, cicak juga bersuara saat merasa terancam oleh serangga pemangsa atau saat berebut spot lampu yang banyak nyamuknya! Mitos cicak apa yang paling sering kamu dengar? Cerita di komentar ya!"
        ]
    },
    # 28. Project 49
    {
        "num": 28,
        "id": "49_kenapa_bapak2_kunci_stang_kanan",
        "title": "Kenapa Bapak-Bapak Suka Ngunci Stang Motor Harus ke Arah Kanan?",
        "audio": "49_kuncistang.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau parkir motor selalu ngotot stangnya wajib dibelokkan dan dikunci ke arah kanan, bukan ke arah kiri seperti orang kebanyakan?",
            "Banyak anak muda yang menganggap ini cuma mitos jadul yang bikin ribet saat mau standar samping, tapi ada sejarah kejahatan otomotif di baliknya!",
            "Dulu beredar kabar bahwa stang yang dikunci ke kanan membuat ruang gerak lubang kunci tertutup rapat oleh bodi motor, sehingga maling susah memasukkan kunci T.",
            "Padahal di era motor modern saat ini, pabrikan sudah mendesain lubang pin pengunci stang dengan kekuatan silinder yang sama persis di kedua sisi!",
            "Meskipun bedanya tipis, kebiasaan ini bukti betapa telitinya bapak-bapak dalam menjaga aset keluarga dari risiko kehilangan! Kamu sendiri kalau parkir motor tim kunci stang kiri atau kanan nih? Komen ya!"
        ]
    },
    # 29. Project 50
    {
        "num": 29,
        "id": "50_kenapa_bisa_tumbuh_sehelai_jenggot_putih_kaku",
        "title": "Kenapa Bisa Tumbuh Sehelai Jenggot Putih yang Tebel dan Kaku?",
        "audio": "50_ubanjenggot.mp3",
        "scenes": [
            "Kenapa di dagu, pipi, atau kumis pria tiba-tiba bisa tumbuh satu helai bulu putih aneh yang panjang, tebal, dan kaku banget kayak kawat pancing?",
            "Padahal bulu di sekitarnya masih hitam halus dan normal, cuma satu helai mutan ini aja yang tumbuh mencolok sendirian!",
            "Fenomena unik ini di dunia dermatologi berkaitan dengan anomali folikel rambut bernama Pili Multigemini atau mutasi hipertrofi folikel lokal.",
            "Satu kantung folikel rambut mengalami lonjakan stimulasi hormon androgen yang berlebihan, sementara sel melanositnya kehabisan pigmen melanin.",
            "Akibatnya, helai rambut tersebut tumbuh super tebal, berwarna putih bening, dan memiliki tekstur sangat kaku! Kamu pernah nemu sehelai bulu kawat putih gini di wajahmu gak? Cabut atau biarin nih? Komen ya!"
        ]
    },
    # 30. Project 51
    {
        "num": 30,
        "id": "51_kenapa_gak_bisa_bersin_buka_mata",
        "title": "Kenapa Kita Gak Bisa Bersin Sambil Buka Mata?",
        "audio": "51_bersinmata.mp3",
        "scenes": [
            "Kenapa mau sekuat apa pun usaha kita menahan kelopak mata dengan jari tangan, kita secara fisik mustahil bisa bersin dalam kondisi mata terbuka?",
            "Banyak mitos menyeramkan yang bilang kalau bersin sambil melek bola mata kita bakal copot meloncat keluar, tapi benarkah secara medis?",
            "Mitos bola mata copot itu seratus persen salah kaprah! Bola mata kita terikat sangat kuat oleh enam otot ekstraokular di dalam rongga tengkorak.",
            "Alasan sebenarnya adalah refleks saraf kranial di batang otak! Begitu pusat bersin terpicu, saraf motorik otomatis mengirim sinyal ke otot orbicularis oculi untuk menutup rapat kelopak mata.",
            "Refleks bawaan ini dirancang alamiah untuk melindungi bola matamu dari paparan partikel kuman dan tekanan udara bersin yang kecepatannya mencapai seratus enam puluh kilometer per jam! Pernah coba maksa melek pas bersin gak? Komen ya!"
        ]
    },
    # 31. Project 52
    {
        "num": 31,
        "id": "52_kenapa_tombol_f_dan_j_ada_garis",
        "title": "Kenapa Tombol F dan J di Keyboard Ada Garis Tonjolan Timbul?",
        "audio": "52_tombolfj.mp3",
        "scenes": [
            "Kenapa dari puluhan tombol di keyboard laptop atau komputermu, cuma huruf F dan huruf J aja yang punya garis tonjolan kecil timbul di permukaannya?",
            "Pernah gak sengaja meraba tonjolan ini pas ngetik di kegelapan dan penasaran siapa orang iseng yang mendesainnya?",
            "Ternyata dua tonjolan kecil ini adalah mahakarya penemuan tahun 1988 oleh seorang wanita bernama June E. Botich untuk teknik mengetik sepuluh jari alias Touch Typing!",
            "Huruf F adalah rumah patokan bagi jari telunjuk kiri, dan huruf J adalah rumah patokan bagi jari telunjuk kanan.",
            "Dengan meraba tonjolan ini, jari-jarimu bisa langsung menempati posisi baris awal tanpa mata perlu menunduk melihat keyboard sama sekali! Kamu kalau ngetik masih harus ngeliat keyboard atau udah bisa merem nih? Komen ya!"
        ]
    },
    # 32. Project 53
    {
        "num": 32,
        "id": "53_kenapa_ngomongin_barang_muncul_iklan",
        "title": "Kenapa Pas Lagi Ngomongin Barang Tiba-Tiba Muncul Iklannya di HP?",
        "audio": "53_iklanhp.mp3",
        "scenes": [
            "Kenapa baru aja tadi siang kita ngobrolin merk sepatu atau kopi bareng temen di kafe, malamnya pas buka Instagram dan TikTok langsung muncul iklan barang itu persis?",
            "Banyak yang langsung paranoid dan yakin mikrofon HP kita diam-diam menyadap dan merekam seluruh percakapan kita setiap detik!",
            "Fakta teknologinya jauh lebih mencengangkan dari sekadar nyadap suara! Perusahaan teknologi gak butuh rekaman suara karena itu makan bandwidth raksasa.",
            "Mereka menggunakan algoritma prediktif berbasis Machine Learning yang membaca kesamaan lokasi GPS, koneksi IP Wi-Fi yang sama dengan temanmu, dan riwayat belanja digital!",
            "Kalau temanmu mencari sepatu itu di HP-nya saat sedang nongkrong bersamamu, algoritma otomatis menyimpulkan kamu juga tertarik pada barang yang sama! Sering ngerasa HP-mu kayak cenayang gak nih? Cerita di komentar ya!"
        ]
    },
    # 33. Project 54
    {
        "num": 33,
        "id": "54_kenapa_bapak2_jalan_mall_tangan_silang",
        "title": "Kenapa Bapak-Bapak Jalan di Mall Tangannya Disilang di Belakang?",
        "audio": "54_jalansilang.mp3",
        "scenes": [
            "Kenapa bapak-bapak kalau lagi nemenin istri belanja keliling mall atau pasar, gaya berjalannya khas banget dengan kedua tangan disilangkan di belakang punggung?",
            "Pose jalan santai ini sering dijuluki gaya bapak-bapak inspeksi proyek, tapi dari kacamata postur tubuh, ada manfaat ergonomis nyata!",
            "Menyilangkan tangan di belakang punggung secara otomatis menarik tulang belikat ke belakang dan membuka postur dada yang bungkuk.",
            "Hal ini memindahkan pusat gravitasi tubuh sedikit ke depan, mengurangi beban tekanan pada persendian lutut saat harus berjalan lambat berjam-jam.",
            "Ditambah lagi sensasi psikologis menahan diri agar gak gatal megang-megang barang belanjaan yang bisa bikin kantong jebol! Bapak kamu kalau jalan di mall gayanya begini juga gak? Komen di bawah ya!"
        ]
    },
    # 34. Project 55
    {
        "num": 55,
        "id": "55_kenapa_bapak2_bersin_suara_petir",
        "title": "Kenapa Bapak-Bapak Kalau Bersin Suaranya Menggelegar Kayak Petir?",
        "audio": "55_bersinpetir.mp3",
        "scenes": [
            "Kenapa bersin bapak-bapak di rumah suaranya selalu menggelegar dahsyat kayak ledakan petir sampai bikin kaget seisi rumah dan burung di genteng beterbangan?",
            "Anak dan istri sering jengkel dan nanya kenapa gak ditahan sedikit suaranya, padahal ada faktor anatomi paru-paru di baliknya!",
            "Kapasitas vital paru-paru dan ketebalan otot diafragma pria dewasa secara biologis jauh lebih besar dibanding wanita atau remaja.",
            "Volume udara yang diledakkan saat membersihkan saluran pernapasan bisa mencapai desibel sangat tinggi jika pita suara ikut bergetar lepas.",
            "Faktor kedua adalah hilangnya rasa jaim sosial! Menahan bersin justru berbahaya karena bisa merobek gendang telinga atau pembuluh darah mata! Bersin bapak kamu seberapa kencang nih suaranya? Komen ya!"
        ]
    },
    # 35. Project 56
    {
        "num": 56,
        "id": "56_kenapa_bapak2_nyelipin_pulpen_telinga",
        "title": "Kenapa Bapak-Bapak Suka Nyelipin Pulpen di Daun Telinga?",
        "audio": "56_pulpentelinga.mp3",
        "scenes": [
            "Kenapa bapak-bapak, mandor bangunan, atau pedagang pasar suka banget nyelipin pulpen, pensil kayu, atau rokok di atas daun telinga mereka?",
            "Gaya ini sering dianggap ikonik dan nyentrik, tapi secara fungsi kerja, ini adalah teknik akses tercepat yang pernah diciptakan manusia!",
            "Secara anatomi, lekukan aurikula dan fossa triangularis di atas daun telinga manusia membentuk klem elastis alami yang pas menjepit benda silinder.",
            "Menaruh pulpen di telinga membuat tangan tetap bebas bekerja dan mencegah pulpen hilang terselip di dalam tumpukan kantong celana yang sempit.",
            "Sensasi sentuhan di daun telinga juga menjadi pengingat sensorik langsung bahwa alat tulis selalu siap digunakan dalam hitungan detik! Kamu pernah coba nyelipin pulpen di telinga juga gak? Komen ya!"
        ]
    },
    # 36. Project 57
    {
        "num": 36,
        "id": "57_kenapa_mata_keluar_bintik_cacing",
        "title": "Kenapa Mata Suka Keluar Bintik Melayang Kayak Cacing Bening?",
        "audio": "57_eyefloaters.mp3",
        "scenes": [
            "Kenapa pas kita lagi natap langit biru cerah atau tembok putih polos, tiba-tiba ada bintik-bintik transparan melayang kayak cacing bening yang kalau dilihat malah kabur?",
            "Banyak yang panik takut ada cacing sungguhan masuk ke bola mata, padahal fenomena medis ini bernama Eye Floaters!",
            "Bola mata kita diisi oleh cairan kental mirip jeli bernama vitreous humor yang menjaga bentuk bola mata tetap bulat sempurna.",
            "Seiring bertambahnya usia, serat protein kolagen di dalam cairan jeli ini bisa mengering dan menggumpal menjadi serpihan mikroskopis.",
            "Saat cahaya masuk ke mata, serpihan kolagen mengambang ini melemparkan bayangan gelap ke permukaan retina kita! Selama jumlahnya gak mendadak ribuan disertai kilatan cahaya, floaters ini sangat normal! Kamu sering liat cacing bening ini juga gak? Komen ya!"
        ]
    },
    # 37. Project 58
    {
        "num": 37,
        "id": "58_kenapa_nafas_bangun_tidur_bau",
        "title": "Kenapa Nafas Bangun Tidur Baunya Kayak Naga Purba?",
        "audio": "58_nafasbau.mp3",
        "scenes": [
            "Kenapa orang yang sebelum tidur udah rajin sikat gigi dan kumur antiseptik pun, pas bangun tidur di pagi hari nafasnya tetap berbau tajam menyengat kayak naga purba?",
            "Banyak yang malu sama pasangannya dan langsung buru-buru tutup mulut, padahal fenomena Morning Breath adalah proses biologi alami yang dialami semua manusia!",
            "Kuncinya ada pada produksi air liur atau saliva! Di siang hari, air liur terus mengalir membilas sisa makanan dan membunuh bakteri jahat di mulut.",
            "Tapi saat kita tidur nyenyak selama delapan jam, produksi air liur turun drastis hingga sembilan puluh persen, membuat rongga mulut menjadi kering kerontang.",
            "Kondisi kering tanpa oksigen ini jadi surga bagi milyaran bakteri anaerob untuk berpesta memecah sisa protein menjadi gas sulfur yang baunya busuk! Minum air putih hangat langsung bikin baunya hilang loh! Pernah ngalamin bau naga ini kan? Komen ya!"
        ]
    },
    # 38. Project 59
    {
        "num": 38,
        "id": "59_kenapa_kebelet_bab_masuk_toko_buku",
        "title": "Kenapa Orang Suka Mendadak Kebelet BAB Pas Masuk Toko Buku?",
        "audio": "59_tokobukubab.mp3",
        "scenes": [
            "Kenapa pas kita baru beberapa langkah masuk ke dalam toko buku atau perpustakaan yang sunyi, mendadak perut melilit dan kebelet buang air besar?",
            "Fenomena aneh tapi nyata ini sangat terkenal di dunia dengan sebutan Fenomena Mariko Aoki, diambil dari nama wanita Jepang yang pertama kali curhat di majalah tahun 1985!",
            "Penyebab pertamanya adalah aroma khas kertas dan tinta cetak! Senyawa kimia pelarut tinta buku diketahui memiliki efek menenangkan yang merangsang saraf parasimpatis usus.",
            "Penyebab keduanya adalah kondisi psikologis rileks! Saat otak berpindah dari jalanan yang bising ke suasana toko buku yang tenang dan ber-AC dingin, otot perut dan sfingter anus mengalami dekompresi relaksasi.",
            "Akibatnya, gerakan peristaltik usus langsung aktif mendorong sisa pencernaan ke bawah! Kamu pernah ngerasa kebelet BAB pas masuk toko buku juga gak nih? Ngaku di komentar ya!"
        ]
    },
    # 39. Project 60
    {
        "num": 39,
        "id": "60_kenapa_suara_gesekan_kapur_bikin_ngilu",
        "title": "Kenapa Suara Gesekan Kapur di Papan Tulis Bikin Ngilu Parah?",
        "audio": "60_ngilukapur.mp3",
        "scenes": [
            "Kenapa mendengar suara gesekan kuku, kapur tulis, atau garpu di piring kaca bisa langsung bikin gigi ngilu, telinga sakit, dan bulu kuduk merinding parah?",
            "Hanya membayangkan suaranya saja sudah bisa bikin kita bergidik, padahal volumenya gak sekeras suara knalpot motor balap!",
            "Studi neurosains membuktikan suara gesekan ini berada di rentang frekuensi audio dua ribu sampai empat ribu Hertz.",
            "Rentang frekuensi ini ternyata persis sama dengan frekuensi jeritan bahaya bayi manusia purba atau lolongan panik kera saat diserang predator jutaan tahun lalu!",
            "Begitu telinga menangkap nada ini, amigdala otak langsung membunyikan alarm bahaya purba dan memicu lonjakan refleks ngilu di sistem saraf otonom! Suara apa yang paling gak bisa kamu tahan ngilunya? Spill di komentar ya!"
        ]
    },
    # 40. Project 61
    {
        "num": 40,
        "id": "61_kenapa_burung_gereja_jalannya_loncat",
        "title": "Kenapa Burung Gereja di Tanah Jalannya Selalu Loncat-Loncat?",
        "audio": "61_burungloncat.mp3",
        "scenes": [
            "Kenapa burung gereja atau merpati yang lagi nyari remah roti di tanah jalannya selalu melompat-lompat dengan kedua kaki barengan, bukannya melangkah satu per satu kayak ayam?",
            "Apakah kakinya terlalu pendek untuk melangkah, atau ada rahasia biomekanik di balik cara jalan lucu ini?",
            "Jawabannya ada pada habitat evolusi anatomi kakinya! Burung gereja adalah spesies arboreal yang nenek moyangnya menghabiskan seluruh hidup bertengger di ranting pohon.",
            "Otot kaki dan jari-jarinya dirancang otomatis mencengkeram ranting secara simetris, bukan untuk berjalan menjejak di permukaan tanah datar.",
            "Saat berada di tanah, melompat dengan kedua kaki sekaligus jauh lebih hemat energi dan memudahkan mereka langsung lepas landas terbang jika ada kucing mendekat! Pernah perhatiin cara jalan burung gereja kan? Gemas banget! Komen ya!"
        ]
    },
    # 41. Project 62
    {
        "num": 41,
        "id": "62_kenapa_khong_guan_gak_ada_ayah",
        "title": "Kenapa Kaleng Biskuit Khong Guan Cuma Ada Ibu dan Anak Tanpa Ayah?",
        "audio": "62_khongguan.mp3",
        "scenes": [
            "Kenapa lukisan legendaris di kaleng biskuit Khong Guan dari zaman kakek-nenek kita sampai sekarang cuma menampilkan sosok ibu dan dua anaknya yang lagi minum teh tanpa ada sosok ayah?",
            "Misteri ke mana perginya sosok ayah ini sudah melahirkan ribuan teori konspirasi lucu di media sosial selama puluhan tahun!",
            "Fakta sebenarnya diungkapkan langsung oleh sang pelukis legendarisnya, Bapak Bernardus Prasodjo!",
            "Konsep gambar ini dibuat tahun 1970-an untuk membidik target pasar utama biskuit keluarga, yaitu ibu rumah tangga yang sedang menikmati sore bersama anak-anaknya di ruang makan.",
            "Sosok ayahnya sama sekali gak hilang, melainkan sedang bekerja mencari nafkah di luar rumah, atau dialah yang sedang memotret momen hangat keluarga tersebut! Di rumahmu kaleng Khong Guan isinya biskuit asli atau rengginang nih? Komen ya!"
        ]
    },
    # 42. Project 63
    {
        "num": 42,
        "id": "63_kenapa_kecoa_mati_posisi_terlentang",
        "title": "Kenapa Kecoa Kalau Mati Posisinya Hampir Selalu Terlentang?",
        "audio": "63_kecoamutlak.mp3",
        "scenes": [
            "Kenapa setiap kali kita nemuin bangkai kecoa di lantai kamar mandi atau bawah lemari, posisinya hampir seratus persen selalu terlentang dengan enam kakinya mengarah ke atas langit?",
            "Apakah kecoa punya ritual khusus sebelum meninggal, atau ada alasan hukum gravitasi di baliknya?",
            "Di alam liar, kecoa hidup di atas tumpukan daun dan tanah gembur yang mudah dicengkeram cakarnya untuk membalikkan badan saat terjatuh.",
            "Tapi di lantai rumah modern yang terbuat dari keramik licin, cakar kecoa gak bisa mendapatkan daya cengkeram traksi sama sekali!",
            "Begitu kecoa lemas terkena semprotan insektisida, otot kakinya mengalami kejang tremor dan gravitasi menarik punggungnya yang berat dan membulat membalik ke lantai tanpa bisa bangun lagi! Kamu tipe yang berani basmi kecoa atau auto teriak lari nih? Komen ya!"
        ]
    },
    # 43. Project 64
    {
        "num": 43,
        "id": "64_kenapa_minuman_boba_es_doang_di_akhir",
        "title": "Kenapa Minuman Boba Kalau Disedot Sering Bobanya Abis Duluan?",
        "audio": "64_bobasisa.mp3",
        "scenes": [
            "Kenapa setiap kali kita beli minuman boba milk tea, butiran kenyal bobanya sering kali habis duluan di tengah jalan, atau kebalikannya: minumannya udah habis tapi butiran bobanya masih numpuk di dasar gelas?",
            "Tragedi minum boba gak seimbang ini sering bikin kita overthinking, padahal ada hukum dinamika fluida dan gravitasi butiran yang mengaturnya!",
            "Sedotan boba memiliki diameter lubang besar yang dirancang khusus untuk memotong hambatan viskositas cairan susu kental.",
            "Saat kamu menyedot dengan posisi sedotan miring menyentuh dasar gelas, tekanan vakum paling kuat tercipta tepat di dasar tempat butiran boba mengendap karena massa jenisnya yang padat.",
            "Akibatnya butiran tapioka terhisap jauh lebih cepat dibanding cairan di atasnya! Trik ampuhnya: angkat ujung sedotan satu sentimeter dari dasar gelas agar boba dan teh terminum seimbang sampai tetes terakhir! Kamu tim boba habis duluan atau boba sisa banyak nih? Komen ya!"
        ]
    }
]

def main():
    print(f"🚀 Memperbarui 43 project.json dan membuat NASKAH_TELEPROMPTER_SIAP_REKAM.md...")
    
    # 1. Update project.json in all 43 folders
    for item in ALL_43_SCRIPTS:
        p_id = item["id"]
        p_dir = os.path.join(PROJECTS_DIR, p_id)
        p_json_path = os.path.join(p_dir, "project.json")
        
        if os.path.exists(p_json_path):
            try:
                with open(p_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Update scene texts with exact teleprompter text
                for idx, sc_text in enumerate(item["scenes"]):
                    if idx < len(data.get("scenes", [])):
                        data["scenes"][idx]["text"] = sc_text
                        # Update subtitles
                        words = sc_text.split()
                        mid = len(words) // 2
                        data["scenes"][idx]["subtitles"] = [
                            {"start": 0.1, "end": 3.0, "text": " ".join(words[:mid]), "highlight": False},
                            {"start": 3.0, "end": 6.5, "text": " ".join(words[mid:]), "highlight": True}
                        ]
                
                with open(p_json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  [SYNCED] {p_id}")
            except Exception as e:
                print(f"  [ERROR] {p_id}: {e}")

    # 2. Build Master Markdown Teleprompter
    md_lines = [
        "# 🎙️ NASKAH TELEPROMPTER LENGKAP 43 KONTEN: ADHI STUDIO",
        "## Master Batch Siap Rekam (Project 22 s/d 64)",
        "",
        "> 📁 **Folder Tujuan Export Audio Audacity**:  ",
        "> `/home/integer009/PROJECTS/adhi_studio_portable/adhi_studio/assets/audio_record/`  ",
        "> *(Sistem mendukung nama pendek seperti `22_kentut.mp3` atau `kentut.mp3`)*",
        ">",
        "> 💡 **Panduan & Tips Rekam Mas Adhi**:  ",
        "> - Format rekaman: Mono / Stereo, 44.1 kHz / 48 kHz.  ",
        "> - Beri jeda hening sekitar 0.5 detik di antara perpindahan adegan (Scene).  ",
        "> - Buka naskah ini di layar samping monitor sambil jalankan Audacity!  ",
        "> - Setelah selesai rekam, cukup ketik: `python3 engine/batch_runner.py` untuk auto-render video!",
        "",
        "---",
        ""
    ]

    for item in ALL_43_SCRIPTS:
        md_lines.append(f"### {item['num']}. Project {item['id'][:2]}: {item['title']}")
        md_lines.append(f"*Audio Export*: **`{item['audio']}`** (atau `{item['audio'].split('_')[-1]}`) | *Durasi Target*: ~45-50 detik")
        md_lines.append("")
        for s_idx, sc_text in enumerate(item["scenes"]):
            s_num = s_idx + 1
            lbl = "Hook" if s_num == 1 else ("Mitos/Kontras" if s_num == 2 else ("Penjelasan Sains" if s_num == 3 else ("Analogi AHA" if s_num == 4 else "Call To Action (CTA)")))
            md_lines.append(f"* **[Scene {s_num} - {lbl}]**  ")
            md_lines.append(f"  > *\"{sc_text}\"*")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    full_md = "\n".join(md_lines)

    # Write to adhi_studio and root
    path1 = os.path.join(BASE_DIR, "NASKAH_TELEPROMPTER_SIAP_REKAM.md")
    path2 = os.path.join(os.path.dirname(BASE_DIR), "NASKAH_TELEPROMPTER_SIAP_REKAM.md")

    with open(path1, "w", encoding="utf-8") as f:
        f.write(full_md)
    with open(path2, "w", encoding="utf-8") as f:
        f.write(full_md)

    print(f"🎉 SUKSES! NASKAH_TELEPROMPTER_SIAP_REKAM.md berisi 43 KONTEN LENGKAP berhasil disimpan di:")
    print(f"  1. {path1}")
    print(f"  2. {path2}")

if __name__ == "__main__":
    main()
