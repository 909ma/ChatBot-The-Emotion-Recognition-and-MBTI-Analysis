# 말뭉치 분석 및 명사 추출 패키지 로드
from konlpy.tag import Kkma

# 함수 설정
kkma = Kkma()

# 기타 패키지 로드
import pandas as pd
import os
import csv
from collections import Counter


# 글 내용이 없는 경우 nan이 리턴되는데 이를 방지해주는 함수
def isNaN(string):
    return string != string


# entp,
MBTI = "entp 진행이 안 됨"
InputTitle = f"./MBTI Source/{MBTI}_source_txt.csv"
OutputTitle = f"{MBTI}_weight.csv"

# 작업 디렉토리 지정
os.chdir("./")
# 데이터 입력 포맷 결정
data = pd.read_csv(InputTitle, encoding="UTF-8")
print(f"{InputTitle[14:]} 읽기 완료")
# 제목과 내용 분리
title = data.title
content = data.content

result = []
print("제목 시작")
for i in title:
    check = isNaN(i)
    if check == True:
        continue
    title_part = kkma.nouns(i)  # 각 제목으로부터 명사 추출
    result.extend(title_part)  # 각 제목으로부터 명사 출력 결과 저장
    print(".", end="")

print("\n내용 시작")
for i in content:
    check = isNaN(i)
    if check == True:
        continue
    content_part = kkma.nouns(i)  # 각 내용으로부터 명사 추출
    result.extend(content_part)  # 각 내용으로부터 명사 저장
    print(".", end="")

print("\n정렬 중")
# 명사 오름차순으로 정렬
result = sorted(result, reverse=False)

# 단어 빈도수 세기
word_count = Counter(result)

# 출력 파일 쓰기
with open(OutputTitle, "w", newline="", encoding="UTF-8") as myfile:
    wr = csv.writer(myfile)
    wr.writerow(["word", "count"])  # 헤더 추가
    for word, count in word_count.items():
        wr.writerow([word, count])

print(f"{OutputTitle} 저장 완료")
