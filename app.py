import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

COMPANY_ID = "1"
APP_ID = "6851a46273eb826c13033cc7"
THEME_ID = "685c13029f286f4a1da1e892"
PAGE_ID = "6a1d5c188e530da987fb7893"

DEFAULT_API_HOST = "https://api.sit.ajiojcp.com"
THEME_PATH = f"/service/platform/theme/v1.0/company/{COMPANY_ID}/application/{APP_ID}/{THEME_ID}"
SWIPE_GALLERY_SECTIONS = ["Swipe Gallery 1", "Swipe Gallery 2"]

st.set_page_config(page_title="JCP Swipe Banner Manager | PRABHU-TEST", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

def get_base_url(api_host):
    return api_host.rstrip("/") + THEME_PATH

def get_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@st.cache_data(ttl=30, show_spinner=False)
def fetch_page_data(token, api_host):
    url = f"{get_base_url(api_host)}/page?page_no=1&page_size=200"
    try:
        r = requests.get(url, headers=get_headers(token), timeout=15)
        r.raise_for_status()
        for page in r.json().get("pages", []):
            if page.get("_id") == PAGE_ID:
                return page
        st.error("PRABHU-TEST page not found in API response.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ **Connection failed** — cannot reach `{api_host}`")
        st.info("""
**The JCP API is on a private/internal network.** To use from Streamlit Cloud:

**Option 1 — ngrok tunnel (recommended):**
1. On a machine inside the company network, install ngrok: https://ngrok.com
2. Run: `ngrok http https://api.sit.ajiojcp.com --host-header=api.sit.ajiojcp.com`
3. Copy the ngrok HTTPS URL (e.g. https://abc123.ngrok-free.app)
4. Paste it in **"API Host Override"** in the sidebar (under Network Settings)

**Option 2 — Run locally:**
Run `streamlit run app.py` on any machine inside the company network.
See **ℹ️ Help** for more details.
""")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"GET failed: {e}")
        return None

def update_page_data(token, api_host, page_obj):
    url = f"{get_base_url(api_host)}/page"
    try:
        r = requests.put(url, headers=get_headers(token), json={"pages": [page_obj]}, timeout=20)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"PUT failed: {e}")
        return False

def get_swipe_sections(page_obj):
    return {s.get("label",""): s for s in page_obj.get("sections",[]) if s.get("label","") in SWIPE_GALLERY_SECTIONS}

def get_tiles(section):
    return section.get("blocks", [])

def create_new_block(image_url, alt_text, redirect_url, show_block=True):
    return {
        "type": "gallery_tile", "name": "Gallery Tile",
        "props": {
            "showBlock": {"type": "checkbox", "value": show_block},
            "enableAdspot": {"type": "checkbox", "value": False},
            "adspotId": {"type": "text", "value": ""},
            "enableOsmos": {"type": "checkbox", "value": False},
            "osmosAdspotId": {"type": "text", "value": ""},
            "media_type": {"type": "radio", "value": "image"},
            "image": {"type": "image_picker_hotspot", "value": {"image": image_url, "hotspots": [], "imageWidth": 480, "imageHeight": 720}},
            "altText": {"type": "text", "value": alt_text},
            "redirectImageURL": {"type": "text", "value": ""},
            "video": {"type": "file", "value": ""},
            "autoPlay": {"type": "checkbox", "value": False},
            "calltoaction": {"type": "checkbox", "value": False},
            "buttonText": {"type": "text", "value": ""},
            "redirectURL": {"type": "text", "value": redirect_url},
            "darkModeButton": {"type": "checkbox", "value": False},
            "enableAdsPlp": {"type": "radio", "value": "false"},
        },
    }

def tile_to_row(idx, block):
    props = block.get("props", {})
    image_val = props.get("image", {}).get("value", {})
    return {
        "No.": idx+1,
        "Visible": props.get("showBlock",{}).get("value", True),
        "Alt Text": props.get("altText",{}).get("value",""),
        "Image URL": image_val.get("image","") if isinstance(image_val,dict) else str(image_val),
        "Redirect URL": props.get("redirectURL",{}).get("value",""),
        "Media Type": props.get("media_type",{}).get("value","image"),
    }

