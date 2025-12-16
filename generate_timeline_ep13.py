
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import datetime

# Setup Thai Font (MacOS usually has 'Thonburi' or 'Ayuthaya')
# Try to find a suitable font
font_path = '/System/Library/Fonts/Thonburi.ttc' # Standard on newer MacOS
prop = font_manager.FontProperties(fname=font_path, size=12)

# If Thonburi not found, fallback (start with a basic check, but here we assume MacOS)
plt.rcParams['font.family'] = 'sans-serif' 

# Data
dates = [
    datetime.date(2004, 8, 27),   # Start: 27 ส.ค. 47
    datetime.date(2004, 12, 22),  # Request: 22 ธ.ค. 47
    datetime.date(2004, 12, 24),  # End Contract: 24 ธ.ค. 47
    datetime.date(2005, 4, 28),   # Perm Granted: 28 เม.ย. 48
    datetime.date(2005, 9, 29)    # Done: 29 ก.ย. 48
]

labels = [
    "27 ส.ค. 47\nเริ่มสัญญา",
    "22 ธ.ค. 47\nขออนุญาต",
    "24 ธ.ค. 47\nครบสัญญา",
    "28 เม.ย. 48\nได้ใบอนุญาต",
    "29 ก.ย. 48\nงานแล้วเสร็จ"
]

colors = ['green', 'purple', 'red', 'blue', 'black']
offsets = [1.0, -1.0, 1.0, -1.0, 1.0] # Alternating top/bottom labels

# Plot setup
fig, ax = plt.subplots(figsize=(12, 4))

# Draw main line
start_date = dates[0]
end_date = dates[-1]
ax.plot([start_date, end_date], [0, 0], color="black", linewidth=2, zorder=1)

# Plot points and labels
for i, (d, label, color, offset) in enumerate(zip(dates, labels, colors, offsets)):
    ax.scatter(d, 0, color=color, s=100, zorder=2, edgecolors='white', linewidth=2)
    
    # Text position
    y_pos = 0.2 if offset > 0 else -0.3
    va = 'bottom' if offset > 0 else 'top'
    
    # Draw connector line
    ax.plot([d, d], [0, y_pos * 0.8], color=color, linestyle='--', linewidth=1, alpha=0.5)
    
    # Add text with Thai font
    ax.text(d, y_pos, label, ha='center', va=va, color=color, fontproperties=prop)

# Add Duration Brackets (Manually drawn)
# Bracket 1: Exempt (25 Dec 04 - 28 Apr 05)
start_exempt = datetime.date(2004, 12, 25)
end_exempt = datetime.date(2005, 4, 28)
mid_exempt = start_exempt + (end_exempt - start_exempt) / 2

# Draw bracket line below
bracket_y = -0.5
ax.annotate('', xy=(start_exempt, bracket_y), xytext=(end_exempt, bracket_y),
            arrowprops=dict(arrowstyle='|-|', color='gray', lw=1.5))
ax.text(mid_exempt, bracket_y - 0.15, "งดค่าปรับ 125 วัน\n(รอใบอนุญาต)", 
        ha='center', va='top', color='gray', fontproperties=prop)

# Bracket 2: Fine (28 Apr 05 - 29 Sep 05) - Simplified start from exemption end
start_fine = datetime.date(2005, 4, 28)
end_fine = datetime.date(2005, 9, 29)
mid_fine = start_fine + (end_fine - start_fine) / 2

ax.annotate('', xy=(start_fine, bracket_y), xytext=(end_fine, bracket_y),
            arrowprops=dict(arrowstyle='|-|', color='red', lw=1.5, linestyle='--'))
ax.text(mid_fine, bracket_y - 0.15, "ปรับล่าช้า\n(ช่วงทำงานจริง)", 
        ha='center', va='top', color='red', fontproperties=prop)


# Clean up axis
ax.set_ylim(-1.0, 1.0)
ax.axis('off')

# Save
output_path = '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/articles/images/ep13_timeline_gen.png'
plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"Saved timeline to {output_path}")

