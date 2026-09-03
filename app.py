import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import io

st.set_page_config(page_title="コントロールテスト フィードバック", page_icon="🏃", layout="wide")

st.markdown("""
    <style>
    * { margin: 0; padding: 0; }
    
    /* 背景を臙脂色に馴染む深いダークレッド・ブラックに */
    body { background: linear-gradient(135deg, #190f13 0%, #2a161d 100%); color: #ffffff; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #190f13 0%, #2a161d 100%); }
    [data-testid="stHeader"] { background-color: transparent; }
    
    /* メインタイトル・サブタイトル */
    .main-title {
        background: linear-gradient(135deg, #c73a54 0%, #a63446 50%, #722c46 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.0em; font-weight: 900; margin-bottom: 5px;
        text-shadow: 0 4px 20px rgba(166, 52, 70, 0.4); letter-spacing: -0.5px;
    }
    .subtitle { color: #ffffff; font-size: 1.1em; margin-bottom: 20px; font-weight: 700; }
    
    /* 上部のメトリック（ID, 氏名など） */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(74, 25, 40, 0.6), rgba(42, 15, 22, 0.8)) !important;
        border: 2px solid rgba(166, 52, 70, 0.6) !important; border-radius: 12px !important;
        padding: 12px 16px !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stMetric"] label { color: #ffffff !important; font-size: 0.8em !important; font-weight: 800 !important; letter-spacing: 0.5px !important; }
    [data-testid="stMetric"] div:nth-child(2) { font-size: 1.1em !important; font-weight: 900 !important; color: #ffffff !important; }
    
    /* アスリートタイプ */
    .athlete-type-section {
        background: linear-gradient(135deg, rgba(166, 52, 70, 0.25), rgba(114, 44, 70, 0.25));
        border-left: 5px solid #c73a54; padding: 20px; border-radius: 12px; margin: 20px 0;
    }
    .athlete-type-label { color: #ffffff; font-size: 0.95em; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; font-weight: 800; }
    .athlete-type-badge {
        background: linear-gradient(135deg, #c73a54 0%, #a63446 100%);
        color: #ffffff; font-size: 2em; font-weight: 900; padding: 18px 30px;
        border-radius: 12px; display: inline-block;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5); box-shadow: 0 8px 24px rgba(166, 52, 70, 0.5); letter-spacing: 0.5px;
    }
    
    /* タブデザイン（すべて白文字化） */
    [data-baseweb="tab-list"] { border-bottom: 3px solid rgba(166, 52, 70, 0.5) !important; }
    [data-baseweb="tab"] {
        background-color: transparent !important; color: #ffffff !important;
        border-radius: 8px 8px 0 0 !important; font-weight: 700 !important;
        padding: 10px 15px !important; font-size: 1.0em !important; opacity: 0.7;
    }
    [aria-selected="true"] {
        background: linear-gradient(135deg, #c73a54 0%, #a63446 100%) !important; color: #ffffff !important;
        box-shadow: 0 -4px 12px rgba(166, 52, 70, 0.4) !important; opacity: 1.0 !important;
    }
    
    /* 詳細データ・解説テキスト */
    .data-row {
        background: rgba(42, 15, 22, 0.8);
        padding: 16px; border-radius: 8px; margin: 10px 0;
        border-left: 5px solid #c73a54; border-top: 1px solid rgba(166, 52, 70, 0.5);
    }
    .data-label { color: #ffffff !important; font-size: 1.1em !important; font-weight: 800 !important; letter-spacing: 0.5px; }
    .data-value { color: #ffffff !important; font-weight: 900 !important; font-size: 1.25em !important; margin-left: 12px; }
    .description-text {
        color: #ffffff !important; font-size: 0.95em !important; font-weight: 600 !important;
        margin-top: 10px; line-height: 1.6;
    }
    
    /* ランクバッジ */
    .rank-badge {
        display: inline-block; font-weight: 900; font-size: 1.2em; padding: 4px 12px;
        border-radius: 6px; min-width: 45px; text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); margin-right: 12px;
    }
    .rank-s { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #451a03; }
    .rank-a { background: linear-gradient(135deg, #f87171, #ef4444); color: #ffffff; }
    .rank-b { background: linear-gradient(135deg, #60a5fa, #3b82f6); color: #ffffff; }
    .rank-c { background: linear-gradient(135deg, #4ade80, #22c55e); color: #ffffff; }
    .rank-none { background: #4a4a4a; color: #ffffff; }
    
    /* コメント・警告ボックス */
    .info-box, .warning-box {
        border-left: 5px solid #c73a54; padding: 18px; border-radius: 8px; margin: 12px 0;
        font-size: 1.0em; line-height: 1.6; font-weight: 700; color: #ffffff !important;
    }
    .info-box { background: linear-gradient(135deg, rgba(166, 52, 70, 0.2), rgba(114, 44, 70, 0.2)); }
    .warning-box { background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(166, 52, 70, 0.2)); }
    
    /* UIパーツ（プルダウン・ボタン） */
    [data-testid="stSelectbox"] label { color: #ffffff !important; font-weight: 800 !important; }
    [data-testid="stSelectbox"] div, [data-baseweb="select"], [data-baseweb="select"] div { background-color: #ffffff !important; color: #000000 !important; font-weight: 700 !important; }
    [data-testid="stExpander"] button { background-color: rgba(74, 25, 40, 0.8) !important; color: #ffffff !important; font-weight: 800 !important; border: 1px solid #c73a54 !important; }
    [data-testid="stExpanderDetails"] { background-color: transparent !important; }
    
    /* スマホ画面向けの最適化 */
    @media (max-width: 768px) {
        .main-title { font-size: 1.6em; }
        .athlete-type-badge { font-size: 1.4em; padding: 12px 20px; }
        [data-testid="stMetric"] { padding: 8px 12px !important; }
    }
    </style>
""", unsafe_allow_html=True)

