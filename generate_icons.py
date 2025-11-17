"""
Generate PWA icons for the note-taking app
Run this once to create the icons: python generate_icons.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create a simple icon with the note emoji/symbol"""
    # Create image with gradient background
    img = Image.new('RGB', (size, size), color='#6366f1')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple notepad shape
    margin = size // 8
    note_color = '#ffffff'
    
    # Draw note rectangle
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        fill=note_color,
        outline='#4f46e5',
        width=size // 40
    )
    
    # Draw lines to simulate text
    line_margin = margin * 2
    line_spacing = size // 8
    line_width = size // 30
    
    for i in range(3):
        y = line_margin + margin + (i * line_spacing)
        draw.rectangle(
            [line_margin, y, size - line_margin, y + line_width],
            fill='#6366f1'
        )
    
    # Save the image
    img.save(output_path, 'PNG')
    print(f'✅ Created {output_path}')

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Generate icons
    create_icon(192, 'static/icon-192.png')
    create_icon(512, 'static/icon-512.png')
    
    print('🎉 Icons generated successfully!')
    print('You can now use the app as a PWA!')

