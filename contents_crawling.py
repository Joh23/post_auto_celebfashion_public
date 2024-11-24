import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyairtable import Table
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
import heapq

# NLTK 데이터 다운로드
nltk.download('punkt')
nltk.download('stopwords')

# 에어테이블 API 설정
AIRTABLE_API_KEY = 'patLP0qMfUyjuyE2V.6a85b057fddcb8f276c0b97d44f6d75a3da70fc255b13f7e4d088e475fed72fb'
BASE_ID = 'appYlgoRy8QQ7YLJS'
TABLE_NAME = '셀럽패션'
table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_naver_blog(url):
    driver = setup_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it("mainFrame"))
        
        title = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".se-title-text"))
        ).text
        
        content_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".se-main-container .se-text-paragraph"))
        )
        content = "\n".join([element.text for element in content_elements if element.text.strip() != ''])
        
        return title, content
    except Exception as e:
        return f"Error scraping URL: {str(e)}", ""
    finally:
        driver.quit()

def summarize_text(text, num_sentences=5):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    word_frequencies = FreqDist(word for word in words if word not in stop_words)
    
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies.keys():
                if len(sentence.split()) < 30:  # 너무 긴 문장 제외
                    if sentence not in sentence_scores.keys():
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]
    
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary

def scrape_instagram_images(url):
    driver = setup_driver()
    image_urls = []
    try:
        # 첫 번째 이미지 가져오기
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "_aagv")))
        image_element = driver.find_element(By.CSS_SELECTOR, "._aagv img")
        image_url = image_element.get_attribute('src')
        image_urls.append(image_url)

        # 두 번째 이미지부터 스크래핑 시작
        for i in range(2, 11):
            new_url = f"{url}?hl=ko&img_index={i}"
            driver.get(new_url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "_aagv")))
            
            # 현재 URL 확인
            current_url = driver.current_url
            current_index = int(current_url.split('img_index=')[-1])
            
            # 이미 마지막 이미지에 도달했는지 확인
            if current_index < i:
                break
            
            image_element = driver.find_element(By.CSS_SELECTOR, "._aagv img")
            image_url = image_element.get_attribute('src')
            
            # 중복 이미지 체크
            if image_url not in image_urls:
                image_urls.append(image_url)
            else:
                break

    except Exception as e:
        print(f"Error scraping Instagram images: {str(e)}")
    finally:
        driver.quit()
    
    return image_urls

def save_to_airtable(data):
    table.create(data)

def main():
    st.title("네이버 블로그, 제품 정보 및 인스타그램 URL 저장")
    
    # 1. 콘텐츠 형식, 톤앤매너, 핵심 키워드
    st.header("1. 콘텐츠 설정")
    content_formats = ["블로그 포스트", "매거진 기사", "인스타그램 게시글"]
    selected_format = st.selectbox("원하는 콘텐츠 형식", options=content_formats, index=0)
    
    tone_options = [
        "친근한/대화체",
        "전문적/분석적",
        "유머러스/위트 있는",
        "감성적/서정적",
        "트렌디/힙한",
        "간결한/직설적"
    ]
    selected_tone = st.selectbox("글의 전체적인 톤앤매너", options=tone_options, index=0)
    
    keywords = st.text_input("핵심 키워드 (SEO를 위해 사용)")
    
    # 2. 네이버 블로그 URL 입력란
    st.header("2. 네이버 블로그 URL 입력")
    url1 = st.text_input("네이버 블로그 URL 1:")
    url2 = st.text_input("네이버 블로그 URL 2:")
    url3 = st.text_input("네이버 블로그 URL 3:")
    
    text_input1 = st.text_area("텍스트 입력 1:")
    text_input2 = st.text_area("텍스트 입력 2:")
    
    # 3. 제품 정보 입력란
    st.header("3. 제품 정보 입력")
    product_url = st.text_input("제품 URL:")
    product_info = st.text_area("제품 정보:")
    product_image_url1 = st.text_input("제품 이미지 URL 1:")
    product_image_url2 = st.text_input("제품 이미지 URL 2:")
    product_image_url3 = st.text_input("제품 이미지 URL 3:")
    product_image_url4 = st.text_input("제품 이미지 URL 4:")
    product_image_url5 = st.text_input("제품 이미지 URL 5:")
    product_image_url6 = st.text_input("제품 이미지 URL 6:")
    
    # 4. 인스타그램 URL 입력란
    st.header("4. 인스타그램 URL 입력")
    instagram_url = st.text_input("인스타그램 URL:")
    
    if st.button("크롤링 및 저장"):
        data = {}
        
        # 네이버 블로그 URL 크롤링
        if url1:
            with st.spinner(f"{url1}에서 텍스트를 추출 중..."):
                title1, content1 = scrape_naver_blog(url1)
                data.update({'URL1': url1, 'Title1': title1, 'Content1': content1})
        
        if url2:
            with st.spinner(f"{url2}에서 텍스트를 추출 중..."):
                title2, content2 = scrape_naver_blog(url2)
                data.update({'URL2': url2, 'Title2': title2, 'Content2': content2})
        
        if url3:
            with st.spinner(f"{url3}에서 텍스트를 추출 중..."):
                title3, content3 = scrape_naver_blog(url3)
                data.update({'URL3': url3, 'Title3': title3, 'Content3': content3})
        
        # 직접 입력한 텍스트 저장
        if text_input1:
            data.update({'Text1': text_input1})
        
        if text_input2:
            data.update({'Text2': text_input2})
        
        # 콘텐츠 형식, 톤앤매너, 핵심 키워드 저장
        data.update({
            '콘텐츠형식': selected_format,
            '톤앤매너': selected_tone,
            '핵심키워드': keywords
        })
        
        # 제품 정보 저장
        if product_url:
            data.update({
                'ProductURL': product_url,
                'ProductInfo': product_info,
            })
            if product_image_url1:
                data.update({'ProductImage1': [{'url': product_image_url1}]})
            if product_image_url2:
                data.update({'ProductImage2': [{'url': product_image_url2}]})
            if product_image_url3:
                data.update({'ProductImage3': [{'url': product_image_url3}]})
            if product_image_url4:
                data.update({'ProductImage4': [{'url': product_image_url4}]})
            if product_image_url5:
                data.update({'ProductImage5': [{'url': product_image_url5}]})
            if product_image_url6:
                data.update({'ProductImage6': [{'url': product_image_url6}]})
        
        # 인스타그램 URL 및 이미지 저장
        if instagram_url:
            data.update({'InstagramURL': instagram_url})
            instagram_images = scrape_instagram_images(instagram_url)
            for i, img_url in enumerate(instagram_images, start=1):
                data.update({f'InstagramImage{i}': [{'url': img_url}]})
        
        # 에어테이블에 데이터 저장
        if data:
            save_to_airtable(data)
            st.success("데이터가 성공적으로 저장되었습니다.")
        else:
            st.error("입력된 데이터가 없습니다.")

if __name__ == "__main__":
    main()