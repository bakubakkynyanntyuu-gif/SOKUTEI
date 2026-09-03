import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import io

st.set_page_config(page_title="コントロールテスト フィードバック", page_icon="🏃", layout="wide")

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
    if pd.isna(score):
        return "−"
    elif score >= 65:
        return "S"
    elif score >= 55:
        return "A"
    elif score >= 45:
        return "B"
    else:
        return "C"

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

st.title("🏃 コントロールテスト フィードバック")

st.sidebar.image("https://img.icons8.com/color/96/000000/running.png", width=64)
st.sidebar.title("コントロールテスト")
uploaded_file = st.sidebar.file_uploader("Excelデータをアップロード", type=["xlsx", "xls"])
excel_file = "KYOSO_SOKUTEI.xlsx"

df = load_excel_data(uploaded_file) if uploaded_file else (load_excel_data(excel_file) if os.path.exists(excel_file) else None)
if df is None or df.empty or '名前' not in df.columns:
    st.warning("📊 Excelファイルをアップロードしてください。")
    st.info("""
    **必要な列:**
    - 名前 / 氏名
    - ID（M2024, F2023など）
    - 測定日
    - 身長, 体重
    - 測定項目（垂直跳び、DJ_RSI、立ち幅跳び、12段跳び、前投げ、後ろ投げ、SQ_1RM、懸垂、RAST関連、シャトルラン）
    """)
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 選手選択")
selected_year = st.sidebar.selectbox("入学年度", sorted(df['入学年度'].unique(), reverse=True))
filtered_df = df[df['入学年度'] == selected_year]
if filtered_df.empty: st.stop()

meas_cols = list(academic_standards['男'].keys())
valid_df = filtered_df.dropna(subset=meas_cols, how='all')

if valid_df.empty:
    st.sidebar.warning("※この年度にはデータ入力済みの選手がいません。")
    st.stop()

selected_name = st.sidebar.selectbox("氏名", valid_df['名前'].dropna().unique())
player_data = valid_df[valid_df['名前'] == selected_name].sort_values('測定日')
if player_data.empty: st.stop()
latest_data = player_data.iloc[-1]
player_gender = latest_data.get('性別', '男')
if player_gender not in ['男', '女']: player_gender = '男'

st.sidebar.markdown("---")
st.sidebar.subheader("📤 共有・保存")

csv_data = player_data.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 この選手のデータをCSVで保存",
    data=csv_data,
    file_name=f"{selected_name}_control_test.csv",
    mime='text/csv',
)

st.header("ATHLETE PERFORMANCE DASHBOARD")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("選手 ID", latest_data['ID'])
col2.metric("氏名", f"{latest_data.get('名前', '---')} ({player_gender})")
col3.metric("最新測定日", latest_data['測定日'])
col4.metric("身長", f"{latest_data['身長']:.1f} cm" if pd.notna(latest_data.get('身長')) else "---")
col5.metric("体重", "非表示" if player_gender == '女' else f"{latest_data['体重']:.1f} kg" if pd.notna(latest_data.get('体重')) else "---")

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
marker_colors = ['#DC143C' if s == 'x' else '#1e3c72' for s in radar_symbols_closed]
marker_sizes = [12 if s == 'x' else 8 for s in radar_symbols_closed]

tab1, tab2, tab3 = st.tabs(["📊 総合評価 (レーダー)", "📈 経時変化 (推移)", "📋 測定データ詳細"])

with tab1:
    col_chart, col_info = st.columns([3, 2])
    with col_chart:
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=radar_values_closed, theta=radar_categories_closed, fill='toself',
            fillcolor='rgba(42, 82, 152, 0.35)', line=dict(color='#1e3c72', width=3), 
            mode='lines+markers', marker=dict(symbol=radar_symbols_closed, size=marker_sizes, color=marker_colors)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[20, 80], gridcolor="#e9ecef"), angularaxis=dict(gridcolor="#e9ecef")),
            showlegend=False, margin=dict(l=40, r=40, t=20, b=20), height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("未測定により計算できない軸はスコア50として「✕」印で表示しています。")

    with col_info:
        st.subheader("🧬 あなたのアスリートタイプ")
        st.write(f"**⭐ {athlete_type}**")
        
        st.subheader("💬 自動分析コメント")
        if "データ不足" in athlete_type:
            st.warning("有効なデータが不足しています。各能力の傾向を分析するため、より多くの測定項目を入力してください。")
        elif "オールラウンダー" in athlete_type:
            st.info("すべての項目において弱点がなく、非常にバランスの取れた能力を持っています。")
        else:
            st.info(f"最大の武器は【{top1_cat}】です。ボトルネックは【{worst_cat}】（スコア: {worst_score:.1f}）です。")

with tab2:
    metric_options = list(academic_standards['男'].keys())
    selected_metric = st.selectbox("分析したい項目を選択", metric_options)
    if len(player_data) > 1 and selected_metric in player_data.columns:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=player_data['測定日'], y=player_data[selected_metric], mode='lines+markers+text',
            text=[f"{v:.1f}" if pd.notna(v) else "" for v in player_data[selected_metric]], textposition="top center",
            line=dict(color='#2a5298', width=3), marker=dict(size=10, color='#1e3c72')
        ))
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("データが1件のみのため、グラフは表示されません。")

with tab3:
    st.subheader("測定データ詳細 & 項目解説")
    st.markdown("Sランク：65以上 | Aランク：55以上 | Bランク：45以上 | Cランク：45未満")
    
    categories_ui = {
        "🚀 跳躍・下肢パワー（垂直・水平・SSC）": ['垂直跳び', 'DJ_RSI', '立ち幅跳び', '12段跳び'],
        "🔥 全身パワー・投擲": ['前投げ', '後ろ投げ'],
        "🏋️ 基礎筋力": ['SQ_1RM', '懸垂'],
        "⚡ 無酸素パワー（RAST）": ['RAST_max_bw', 'RAST_min_bw', 'RAST_mean_bw', 'RAST_drop_bw'],
        "🫁 有酸素能力": ['シャトルラン']
    }
    
    descriptions = {
        '垂直跳び': 'SSCを伴わない、下肢の純粋な爆発的パワーを評価します。',
        'DJ_RSI': '短い接地時間での反応筋力指数。下肢のバネ性能を表します。',
        '立ち幅跳び': '下肢の水平方向への爆発的パワー発揮能力。スプリント能力と相関があります。',
        '12段跳び': '連続跳躍による水平推進力と弾性エネルギーの再利用能力を評価します。',
        '前投げ': '体幹から上半身への力の伝達と全身連動性を評価します。',
        '後ろ投げ': '股関節伸展を主体とした全身爆発的パワーを評価します。',
        'SQ_1RM': '下肢の最大筋力。すべてのパワーの土台となる基礎的な力の大きさです。',
        '懸垂': '上半身の引く筋力および筋持久力。',
        'RAST_max_bw': '無酸素運動における最高出力。',
        'RAST_min_bw': '疲労状態での底力。',
        'RAST_mean_bw': '無酸素運動を持続するための総合容量。',
        'RAST_drop_bw': 'パワー減少率。低いほど疲労耐性が高い。',
        'シャトルラン': '有酸素性能力（全身持久力）。'
    }

    for cat_name, items in categories_ui.items():
        with st.expander(cat_name, expanded=False):
            for k in items:
                val = latest_data.get(k, np.nan)
                val_str = f"{val:.2f}" if pd.notna(val) else "未測定"
                score = scores.get(k, np.nan)
                rank = get_rank_label(score)
                
                st.write(f"**[{rank}] {k}** : {val_str}")
                st.caption(descriptions[k])
