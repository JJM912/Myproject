def apply_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
        }

        /* 앱 전체 배경: 흰색 */
        .stApp {
            background: #FFFFFF;
        }

        /* 왼쪽 사이드바: 하늘색 */
        section[data-testid="stSidebar"] {
            background: #E0F2FE;
        }

        section[data-testid="stSidebar"] * {
            color: #0369A1 !important;
        }

        /* 사이드바 제목 */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #0369A1 !important;
            font-weight: 800;
        }

        /* 학번 입력창 */
        section[data-testid="stSidebar"] input {
            background: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #7DD3FC !important;
            border-radius: 10px !important;
        }

        /* 왼쪽 메뉴 버튼 */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            background: #FFFFFF !important;
            color: #0284C7 !important;
            border: 1px solid #BAE6FD !important;
            border-radius: 12px;
            font-weight: 900;
            text-align: left;
            margin-bottom: 6px;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
            color: #0284C7 !important;
            font-weight: 900 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            background: #F0F9FF !important;
            border: 1px solid #38BDF8 !important;
            color: #0369A1 !important;
        }

        /* 일반 버튼 */
        div[data-testid="stButton"] > button {
            border-radius: 12px;
            font-weight: 800;
        }

        /* 홈 화면 학교명: 하늘색 */
        .home-school {
            text-align: center;
            font-size: 1.25rem;
            font-weight: 900;
            letter-spacing: .18em;
            color: #0284C7;
            text-transform: uppercase;
            margin-top: 18px;
            margin-bottom: 8px;
        }

        /* 홈 화면 제목 */
        .home-title {
            text-align: center;
            font-size: 3.6rem;
            font-weight: 900;
            color: #0F172A;
            margin-bottom: 18px;
            line-height: 1.1;
        }

        /* Reading Class: 하늘색 */
        .home-title .blue {
            color: #0284C7;
        }

        .sidebar-footer {
            font-size: 12px;
            color: #0369A1 !important;
            margin-top: 20px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