academic_standards = {
    '男': {
        '垂直跳び': {'mean': 60, 'std': 10}, 'DJ_RSI': {'mean': 2.2, 'std': 0.3},
        '立ち幅跳び': {'mean': 2.6, 'std': 0.2}, '12段跳び': {'mean': 30, 'std': 2},
        '前投げ': {'mean': 12, 'std': 1.5}, '後ろ投げ': {'mean': 13, 'std': 1.5},
        'SQ_1RM': {'mean': 120, 'std': 20}, '懸垂': {'mean': 12, 'std': 4},
        'RAST_max_bw': {'mean': 11.0, 'std': 1.2}, 'RAST_min_bw': {'mean': 7.0, 'std': 1.0},
        'RAST_mean_bw': {'mean': 8.5, 'std': 1.0}, 'RAST_drop_bw': {'mean': 4.0, 'std': 1.0},
        'シャトルラン': {'mean': 100, 'std': 10}
    },
    '女': {
        '垂直跳び': {'mean': 50, 'std': 8}, 'DJ_RSI': {'mean': 1.8, 'std': 0.3},
        '立ち幅跳び': {'mean': 2.1, 'std': 0.2}, '12段跳び': {'mean': 25, 'std': 2},
        '前投げ': {'mean': 8, 'std': 1.5}, '後ろ投げ': {'mean': 9, 'std': 1.5},
        'SQ_1RM': {'mean': 80, 'std': 15}, '懸垂': {'mean': 5, 'std': 3},
        'RAST_max_bw': {'mean': 8.5, 'std': 1.0}, 'RAST_min_bw': {'mean': 6.0, 'std': 1.0},
        'RAST_mean_bw': {'mean': 7.2, 'std': 1.0}, 'RAST_drop_bw': {'mean': 4.5, 'std': 1.0},
        'シャトルラン': {'mean': 80, 'std': 8}
    }
}

def calc_t_score(val, mean, std):
    if pd.isna(val) or std == 0 or pd.isna(std): return None
    return (val - mean) / std * 10 + 50