st.sidebar.markdown("## 🎯 JCP Swipe Banner Manager")
st.sidebar.markdown("**Page:** PRABHU-TEST")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["📋 Manage Tiles","➕ Add / Edit Tile","📊 Summary & Export","ℹ️ Help"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 API Authentication")
token_input = st.sidebar.text_input("Bearer Token", type="password", placeholder="Paste your JCP token (oa-...)")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Network Settings")
api_host_input = st.sidebar.text_input("API Host Override", value=DEFAULT_API_HOST, placeholder="https://api.sit.ajiojcp.com",
    help="Change to your ngrok URL when running on Streamlit Cloud")
st.sidebar.caption("⚠️ Default API is on a private network. Use an ngrok tunnel when accessing from Streamlit Cloud.")
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.markdown("""<div style="background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);border-radius:12px;padding:24px 32px;margin-bottom:24px;color:white">
  <h1 style="margin:0;font-size:2rem">🎯 Swipe Banner Manager</h1>
  <p style="margin:4px 0 0;opacity:.8">PRABHU-TEST · Jio Commerce Platform · Swipe Gallery Component</p>
</div>""", unsafe_allow_html=True)

if api_host_input == DEFAULT_API_HOST:
    st.warning("⚠️ **Private network API** — `api.sit.ajiojcp.com` is only reachable from inside the company network. "
               "If you get a connection error, set up an ngrok tunnel and enter the URL in **Network Settings**. See **ℹ️ Help** for details.", icon="🔒")

if not token_input:
    st.info("👈 Enter your JCP Bearer Token in the sidebar to get started.")
    st.markdown("""### How to get your token:
1. Open **JCP Platform** (platform.sit.ajiojcp.com) in another tab
2. Open DevTools (F12) → Console
3. Run: `sessionStorage.getItem('oauth_token')`
4. Copy the value (starts with `oa-`) and paste it in the sidebar""")
    st.stop()

page_data = fetch_page_data(token_input, api_host_input)
if page_data is None:
    st.stop()

sections = get_swipe_sections(page_data)
if not sections:
    st.warning("No Swipe Gallery sections found on PRABHU-TEST.")
    st.stop()

if nav == "📋 Manage Tiles":
    st.subheader("📋 Manage Tiles")
    selected_section_name = st.selectbox("Select Section", list(sections.keys()))
    section = sections[selected_section_name]
    tiles = get_tiles(section)
    st.markdown(f"**{len(tiles)} tile(s)** in *{selected_section_name}*")
    if tiles:
        st.dataframe(pd.DataFrame([tile_to_row(i,b) for i,b in enumerate(tiles)]), use_container_width=True, hide_index=True)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✏️ Edit Tile")
            edit_idx = st.number_input("Tile # to edit", min_value=1, max_value=len(tiles), value=1, step=1, key="edit_idx") - 1
            ep = tiles[edit_idx].get("props",{})
            img_val = ep.get("image",{}).get("value",{})
            new_image_url = st.text_input("Image URL", value=img_val.get("image","") if isinstance(img_val,dict) else "", key="edit_img")
            new_alt = st.text_input("Alt Text", value=ep.get("altText",{}).get("value",""), key="edit_alt")
            new_redirect = st.text_input("Redirect URL", value=ep.get("redirectURL",{}).get("value",""), key="edit_redirect")
            new_visible = st.checkbox("Visible", value=ep.get("showBlock",{}).get("value",True), key="edit_visible")
            if st.button("💾 Save Changes", key="save_edit", use_container_width=True):
                if isinstance(tiles[edit_idx]["props"]["image"]["value"], dict):
                    tiles[edit_idx]["props"]["image"]["value"]["image"] = new_image_url
                else:
                    tiles[edit_idx]["props"]["image"]["value"] = {"image":new_image_url,"hotspots":[],"imageWidth":480,"imageHeight":720}
                tiles[edit_idx]["props"]["altText"]["value"] = new_alt
                tiles[edit_idx]["props"]["redirectURL"]["value"] = new_redirect
                tiles[edit_idx]["props"]["showBlock"]["value"] = new_visible
                section["blocks"] = tiles
                if update_page_data(token_input, api_host_input, page_data):
                    st.success(f"✅ Tile {edit_idx+1} updated!")
                    st.cache_data.clear(); st.rerun()
        with col2:
            st.markdown("#### 🗑️ Delete Tile")
            del_idx = st.number_input("Tile # to delete", min_value=1, max_value=len(tiles), value=1, step=1, key="del_idx") - 1
            st.caption(f"Will delete: **{tile_to_row(del_idx, tiles[del_idx])['Alt Text'] or 'Untitled'}**")
            confirm_del = st.checkbox("I confirm deletion", key="confirm_del")
            if st.button("🗑️ Delete Tile", key="do_delete", disabled=not confirm_del, use_container_width=True):
                tiles.pop(del_idx)
                section["blocks"] = tiles
                if update_page_data(token_input, api_host_input, page_data):
                    st.success("✅ Tile deleted!"); st.cache_data.clear(); st.rerun()
        st.markdown("---")
        st.markdown("#### 🔀 Reorder Tiles")
        default_order = ", ".join([str(i+1) for i in range(len(tiles))])
        new_order_str = st.text_input(f"New order (e.g. {default_order})", value=default_order, key="reorder")
        if st.button("🔀 Apply Reorder", key="do_reorder", use_container_width=True):
            try:
                new_order = [int(x.strip())-1 for x in new_order_str.split(",")]
                if sorted(new_order) != list(range(len(tiles))):
                    st.error("Include each tile number exactly once.")
                else:
                    section["blocks"] = [tiles[i] for i in new_order]
                    if update_page_data(token_input, api_host_input, page_data):
                        st.success("✅ Reordered!"); st.cache_data.clear(); st.rerun()
            except ValueError:
                st.error("Comma-separated numbers only.")
    else:
        st.info("No tiles yet. Use 'Add / Edit Tile' to create one.")

elif nav == "➕ Add / Edit Tile":
    st.subheader("➕ Add New Tile")
    target_section = st.selectbox("Target Section", list(sections.keys()), key="add_section")
    section = sections[target_section]
    tiles = get_tiles(section)
    with st.form("add_tile_form"):
        col1, col2 = st.columns(2)
        with col1:
            image_url = st.text_input("Image URL *", placeholder="https://cdn.example.com/banner.jpg")
            alt_text = st.text_input("Alt Text *", placeholder="e.g. Summer Sale Banner")
        with col2:
            redirect_url = st.text_input("Redirect URL", placeholder="https://www.ajio.com/sale")
            visible = st.checkbox("Visible", value=True)
        insert_opts = [f"After tile {i+1}" for i in range(len(tiles))] + ["At the end"]
        insert_pos = st.selectbox("Insert Position", insert_opts, index=len(tiles))
        submitted = st.form_submit_button("➕ Add Tile", use_container_width=True)
    if submitted:
        if not image_url: st.error("Image URL is required.")
        elif not alt_text: st.error("Alt Text is required.")
        else:
            nb = create_new_block(image_url, alt_text, redirect_url, visible)
            if insert_pos == "At the end": tiles.append(nb)
            else: tiles.insert(int(insert_pos.split("After tile ")[1]), nb)
            section["blocks"] = tiles
            if update_page_data(token_input, api_host_input, page_data):
                st.success(f"✅ Tile added to {target_section}!"); st.cache_data.clear(); st.rerun()
    st.markdown("---")
    st.markdown("### 📤 Bulk Import from CSV")
    st.caption("Columns: image_url, alt_text, redirect_url (optional), visible (optional)")
    csv_file = st.file_uploader("Upload CSV", type=["csv"])
    bulk_section = st.selectbox("Target Section for Bulk Import", list(sections.keys()), key="bulk_section")
    if csv_file:
        df_upload = pd.read_csv(csv_file)
        st.dataframe(df_upload, use_container_width=True)
        if st.button("📤 Import All Rows", use_container_width=True):
            target_sec = sections[bulk_section]
            target_tiles = get_tiles(target_sec)
            added, errors = 0, []
            for _, row in df_upload.iterrows():
                img = str(row.get("image_url","")).strip()
                alt = str(row.get("alt_text","")).strip()
                if not img or not alt: errors.append("Skipped — missing image_url or alt_text"); continue
                target_tiles.append(create_new_block(img, alt, str(row.get("redirect_url","")).strip(), str(row.get("visible","true")).lower()!="false"))
                added += 1
            target_sec["blocks"] = target_tiles
            if update_page_data(token_input, api_host_input, page_data):
                st.success(f"✅ Imported {added} tiles!")
                if errors: st.warning("\n".join(errors))
                st.cache_data.clear(); st.rerun()

elif nav == "📊 Summary & Export":
    st.subheader("📊 Summary & Export")
    all_rows = []
    for sec_name, section in sections.items():
        for i, block in enumerate(get_tiles(section)):
            row = tile_to_row(i, block); row["Section"] = sec_name; all_rows.append(row)
    if all_rows:
        df_all = pd.DataFrame(all_rows)[["Section","No.","Visible","Alt Text","Image URL","Redirect URL","Media Type"]]
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download CSV", data=df_all.to_csv(index=False),
                file_name=f"jcp_banners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
        with col2:
            st.download_button("⬇️ Download JSON",
                data=json.dumps({s:[tile_to_row(i,b) for i,b in enumerate(get_tiles(sec))] for s,sec in sections.items()}, indent=2),
                file_name=f"jcp_banners_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json", use_container_width=True)
        st.markdown("---")
        for sec_name, section in sections.items():
            tiles = get_tiles(section)
            st.metric(sec_name, f"{len(tiles)} tiles", delta=f"{sum(1 for b in tiles if b.get('props',{}).get('showBlock',{}).get('value',True))} visible")
    else:
        st.info("No tiles found.")

elif nav == "ℹ️ Help":
    st.subheader("ℹ️ Help & Reference")
    st.markdown("### 🔒 Connecting from Streamlit Cloud (Private Network Fix)")
    st.info("The JCP API (`api.sit.ajiojcp.com`) is on a private/internal network and cannot be reached from Streamlit Community Cloud. Use one of these options:")
    st.markdown("""
#### Option 1 — ngrok Tunnel (for Streamlit Cloud)
On a machine **inside the company network**:
```bash
# Install ngrok: https://ngrok.com/download
ngrok http https://api.sit.ajiojcp.com --host-header=api.sit.ajiojcp.com
```
Copy the HTTPS URL (e.g. `https://abc123.ngrok-free.app`) → paste in **Network Settings → API Host Override**.

#### Option 2 — Run Locally
```bash
pip install streamlit requests pandas
streamlit run app.py
```
Works on any machine inside the company network — no ngrok needed.

---
### 🔑 Getting Your Bearer Token
1. Open **JCP Platform** (platform.sit.ajiojcp.com)
2. Press F12 → Console
3. Run: `sessionStorage.getItem('oauth_token')`
4. Copy the `oa-...` value → paste in **API Authentication** sidebar

---
### 📡 API Reference
| Operation | Endpoint |
|-----------|----------|
| GET page data | `GET {api_host}{THEME_PATH}/page?page_no=1&page_size=200` |
| PUT page update | `PUT {api_host}{THEME_PATH}/page` body: `{"pages":[pageObj]}` |

### 🔑 Key IDs
- Company ID: `1` · App ID: `6851a46273eb826c13033cc7`
- Theme ID: `685c13029f286f4a1da1e892` · Page ID: `6a1d5c188e530da987fb7893`
    """)
