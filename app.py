import streamlit as st
import google.generativeai as genai
from PIL import Image

# 페이지 기본 설정
st.set_page_config(page_title="웹소설 캐릭터 분석기", layout="wide")
st.title("📚 멀티 웹소설 캐릭터 분석 & 프롬프트 생성기")
st.markdown("소설 입력 칸을 자유롭게 추가하여 여러 편의 소설이나 설정집을 붙여넣고 통합 분석할 수 있습니다.")

# 1. 세션 상태 초기화 (입력 칸 개수 관리)
if "novel_inputs" not in st.session_state:
    st.session_state.novel_inputs = [""]

# 입력 칸 추가 함수
def add_novel_input():
    st.session_state.novel_inputs.append("")

# 입력 칸 삭제 함수
def remove_novel_input(index):
    if len(st.session_state.novel_inputs) > 1:
        st.session_state.novel_inputs.pop(index)

# 2. 사이드바: API 키 및 모델 설정
with st.sidebar:
    st.header("🔑 API 키 설정")
    api_key = st.text_input("Google AI Studio API Key", type="password")
    st.markdown("[무료 API 키 발급받기](https://aistudio.google.com/app/apikey)")
    
    # 3.5 Flash 및 3.6 Flash 선택 옵션
    model_choice = st.selectbox(
        "AI 모델 선택",
        ["gemini-3.6-flash", "gemini-3.5-flash", "직접 입력"],
        help="사용하실 Flash 모델을 선택하세요."
    )
    
    if model_choice == "직접 입력":
        selected_model = st.text_input("모델명 직접 입력", value="gemini-3.6-flash")
    else:
        selected_model = model_choice

if api_key:
    genai.configure(api_key=api_key)
    
    system_instruction = """
    너는 웹소설 및 서사 분석 전문 AI이자 캐릭터 프롬프트 엔지니어이다.
    제공된 여러 소설 본문/설정 텍스트들과 캐릭터 이미지를 종합적으로 연계 분석하여 캐릭터 상세 정보(외형, 말투, 특징)를 추출하라.
    여러 에피소드나 작품에 걸쳐 등장하는 캐릭터의 서사적 변화나 입체적인 정보도 함께 반영하라.
    
    결과 작성시 반드시 아래 항목을 포함하라:
    1. 인물 상세 분석 (외형, 말투/어조, 주요 특징 및 인간관계)
    2. 이미지 생성용 영문 프롬프트 (Midjourney/Stable Diffusion 용)
    3. AI 롤플레잉/챗봇 설정용 시스템 프롬프트 (성격, 말투 지침 등)
    사용자의 추가 질문이 있다면 이를 최우선으로 반영하라.
    """
    
    model = genai.GenerativeModel(
        model_name=selected_model,
        system_instruction=system_instruction
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 1. 소설 및 이미지 입력")
        
        # 1-1. 동적 소설 입력 칸 생성
        st.write("📖 **소설 본문 / 설정집 입력**")
        for i in range(len(st.session_state.novel_inputs)):
            col_text, col_del = st.columns([0.85, 0.15])
            with col_text:
                st.session_state.novel_inputs[i] = st.text_area(
                    f"소설 텍스트 #{i+1}", 
                    value=st.session_state.novel_inputs[i], 
                    height=150,
                    key=f"novel_text_{i}"
                )
            with col_del:
                st.write("") 
                st.write("")
                if len(st.session_state.novel_inputs) > 1:
                    st.button("❌ 삭제", key=f"del_{i}", on_click=remove_novel_input, args=(i,))

        # 입력 칸 추가 버튼
        st.button("➕ 소설 입력 칸 추가하기", on_click=add_novel_input)
        
        st.divider()

        # 1-2. 여러 텍스트 파일 업로드
        uploaded_txt_files = st.file_uploader(
            "📂 텍스트 파일(.txt)로 여러 개 올리기 (선택사항)", 
            type=["txt"], 
            accept_multiple_files=True
        )
        
        # 1-3. 캐릭터 이미지 업로드
        uploaded_img_files = st.file_uploader(
            "🖼️ 캐릭터 삽화/설정집 이미지 업로드 (선택사항)", 
            type=["png", "jpg", "jpeg", "webp"], 
            accept_multiple_files=True
        )
        
        custom_question = st.text_input("💡 추가 분석 요청사항 (예: 특정 인물 간의 관계성 위주로 정리해줘)")
        submit_btn = st.button("🚀 통합 캐릭터 분석 시작", type="primary")

    with col2:
        st.subheader("📊 2. 통합 분석 결과 및 프롬프트")
        
        if submit_btn:
            has_text = any(t.strip() for t in st.session_state.novel_inputs)
            if not has_text and not uploaded_txt_files and not uploaded_img_files:
                st.warning("⚠️ 소설 텍스트, 파일, 이미지 중 최소 하나 이상은 입력해야 합니다!")
            else:
                with st.spinner("입력하신 모든 소설 내용과 이미지를 통합 분석 중입니다..."):
                    try:
                        prompt_parts = []
                        
                        # 붙여넣은 소설 입력 칸들 내용 취합
                        for idx, content in enumerate(st.session_state.novel_inputs):
                            if content.strip():
                                prompt_parts.append(f"[소설 입력 #{idx+1}]:\n{content}\n")
                        
                        # 업로드된 TXT 파일 내용 읽기
                        if uploaded_txt_files:
                            for idx, txt_file in enumerate(uploaded_txt_files):
                                file_content = txt_file.read().decode("utf-8", errors="ignore")
                                prompt_parts.append(f"[소설 파일: {txt_file.name}]:\n{file_content}\n")
                        
                        # 업로드된 이미지 반영
                        if uploaded_img_files:
                            for img_file in uploaded_img_files:
                                image = Image.open(img_file)
                                prompt_parts.append(image)
                                
                        # 추가 요청사항
                        if custom_question:
                            prompt_parts.append(f"[추가 요청사항]:\n{custom_question}\n")

                        # AI에 분석 요청
                        response = model.generate_content(prompt_parts)
                        st.success("통합 분석 완료!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("👈 왼쪽 사이드바에 Google AI Studio API 키를 입력하면 작동합니다.")