def get_rank_label(score):
    if pd.isna(score): return "−"
    elif score >= 65: return "S"
    elif score >= 55: return "A"
    elif score >= 45: return "B"
    else: return "C"

def get_rank_class(score):
    if pd.isna(score): return "rank-badge rank-none"
    elif score >= 65: return "rank-badge rank-s"
    elif score >= 55: return "rank-badge rank-a"
    elif score >= 45: return "rank-badge rank-b"
    else: return "rank-badge rank-c"

@st.cache_data(ttl=60)
def load_excel_data(file_path_or_buffer):
    df = pd.read_excel(file_path_or_buffer)
    current_cols = [str(c) for c in df.columns]
    if not any('名前' in c or '氏名' in c for c in current_cols):
        for i, row in df.head(10).iterrows():
            row_strs = [str(val) for val in row.values]
            if any('名前' in val or '氏名' in val for val in row_strs):
                df.columns = row.values
                df = df.iloc[i+1:].reset_index(drop=True)
                break
    df.columns = [str(c).strip().replace('\n', '') for c in df.columns]
    col_mapping = {
        '氏名': '名前', '選手名': '名前', '垂直飛び': '垂直跳び', '垂直飛びcm': '垂直跳び',
        'DJ(RSI)': 'DJ_RSI', 'DJ': 'DJ_RSI', '立ち幅跳び': '立ち幅跳び', '立ち幅飛び': '立ち幅跳び',
        '12段跳び': '12段跳び', '12段飛び': '12段跳び', '前投げ': '前投げ', '後ろ投げ': '後ろ投げ',
        '懸垂': '懸垂', '懸垂(回)': '懸垂', 'SQ 1RM': 'SQ_1RM', 'SQ1RM': 'SQ_1RM', 'ＳＱ１ＲＭ': 'SQ_1RM',
        'シャトルラン': 'シャトルラン'
    }
    df.rename(columns=col_mapping, inplace=True)
    
    for col in df.columns:
        if '無酸素素最大/BW' in col or ('最大' in col and 'BW' in col): df['RAST_max_bw'] = pd.to_numeric(df[col], errors='coerce')
        elif '無酸素素小/BW' in col or ('小' in col and 'BW' in col) or ('最小' in col and 'BW' in col): df['RAST_min_bw'] = pd.to_numeric(df[col], errors='coerce')
        elif '無酸素素平均/BW' in col or ('平均' in col and 'BW' in col): df['RAST_mean_bw'] = pd.to_numeric(df[col], errors='coerce')
        elif '減少率' in col and 'BW' in col: df['RAST_drop_bw'] = pd.to_numeric(df[col], errors='coerce')

    if '名前' not in df.columns: return df
    if '測定日' not in df.columns:
        if '学年' in df.columns: df.rename(columns={'学年': '測定日'}, inplace=True)
        elif len(df.columns) > 1: df.rename(columns={df.columns[1]: '測定日'}, inplace=True)

    df['測定日'] = pd.to_datetime(df['測定日'], errors='coerce').fillna(pd.to_datetime('2026-04-01')).dt.strftime('%Y-%m-%d')
    if 'ID' not in df.columns: df['ID'] = 'M0000'
    df['ID'] = df['ID'].astype(str)
    df = df[~df['ID'].isin(['nan', 'ID', 'None', 'NaN'])]
    df['性別'] = df['ID'].str[0].str.upper().map({'M': '男', 'F': '女'}).fillna('不明')
    df['入学年度'] = df['ID'].apply(lambda x: f"20{x[1:3]}年入学" if len(x) >= 3 and x[1:3].isdigit() else "年度不明")
    
    numeric_cols = list(academic_standards['男'].keys()) + ['身長', '体重']
    for col in numeric_cols:
        if col in df.columns: 
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].replace(0, np.nan)
            
    return df

