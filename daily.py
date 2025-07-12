import streamlit as st
import sqlite3
import datetime
import pandas as pd
import calendar

# 创建数据库和表
def create_database():
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    
    # 创建日记表
    c.execute('''CREATE TABLE IF NOT EXISTS entries (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 date TEXT NOT NULL,
                 title TEXT NOT NULL,
                 content TEXT NOT NULL,
                 mood TEXT NOT NULL,
                 tags TEXT)''')
    
    conn.commit()
    conn.close()

# 添加新日记
def add_entry(date, title, content, mood, tags):
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO entries (date, title, content, mood, tags) VALUES (?, ?, ?, ?, ?)", 
                  (date, title, content, mood, tags))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"添加日记失败: {e}")
        return False
    finally:
        conn.close()

# 获取所有日记
def get_all_entries():
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM entries ORDER BY date DESC")
    entries = c.fetchall()
    
    conn.close()
    
    # 转换为DataFrame
    columns = ["id", "日期", "标题", "内容", "心情", "标签"]
    df = pd.DataFrame(entries, columns=columns)
    return df

# 按日期获取日记
def get_entry_by_date(date):
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM entries WHERE date = ?", (date,))
    entry = c.fetchone()
    
    conn.close()
    return entry

# 更新日记
def update_entry(entry_id, title, content, mood, tags):
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    
    try:
        c.execute("UPDATE entries SET title = ?, content = ?, mood = ?, tags = ? WHERE id = ?", 
                  (title, content, mood, tags, entry_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"更新日记失败: {e}")
        return False
    finally:
        conn.close()

# 删除日记
def delete_entry(entry_id):
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"删除日记失败: {e}")
        return False
    finally:
        conn.close()

# 生成日历视图
def generate_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # 获取该月所有日记日期
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"
    
    conn = sqlite3.connect('personal_diary.db')
    c = conn.cursor()
    c.execute("SELECT date FROM entries WHERE date BETWEEN ? AND ?", (start_date, end_date))
    diary_dates = [row[0] for row in c.fetchall()]
    conn.close()
    
    # 创建日历HTML
    html = f"<div style='text-align: center; margin-bottom: 20px;'><h3>{month_name} {year}</h3></div>"
    html += "<table style='width:100%; border-collapse: collapse;'>"
    html += "<tr><th style='border:1px solid #ddd; padding:8px;'>周一</th><th style='border:1px solid #ddd; padding:8px;'>周二</th><th style='border:1px solid #ddd; padding:8px;'>周三</th><th style='border:1px solid #ddd; padding:8px;'>周四</th><th style='border:1px solid #ddd; padding:8px;'>周五</th><th style='border:1px solid #ddd; padding:8px;'>周六</th><th style='border:1px solid #ddd; padding:8px;'>周日</th></tr>"
    
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td style='border:1px solid #ddd; padding:8px; background-color:#f9f9f9;'></td>"
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in diary_dates:
                    html += f"<td style='border:1px solid #ddd; padding:8px; background-color:#e6f7ff; text-align:center;'><a href='?date={date_str}' style='color:#1890ff; text-decoration:none;'>{day}</a></td>"
                else:
                    html += f"<td style='border:1px solid #ddd; padding:8px; text-align:center;'><a href='?date={date_str}' style='color:#333; text-decoration:none;'>{day}</a></td>"
        html += "</tr>"
    
    html += "</table>"
    return html
