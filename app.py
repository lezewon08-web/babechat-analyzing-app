import streamlit as st
import google.generativeai as genai
from PIL import Image

# 페이지 기본 설정
st.set_page_config(page_title="소설 캐릭터 분석기", layout="wide")
st.title("📚 웹소설 캐릭터 분석 & 프롬프트 생성기")
st.markdown("소설 텍스트와 캐릭터 이미지를 넣으면 AI가 캐릭터의 설정을 분석하고 프롬프트를 만들어줍니다.")

# 1. 사이드바: API 키 입력
with st.sidebar:
    st.header("🔑 API 키 설정")
    api_key = st.text_input("Google AI Studio API Key", type="password")
    st.markdown("[이곳에서 무료 API 키를 발급받으세요](https://aistudio.google.com/app/apikey)")

# API 키가 입력되었을 때만 메인 화면 실행
if api_key:
    # AI 모델 설정
    genai.configure(api_key=api_key)
    
    # AI에게 내릴 강력한 지시사항 (프롬프트 깎기)
    system_instruction = """
    너는 웹소설 및 서사 분석 전문 AI이자 캐릭터 프롬프트 엔지니어이다.
    제공된 소설 본문과 캐릭터 이미지를 종합 분석하여 캐릭터 상세 정보(외형, 말투, 특징)를 추출하라.
    그리고 결과의 마지막에는 반드시 두 가지를 제공하라:
    1. 이미지 생성용 영문 프롬프트 (Midjourney/Stable Diffusion 용)
    2. AI 롤플레잉/챗봇 설정용 시스템 프롬프트 (성격, 말투 지침 등)
    사용자의 추가 질문이 있다면 이를 최우선으로 반영해라.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )

    # 2. 메인 화면: 좌우 반으로 나누기
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 1. 데이터 입력")
        text_input = st.text_area("📖 소설 본문 또는 설정집 텍스트 붙여넣기", height=250)
        uploaded_file = st.file_uploader("🖼️ 캐릭터 삽화 이미지 업로드 (선택사항)", type=["png", "jpg", "jpeg", "webp"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="업로드된 이미지 미리보기", use_column_width=True)
            
        custom_question = st.text_input("💡 추가로 알고 싶은 정보나 특별한 요청사항 (선택사항)")
        submit_btn = st.button("🚀 캐릭터 분석 시작", type="primary")

    with col2:
        st.subheader("📊 2. 분석 결과 및 프롬프트")
        
        if submit_btn:
            if not text_input and not uploaded_file:
                st.warning("⚠️ 소설 텍스트나 이미지 중 하나는 반드시 입력해야 합니다!")
            else:
                with st.spinner("AI가 텍스트와 이미지를 열심히 분석하고 있습니다. 잠시만 기다려주세요..."):
                    try:
                        prompt_parts = []
                        if text_input:
                            prompt_parts.append(f"[소설 본문]:\n{text_input}\n")
                        if custom_question:
                            prompt_parts.append(f"[추가 요청사항]:\n{custom_question}\n")
                        if uploaded_file:
                            image = Image.open(uploaded_file)
                            prompt_parts.append(image)

                        # AI에게 데이터 전송 및 답변 받기
                        response = model.generate_content(prompt_parts)
                        st.success("분석 완료!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"오류가 발생했습니다. API 키가 정확한지 확인해주세요. 내용: {e}")
else:
    st.info("👈 왼쪽 사이드바에 Google AI Studio API 키를 입력해야 앱이 작동합니다.")