st.markdown("<div class='main-title'>🏃 ATHLETE PERFORMANCE</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>コントロールテスト測定結果＆パフォーマンス分析</div>", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/color/96/000000/running.png", width=64)
st.sidebar.title("⚙️ 管理メニュー")
uploaded_file = st.sidebar.file_uploader("Excelデータを更新", type=["xlsx", "xls"])
excel_file = "KYOSO_SOKUTEI.xlsx"

df = load_excel_data(uploaded_file) if uploaded_file else (load_excel_data(excel_file) if os.path.exists(excel_file) else None)
if df is None or df.empty or '名前' not in df.columns:
    st.info("📊 Excelファイルをアップロードしてください")
    st.stop()

st.markdown("---")

sel_col1, sel_col2 = st.columns(2)
with sel_col1:
    selected_year = st.selectbox("📅 入学年度を選択", sorted(df['入学年度'].unique(), reverse=True))

filtered_df = df[df['入学年度'] == selected_year]
meas_cols = list(academic_standards['男'].keys())
valid_df = filtered_df.dropna(subset=meas_cols, how='all')

if valid_df.empty:
    st.warning("※この年度にはデータ入力済みの選手がいません。")
    st.stop()

with sel_col2:
    selected_name = st.selectbox("👤 選手を選択", valid_df['名前'].dropna().unique())

player_data = valid_df[valid_df['名前'] == selected_name].sort_values('測定日')
if player_data.empty: st.stop()
latest_data = player_data.iloc[-1]
player_gender = latest_data.get('性別', '男')
if player_gender not in ['男', '女']: player_gender = '男'

st.sidebar.markdown("---")
csv_data = player_data.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(label="💾 個人のCSVデータ出力", data=csv_data, file_name=f"{selected_name}_results.csv", mime='text/csv')

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("ID", latest_data['ID'])
with col2: st.metric("選手", latest_data.get('名前', '---')[:10])
with col3: st.metric("性別", player_gender)
with col4: st.metric("身長", f"{latest_data['身長']:.0f}cm" if pd.notna(latest_data.get('身長')) else "---")
with col5: st.metric("体重", "−" if player_gender == '女' else f"{latest_data['体重']:.0f}kg" if pd.notna(latest_data.get('体重')) else "---")

scores = {}
gender_df = df[df['性別'] == player_gender]

for key in academic_standards[player_gender].keys():
    if key in latest_data and pd.notna(latest_data[key]):
        t_mean, t_std = gender_df[key].mean(), gender_df[key].std()
        team_t = calc_t_score(latest_data[key], t_mean, t_std)
        a_mean, a_std = academic_standards[player_gender][key]['mean'], academic_standards[player_gender][key]['std']
        acad_t = calc_t_score(latest_data[key], a_mean, a_std)
        scores[key] = (team_t + acad_t) / 2
    else: scores[key] = None

axis_defs = {
    '水平パワー': [('立ち幅跳び', 0.7), ('12段跳び', 0.3)],
    '垂直パワー': [('垂直跳び', 0.7), ('DJ_RSI', 0.3)],
    'SSC': [('DJ_RSI', 0.7), ('12段跳び', 0.3)],
    '全身パワー': [('前投げ', 0.3), ('後ろ投げ', 0.3), ('立ち幅跳び', 0.2), ('垂直跳び', 0.2)],
    '基礎筋力': [('SQ_1RM', 0.7), ('懸垂', 0.3)],
    '無酸素パワー': [('RAST_max_bw', 0.25), ('RAST_min_bw', 0.25), ('RAST_mean_bw', 0.25), ('RAST_drop_bw', 0.25)],
    '有酸素能力': [('シャトルラン', 1.0)]
}

radar_dict = {}
radar_symbols_dict = {}

for axis, components in axis_defs.items():
    valid_scores = []
    valid_weights = []
    for key, weight in components:
        if scores.get(key) is not None:
            valid_scores.append(scores[key])
            valid_weights.append(weight)
    
    if not valid_scores:
        radar_dict[axis] = 50.0
        radar_symbols_dict[axis] = 'x'
    else:
        total_weight = sum(valid_weights)
        final_score = sum(s * (w / total_weight) for s, w in zip(valid_scores, valid_weights))
        radar_dict[axis] = final_score
        radar_symbols_dict[axis] = 'circle'

name_map = {
    '垂直パワー': '垂直ジャンプ', '水平パワー': '水平技術', 
    '全身パワー': 'パワー発揮', 'SSC': 'バネ', '基礎筋力': '最高出力',
    '無酸素パワー': '無酸素運動', '有酸素能力': 'タフネス'
}

valid_categories = {k: v for k, v in radar_dict.items() if radar_symbols_dict[k] != 'x'}

if len(valid_categories) < 2:
    athlete_type = "データ不足（測定推奨）"
    top1_cat, worst_cat, worst_score = "---", "---", 0
elif len(valid_categories) == 7:
    scores_list = list(valid_categories.values())
    score_range = max(scores_list) - min(scores_list)
    mean_score = np.mean(scores_list)
    if score_range < 15:
        athlete_type = "高水準オールラウンダー" if mean_score >= 55 else "オールラウンダー"
    else: athlete_type = None
else: athlete_type = None

if athlete_type is None and len(valid_categories) >= 2:
    sorted_categories = sorted(valid_categories.items(), key=lambda x: x[1], reverse=True)
    top1_cat, top1_score = sorted_categories[0]
    top2_cat, top2_score = sorted_categories[1]
    worst_cat, worst_score = sorted_categories[-1]
    
    top2_set = {top1_cat, top2_cat}
    if {"水平パワー", "垂直パワー"}.issubset(top2_set): athlete_type = "ジャンプ得意型"
    elif {"SSC", "水平パワー"}.issubset(top2_set): athlete_type = "水平高速度得意型"
    elif {"SSC", "垂直パワー"}.issubset(top2_set): athlete_type = "高ジャンプ高速度得意型"
    elif "全身パワー" in top2_set and ("水平パワー" in top2_set or "垂直パワー" in top2_set): athlete_type = "高速度出力得意型"
    elif {"基礎筋力", "全身パワー"}.issubset(top2_set): athlete_type = "筋出力高水準型"
    elif {"無酸素パワー", "有酸素能力"}.issubset(top2_set): athlete_type = "高タフネスエコノミー特化型"
    elif {"SSC", "無酸素パワー"}.issubset(top2_set): athlete_type = "高出力スプリント得意型"
    elif {"SSC", "有酸素能力"}.issubset(top2_set): athlete_type = "ランニングエコノミー特化型"
    else: athlete_type = f"{name_map[top1_cat]}{name_map[top2_cat]}型"

radar_categories = list(radar_dict.keys())
radar_values = list(radar_dict.values())
radar_symbols = list(radar_symbols_dict.values())

radar_values_closed = radar_values + [radar_values[0]]
radar_categories_closed = radar_categories + [radar_categories[0]]
radar_symbols_closed = radar_symbols + [radar_symbols[0]]
marker_colors = ['#ef4444' if s == 'x' else '#c73a54' for s in radar_symbols_closed]
marker_sizes = [12 if s == 'x' else 8 for s in radar_symbols_closed]

tab1, tab2, tab3 = st.tabs(["📊 レーダーチャート", "📈 推移グラフ", "📋 詳細データ"])

with tab1:
    col_chart, col_info = st.columns([3, 2])
    with col_chart:
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=radar_values_closed, theta=radar_categories_closed, fill='toself',
            fillcolor='rgba(199, 58, 84, 0.3)', line=dict(color='#c73a54', width=3), 
            mode='lines+markers', marker=dict(symbol=radar_symbols_closed, size=marker_sizes, color=marker_colors)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[20, 80], gridcolor="rgba(255, 255, 255, 0.15)"),
                angularaxis=dict(gridcolor="rgba(255, 255, 255, 0.15)")
            ),
            showlegend=False, margin=dict(l=40, r=40, t=20, b=20), height=450,
            plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='#ffffff', size=13)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_info:
        st.markdown("""
            <div class='athlete-type-section'>
                <div class='athlete-type-label'>あなたのアスリートタイプ</div>
                <div class='athlete-type-badge'>⭐ """ + athlete_type + """</div>
            </div>
        """, unsafe_allow_html=True)
        
        if "データ不足" in athlete_type:
            st.markdown("""
                <div class='warning-box'>
                📝 有効なデータが不足しています。<br>各能力の傾向を分析するため、より多くの測定項目を入力してください。
                </div>
            """, unsafe_allow_html=True)
        elif "オールラウンダー" in athlete_type:
            st.markdown("""
                <div class='info-box'>
                ✨ すべての項目において弱点がなく、非常にバランスの取れた能力を持っています。
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='info-box'>
                💪 <strong>最大の武器</strong>：{top1_cat}<br>
                ⚠️ <strong>ボトルネック</strong>：{worst_cat} (スコア: {worst_score:.1f})
                </div>
            """, unsafe_allow_html=True)

