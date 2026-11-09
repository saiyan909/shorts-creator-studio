import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def draw_sparkle(draw, center, radius, fill):
    cx, cy = center
    r_in = radius * 0.22
    points = [
        (cx, cy - radius),
        (cx + r_in, cy - r_in),
        (cx + radius, cy),
        (cx + r_in, cy + r_in),
        (cx, cy + radius),
        (cx - r_in, cy + r_in),
        (cx - radius, cy),
        (cx - r_in, cy - r_in)
    ]
    draw.polygon(points, fill=fill)

def create_minimalist_thumbnail(topic: str, output_path: str, part_num: int = None, include_qmark: bool = True):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    w, h = 1080, 1920
    cx, cy = w // 2, h // 2

    # Fonts
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_black = os.path.join(base_dir, "assets", "fonts", "Poppins-Black.ttf")
    font_bold = os.path.join(base_dir, "assets", "fonts", "Poppins-Bold.ttf")

    if not os.path.exists(font_black):
        font_black = os.path.join(base_dir, "assets", "fonts", "Montserrat-Black.ttf")
        font_bold = os.path.join(base_dir, "assets", "fonts", "Montserrat-Bold.ttf")

    if not os.path.exists(font_black):
        font_black = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    img = Image.new("RGBA", (w, h), (252, 253, 255, 255))
    
    # 1. Subtle dot grid in background to kill monotony
    grid_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid_layer)
    for x in range(60, w, 70):
        for y in range(380, 1580, 70):
            gd.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(203, 213, 225, 45))
    img = Image.alpha_composite(img, grid_layer)
    
    # 2. Ambient cyan radiant glow
    aura = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    ad.ellipse([cx - 520, cy - 520, cx + 520, cy + 520], fill=(207, 250, 254, 150))
    aura = aura.filter(ImageFilter.GaussianBlur(150))
    img = Image.alpha_composite(img, aura)
    
    # 3. Giant Tilted Watermark '?'
    q_font = ImageFont.truetype(font_black, 1200)
    q_box = Image.new("RGBA", (1400, 1400), (0, 0, 0, 0))
    qbd = ImageDraw.Draw(q_box)
    bb = qbd.textbbox((0, 0), "?", font=q_font)
    qw = bb[2] - bb[0]
    qh = bb[3] - bb[1]
    qbd.text(((1400 - qw)//2 - bb[0], (1400 - qh)//2 - bb[1]), "?", font=q_font, fill=(6, 182, 212, 60))
    q_rot = q_box.rotate(-18, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(q_rot, (cx - 700 + 40, cy - 700 - 40))
    
    # 4. Floating vector sparkles & micro-elements
    spark_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spark_layer)
    draw_sparkle(sd, (cx - 380, cy - 320), 42, (0, 210, 238, 200))
    draw_sparkle(sd, (cx + 360, cy - 260), 32, (255, 184, 0, 220)) # warm gold spark
    draw_sparkle(sd, (cx + 340, cy + 320), 28, (0, 210, 238, 170))
    draw_sparkle(sd, (cx - 360, cy + 280), 24, (14, 165, 233, 160))
    sd.ellipse([cx - 410, cy - 200, cx - 398, cy - 188], fill=(0, 210, 238, 180))
    sd.ellipse([cx + 390, cy + 180, cx + 402, cy + 192], fill=(255, 184, 0, 190))
    img = Image.alpha_composite(img, spark_layer)
    
    # 5. DIE-CUT POP STICKER LAYER (Render on dedicated surface and rotate -4 deg)
    cw, ch = 1000, 800
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    
    font_main = ImageFont.truetype(font_black, 190)
    font_sub = ImageFont.truetype(font_bold, 58)
    
    bb_k = cd.textbbox((0, 0), "KENAPA", font=font_main)
    bb_q = cd.textbbox((0, 0), "?", font=font_main)
    wk = bb_k[2] - bb_k[0]
    wq = bb_q[2] - bb_q[0]
    total_w = wk + wq + 12
    
    kx = (cw - total_w) // 2
    ky = 70
    
    # Draw Die-Cut White Border / Sticker Background behind KENAPA?
    sticker_mask = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    smd = ImageDraw.Draw(sticker_mask)
    outline_r = 16
    for ox in range(-outline_r, outline_r + 1, 4):
        for oy in range(-outline_r, outline_r + 1, 4):
            if ox*ox + oy*oy <= outline_r*outline_r:
                smd.text((kx + ox, ky + oy), "KENAPA", font=font_main, fill=(255, 255, 255, 255))
                smd.text((kx + wk + 12 + ox, ky + oy), "?", font=font_main, fill=(255, 255, 255, 255))
                
    # Soft drop shadow for the vinyl sticker
    shadow_card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    scd = ImageDraw.Draw(shadow_card)
    scd.bitmap((4, 14), sticker_mask, fill=(15, 23, 42, 60))
    shadow_card = shadow_card.filter(ImageFilter.GaussianBlur(8))
    card = Image.alpha_composite(card, shadow_card)
    card = Image.alpha_composite(card, sticker_mask)
    
    # Re-draw text inside sticker
    cd = ImageDraw.Draw(card)
    cd.text((kx, ky), "KENAPA", font=font_main, fill=(15, 23, 42, 255))
    cd.text((kx + wk + 12, ky), "?", font=font_main, fill=(0, 210, 238, 255))
    
    # Helper function to auto-scale font size so text never exceeds max_w
    def fit_text_font(txt, max_w=760, start_size=52, min_size=26):
        for s in range(start_size, min_size - 1, -2):
            f = ImageFont.truetype(font_bold, s)
            bb = cd.textbbox((0, 0), txt, font=f)
            if (bb[2] - bb[0]) <= max_w:
                return f, (bb[2] - bb[0]), (bb[3] - bb[1])
        f = ImageFont.truetype(font_bold, min_size)
        bb = cd.textbbox((0, 0), txt, font=f)
        return f, (bb[2] - bb[0]), (bb[3] - bb[1])

    # Intelligent topic split into line 1 and highlighted line 2 tape
    clean_topic = topic.upper().replace("KENAPA", "").strip(" ?.\n")
    sub1 = ""
    sub2 = ""

    # Cek jika ada pemisah kontras alami seperti 'TAPI', 'PADAHAL', 'SEDANGKAN', atau koma
    for contrast_word in [" TAPI ", " PADAHAL ", " SEDANGKAN ", ", "]:
        if contrast_word in clean_topic:
            parts = clean_topic.split(contrast_word, 1)
            sub1 = parts[0].strip(" ,")
            sub2 = (contrast_word.strip() + " " + parts[1]).strip(" ,")
            break
    else:
        words = clean_topic.split()
        if len(words) <= 3:
            sub1 = words[0] if words else ""
            sub2 = " ".join(words[1:]) if len(words) > 1 else ""
        elif len(words) <= 5:
            sub1 = " ".join(words[:2])
            sub2 = " ".join(words[2:])
        else:
            split_idx = len(words) // 2
            sub1 = " ".join(words[:split_idx])
            sub2 = " ".join(words[split_idx:])

    if part_num:
        sub2 = f"{sub2} [PART {part_num}]".strip()

    # Draw Subtitle Line 1 with fitted font
    font_sub1, w1, h1 = fit_text_font(sub1, max_w=760)
    y1 = ky + (bb_k[3] - bb_k[1]) + 85
    cd.text(((cw - w1) // 2, y1), sub1, font=font_sub1, fill=(30, 41, 59, 255))
    
    # Subtitle Line 2 in Highlighter Box with fitted font
    if sub2:
        font_sub2, w2, h2 = fit_text_font(sub2, max_w=740)
        y2 = y1 + h1 + 35
        
        box_pad_x = 28
        box_pad_y = 12
        bx1 = (cw - w2) // 2 - box_pad_x
        by1 = y2 - box_pad_y
        bx2 = (cw + w2) // 2 + box_pad_x
        by2 = y2 + h2 + box_pad_y + 4
        
        # Shadow for tape
        cd.rounded_rectangle([bx1 + 4, by1 + 6, bx2 + 4, by2 + 6], radius=16, fill=(15, 23, 42, 35))
        # Vivid Neon Cyan Tape
        cd.rounded_rectangle([bx1, by1, bx2, by2], radius=16, fill=(0, 229, 255, 255))
        # Text inside tape
        cd.text(((cw - w2) // 2, y2), sub2, font=font_sub2, fill=(10, 18, 32, 255))
    
    # Rotate entire card -4 degrees for dynamic pop
    card_rot = card.rotate(-4.0, resample=Image.BICUBIC, expand=True)
    rcw, rch = card_rot.size
    img.alpha_composite(card_rot, (cx - rcw // 2, cy - rch // 2 - 20))
    
    final = img.convert("RGB")
    final.save(output_path, "JPEG", quality=95)
    return output_path

if __name__ == "__main__":
    create_minimalist_thumbnail("Es di Tumbler Nggak Mencair Seharian?", "/tmp/test_thumb.jpg")
    print("Thumbnail created at /tmp/test_thumb.jpg")
