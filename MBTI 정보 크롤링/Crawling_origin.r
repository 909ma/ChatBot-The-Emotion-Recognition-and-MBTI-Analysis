# 필요한 패키지 로드
library(rvest)
library(stringr)
library(tidyverse)
library(dplyr)
library(rvest)

# 딜레이 시간 설정
times <- 2

# 데이터 프레임 생성
data_full <- data.frame()

# 갤러리 이름 설정
# enfj: Number 18386 ~ 19386의 약 1,000개 이하의 게시글 크롤링
# enfp: Number 23991 ~ 24987의 약 1,000개 이하의 게시글 크롤링
# entj: Number 13970 ~ 14970의 약 1,000개 이하의 게시글 크롤링
# entp: Number 617509 ~ 618509의 약 1,000개 이하의 게시글 크롤링
# ESFP: Number 6168 ~ 7168의 약 1,000개 이하의 게시글 크롤링
# esfj: Number 6371 ~ 7371의 약 1,000개 이하의 게시글 크롤링
# estj: Number 7671 ~ 8671의 약 1,000개 이하의 게시글 크롤링
# ESTP: Number (게시글 넘버 직접 지정)
# INFJ: Number 115767 ~ 116767의 약 1,000개 이하의 게시글 크롤링
# infp: Number 480578 ~ 481578의 약 1,000개 이하의 게시글 크롤링
# intj: Number 
# INTP: Number 
# ISFJ: Number 
# ISFP: Number 80611 ~ 81611의 약 1,000개 이하의 게시글 크롤링
# ISTJ: Number 21170 ~ 22170의 약 1,000개 이하의 게시글 크롤링
# ISTP: Number 176435 ~ 177435의 약 1,000개 이하의 게시글 크롤링
# INTP: 갤러리 폐쇄로 인해 데이터 추출 불가
# ISFJ: Number 
gallery <- "isfj" # R 언어 문법에 익숙하지 못해 일일이 바꿔줘야 된다.

# URL 설정
url <- paste0("https://gall.dcinside.com/mgallery/board/lists?id=", gallery)

# HTML 페이지 가져오기
html_page <- read_html(url)

# 원하는 정보 추출
gall_num <- html_text(html_nodes(html_page, ".gall_num"))

# 가장 큰 숫자 찾기
max_num <- max(as.numeric(gall_num))

# 게시글 범위 설정
EndNumber <- max_num
StartNumber = EndNumber - 1000

# 게시판 글 숫자 만큼의 루프문 생성
for (i in StartNumber:EndNumber) {
  
  # URL 지정
  url_intp <- paste0("https://gall.dcinside.com/mgallery/board/view/?id=",gallery,"&no=", i)
  
  # read html page #
  tryCatch({
    html_page <- read_html(url_intp)
  }, error = function(e) {
    html_page <- NULL
  })
  # read html page #

  # 404 에러가 발생하는 경우 다음 루프를 진행
  if (is.null(html_page)) {
    print("error 404! next loop!")
    Sys.sleep(times)
    next
  }

  #### title 추출 ####
  html_title <- html_text(html_nodes(html_page, '.title_subject'))

  #### contents 추출 #### 
  html_content1 <- html_nodes(html_page, '.writing_view_box')
  html_content2 <- html_nodes(html_content1, 'div')

  html_content3 <- str_replace_all(html_text(html_content2)[4], "\r", "")

  if (is.na(html_content3)){
    html_content3 <- str_replace_all(html_text(html_content2)[3], "\r", "")
  }

  if (is.na(html_content3)){
    html_content3 <- str_replace_all(html_text(html_content2)[2], "\r", "")
  }

  html_content4 <- str_replace_all(html_content3, "\t", "")
  html_content_fin <- str_replace_all(html_content4, "\n", "")

  # 중복된 내용은 건너뜀
  if (i > StartNumber && html_content_fin == data_full$content[nrow(data_full)]) {
    next
  }

  # 데이터 프레임 병합
  data <- data.frame(num = i, title = html_title, content = html_content_fin)

  # 데이터 프레임 병합
  data_full <- bind_rows(data_full, data)

  # 딜레이 지정
  Sys.sleep(times)

  print(i)

}

# 현재 R 스크립트 파일의 경로 알아내기
script_path <- dirname(sys.frame(1)$ofile)

# 결과파일 저장
FileTitle <- paste0(gallery, "_source_txt.csv")
output_file <- file.path(script_path, FileTitle)
write.csv(data_full, output_file)