with tab2:
    metric_options = list(academic_standards['男'].keys())
    selected_metric = st.selectbox("分析したい項目を選択", metric_options)
    if len(player_data) > 1 and selected_metric in player_data.columns:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=player_data['測定日'], y=player_data[selected_metric], mode='lines+markers+text',
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in player_data[selected_metric]], textposition="top center",
            line=dict(color='#c73a54', width=4), marker=dict(size=12, color='#ffffff', line=dict(color='#c73a54', width=2))
        ))
        fig_line.update_layout(
            showlegend=False, margin=dict(l=40, r=40, t=20, b=20), height=400,
            plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='#ffffff', size=13),
            xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'), yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)')
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("📊 複数回の測定データが必要です")

with tab3:
    st.markdown("**ランク基準** | **S**：65以上 | **A**：55以上 | **B**：45以上 | **C**：45未満")
    
    categories_ui = {
        "🚀 跳躍・下肢パワー": ['垂直跳び', 'DJ_RSI', '立ち幅跳び', '12段跳び'],
        "🔥 全身パワー・投擲": ['前投げ', '後ろ投げ'],
        "🏋️ 基礎筋力": ['SQ_1RM', '懸垂'],
        "⚡ 無酸素パワー": ['RAST_max_bw', 'RAST_min_bw', 'RAST_mean_bw', 'RAST_drop_bw'],
        "🫁 有酸素能力": ['シャトルラン']
    }
    
    descriptions = {
        '垂直跳び': 'SSCを伴わない下肢の純粋な爆発的パワー',
        'DJ_RSI': '下肢のバネ性能を示す反応筋力指数',
        '立ち幅跳び': '水平方向への爆発的パワー発揮能力',
        '12段跳び': '連続跳躍による推進力と弾性エネルギーの再利用',
        '前投げ': '体幹から上半身への力の伝達',
        '後ろ投げ': '股関節伸展を主体とした全身爆発力',
        'SQ_1RM': 'すべてのパワーの土台となる基礎筋力',
        '懸垂': '上半身の引く筋力および筋持久力',
        'RAST_max_bw': '無酸素運動における最高出力',
        'RAST_min_bw': '疲労状態での底力',
        'RAST_mean_bw': '無酸素運動を持続するための総合容量',
        'RAST_drop_bw': 'パワー減少率（低いほど疲労耐性が高い）',
        'シャトルラン': '有酸素性能力（全身持久力）'
    }

    for cat_name, items in categories_ui.items():
        with st.expander(cat_name, expanded=False):
            for k in items:
                val = latest_data.get(k, np.nan)
                val_str = f"{val:.2f}" if pd.notna(val) else "未測定"
                score = scores.get(k, np.nan)
                rank = get_rank_label(score)
                rank_class = get_rank_class(score)
                
                st.markdown(f"""
                    <div class='data-row'>
                        <span class='data-label'>{k}</span><br>
                        <div style='margin-top: 8px; margin-bottom: 8px;'>
                            <span class='{rank_class}'>{rank}</span><span class='data-value'>{val_str}</span>
                        </div>
                        <div class='description-text'>{descriptions[k]}</div>
                    </div>
                """, unsafe_allow_html=True)