# 在 main() 开头添加
st.markdown("""
    <link rel="manifest" href="/manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/service-worker.js');
            });
        }
    </script>
""", unsafe_allow_html=True)
# 主应用
def main():
    # 页面配置
    st.set_page_config(
        page_title="个人日记本",
        page_icon="📔",
        layout="wide"
    )
    
    # 自定义样式
    st.markdown("""
        <style>
            .main {background-color: #f8f9fa;}
            .stApp {background-color: #f8f9fa;}
            .header {color: #2c3e50; text-align: center; padding: 10px;}
            .diary-entry { 
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            .diary-title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .diary-date {
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 15px;
            }
            .diary-content {
                color: #34495e;
                line-height: 1.8;
                font-size: 16px;
                white-space: pre-line;
            }
            .mood-tag {
                display: inline-block;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 13px;
                margin-right: 8px;
                margin-top: 10px;
            }
            .calendar-container {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            .tag {
                display: inline-block;
                background-color: #e0f7fa;
                color: #006064;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-right: 5px;
                margin-top: 5px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 初始化数据库
    create_database()
    
    # 获取URL参数 - 正确使用 st.query_params
    # 注意：st.query_params 是一个属性，不是函数，不要加括号
    query_params = st.query_params
    selected_date = query_params.get("date", None)
    
    # 如果 date 参数是列表，取第一个值
    if isinstance(selected_date, list) and selected_date:
        selected_date = selected_date[0]
    
    # 当前日期
    today = datetime.date.today().isoformat()
    
    # 页面标题
    st.markdown('<div class="header"><h1>📔 个人日记本</h1></div>', unsafe_allow_html=True)
    st.caption("记录生活点滴，珍藏美好回忆")
    
    # 侧边栏导航
    st.sidebar.title("导航")
    menu = st.sidebar.radio("选择功能", ["写日记", "看日记", "日历视图", "搜索日记", "关于"])
    
    # 写日记页面
    if menu == "写日记":
        st.subheader("写新日记")
        
        # 默认使用URL参数中的日期或今天
        default_date = selected_date if selected_date else today
        
        with st.form("add_entry_form", clear_on_submit=True):
            date = st.date_input("日期", value=datetime.date.fromisoformat(default_date))
            title = st.text_input("标题", placeholder="今天的美好时刻")
            
            mood = st.selectbox("心情", ["😊 开心", "😄 兴奋", "😌 平静", "😢 难过", "😠 生气", "😔 忧郁", "😴 疲惫", "🤔 思考"])
            
            tags = st.text_input("标签 (用逗号分隔)", placeholder="例如: 旅行, 生日, 感悟")
            
            content = st.text_area("日记内容", height=300, 
                                  placeholder="写下今天的经历和感受...", 
                                  help="尽情表达你的想法和情感")
            
            submitted = st.form_submit_button("保存日记")
            
            if submitted:
                if not content:
                    st.warning("请填写日记内容！")
                else:
                    date_str = date.isoformat()
                    success = add_entry(date_str, title, content, mood, tags)
                    if success:
                        st.success("日记保存成功！")
                        # 清除表单
                        st.rerun()
    
    # 看日记页面
    elif menu == "看日记":
        st.subheader("我的日记")
        
        # 获取所有日记
        entries_df = get_all_entries()
        
        if entries_df.empty:
            st.info("还没有日记，开始写下你的第一篇日记吧！")
        else:
            # 日期筛选
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期", value=datetime.date.fromisoformat(entries_df["日期"].min()))
            with col2:
                end_date = st.date_input("结束日期", value=datetime.date.fromisoformat(entries_df["日期"].max()))
            
            # 心情筛选
            moods = ["😊 开心", "😄 兴奋", "😌 平静", "😢 难过", "😠 生气", "😔 忧郁", "😴 疲惫", "🤔 思考"]
            selected_moods = st.multiselect("心情筛选", options=moods, default=moods)
            
            # 标签筛选
            all_tags = set()
            for tags_str in entries_df["标签"]:
                if tags_str:
                    all_tags.update(tag.strip() for tag in tags_str.split(','))
            selected_tags = st.multiselect("标签筛选", options=sorted(all_tags))
            
            # 应用筛选
            filtered_entries = entries_df.copy()
            filtered_entries = filtered_entries[
                (filtered_entries["日期"] >= start_date.isoformat()) &
                (filtered_entries["日期"] <= end_date.isoformat()) &
                (filtered_entries["心情"].isin(selected_moods))
            ]
            
            if selected_tags:
                filtered_entries = filtered_entries[
                    filtered_entries["标签"].apply(
                        lambda x: any(tag in (x.split(',') if x else []) for tag in selected_tags)
                    )
                ]
            
            # 显示日记
            if filtered_entries.empty:
                st.info("没有找到符合条件的日记")
            else:
                st.write(f"找到 {len(filtered_entries)} 篇日记")
                
                for _, row in filtered_entries.iterrows():
                    with st.container():
                        st.markdown(f"<div class='diary-entry'>", unsafe_allow_html=True)
                        
                        # 日期和心情
                        mood_bg_color = '#e3f2fd' if '开心' in row['心情'] or '兴奋' in row['心情'] else '#ffebee' if '难过' in row['心情'] or '生气' in row['心情'] else '#f3e5f5'
                        st.markdown(f"<div class='diary-date'>{row['日期']} <span class='mood-tag' style='background-color:{mood_bg_color};'>{row['心情']}</span></div>", unsafe_allow_html=True)
                        
                        # 标题
                        st.markdown(f"<div class='diary-title'>{row['标题']}</div>", unsafe_allow_html=True)
                        
                        # 标签
                        if row['标签'] and isinstance(row['标签'], str):
                            tags_html = "<div style='margin-bottom: 10px;'>"
                            for tag in row['标签'].split(','):
                                tags_html += f"<span class='tag'>{tag.strip()}</span>"
                            tags_html += "</div>"
                            st.markdown(tags_html, unsafe_allow_html=True)
                        
                        # 内容
                        st.markdown(f"<div class='diary-content'>{row['内容']}</div>", unsafe_allow_html=True)
                        
                        # 操作按钮
                        col_btn1, col_btn2 = st.columns([1, 9])
                        with col_btn1:
                            if st.button("编辑", key=f"edit_{row['id']}"):
                                st.session_state.edit_entry = row['id']
                        with col_btn2:
                            if st.button("删除", key=f"delete_{row['id']}"):
                                if delete_entry(row['id']):
                                    st.success("日记已删除！")
                                    st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
    
    # 日历视图
    elif menu == "日历视图":
        st.subheader("日历视图")
        st.info("点击有日记的日期可以查看或编辑那天的日记")
        
        # 选择年月
        today = datetime.date.today()
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("选择年份", min_value=2000, max_value=2100, value=today.year)
        with col2:
            month = st.selectbox("选择月份", range(1, 13), index=today.month-1)
        
        # 生成日历
        cal_html = generate_calendar(year, month)
        st.markdown(f"<div class='calendar-container'>{cal_html}</div>", unsafe_allow_html=True)
        
        # 显示选定日期的日记
        if selected_date:
            entry = get_entry_by_date(selected_date)
            if entry:
                st.subheader(f"{selected_date} 的日记")
                st.markdown(f"<div class='diary-entry'>", unsafe_allow_html=True)
                st.markdown(f"<div class='diary-date'>{entry[1]} <span class='mood-tag'>{entry[4]}</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='diary-title'>{entry[2]}</div>", unsafe_allow_html=True)
                
                if entry[5]:
                    tags_html = "<div style='margin-bottom: 10px;'>"
                    for tag in entry[5].split(','):
                        tags_html += f"<span class='tag'>{tag.strip()}</span>"
                    tags_html += "</div>"
                    st.markdown(tags_html, unsafe_allow_html=True)
                
                st.markdown(f"<div class='diary-content'>{entry[3]}</div>", unsafe_allow_html=True)
                
                # 编辑按钮
                if st.button("编辑这篇日记"):
                    st.session_state.edit_entry = entry[0]
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info(f"{selected_date} 还没有日记")
                if st.button(f"为 {selected_date} 写日记"):
                    # 使用新的 query_params 设置日期
                    st.query_params["date"] = selected_date
                    st.rerun()
    
    # 搜索日记
    elif menu == "搜索日记":
        st.subheader("搜索日记")
        
        search_query = st.text_input("搜索内容", placeholder="输入关键词搜索日记...")
        
        if search_query:
            entries_df = get_all_entries()
            if entries_df.empty:
                st.info("还没有日记")
            else:
                # 执行搜索
                results = entries_df[
                    entries_df["标题"].str.contains(search_query, case=False) |
                    entries_df["内容"].str.contains(search_query, case=False) |
                    entries_df["标签"].str.contains(search_query, case=False)
                ]
                
                if results.empty:
                    st.info("没有找到匹配的日记")
                else:
                    st.write(f"找到 {len(results)} 篇匹配的日记")
                    
                    for _, row in results.iterrows():
                        with st.container():
                            st.markdown(f"<div class='diary-entry'>", unsafe_allow_html=True)
                            
                            # 日期和心情
                            st.markdown(f"<div class='diary-date'>{row['日期']} <span class='mood-tag'>{row['心情']}</span></div>", unsafe_allow_html=True)
                            
                            # 标题
                            st.markdown(f"<div class='diary-title'>{row['标题']}</div>", unsafe_allow_html=True)
                            
                            # 标签
                            if row['标签'] and isinstance(row['标签'], str):
                                tags_html = "<div style='margin-bottom: 10px;'>"
                                for tag in row['标签'].split(','):
                                    tags_html += f"<span class='tag'>{tag.strip()}</span>"
                                tags_html += "</div>"
                                st.markdown(tags_html, unsafe_allow_html=True)
                            
                            # 内容预览
                            content_preview = row['内容'][:300] + "..." if len(row['内容']) > 300 else row['内容']
                            st.markdown(f"<div class='diary-content'>{content_preview}</div>", unsafe_allow_html=True)
                            
                            # 查看完整日记按钮
                            if st.button("查看全文", key=f"view_{row['id']}"):
                                st.session_state.view_entry = row['id']
                            
                            st.markdown("</div>", unsafe_allow_html=True)
    
    # 关于页面
    elif menu == "关于":
        st.subheader("关于个人日记本")
        
        st.markdown("""
            ## 📖 个人日记本软件
            
            **个人日记本**是一个专为个人设计的日记记录软件，帮助您：
            
            - ✍️ 记录日常生活和重要时刻
            - 😊 标记心情状态和情感变化
            - 🏷️ 使用标签整理日记内容
            - 📅 通过日历视图浏览日记
            - 🔍 快速搜索过去的日记
            
            ### 主要功能
            
            1. **写日记**：
               - 记录每天的所思所想
               - 标记心情状态
               - 添加自定义标签
            
            2. **看日记**：
               - 按时间顺序浏览所有日记
               - 按日期范围、心情、标签筛选
            
            3. **日历视图**：
               - 直观查看有日记的日期
               - 点击日期查看或编辑日记
            
            4. **搜索日记**：
               - 通过关键词搜索日记内容
               - 快速找到特定主题的日记
            
            ### 隐私保护
            
            - 所有数据存储在本地数据库（personal_diary.db）
            - 无需联网，完全私密
            - 您的日记只属于您一个人
            
            ### 使用说明
            
            1. 首次使用会自动创建数据库
            2. 在"写日记"页面开始记录
            3. 使用"看日记"或"日历视图"回顾过去的日记
            4. 使用"搜索日记"查找特定内容
            
            **您的所有日记都保存在本地计算机上，请定期备份 personal_diary.db 文件以防数据丢失。**
        """)
        
        st.markdown("---")
        st.info("个人日记本 v1.0 | 设计: 您的私人记忆守护者 | 2025年")

    # 编辑日记（特殊状态）
    if 'edit_entry' in st.session_state:
        entry_id = st.session_state.edit_entry
        conn = sqlite3.connect('personal_diary.db')
        c = conn.cursor()
        c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        entry = c.fetchone()
        conn.close()
        
        if entry:
            st.subheader("编辑日记")
            
            with st.form("edit_entry_form"):
                date = st.date_input("日期", value=datetime.date.fromisoformat(entry[1]))
                title = st.text_input("标题", value=entry[2])
                
                mood = st.selectbox("心情", ["😊 开心", "😄 兴奋", "😌 平静", "😢 难过", "😠 生气", "😔 忧郁", "😴 疲惫", "🤔 思考"], 
                                  index=["😊 开心", "😄 兴奋", "😌 平静", "😢 难过", "😠 生气", "😔 忧郁", "😴 疲惫", "🤔 思考"].index(entry[4]))
                
                tags = st.text_input("标签 (用逗号分隔)", value=entry[5])
                
                content = st.text_area("日记内容", value=entry[3], height=300)
                
                col1, col2 = st.columns(2)
                with col1:
                    save_btn = st.form_submit_button("保存修改")
                with col2:
                    cancel_btn = st.form_submit_button("取消编辑")
                
                if save_btn:
                    date_str = date.isoformat()
                    if update_entry(entry_id, title, content, mood, tags):
                        st.success("日记更新成功！")
                        del st.session_state.edit_entry
                        st.rerun()
                
                if cancel_btn:
                    del st.session_state.edit_entry
                    st.rerun()

# 运行应用
if __name__ == "__main__":
    main()
