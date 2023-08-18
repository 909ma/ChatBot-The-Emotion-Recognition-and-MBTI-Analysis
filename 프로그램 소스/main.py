import urllib.request
import json
import requests
from konlpy.tag import Komoran
import random
import os
import tensorflow as tf
import pandas as pd
from tensorflow.keras.models import Model, load_model
from tensorflow.keras import preprocessing

komoran = Komoran()


def SearchingMBTI(nouns, TargetMBTI, FileTitle):
    for item in nouns:
        # MBTI.csv 파일 읽기
        mbti_data = pd.read_csv(FileTitle)

        # MBTI.csv에서 단어 확인 및 해당하는 값 가져오기
        matching_row = mbti_data[mbti_data["word"] == item]

        if not matching_row.empty:
            mbti_value = matching_row.iloc[0]["count"]
            TargetMBTI = TargetMBTI + mbti_value
        else:
            pass

        return TargetMBTI


def ChatBot(InputText):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

    # 입력된 채팅
    # InputText = "오늘 사람을 하나 묻었다."
    print(f"입력된 메세지: {InputText}")
    ReturnMessage = ""

    # 감정 인식 ---------------------------------------------------------------------------------------
    # 1 데이터 읽어오기
    train_file = "chatbot_data.csv"
    data = pd.read_csv(train_file, delimiter=",")
    features = data["Q"].tolist()

    features.append(InputText)

    # 2 단어 인덱스 시퀀스 벡터
    corpus = [preprocessing.text.text_to_word_sequence(text) for text in features]

    tokenizer = preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts(corpus)  # fit_on_texts() 메서드는 문자 데이터를 입력받아서 리스트의 형태로 변환합니다.
    sequences = tokenizer.texts_to_sequences(corpus)

    MAX_SEQ_LEN = 15
    padded_seqs = preprocessing.sequence.pad_sequences(
        sequences, maxlen=MAX_SEQ_LEN, padding="post"
    )

    # 4 감정 분류 CNN 모델 불러 오기
    os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
    model = load_model("cnn_model.keras")

    picks = [len(features) - 1]

    try:
        predict = model.predict(padded_seqs[picks])
        predict_class = tf.math.argmax(predict, axis=1)
        emo = predict_class.numpy()[0]
    except:
        emo = 0

    emotions = {0: "보통", 1: "부정", 2: "긍정"}

    # MBTI 분석 -----------------------------------------------------------------------------------------
    # 명사만 추출
    nouns = komoran.nouns(InputText)

    # 변수 초기화
    MBTI_user = ""
    MBTI_E = 0
    MBTI_S = 0
    MBTI_T = 0
    MBTI_J = 0

    MBTI_I = 0
    MBTI_N = 0
    MBTI_F = 0
    MBTI_P = 0

    # E 성향 검사 ------------------------------------------
    MBTI_E = SearchingMBTI(nouns, MBTI_E, "MBTI_E.csv")
    # S 성향 검사 ------------------------------------------
    MBTI_S = SearchingMBTI(nouns, MBTI_S, "MBTI_S.csv")
    # T 성향 검사 ------------------------------------------
    MBTI_T = SearchingMBTI(nouns, MBTI_T, "MBTI_T.csv")
    # J 성향 검사 ------------------------------------------
    MBTI_J = SearchingMBTI(nouns, MBTI_J, "MBTI_J.csv")

    # I 성향 검사 ------------------------------------------
    MBTI_I = SearchingMBTI(nouns, MBTI_I, "MBTI_I.csv")
    # N 성향 검사 ------------------------------------------
    MBTI_N = SearchingMBTI(nouns, MBTI_N, "MBTI_N.csv")
    # F 성향 검사 ------------------------------------------
    MBTI_F = SearchingMBTI(nouns, MBTI_F, "MBTI_F.csv")
    # P 성향 검사 ------------------------------------------
    MBTI_P = SearchingMBTI(nouns, MBTI_P, "MBTI_P.csv")

    # 결과 출력 --------------------------------------------
    if MBTI_E > MBTI_I:
        MBTI_user = MBTI_user + "E"
    elif MBTI_I > MBTI_E:
        MBTI_user = MBTI_user + "I"
    else:  # 정확히 반반인 경우
        MBTI_user = MBTI_user + "_"

    if MBTI_S > MBTI_N:
        MBTI_user = MBTI_user + "S"
    elif MBTI_N > MBTI_S:
        MBTI_user = MBTI_user + "N"
    else:  # 정확히 반반인 경우
        MBTI_user = MBTI_user + "_"

    if MBTI_T > MBTI_F:
        MBTI_user = MBTI_user + "T"
    elif MBTI_F > MBTI_T:
        MBTI_user = MBTI_user + "F"
    else:  # 정확히 반반인 경우
        MBTI_user = MBTI_user + "_"

    if MBTI_J > MBTI_P:
        MBTI_user = MBTI_user + "J"
    elif MBTI_P > MBTI_J:
        MBTI_user = MBTI_user + "P"
    else:  # 정확히 반반인 경우
        MBTI_user = MBTI_user + "_"

    ReturnMessage = ReturnMessage + f"당신의 MBTI는 {MBTI_user}입니다.\n"
    ReturnMessage = ReturnMessage + f"감정 : {emotions[emo]}\n"
    ReturnMessage = ReturnMessage + "=" * 50 + "\n"

    # 네이버 검색 API ----------------------------------------------------------------------------------
    # 네이버 검색 API 인증 정보
    client_id = "CuOIdXJEpXjVP_pHajYc"
    client_secret = "jezGrtdSa3"
    query = "MBTI " + MBTI_user

    if emotions[emo] == "부정":
        query = query + ' "스트레스"'  # 일상, 궁합, 스트레스
        # API 호출 URL
        url = f"https://openapi.naver.com/v1/search/blog?query={query}"

        # API 요청 헤더 설정
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        }

        # API 호출 및 응답 받아오기
        response = requests.get(url, headers=headers)
        data = response.json()

        # 검색 결과 출력
        if "items" in data:
            for idx, item in enumerate(data["items"][:3], start=1):
                title = item["title"]
                link = item["link"]
                ReturnMessage = ReturnMessage + f"Result {idx}\n"
                ReturnMessage = ReturnMessage + f"Title: {title}\n"
                ReturnMessage = ReturnMessage + f"Link: {link}\n"
                ReturnMessage = ReturnMessage + "=" * 50 + "\n"
        else:
            ReturnMessage = ReturnMessage + "검색 결과가 없습니다."
    elif emotions[emo] == "긍정":
        query = query + ' "궁합"'  # 일상, 궁합, 스트레스
        # API 호출 URL
        url = f"https://openapi.naver.com/v1/search/blog?query={query}"

        # API 요청 헤더 설정
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        }

        # API 호출 및 응답 받아오기
        response = requests.get(url, headers=headers)
        data = response.json()

        # 검색 결과 출력
        if "items" in data:
            for idx, item in enumerate(data["items"][:3], start=1):
                title = item["title"]
                link = item["link"]
                ReturnMessage = ReturnMessage + f"Result {idx}\n"
                ReturnMessage = ReturnMessage + f"Title: {title}\n"
                ReturnMessage = ReturnMessage + f"Link: {link}\n"
                ReturnMessage = ReturnMessage + "=" * 50 + "\n"
        else:
            ReturnMessage = ReturnMessage + "검색 결과가 없습니다."
    else:
        query = query + ' "일상"'  # 일상, 궁합, 스트레스
        # API 호출 URL
        url = f"https://openapi.naver.com/v1/search/blog?query={query}"

        # API 요청 헤더 설정
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        }

        # API 호출 및 응답 받아오기
        response = requests.get(url, headers=headers)
        data = response.json()

        # 검색 결과 출력
        if "items" in data:
            for idx, item in enumerate(data["items"][:3], start=1):
                title = item["title"]
                link = item["link"]
                ReturnMessage = ReturnMessage + f"Result {idx}\n"
                ReturnMessage = ReturnMessage + f"Title: {title}\n"
                ReturnMessage = ReturnMessage + f"Link: {link}\n"
                ReturnMessage = ReturnMessage + "=" * 50 + "\n"
        else:
            ReturnMessage = ReturnMessage + "검색 결과가 없습니다."

    return ReturnMessage


InputText = "길고 긴 연애의 끝은 가정과 책임이었다."
message = ChatBot(InputText)
print(message)
