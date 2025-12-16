
import datetime

dates = [
    (datetime.date(2004, 8, 27), "27 ส.ค. 47", "เริ่มสัญญา", "#4CAF50", "top"),
    (datetime.date(2004, 12, 22), "22 ธ.ค. 47", "ขออนุญาต", "#9C27B0", "bottom"),
    (datetime.date(2004, 12, 24), "24 ธ.ค. 47", "ครบสัญญา", "#F44336", "top"),
    (datetime.date(2005, 4, 28), "28 เม.ย. 48", "ได้รับอนุญาต", "#9C27B0", "bottom"),
    (datetime.date(2005, 9, 29), "29 ก.ย. 48", "งานแล้วเสร็จ", "#000000", "top")
]

# Calculate positions
start_date = dates[0][0]
end_date = dates[-1][0]
total_days = (end_date - start_date).days
width = 800
height = 300
margin_x = 50
draw_width = width - 2 * margin_x
y_line = height / 2

def get_x(date_obj):
    delta = (date_obj - start_date).days
    return margin_x + (delta / total_days) * draw_width

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background-color: white;">
<style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; font-size: 14px; text-anchor: middle; }}
    .date {{ font-size: 12px; fill: #666; }}
    .label {{ font-weight: bold; font-size: 14px; }}
</style>

<!-- Main Line -->
<line x1="{margin_x}" y1="{y_line}" x2="{width - margin_x}" y2="{y_line}" stroke="black" stroke-width="4" stroke-linecap="round"/>
<polygon points="{width-margin_x-10},{y_line-5} {width-margin_x-10},{y_line+5} {width-margin_x+5},{y_line}" fill="black" />
'''

# Draw Points and Labels
for d, date_str, label_str, color, pos in dates:
    x = get_x(d)
    
    # Point
    svg_content += f'<circle cx="{x}" cy="{y_line}" r="8" fill="{color}" stroke="white" stroke-width="2"/>'
    
    # Connector and Text
    if pos == "top":
        text_y_label = y_line - 40
        text_y_date = y_line - 25
        line_y2 = y_line - 15
        svg_content += f'<line x1="{x}" y1="{y_line}" x2="{x}" y2="{line_y2}" stroke="{color}" stroke-width="1" stroke-dasharray="2,2" />'
        svg_content += f'<text x="{x}" y="{text_y_label}" class="label" fill="{color}">{label_str}</text>'
        svg_content += f'<text x="{x}" y="{text_y_date}" class="date">{date_str}</text>'
    else: # bottom
        text_y_label = y_line + 50
        text_y_date = y_line + 35
        line_y2 = y_line + 15
        svg_content += f'<line x1="{x}" y1="{y_line}" x2="{x}" y2="{line_y2}" stroke="{color}" stroke-width="1" stroke-dasharray="2,2" />'
        svg_content += f'<text x="{x}" y="{text_y_label}" class="label" fill="{color}">{label_str}</text>'
        svg_content += f'<text x="{x}" y="{text_y_date}" class="date">{date_str}</text>'

# Duration Brackets
# 1. Exempt
d_start = datetime.date(2004, 12, 25)
d_end = datetime.date(2005, 4, 28)
x1 = get_x(d_start)
x2 = get_x(d_end)
mid_x = (x1 + x2) / 2
bracket_y = y_line + 70

svg_content += f'''
<!-- Exempt Bracket -->
<path d="M{x1},{bracket_y} v10 h{x2-x1} v-10" fill="none" stroke="#666" stroke-width="1.5" />
<text x="{mid_x}" y="{bracket_y + 25}" class="date" fill="#666">งดค่าปรับ 125 วัน (รอใบอนุญาต)</text>
'''

# 2. Delay
d_start_fine = datetime.date(2005, 4, 28)
d_end_fine = datetime.date(2005, 9, 29)
x1 = get_x(d_start_fine)
x2 = get_x(d_end_fine)
mid_x = (x1 + x2) / 2
bracket_y = y_line + 70

svg_content += f'''
<!-- Fine Bracket -->
<path d="M{x1},{bracket_y} v10 h{x2-x1} v-10" fill="none" stroke="#F44336" stroke-width="1.5" stroke-dasharray="4,2"/>
<text x="{mid_x}" y="{bracket_y + 25}" class="date" fill="#F44336">ปรับล่าช้า (ช่วงทำงานหลังจากได้ใบอนุญาต)</text>
'''

svg_content += '</svg>'

with open("articles/images/ep13_timeline_gen.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("SVG Generated successfully")
