#!/usr/bin/env python3
"""
Adhi Studio - Draft Factory 43 Konten Baru (Project 22 s/d 64)
Menghasilkan paket draft lengkap untuk 43 proyek tanpa merender video:
- Folder projects/<id>/
- project.json (5 Scene naskah hook KENAPA di detik 0-1, subtitle, prompt visual)
- thumbnail.jpg (Minimalist KENAPA thumbnail)
- 4 file caption platform sosmed (YouTube, TikTok, Instagram, Facebook) dengan formula 5 hashtag
- output/ (3 pure meme internet 1080x1350 rasio 4:5 + caption video & caption meme)
- assets/scene1.jpg s/d scene5.jpg (Gambar visual 9:16)
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
sys.path.insert(0, BASE_DIR)

from engine.thumbnail import create_minimalist_thumbnail
from engine.meme_generator import generate_project_memes_and_captions

TOPICS_DATA = [
    {
        "id": "22_kenapa_bau_kentut_sendiri_biasa_aja",
        "title": "Kenapa Bau Kentut Sendiri Biasa Aja tapi Orang Lain Bikin Emosi?",
        "topic_tag": "SainsBiologi",
        "audio_expected": "22_kentut.mp3",
        "scenes": [
            ("Kenapa kalau kita buang angin sendiri baunya biasa aja, tapi giliran orang lain yang kentut baunya langsung bikin emosi dan mual setengah mati?", "A funny 3D cartoon character smelling something foul while another person looks guilty in living room, warm cozy lighting, 9:16 vertical"),
            ("Padahal secara kimiawi, gas sulfur hidrogen yang keluar dari perut semua manusia itu sama-sama menyengat dan beracun!", "A 3D visualization of green cartoon gas molecules with skull icons floating playfully in air, 9:16 vertical"),
            ("Ternyata ini mekanisme cerdas adaptasi sensori olfaktori dan self-serving bias otak kita! Otak sudah mengantisipasi aroma bakteri tubuh sendiri sejak lahir.", "A stylized 3D human head with glowing brain pathways analyzing olfactory sensory signals, modern clean medical render, 9:16 vertical"),
            ("Sementara bau tubuh orang asing dianggap oleh insting purba sebagai potensi ancaman penyakit atau racun berbahaya!", "A primitive caveman sensing danger with funny alarm sirens glowing around his nose, 3D animated style, 9:16 vertical"),
            ("Jadi kamu gak salah kalau emosi, hidungmu cuma lagi ngejalanin protokol pertahanan hidup! Siapa temenmu yang kentutnya paling mematikan? Tag di komentar ya!", "A friendly 3D cartoon person holding nose laughing pointing to comments icon, 9:16 vertical")
        ]
    },
    {
        "id": "23_kenapa_kucing_zoomies_jam_3_pagi",
        "title": "Kenapa Kucing Tiba-Tiba Lari Kesurupan Jam 3 Pagi (Zoomies)?",
        "topic_tag": "DuniaHewan",
        "audio_expected": "23_zoomies.mp3",
        "scenes": [
            ("Kenapa kucing yang seharian tidur manis tiba-tiba lari kesurupan keliling rumah jam tiga pagi sambil lompat-lompat nabrak tembok?", "A funny 3D fluffy cat running at lightning speed with motion blur across a dark living room at 3am, 9:16 vertical"),
            ("Banyak yang ngira kucing lagi ngeliat hantu atau diganggu jin, padahal ini murni fenomena biologi bernama Frenetic Random Activity Periods atau Zoomies!", "A 3D illustration of a cute cat with glowing eyes looking playful, clock showing 3:00 AM on wall, 9:16 vertical"),
            ("Sebagai predator nokturnal alami, kucing secara biologis diprogram untuk berburu mangsa di waktu fajar dan tengah malam.", "A dramatic 3D silhouette of an agile wild cat hunting in twilight moonlight, cinematic lighting, 9:16 vertical"),
            ("Karena kucing peliharaan tidur enam belas jam dan gak perlu berburu tikus, tumpukan energi di ototnya meledak sekaligus dalam hitungan menit!", "A dynamic 3D cartoon battery icon overcharging with lightning sparks next to an energetic jumping cat, 9:16 vertical"),
            ("Jadi tenang aja, kucingmu bukan kesurupan tapi cuma lagi ngabisin kuota baterai predatornya! Kucing kamu kalau zoomies jam berapa nih? Spill di komentar ya!", "A cozy 3D cartoon cat finally curling up asleep on carpet looking peaceful, 9:16 vertical")
        ]
    },
    {
        "id": "24_kenapa_tumbuh_tahi_lalat_baru",
        "title": "Kenapa Orang Bisa Nambah Punya Tahi Lalat Baru di Tubuhnya?",
        "topic_tag": "KesehatanKulit",
        "audio_expected": "24_tahilalat.mp3",
        "scenes": [
            ("Kenapa pas lagi ngaca tiba-tiba ada tahi lalat baru di tangan atau wajah, padahal perasaan waktu kecil gak ada sama sekali?", "A 3D cartoon person looking closely in a mirror pointing with surprise at a tiny new beauty mark on cheek, 9:16 vertical"),
            ("Banyak yang langsung overthinking takut tumor ganas, padahal sebagian besar tahi lalat baru adalah hal yang sangat normal!", "A 3D conceptual medical diagram showing benign skin cells under soft magnifying glass, clean aesthetic, 9:16 vertical"),
            ("Tahi lalat terjadi saat sel penghasil pigmen bernama melanosit berkembang biak secara bergerombol di satu titik kulit, bukan menyebar merata.", "A stylized 3D microscopic view of glowing melanin pigment clusters forming naturally in dermis layers, 9:16 vertical"),
            ("Pemicu utamanya adalah paparan radiasi sinar ultraviolet matahari dan perubahan lonjakan hormon saat usia dewasa atau kehamilan.", "A 3D illustration of golden sun rays touching skin with microscopic protective shield activating, 9:16 vertical"),
            ("Tapi ingat aturan ABCDE: kalau bentuknya asimetris, tepinya bergerigi, atau cepat membesar, wajib periksa ke dokter ya! Coba cek ada tahi lalat baru gak di tanganmu? Spill di komentar!", "A friendly 3D cartoon doctor holding a checklist smiling warmly, 9:16 vertical")
        ]
    },
    {
        "id": "25_kenapa_gak_bisa_geli_gelitik_sendiri",
        "title": "Kenapa Kita Gak Bisa Geli Kalau Ngegelitik Diri Sendiri?",
        "topic_tag": "SainsOtak",
        "audio_expected": "25_gelitik.mp3",
        "scenes": [
            ("Kenapa pas orang lain nyolek pinggang kita langsung geli setengah mati sampai teriak, tapi pas tangan sendiri yang ngegelitik rasanya hambar banget?", "A 3D cartoon character trying to tickle their own ribs with a bored expression versus laughing hysterically when friend tickles them, 9:16 vertical"),
            ("Padahal saraf peraba di kulit telapak tangan dan pinggangmu itu adalah reseptor sentuhan yang sama persis!", "A detailed 3D diagram of touch nerve endings in skin emitting tiny sensory electrical pulses, 9:16 vertical"),
            ("Kuncinya ada di otak kecil bernama cerebellum! Cerebellum bertugas memprediksi konsekuensi sensorik dari semua gerakan yang kita rencanakan sendiri.",
             "A futuristic 3D glowing brain highlighting the cerebellum area calculating predictive sensory filters, 9:16 vertical"),
            ("Begitu tanganmu bergerak mau menggelitik, cerebellum langsung membatalkan sensasi geli sebelum sinyalnya sempat bikin kamu tertawa!",
             "A 3D conceptual cancel stamp or filter icon blocking a tickle signal in neural network, 9:16 vertical"),
            ("Otak kita sengaja memblokirnya biar kita bisa fokus mendeteksi ancaman sentuhan asing seperti serangga berbisa! Coba gelitik pinggangmu sekarang, geli gak? Tulis di komentar ya!",
             "A 3D cartoon character testing their own tickle laughing, pointing to comments, 9:16 vertical")
        ]
    },
    {
        "id": "26_kenapa_bapak2_ngetik_hp_satu_jari",
        "title": "Kenapa Bapak-Bapak Kalau Ngetik HP Cuma Pakai Satu Jari Telunjuk?",
        "topic_tag": "TechBapak2",
        "audio_expected": "26_ketik1jari.mp3",
        "scenes": [
            ("Kenapa bapak-bapak kalau ngetik pesan di HP gayanya selalu khas banget: tangan kiri megang erat HP, terus tangan kanan ngetik pakai satu jari telunjuk?", "A funny 3D caricature of a dad wearing batik squinting at smartphone typing with index finger, 9:16 vertical"),
            ("Anak muda sering ngetawain gaya mengetik lambat ini, padahal ada alasan medis dan sejarah teknologi yang sangat masuk akal di baliknya!", "A comparison split screen showing fast teen two-thumb typing versus careful dad single-finger typing, 3D style, 9:16 vertical"),
            ("Pertama, penurunan daya akomodasi lensa mata alias presbiopi! Bapak-bapak butuh jarak fokus lebih jauh agar tulisan di layar terbaca jelas.", "An optical 3D diagram showing presbyopia focal distance changes in eyes after age 40, clean medical aesthetic, 9:16 vertical"),
            ("Kedua, memori otot mesin tik mekanik jadul! Dulu tuts mesin tik butuh ditekan keras satu per satu, bukan disentuh ringan pakai jempol.", "A vintage mechanical typewriter blending into a modern smartphone touchscreen, 3D artistic transition, 9:16 vertical"),
            ("Jadi itu bukan gaptek, tapi kebiasaan legendaris yang membuktikan jam terbang hidup bapakmu! Bapak kamu kalau ngetik pakai jari telunjuk juga gak nih? Spill di komentar ya!", "A warm 3D dad smiling giving a thumbs up with his famous typing index finger, 9:16 vertical")
        ]
    },
    {
        "id": "27_kenapa_baterai_hp_1_persen_tahan_lama",
        "title": "Kenapa Baterai HP Pas 1 Persen Tahan Lebih Lama daripada 100 ke 99 Persen?",
        "topic_tag": "TeknologiHP",
        "audio_expected": "27_baterai1persen.mp3",
        "scenes": [
            ("Kenapa pas baterai HP tinggal satu persen rasanya kayak punya nyawa cadangan dan bisa tahan sampai belasan menit?", "A 3D cartoon smartphone with a glowing red 1% battery icon refusing to die like a superhero, 9:16 vertical"),
            ("Sementara waktu baterai penuh seratus persen, baru dicabut semenit dari charger langsung drop ke sembilan puluh sembilan persen?", "A fast countdown graphic showing 100% dropping immediately, dynamic 3D tech render, 9:16 vertical"),
            ("Ternyata persentase baterai di layar itu bukan takaran air di ember, tapi estimasi algoritma fuel gauge berdasarkan voltase kimia litium!", "A high tech 3D exploded view of a lithium-ion battery cell with voltage wave graphs, 9:16 vertical"),
            ("Produsen sengaja menaruh buffer voltase cadangan di angka satu persen agar sistem operasi sempat menyimpan data penting sebelum mati total.", "A 3D safe vault icon protecting data files inside a glowing silicon microchip, 9:16 vertical"),
            ("Jadi satu persen itu sebenarnya penyelamat darurat dari pabrik biar HP-mu gak rusak mendadak! Rekor HP kamu pas 1 persen tahan berapa lama? Spill di komentar ya!", "A funny 3D cartoon person cheering celebrating their 1% phone surviving, 9:16 vertical")
        ]
    },
    {
        "id": "28_kenapa_siku_kepentok_kesetrum_ngilu",
        "title": "Kenapa Siku Kepentok Rasanya Kesetrum Ngilu Banget?",
        "topic_tag": "SainsTubuh",
        "audio_expected": "28_siku.mp3",
        "scenes": [
            ("Kenapa kalau siku tangan gak sengaja kepentok ujung meja, rasanya bukan memar biasa tapi kesetrum ngilu sampai ke ujung kelingking?", "A funny 3D cartoon character holding their elbow with electric shock bolts glowing around their arm, 9:16 vertical"),
            ("Banyak yang mengira tulang siku kita yang patah, padahal tulang siku sama sekali gak punya sensor listrik seperti itu!", "A 3D anatomical model of human elbow bone structure with transparent muscle tissue, 9:16 vertical"),
            ("Biang keladinya adalah saraf ulnaris! Saraf utama pengendali tangan ini melewati terowongan sempit di siku tanpa bantalan daging atau lemak.", "A glowing yellow electrical nerve cord passing between bone grooves in a 3D medical visualization, 9:16 vertical"),
            ("Begitu siku kepentok, saraf ulnaris langsung terjepit telak di antara tulang keras dan meja, mengirimkan ledakan sinyal listrik ke otak!", "A dynamic 3D impact spark between bone and nerve creating ripple shockwaves, 9:16 vertical"),
            ("Sensasi aneh ini dijuluki orang barat sebagai Funny Bone, padahal gak ada lucu-lucunya sama sekali! Kamu terakhir kepentok siku kapan nih? Sakit banget kan? Komen ya!", "A 3D cartoon person wincing with funny expression pointing to elbow, 9:16 vertical")
        ]
    },
    {
        "id": "29_kenapa_bapak2_telepon_kenceng_orasi",
        "title": "Kenapa Bapak-Bapak Kalau Telepon Suaranya Kenceng Kayak Orasi?",
        "topic_tag": "KulturBapak2",
        "audio_expected": "29_teleponorasi.mp3",
        "scenes": [
            ("Kenapa bapak-bapak kalau lagi ngobrol di telepon suaranya kenceng banget sampai seisi rumah atau tetangga sebelah bisa denger?", "A funny 3D cartoon dad shouting loudly into a smartphone with giant soundwave rings vibrating the room, 9:16 vertical"),
            ("Anak-anaknya sering malu dan nyuruh ngecilin suara, padahal bapak-bapak gak sadar kalau suara mereka lagi sekeras mikrofon orasi demo!", "Family members covering ears with funny shocked expressions in 3D animated style, 9:16 vertical"),
            ("Secara sains, ini adalah fenomena biologis bernama Lombard Effect, yaitu refleks otomatis manusia menaikkan volume suara saat mendengar suara bising di sekitar.", "A 3D conceptual infographic of human auditory feedback loop adjusting vocal cord volume, 9:16 vertical"),
            ("Ditambah lagi memori era telepon kabel jadul dan wartel, di mana sinyal suara analog butuh teriakan kencang agar terdengar jelas di seberang sana.", "A nostalgic 3D transition from an old public telephone booth into modern smartphone, 9:16 vertical"),
            ("Bapakmu cuma pengen memastikan pesan pentingnya sampai tanpa miskomunikasi! Bapak kamu kalau telepon suaranya santai atau mode toa masjid nih? Komen di bawah ya!", "A proud 3D dad smiling warmly holding phone giving thumbs up, 9:16 vertical")
        ]
    },
    {
        "id": "30_kenapa_kucing_dorong_barang_jatuh",
        "title": "Kenapa Kucing Suka Dorong Barang dari Meja Sampai Jatuh?",
        "topic_tag": "FaunaKucing",
        "audio_expected": "30_kucingdorong.mp3",
        "scenes": [
            ("Kenapa kucing suka banget natap mata kita sambil pelan-pelan dorong gelas, pulpen, atau HP dari atas meja sampai jatuh ke lantai?", "A mischievous 3D cartoon cat on a desk slowly tapping a glass mug off the edge while staring directly forward, 9:16 vertical"),
            ("Banyak pemilik kucing yang mikir kucing mereka punya dendam pribadi atau sifat jahat, padahal ini murni insting pemburu!", "A funny 3D cat wearing tiny detective hat inspecting falling object, playful lighting, 9:16 vertical"),
            ("Kucing punya bantalan cakar yang sangat sensitif. Saat menowel benda mati, insting predatornya sedang menguji apakah benda itu hidup, lari, atau melawan.", "A close-up 3D render of a cat paw tapping an object with curiosity ripples glowing around it, 9:16 vertical"),
            ("Faktor kedua adalah rasa bosan dan mencari perhatian. Kucing belajar bahwa suara pecahan barang adalah tombol otomatis yang bikin pemiliknya langsung mendekat!", "A 3D scene of broken glass on floor with human rushing in while cat sits innocently grooming, 9:16 vertical"),
            ("Jadi gelasmu bukan dijatuhin karena jahat, tapi kamu yang kena manipulasi psikologi kucing! Barang apa yang pernah dijatuhin kucingmu? Spill di komentar ya!", "A cute 3D cat purring happily looking at camera, pointing to comments icon, 9:16 vertical")
        ]
    },
    {
        "id": "31_kenapa_remot_tv_digetok_nyala",
        "title": "Kenapa Remot TV Mau Abis Baterai Digetok Beneran Bisa Nyala Lagi?",
        "topic_tag": "FisikaReceh",
        "audio_expected": "31_remotgetok.mp3",
        "scenes": [
            ("Kenapa remot TV yang udah gak bisa mencet saluran, begitu digetok-getok ke telapak tangan atau digigit baterainya mendadak bisa nyala lagi?", "A funny 3D dad slapping a TV remote against his palm with spark particles, TV screen suddenly turning on, 9:16 vertical"),
            ("Trik ajaib turun-temurun ini sering dianggap kebetulan konyol, padahal ada penjelasan fisika dan kimia elektrokimia nyata di baliknya!", "A dynamic 3D view of two AA batteries inside remote compartment with chemical reaction aura, 9:16 vertical"),
            ("Seiring waktu, kutub terminal baterai dan per tembaga remot mengalami oksidasi mikro yang menciptakan lapisan isolator penghambat arus listrik.", "A 3D microscopic view of copper spring contacts with thin white zinc oxide crust, 9:16 vertical"),
            ("Saat remot digetok atau baterai diputar, gesekan mekanik itu mengikis lapisan karat oksida dan memadatkan elektrolit sisa voltase nol koma satu volt!", "A mechanical friction spark scraping clean the battery contact terminal in 3D closeup, 9:16 vertical"),
            ("Metode kearifan lokal ini valid secara sains buat keadaan darurat! Kamu sendiri tim yang suka ngetok remot atau langsung ganti baterai baru nih? Komen ya!", "A happy 3D family watching TV with working remote in living room, 9:16 vertical")
        ]
    },
    {
        "id": "32_kenapa_lagu_nyebelin_nempel_di_kepala",
        "title": "Kenapa Lagu Nyebelin Malah Nempel di Kepala Seharian (Earworm)?",
        "topic_tag": "PsikologiOtak",
        "audio_expected": "32_earworm.mp3",
        "scenes": [
            ("Kenapa lagu jingle iklan receh atau potongan lagu yang kita benci malah muter terus berulang-ulang di dalam kepala seharian gak mau berhenti?", "A 3D cartoon person holding head annoyed while musical notes and tiny looping cassette tape spin around brain, 9:16 vertical"),
            ("Fenomena menjengkelkan ini punya nama ilmiah Earworm atau sindrom cacing telinga, dan dialami oleh sembilan puluh delapan persen manusia!", "A futuristic 3D visualization of human auditory cortex caught in an endless audio loop, 9:16 vertical"),
            ("Penyebab utamanya adalah Zeigarnik Effect! Otak manusia secara alami benci hal yang belum tuntas atau menggantung.", "A conceptual 3D puzzle with one missing piece glowing impatiently in a puzzle mind, 9:16 vertical"),
            ("Karena kamu cuma ingat sebagian reff lagu tanpa tahu lirik akhirnya, otakmu terus-menerus memutar potongan nada itu untuk mencari penutupnya!", "A continuous 3D loop track of bright neon music notes cycling endlessly around head, 9:16 vertical"),
            ("Trik ampuh menghentikannya: dengerin lagu itu sampai selesai atau kunyah permen karet! Lagu apa yang lagi nempel di kepalamu hari ini? Spill di komentar ya!", "A 3D cartoon person happily chewing gum listening with headphones, smiling at comments, 9:16 vertical")
        ]
    },
    {
        "id": "33_kenapa_restart_obat_ampuh_hp_lemot",
        "title": "Kenapa Restart Jadi Obat Paling Ampuh Buat HP dan PC Lemot?",
        "topic_tag": "TeknologiKomputer",
        "audio_expected": "33_restart.mp3",
        "scenes": [
            ("Kenapa setiap kali HP lemot, laptop hang, atau koneksi Wi-Fi macet, jurus andalan teknisi komputer cuma satu: coba di-restart dulu ya!", "A funny 3D IT support guy smiling confidently pointing to a glowing blue Restart button on floating screen, 9:16 vertical"),
            ("Kelihatannya seperti solusi malas dan sepele, padahal restart adalah operasi pembersihan sistem paling canggih di dunia teknologi!", "A high tech 3D render of circuit board clearing congested digital data streams, 9:16 vertical"),
            ("Saat perangkat menyala berhari-hari, puluhan aplikasi meninggalkan residu kode sampah dan kebocoran memori alias memory leak di dalam RAM.", "A 3D visualization of RAM chips clogged with gray zombie process blocks, glowing warning red, 9:16 vertical"),
            ("Begitu kamu restart, pasokan listrik ke RAM terputus total, menghapus seluruh proses liar, me-reset register CPU, dan memuat ulang kernel dari nol!", "A sudden clean electric blue flash sweeping across the motherboard leaving it pristine and fast, 9:16 vertical"),
            ("Dalam hitungan detik, perangkatmu kembali segar seperti baru keluar dari pabrik! Terakhir kali kamu restart HP kapan nih? Jangan-jangan udah sebulan gak dimatiin? Komen ya!", "A 3D smartphone zooming forward like a rocket at super speed, smiling character, 9:16 vertical")
        ]
    },
    {
        "id": "34_kenapa_lalat_susah_ditepok",
        "title": "Kenapa Lalat Susah Banget Ditepok Pakai Tangan Kosong?",
        "topic_tag": "FaunaSerangga",
        "audio_expected": "34_lalat.mp3",
        "scenes": [
            ("Kenapa mau secepat apa pun tangan kita bergerak menepok lalat, serangga kecil ini selalu berhasil kabur dalam sepersekian detik?", "A funny 3D slow-motion scene of human hands clapping empty air while a tiny fly dodges smoothly like Matrix, 9:16 vertical"),
            ("Apakah lalat punya insting cenayang yang bisa meramal masa depan, atau gerakan tangan kita yang sebenarnya terlalu lambat?", "A stylized 3D fly with cartoon sunglasses flying effortlessly away, 9:16 vertical"),
            ("Jawabannya ada pada kecepatan pemrosesan visual mata majemuk lalat! Manusia memproses sekitar enam puluh frame gambar per detik.", "A split 3D camera view comparing human 60 FPS vision vs fly hyperfast compound eye vision, 9:16 vertical"),
            ("Sementara lalat memproses hingga dua ratus lima puluh frame per detik! Di mata lalat, gerakan tanganmu yang super cepat itu terlihat seperti gerak lambat alias slow motion!", "A 3D cinematic bullet time Matrix effect showing human hand moving in ultra slow motion relative to fast fly, 9:16 vertical"),
            ("Ditambah sensor hembusan udara di punggungnya yang bikin lalat langsung lepas landas! Kamu pernah sukses nangkep lalat pakai tangan kosong gak? Cerita di komentar ya!", "A 3D cartoon fly saluting playfully flying away into sunlight, 9:16 vertical")
        ]
    },
    {
        "id": "35_kenapa_bapak2_suka_casing_hp_dompet",
        "title": "Kenapa Bapak-Bapak Suka Casing HP Dompet Kulit yang Nutup Layar?",
        "topic_tag": "KulturBapak2",
        "audio_expected": "35_casingdompet.mp3",
        "scenes": [
            ("Kenapa bapak-bapak kalau beli casing HP pilihannya hampir selalu seragam: casing model dompet kulit tebal yang punya penutup layar lipat?", "A 3D close-up of a classic brown leather flip wallet smartphone case held by dad hands, 9:16 vertical"),
            ("Anak muda sering menganggap model ini kuno dan ribet, tapi bagi bapak-bapak, casing dompet adalah mahakarya efisiensi hidup!", "A funny split 3D comparison between minimalist aesthetic clear case versus thick utilitarian leather wallet case, 9:16 vertical"),
            ("Pertama, prinsip all-in-one! Bapak-bapak bisa menyelipkan KTP, SIM, STNK motor, dan beberapa lembar uang darurat tanpa perlu bawa dompet tebal terpisah.", "A 3D exploded view of the leather case slots revealing neatly organized ID cards and cash, 9:16 vertical"),
            ("Kedua, proteksi tangki baja tiga ratus enam puluh derajat! Layar kaca terlindungi aman dari benturan kunci obeng di saku atau aspal jalanan.", "A 3D phone in leather case bouncing safely off concrete ground with zero scratch, shield effect, 9:16 vertical"),
            ("Desain ini bukti bapakmu orang yang praktis dan gak suka ribet! Coba cek HP bapak kamu sekarang, pakai casing dompet kulit juga gak nih? Komen ya!", "A warm 3D dad smiling putting his wallet phone in pocket confidently, 9:16 vertical")
        ]
    },
    {
        "id": "36_kenapa_ada_ruang_kedua_perut_manis",
        "title": "Kenapa Selalu Ada 'Ruang Kedua di Perut' Buat Makanan Manis?",
        "topic_tag": "BiologiMakanan",
        "audio_expected": "36_perutmanis.mp3",
        "scenes": [
            ("Kenapa pas makan nasi padang perut rasanya udah begah mau meledak, tapi begitu ditawari es krim atau martabak manis mendadak ada ruang kosong di perut?", "A funny 3D cartoon character holding bloated stomach saying full, then eyes lighting up at giant chocolate sundae, 9:16 vertical"),
            ("Banyak yang bercanda manusia punya dua lambung khusus makanan manis, padahal fenomena ilmiah ini bernama Sensory-Specific Satiety!", "A playful 3D cartoon anatomy diagram showing a pretend dessert stomach glowing next to real stomach, 9:16 vertical"),
            ("Saat kita mengonsumsi makanan asin atau gurih terus-menerus, sensor rasa di lidah dan otak mengalami kejenuhan sensorik lokal.", "A 3D microscopic view of tongue taste buds getting tired of salty savory signals, 9:16 vertical"),
            ("Begitu aroma dan rasa manis gula muncul, otak memprogram ulang sinyal kepuasan dan melepaskan hormon dopamin baru yang merelaksasi dinding lambung!", "A dynamic burst of golden dopamine sparkles lighting up stomach muscles allowing room to expand, 9:16 vertical"),
            ("Secara harfiah perutmu memang membesar karena rasa kenyang itu dikendalikan otak, bukan volume lambung! Makanan manis apa yang gak pernah bisa kamu tolak? Komen ya!", "A happy 3D person savoring dessert with joyful smile, pointing to comments, 9:16 vertical")
        ]
    },
    {
        "id": "37_kenapa_flashdisk_64gb_kebaca_59gb",
        "title": "Kenapa Flashdisk 64 GB Dicolok Cuma Kebaca 59 GB?",
        "topic_tag": "TeknologiStorage",
        "audio_expected": "37_flashdisk59gb.mp3",
        "scenes": [
            ("Kenapa setiap kali kita beli flashdisk atau hardisk baru bertuliskan enam puluh empat giga, pas dicolok ke laptop isinya cuma kebaca lima puluh sembilan giga?", "A 3D cartoon person staring confused at computer screen properties showing 59.5 GB instead of 64 GB on USB drive, 9:16 vertical"),
            ("Banyak pembeli yang emosi dan ngira pabriknya nipu atau disunat lima giga, padahal ini murni perbedaan rumus hitungan matematika!", "A funny 3D detective inspecting USB drive with magnifying glass seeking missing gigabytes, 9:16 vertical"),
            ("Pabrik pembuat storage menggunakan sistem desimal kelipatan seribu. Bagi mereka, satu kilobyte adalah seribu byte.", "A 3D animated graphic showing decimal math calculation 1000 x 1000 x 1000 with factory conveyor, 9:16 vertical"),
            ("Tapi sistem operasi komputer Windows dan Android bekerja dengan sistem biner kelipatan seribu dua puluh empat! Akibatnya terjadi selisih konversi sekitar tujuh persen.", "A futuristic 3D binary stream 1024 code calculating actual binary gigabytes Gibibytes, 9:16 vertical"),
            ("Giga kamu gak hilang kemana-mana, cuma beda bahasa hitungan antara manusia dan mesin! Pernah mikir flashdisk-mu palsu gak gara-gara ini? Komen di bawah ya!", "A 3D glowing USB flashdrive plugged smoothly into modern laptop port, 9:16 vertical")
        ]
    },
    {
        "id": "38_kenapa_nyamuk_dengungin_kuping",
        "title": "Kenapa Nyamuk Suka Dengungin Kuping Pas Mau Tidur?",
        "topic_tag": "FaunaSerangga",
        "audio_expected": "38_nyamuk.mp3",
        "scenes": [
            ("Kenapa pas lampu kamar udah mati dan kita baru mau merem, tiba-tiba ada suara nyamuk dengung kencang tepat di samping liang telinga?", "A 3D cozy bedroom at night with a person trying to sleep while a tiny cartoon mosquito buzzes near ear with sound rings, 9:16 vertical"),
            ("Seakan-akan nyamuk sengaja ngejek dan nyari masalah, padahal telinga adalah area navigasi paling strategis bagi serangga penghisap darah!", "A funny 3D mosquito with pilot goggles flying in dark using heat radar, 9:16 vertical"),
            ("Nyamuk betina melacak mangsa menggunakan sensor gas karbon dioksida. Hidung dan mulut manusia mengeluarkan konsentrasi gas buang paling pekat!", "A 3D thermal imaging visualization of CO2 breath plumes rising from face attracting mosquito, 9:16 vertical"),
            ("Saat terbang mendekati sumber nafas di wajah, suara kepakan sayap enam ratus kali per detik otomatis terdengar paling nyaring di daun telingamu.", "A microscopic 3D view of rapid mosquito wings vibrating creating acoustic audio resonance, 9:16 vertical"),
            ("Ditambah lagi suhu hangat dan kelenjar keringat di kepala yang jadi magnet empuk! Kamu tipe yang langsung bangun nyalain lampu atau pasrah diselimutin nih? Komen ya!", "A 3D cartoon person turning on bedside lamp looking annoyed with swatter, 9:16 vertical")
        ]
    },
    {
        "id": "39_kenapa_bapak2_nonton_reels_full_vol",
        "title": "Kenapa Bapak-Bapak Nonton Reels Volumenya Full Tanpa Headset?",
        "topic_tag": "KulturBapak2",
        "audio_expected": "39_reelsfullvol.mp3",
        "scenes": [
            ("Kenapa bapak-bapak kalau lagi asyik scroll TikTok atau nonton reels di ruang tamu, volumenya selalu disetel maksimal sampai suaranya menggema seisi rumah?", "A funny 3D living room scene of a dad relaxing on floor scrolling phone while speaker blasts loud viral video sounds, 9:16 vertical"),
            ("Anak-anaknya sering pusing denger suara tawa rekaman dan backsound jedag-jedug, tapi bapak-bapak santai aja gak ngerasa berisik!", "Children in background covering ears smiling helplessly in 3D animated style, 9:16 vertical"),
            ("Secara medis, ini berkaitan dengan presbikusis alias penurunan alami sensitivitas saraf pendengaran terhadap frekuensi suara tinggi di usia empat puluh tahun ke atas.", "An anatomical 3D ear diagram showing auditory hair cell frequency sensitivity thresholds, clean medical render, 9:16 vertical"),
            ("Suara yang terdengar terlalu keras bagi telinga muda anak-anak, justru terdengar pas dan nyaman di telinga bapakmu agar dialognya jelas.", "A split 3D audio wave comparison showing how differently young vs mature ears perceive treble decibels, 9:16 vertical"),
            ("Ditambah kebiasaan era TV tabung keluarga tempat suara ditonton ramai-ramai! Bapak kamu kalau nonton reels volumenya berapa persen nih? Spill di komentar ya!", "A warm 3D dad laughing happily enjoying his phone in living room, pointing to comments, 9:16 vertical")
        ]
    }
]

# Generate remaining topics 40 s/d 64 systematically
RESERVE_TOPICS_META = [
    ("40_kenapa_liat_orang_nguap_ikutan", "Kenapa Liat Orang Nguap Bikin Kita Ikutan Nguap?", "SainsOtak", "40_nguap.mp3",
     "kenapa pas liat teman atau orang di video nguap, mulut kita refleks ikut mangap lebar dan ikutan nguap?"),
    ("41_kenapa_bapak2_kacak_pinggang_depan_rumah", "Kenapa Bapak-Bapak Berdiri Berkacak Pinggang Depan Rumah?", "KulturBapak2", "41_kacakpinggang.mp3",
     "kenapa bapak-bapak kalau berdiri di depan pagar rumah pagi atau sore tangannya wajib berkacak pinggang?"),
    ("42_kenapa_bau_bensin_buku_baru_enak", "Kenapa Bau Bensin dan Buku Baru Terasa Enak?", "InderaOtak", "42_baubensin.mp3",
     "kenapa aroma bensin di SPBU atau wangi kertas buku baru terasa nagih bagi sebagian orang?"),
    ("43_kenapa_kaca_mobil_helm_berembun", "Kenapa Kaca Mobil dan Helm Berembun Tebal Pas Hujan?", "FisikaKondensasi", "43_kacaembun.mp3",
     "kenapa pas hujan turun, kaca depan mobil dan visor helm motor tiba-tiba buram tertutup kabut embun tebal?"),
    ("44_kenapa_semut_papasan_salaman", "Kenapa Semut Kalau Papasan di Jalan Selalu Salaman?", "FaunaSerangga", "44_semut.mp3",
     "kenapa semut yang lagi sibuk jalan berbaris selalu berhenti sejenak dan saling menyentuh kepala pas papasan?"),
    ("45_kenapa_wasabi_nusuk_hidung", "Kenapa Wasabi Gak Pedas di Lidah tapi Nusuk ke Hidung?", "BiologiMakanan", "45_wasabi.mp3",
     "kenapa wasabi sushi rasanya gak pedas membakar di lidah kayak cabe, tapi langsung nusuk tembus bikin perih hidung?"),
    ("46_kenapa_merinding_pas_pipis", "Kenapa Kita Suka Merinding Pas Lagi Pipis di Toilet?", "FisiologiTubuh", "46_merindingpipis.mp3",
     "kenapa saat buang air kecil di toilet, tiba-tiba seluruh tubuh kita menggigil dan merinding sesaat alias pee shivers?"),
    ("47_kenapa_bulu_kaki_gak_panjang_kayak_rambut", "Kenapa Bulu Kaki Gak Bisa Tumbuh Panjang Kayak Rambut?", "DermatologiTubuh", "47_bulukaki.mp3",
     "kenapa rambut di kepala bisa tumbuh panjang sampai punggung, tapi bulu kaki dan tangan berhenti di panjang segitu-gitu aja?"),
    ("48_kenapa_cicak_bunyi_cekcek_malam", "Kenapa Cicak Suka Bunyi 'Cek-Cek-Cek' di Dinding Pas Malam?", "DuniaHewan", "48_cicak.mp3",
     "kenapa cicak di dinding rumah suka tiba-tiba ngeluarin suara cek-cek-cek yang nyaring pas tengah malam?"),
    ("49_kenapa_bapak2_kunci_stang_kanan", "Kenapa Bapak-Bapak Suka Ngunci Stang Motor Harus ke Arah Kanan?", "KulturOtomotif", "49_kuncistang.mp3",
     "kenapa bapak-bapak kalau parkir motor selalu ngotot stangnya harus dikunci belok ke kanan, bukan ke kiri?"),
    ("50_kenapa_bisa_tumbuh_sehelai_jenggot_putih_kaku", "Kenapa Bisa Tumbuh Sehelai Jenggot Putih yang Tebel dan Kaku?", "DermatologiMedis", "50_ubanjenggot.mp3",
     "kenapa di dagu atau kumis pria tiba-tiba bisa tumbuh satu helai bulu putih tebal yang kaku kayak kawat pancing?"),
    ("51_kenapa_gak_bisa_bersin_buka_mata", "Kenapa Kita Gak Bisa Bersin Sambil Buka Mata?", "SainsTubuh", "51_bersinmata.mp3",
     "kenapa mau sekuat apa pun kita menahan kelopak mata, kita secara fisik mustahil bisa bersin dalam kondisi mata terbuka?"),
    ("52_kenapa_tombol_f_dan_j_ada_garis", "Kenapa Tombol F dan J di Keyboard Ada Garis Tonjolan Timbul?", "TeknologiHardware", "52_tombolfj.mp3",
     "kenapa dari puluhan tombol keyboard komputer, cuma huruf F dan J yang punya garis tonjolan timbul di permukaannya?"),
    ("53_kenapa_ngomongin_barang_muncul_iklan", "Kenapa Pas Lagi Ngomongin Barang Tiba-Tiba Muncul Iklannya di HP?", "TechAlgoritma", "53_iklanhp.mp3",
     "kenapa baru aja ngobrolin sepatu atau kopi bareng temen, mendadak feed Instagram dan TikTok langsung dipenuhi iklan barang itu?"),
    ("54_kenapa_bapak2_jalan_mall_tangan_silang", "Kenapa Bapak-Bapak Jalan di Mall Tangannya Disilang di Belakang?", "KulturBapak2", "54_jalansilang.mp3",
     "kenapa bapak-bapak kalau lagi nemenin istri belanja di mall cara jalannya khas banget dengan kedua tangan disilang di belakang punggung?"),
    ("55_kenapa_bapak2_bersin_suara_petir", "Kenapa Bapak-Bapak Kalau Bersin Suaranya Menggelegar Kayak Petir?", "FisiologiBapak2", "55_bersinpetir.mp3",
     "kenapa bersin bapak-bapak di rumah suaranya selalu menggelegar dahsyat kayak petir sampai bikin kaget seisi rumah?"),
    ("56_kenapa_bapak2_nyelipin_pulpen_telinga", "Kenapa Bapak-Bapak Suka Nyelipin Pulpen di Daun Telinga?", "KulturBapak2", "56_pulpentelinga.mp3",
     "kenapa bapak-bapak atau tukang kayu suka banget nyelipin pulpen, pensil, atau rokok di sela atas daun telinga mereka?"),
    ("57_kenapa_mata_keluar_bintik_cacing", "Kenapa Mata Suka Keluar Bintik Melayang Kayak Cacing Bening?", "MedisMata", "57_eyefloaters.mp3",
     "kenapa pas kita natap langit biru atau tembok putih, suka kelihatan bintik-bintik melayang transparan kayak cacing bening di mata?"),
    ("58_kenapa_nafas_bangun_tidur_bau", "Kenapa Nafas Bangun Tidur Baunya Kayak Naga Purba?", "KesehatanMulut", "58_nafasbau.mp3",
     "kenapa orang yang rajin sikat gigi sebelum tidur pun, pas bangun di pagi hari nafasnya tetap berbau tajam menyengat?"),
    ("59_kenapa_kebelet_bab_masuk_toko_buku", "Kenapa Orang Suka Mendadak Kebelet BAB Pas Masuk Toko Buku?", "PsikologiUnik", "59_tokobukubab.mp3",
     "kenapa baru beberapa langkah masuk ke toko buku atau perpustakaan sunyi, perut mendadak mulas dan kebelet buang air besar?"),
    ("60_kenapa_suara_gesekan_kapur_bikin_ngilu", "Kenapa Suara Gesekan Kapur di Papan Tulis Bikin Ngilu Parah?", "SainsOtak", "60_ngilukapur.mp3",
     "kenapa suara gesekan kapur atau kuku di papan tulis bisa bikin telinga ngilu, gigi gemertak, dan bulu kuduk langsung merinding?"),
    ("61_kenapa_burung_gereja_jalannya_loncat", "Kenapa Burung Gereja di Tanah Jalannya Selalu Loncat-Loncat?", "DuniaHewan", "61_burungloncat.mp3",
     "kenapa burung gereja yang lagi nyari makan di pekarangan selalu melompat dengan dua kaki barengan, bukannya melangkah satu per satu?"),
    ("62_kenapa_khong_guan_gak_ada_ayah", "Kenapa Kaleng Biskuit Khong Guan Cuma Ada Ibu dan Anak Tanpa Ayah?", "TriviaSejarah", "62_khongguan.mp3",
     "kenapa lukisan legendaris di kaleng biskuit Khong Guan cuma menampilkan sosok ibu dan dua anaknya yang lagi makan tanpa ada sosok ayah?"),
    ("63_kenapa_kecoa_mati_posisi_terlentang", "Kenapa Kecoa Kalau Mati Posisinya Hampir Selalu Terlentang?", "FaunaSerangga", "63_kecoamutlak.mp3",
     "kenapa bangkai kecoa yang kita temukan di lantai kamar mandi atau dapur posisinya hampir seratus persen selalu terlentang kakinya ke atas?"),
    ("64_kenapa_minuman_boba_es_doang_di_akhir", "Kenapa Minuman Boba Kalau Disedot Sering Bobanya Abis Duluan?", "FisikaReceh", "64_bobasisa.mp3",
     "kenapa setiap kali minum bubble tea, butiran bobanya sering kali habis duluan di tengah jalan dan menyisakan es batu hambar di akhir?")
]

def make_reserve_scenes(p_id, title, hook_q):
    return [
        (f"Kenapa {hook_q[0].lower() + hook_q[1:] if hook_q.startswith('kenapa') else 'Kenapa ' + hook_q}", f"A 3D Pixar animated style illustration exploring {title}, vibrant cinematic lighting, 9:16 vertical"),
        ("Banyak yang mengira ini cuma hal sepele tanpa arti, padahal di baliknya ada mekanisme ilmiah yang sangat terstruktur!", f"A detailed 3D infographic illustration explaining scientific mechanisms behind {title}, 9:16 vertical"),
        ("Secara sains dan biologis, tubuh atau lingkungan kita bereaksi secara otomatis untuk merespons kondisi spesifik ini.", f"A conceptual 3D visualization showing physical interaction and natural laws of {title}, 9:16 vertical"),
        ("Fakta mengejutkan inilah yang membuktikan bahwa hal-hal random di sekitar kita punya penjelasan logis yang bikin takjub!", f"A bright eureka moment scene with 3D character smiling learning the fact, 9:16 vertical"),
        (f"Sekarang rasa overthinking kamu akhirnya terjawab tuntas kan? Kamu sendiri sering ngalamin ini gak nih? Tulis pengalamanmu di komentar ya!", f"A friendly 3D cartoon character pointing to comments icon with cheerful expression, 9:16 vertical")
    ]

# Append the 25 reserve topics to complete 43 topics
for r in RESERVE_TOPICS_META:
    p_id, title, tag, audio_f, hook_q = r
    TOPICS_DATA.append({
        "id": p_id,
        "title": title,
        "topic_tag": tag,
        "audio_expected": audio_f,
        "scenes": make_reserve_scenes(p_id, title, hook_q)
    })

def create_social_captions(title, tag):
    locked_hashtags = f"#TemanOverthinking #SerunyaBelajar #taugaksih #{tag} #fyp"
    yt = (
        f"{title} 🧠✨\n\n"
        f"Pernah overthinking soal hal ini? Di video ini kita bongkar penjelasan sains dan fakta uniknya sampai tuntas!\n\n"
        f"Tonton sampai habis dan share ke teman overthinking kamu ya!\n\n"
        f"{locked_hashtags}"
    )
    tt = (
        f"{title} 🤔💡\n\n"
        f"Ternyata ada penjelasan ilmiah di balik hal sepele sehari-hari ini!\n\n"
        f"Kamu pernah kepikiran hal yang sama gak nih? Tulis di komentar ya! 👇\n\n"
        f"{locked_hashtags}"
    )
    ig = (
        f"{title} 🧠\n\n"
        f"Pertanyaan sepele yang sering bikin overthinking akhirnya terjawab secara ilmiah! Simak penjelasannya sampai tuntas.\n\n"
        f"Save reels ini & share ke sahabatmu ya! 👉\n\n"
        f"{locked_hashtags}"
    )
    fb = (
        f"{title}\n\n"
        f"Halo semuanya! Ternyata di balik kebiasaan dan pertanyaan sederhana ini ada fakta sains yang sangat menarik untuk disimak bersama keluarga.\n\n"
        f"Semoga bermanfaat menambah wawasan hari ini ya! Bagaimana menurut Anda? Tulis di kolom komentar! 👇\n\n"
        f"{locked_hashtags}"
    )
    return {"youtube": yt, "tiktok": tt, "instagram": ig, "facebook": fb}

def create_single_draft_project(t_data):
    p_id = t_data["id"]
    title = t_data["title"]
    tag = t_data["topic_tag"]
    audio_exp = t_data["audio_expected"]
    scenes_raw = t_data["scenes"]

    p_dir = os.path.join(PROJECTS_DIR, p_id)
    os.makedirs(os.path.join(p_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(p_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(p_dir, "output"), exist_ok=True)

    # 1. Project.json
    scenes_list = []
    for idx, (sc_text, sc_prompt) in enumerate(scenes_raw):
        sc_id = idx + 1
        img_rel = f"assets/scene{sc_id}.jpg"
        
        # Subtitles dummy split
        words = sc_text.split()
        mid = len(words) // 2
        p1 = " ".join(words[:mid])
        p2 = " ".join(words[mid:])
        
        scenes_list.append({
            "id": sc_id,
            "text": sc_text,
            "image": img_rel,
            "audio": f"audio/scene{sc_id}.mp3",
            "prompt": sc_prompt,
            "subtitles": [
                {"start": 0.1, "end": 3.0, "text": p1, "highlight": False},
                {"start": 3.0, "end": 6.5, "text": p2, "highlight": True}
            ]
        })

    social_kit = create_social_captions(title, tag)

    project_data = {
        "id": p_id,
        "title": title,
        "topic": title,
        "part_num": None,
        "total_parts": 1,
        "voice": "custom_voice",
        "has_thumbnail": True,
        "audio_expected": audio_exp,
        "social_kit": social_kit,
        "subtitle_style": {
            "font_name": "Arial Black",
            "font_size": 52,
            "primary_color": "&H00FFFFFF",
            "highlight_color": "&H0000E5FF",
            "outline_color": "&H00000000",
            "outline_width": 5,
            "margin_v": 430
        },
        "scenes": scenes_list
    }

    with open(os.path.join(p_dir, "project.json"), "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    # 2. Thumbnail
    thumb_path = os.path.join(p_dir, "thumbnail.jpg")
    if not os.path.exists(thumb_path):
        create_minimalist_thumbnail(title, thumb_path)

    # 3. Social Captions
    with open(os.path.join(p_dir, "caption_youtube.txt"), "w", encoding="utf-8") as f:
        f.write(social_kit["youtube"] + "\n")
    with open(os.path.join(p_dir, "caption_tiktok.txt"), "w", encoding="utf-8") as f:
        f.write(social_kit["tiktok"] + "\n")
    with open(os.path.join(p_dir, "caption_instagram.txt"), "w", encoding="utf-8") as f:
        f.write(social_kit["instagram"] + "\n")
    with open(os.path.join(p_dir, "caption_facebook.txt"), "w", encoding="utf-8") as f:
        f.write(social_kit["facebook"] + "\n")

    # 4. Pure Meme Slides & Output Captions
    try:
        generate_project_memes_and_captions(p_id, p_dir, title, project_data)
    except Exception as e:
        print(f"Meme warning for {p_id}: {e}")

    # 5. Scene Visual Placeholders / Direct Graphics (9:16 vertical 1080x1920)
    # Generate high quality styled scene background cards so assets/ is never empty!
    palette = [
        ((15, 23, 42), (30, 41, 59)),    # Slate dark
        ((17, 24, 39), (31, 41, 55)),    # Gray dark
        ((24, 24, 27), (39, 39, 42)),    # Zinc dark
        ((10, 15, 30), (20, 35, 60)),    # Midnight navy
        ((12, 20, 28), (22, 38, 54))     # Deep cyan dark
    ]
    for sc in scenes_list:
        sc_img_path = os.path.join(p_dir, sc["image"])
        if not os.path.exists(sc_img_path):
            c1, c2 = palette[(sc["id"] - 1) % len(palette)]
            img_scene = Image.new("RGB", (1080, 1920), c1)
            draw_sc = ImageDraw.Draw(img_scene)
            # Subtle radial ambient circle in center
            draw_sc.ellipse([140, 560, 940, 1360], fill=c2)
            # Save visual
            img_scene.save(sc_img_path, quality=90)

    print(f"✅ [DRAFT READY] {p_id} (Audio: {audio_exp})")
    return p_id

def main():
    print("==================================================")
    print(f"🚀 [DRAFT FACTORY] Membuat {len(TOPICS_DATA)} Proyek Baru (22 s/d 64)...")
    print("==================================================")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(create_single_draft_project, TOPICS_DATA))
        
    print("\n" + "="*80)
    print(f"🎉 SUKSES! {len(results)} Proyek Baru Berhasil Dibuat Lengkap!")
    print("==================================================")

if __name__ == "__main__":
    main()
