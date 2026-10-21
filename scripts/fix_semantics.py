from pathlib import Path

# Fix index.html
p_html = Path("web/index.html")
html = p_html.read_text(encoding="utf-8")
html = html.replace("<button class=", "<button type=\"button\" class=")
p_html.write_text(html, encoding="utf-8")

# Fix app.js
p_js = Path("web/app.js")
js = p_js.read_text(encoding="utf-8")

# Station card as button
old_station = """      <div class="station-card ${st.status === 'ATTENTION_REQUIRED' ? 'active' : ''}" onclick="filterByStation('${st.id}')" tabindex="0" role="button" aria-label="Station ${st.id} status">"""
new_station = """      <button type="button" class="station-card ${st.status === 'ATTENTION_REQUIRED' ? 'active' : ''}" onclick="filterByStation('${st.id}')" aria-label="Station ${st.id} status">"""
js = js.replace(old_station, new_station)

old_station_end = """        </div>
      </div>
    `).join('');"""
new_station_end = """        </div>
      </button>
    `).join('');"""
js = js.replace(old_station_end, new_station_end)

# Incident card as button
old_card = """        <div class="incident-card ${isSelected ? 'selected' : ''}" 
             onclick="selectIncident('${itemId}')"
             onkeydown="if(event.key==='Enter'||event.key===' ') selectIncident('${itemId}')"
             tabindex="0"
             role="option"
             aria-selected="${isSelected ? 'true' : 'false'}">"""
new_card = """        <button type="button" class="incident-card ${isSelected ? 'selected' : ''}" 
             onclick="selectIncident('${itemId}')"
             role="option"
             aria-selected="${isSelected ? 'true' : 'false'}">"""
js = js.replace(old_card, new_card)

old_card_end = """          </div>
        </div>
      `;
    }).join('');"""
new_card_end = """          </div>
        </button>
      `;
    }).join('');"""
js = js.replace(old_card_end, new_card_end)

# Also action buttons
js = js.replace('<button class="btn', '<button type="button" class="btn')

p_js.write_text(js, encoding="utf-8")
print("Semantics audit fixes applied!")
