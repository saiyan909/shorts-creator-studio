import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_watermark(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Ukuran badge
    width = 360
    height = 80
    corner_radius = 22
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(base_dir, "assets", "fonts", "Poppins-Bold.ttf")
    if not os.path.exists(font_path):
        font_path = os.path.join(base_dir, "assets", "fonts", "Montserrat-Bold.ttf")
    
    # 2x supersampling for ultra sharp edges
    scale = 2
    sw, sh = width * scale, height * scale
    
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Pill background with modern dark sleek glassmorphism
    bg_color = (15, 23, 42, 225) # Slate 900
    border_color = (6, 182, 212, 180) # Cyan border
    
    draw.rounded_rectangle(
        [(scale * 2, scale * 2), (sw - scale * 2, sh - scale * 2)],
        radius=corner_radius * scale,
        fill=bg_color,
        outline=border_color,
        width=int(2.5 * scale)
    )
    
    # Cyan accent circle for "?"
    circle_size = 48 * scale
    cx = 22 * scale
    cy = (height - 48) // 2 * scale
    draw.ellipse([(cx, cy), (cx + circle_size, cy + circle_size)], fill=(6, 182, 212, 255))
    
    # Text font for '?'
    q_font = ImageFont.truetype(font_path, int(30 * scale))
    q_bbox = draw.textbbox((0, 0), "?", font=q_font)
    qw = q_bbox[2] - q_bbox[0]
    qh = q_bbox[3] - q_bbox[1]
    q_x = cx + (circle_size - qw) // 2
    q_y = cy + (circle_size - qh) // 2 - int(2 * scale)
    draw.text((q_x, q_y), "?", font=q_font, fill=(15, 23, 42, 255))
    
    # Text "Tanya Kenapa ?"
    text = "Tanya Kenapa ?"
    text_font = ImageFont.truetype(font_path, int(26 * scale))
    tx = cx + circle_size + int(14 * scale)
    t_bbox = draw.textbbox((0, 0), text, font=text_font)
    th = t_bbox[3] - t_bbox[1]
    ty = (sh - th) // 2 - int(4 * scale)
    
    draw.text((tx, ty), text, font=text_font, fill=(255, 255, 255, 250))
    
    # Downsample with Lanczos for ultra crisp anti-aliased look
    final_img = img.resize((width, height), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    print(f"Watermark generated: {output_path} ({width}x{height})")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "branding", "watermark_tanya_kenapa.png")
    generate_watermark(out)
