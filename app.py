import streamlit as st
import datetime, pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import urllib.request
import base64
import json
import jieqi
import kintaiyi
import config
import cn2an
from cn2an import an2cn
from taiyidict import tengan_shiji, su_dist
from taiyimishu import taiyi_yingyang
from historytext import chistory
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from st_screen_stats import WindowQueryHelper

with st.container(height=1, border=False):
    helper_screen_stats = WindowQueryHelper()
    is_mobile = helper_screen_stats.maximum_window_size(max_width=480, key="max_width_480")["status"]
    is_tablet = helper_screen_stats.window_range_width(min_width=481, max_width=768, key="range_width_481_768")["status"]
    is_laptop = helper_screen_stats.window_range_width(min_width=769, max_width=1024, key="range_width_769_1024")["status"]
    is_large_screen = helper_screen_stats.minimum_window_size(min_width=1025, key="min_width_1025")["status"] 

if is_mobile:
    kpi_columns = 1
    number_of_kpi_per_row = 1
    chart_columns = 1
    number_of_charts_per_row = 1
    total_number_of_charts = 4
    
elif is_tablet:
    kpi_columns = 3
    number_of_kpi_per_row = 2
    chart_columns = 2 
    number_of_charts_per_row = 2
    total_number_of_charts = 4
elif is_laptop:
    kpi_columns = 4
    number_of_kpi_per_row = 2
    chart_columns = 2
    number_of_charts_per_row = 2
    total_number_of_charts = 4
else:
    kpi_columns = 6
    number_of_kpi_per_row = 6
    chart_columns = 4 
    number_of_charts_per_row = 4
    total_number_of_charts = 4

if is_mobile:
    kpi_columns = 1
    number_of_kpi_per_row = 1
    chart_columns = 1
    number_of_charts_per_row = 1
    total_number_of_charts = 4
    
elif is_tablet:
    kpi_columns = 3
    number_of_kpi_per_row = 2
    chart_columns = 2 
    number_of_charts_per_row = 2
    total_number_of_charts = 4
elif is_laptop:
    kpi_columns = 4
    number_of_kpi_per_row = 2
    chart_columns = 2
    number_of_charts_per_row = 2
    total_number_of_charts = 4
else:
    kpi_columns = 6
    number_of_kpi_per_row = 6
    chart_columns = 4 
    number_of_charts_per_row = 4
    total_number_of_charts = 4

kpi_data = [
    ("Revenue", "$120K"), ("Orders", "450"), ("Customers", "300"),
    ("Profit", "$30K"), ("Growth", "15%"), ("Retention", "80%")
]

chart_options = {
    "chart": {"type": "column"},
    "title": {"text": "Sales Overview"},
    "xAxis": {"categories": ["Jan", "Feb", "Mar", "Apr"]},
    "series": [{"name": "Sales", "data": [100, 200, 150, 300]}]
}

st.markdown('''
    Dashboard
''', unsafe_allow_html=True)


st.write("")


cols = st.columns(kpi_columns)
for i in range(len(kpi_data)):
    index = i % number_of_kpi_per_row 
    with cols[index]:
        if i < len(kpi_data):
            name, value = kpi_data[i]
            st.metric(label=name, value=value) 
    
st.write("")
cols = st.columns(chart_columns)
for i in range(total_number_of_charts):
    index = i % number_of_charts_per_row
    with cols[index]:
        hchart.streamlit_highcharts(chart_options, key=f"chart_row2_{i}")
# Define custom components
@st.cache_data
def get_file_content_as_string(base_url, path):
    url = base_url + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def format_text(d, parent_key=""):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(format_text(v, new_key + ":").splitlines())
        elif isinstance(v, list):
            items.append(f"{new_key}: {', '.join(map(str, v))}")
        else:
            items.append(f"{new_key}: {v}")
    return "\n\n".join(items)+"\n\n"

def render_svg2(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}"/>'
    st.write(html, unsafe_allow_html=True)

def render_svg(svg):
    # Directly embed raw SVG along with the interactive JavaScript
    html_content = f"""
    <div>
      <svg id="interactive-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 390" width="100%" height="500px" overflow="visible">
        {svg}
      </svg>
       <script>
        const rotations = {{}}; // To store rotation angles for each layer
    
        function rotateLayer(layer) {{
          const id = layer.id;
          if (!rotations[id]) rotations[id] = 0;
          rotations[id] += 30; // Rotate by 30 degrees each click
          const newRotation = rotations[id] % 360;
    
          // Update the group rotation
          layer.setAttribute("transform", `rotate(${{newRotation}})`);
    
          // Adjust text elements inside the group to stay horizontal
          layer.querySelectorAll("text").forEach(text => {{
            const angle = newRotation % 360; // Angle of the layer
            const x = parseFloat(text.getAttribute("x") || 0);
            const y = parseFloat(text.getAttribute("y") || 0);
    
            // Calculate the new text rotation to compensate for the group rotation
            const transform = `rotate(${{-angle}}, ${{x}}, ${{y}})`;
            text.setAttribute("transform", transform);
          }});
        }}
        document.querySelectorAll("g").forEach(group => {{
          group.addEventListener("click", () => rotateLayer(group));
        }});
      </script>
    </div>
    """
    html(html_content, height=600)

def render_svg1(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f"""
    <img src="data:image/svg+xml;base64,{b64}"/>
        <script>
      const rotations = {{}};
      function rotateLayer(layer) {{
        const id = layer.id;
        if (!rotations[id]) rotations[id] = 0;
        rotations[id] += 30; // Rotate by 30 degrees
        layer.setAttribute(
          "transform",
          `rotate(${{rotations[id]}} 0 0)`
        );
      }}
      document.querySelectorAll("g").forEach(group => {{
        group.addEventListener("click", () => rotateLayer(group));
      }});
    </script>
    """
    st.write(html, unsafe_allow_html=True)

def timeline(data, height=800):
    if isinstance(data, str):
        data = json.loads(data)
    json_text = json.dumps(data)
    source_param = 'timeline_json'
    source_block = f'var {source_param} = {json_text};'
    cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
    css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
    js_block = f'<script src="{cdn_path}/js/timeline.js"></script>'
    htmlcode = f'''
        {css_block}
        {js_block}
        <div id='timeline-embed' style="width: 95%; height: {height}px; margin: 1px;"></div>
        <script type="text/javascript">
            var additionalOptions = {{ start_at_end: false, is_embed: true, default_bg_color: {{r:14, g:17, b:23}} }};
            {source_block}
            timeline = new TL.Timeline('timeline-embed', {source_param}, additionalOptions);
        </script>
    '''
    components.html(htmlcode, height=height)

@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

