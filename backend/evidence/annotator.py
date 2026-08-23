import os
import uuid
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
EVIDENCE_DIR = os.path.join(STATIC_DIR, "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

SEVERITY_COLORS = {
    "Critical": (220, 38, 38),   # Vivid Red
    "High": (234, 88, 12),       # Vivid Orange
    "Medium": (202, 138, 4),     # Amber / Yellow
    "Low": (0, 117, 255)         # Cobalt Action Blue
}

def annotate_screenshot(
    image_path: str,
    findings: List[Dict[str, Any]],
    output_filename: Optional[str] = None
) -> str:
    """
    Annotates a screenshot with high-visibility bounding boxes,
    prosecution headers, and regulatory violation tags.
    """
    if not output_filename:
        output_filename = f"annotated_{uuid.uuid4().hex[:12]}.png"
        
    output_path = os.path.join(EVIDENCE_DIR, output_filename)
    
    # If raw image doesn't exist or is synthetic, create a fallback canvas
    if not image_path or not os.path.exists(image_path):
        img = Image.new("RGB", (1280, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (1280, 70)], fill=(0, 0, 0))
        draw.text((20, 25), "HOUDINI AUTOMATED PROSECUTION AUDIT", fill=(255, 255, 255))
    else:
        try:
            img = Image.open(image_path).convert("RGBA")
        except Exception:
            img = Image.new("RGB", (1280, 800), color=(255, 255, 255))

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Draw header bar
    draw.rectangle([(0, 0), (img.width, 42)], fill=(9, 7, 7, 240))
    draw.text((16, 12), "HOUDINI EVIDENCE CAPTURE // FORENSIC DOM & VISUAL PROOF", fill=(255, 255, 255, 255))
    
    # Annotate each finding with bounding boxes and badges
    for i, f in enumerate(findings):
        bbox = f.get("bounding_box")
        severity = f.get("severity", "High")
        pattern = f.get("pattern_name", "Dark Pattern")
        color = SEVERITY_COLORS.get(severity, (220, 38, 38))
        
        if bbox and isinstance(bbox, dict):
            x = bbox.get("x", 50)
            y = bbox.get("y", 100)
            w = bbox.get("width", 200)
            h = bbox.get("height", 60)
            
            # Ensure coordinates are within image bounds
            x0 = max(4, int(x))
            y0 = max(46, int(y))
            x1 = min(img.width - 4, int(x + w))
            y1 = min(img.height - 4, int(y + h))
            
            # Draw semi-transparent highlight fill
            draw.rectangle([(x0, y0), (x1, y1)], fill=(color[0], color[1], color[2], 35))
            
            # Draw multi-line solid border
            for offset in range(3):
                draw.rectangle([(x0-offset, y0-offset), (x1+offset, y1+offset)], outline=(color[0], color[1], color[2], 255))
                
            # Draw callout pill/badge
            badge_text = f" VIOLATION #{i+1}: {pattern.upper()} [{severity.upper()}] "
            text_w = len(badge_text) * 7 + 10
            badge_y0 = max(44, y0 - 24)
            badge_y1 = badge_y0 + 22
            draw.rectangle([(x0, badge_y0), (x0 + text_w, badge_y1)], fill=(color[0], color[1], color[2], 255))
            draw.text((x0 + 4, badge_y0 + 4), badge_text, fill=(255, 255, 255, 255))
        else:
            # Fallback if no specific coordinates: draw callout banner at bottom
            y_offset = img.height - 50 - (i * 45)
            draw.rectangle([(10, y_offset), (img.width - 10, y_offset + 36)], fill=(color[0], color[1], color[2], 220))
            draw.text((20, y_offset + 10), f"FLAGGED: {pattern} [{severity}] - {f.get('plain_explanation', '')[:100]}", fill=(255, 255, 255, 255))

    # Composite overlay onto base image
    final_img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    final_img.save(output_path, "PNG")
    
    return f"/static/evidence/{output_filename}"

