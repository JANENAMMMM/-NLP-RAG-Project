# RAG 통합 최종 버전

다현님, 나현님, 사용자 작업을 통합한 RAG (Retrieval Augmented Generation) 시스템입니다.

## 주요 기능

- **PDF 본문/부칙 분리**: 이화여대 학칙 PDF의 본문과 부칙을 자동으로 분리하여 청킹
- **표 데이터 처리**: CSV 파일을 문장으로 변환하여 벡터 DB에 통합
- **FAISS 벡터 스토어**: Upstage Embeddings를 사용한 효율적인 유사도 검색
- **RAG 파이프라인**: Upstage Solar-pro2 LLM을 활용한 질의응답 시스템

## 파일 구조

- `RAG_통합_최종.ipynb`: 통합 RAG 노트북 (메인 파일)
- `extract_tables.py`: PDF에서 표 데이터 추출 스크립트
- `2019_quota.csv`: 2019학년도 입학정원 데이터
- `degrees.csv`: 학사학위의 종류 데이터
- `contract_dept.csv`: 계약학과 설치·운영 데이터

## 사용 방법

1. 필요한 라이브러리 설치:
```bash
pip install langchain_upstage langchain_community langchain-openai openai pdfplumber pandas faiss-cpu
```

2. Upstage API Key 설정:
   - 노트북 내에서 `UPSTAGE_API_KEY` 환경 변수 설정

3. PDF 및 CSV 파일 준비:
   - `ewha.pdf`: 이화여대 학칙 PDF 파일
   - CSV 파일들: `extract_tables.py` 실행하여 생성

4. 노트북 실행:
   - `RAG_통합_최종.ipynb`의 셀들을 순서대로 실행

## 주요 컴포넌트

### 1. PDF 처리
- **본문/부칙 분리**: "부칙" 키워드 기준으로 자동 분리
- **청킹**: RecursiveCharacterTextSplitter 사용 (chunk_size=1200, chunk_overlap=300)

### 2. CSV 표 데이터 처리
- **학위 정보**: 각 학과의 학위 종류를 문장으로 변환
- **입학정원 정보**: 2019학년도 입학정원을 구조화된 문장으로 변환
- **계약학과 정보**: 계약학과 설치·운영 정보를 문장으로 변환

### 3. 벡터 스토어
- **임베딩 모델**: Upstage Solar-embedding-1-large
- **벡터 DB**: FAISS 사용
- **통합 KB**: 본문 텍스트 + 부칙 텍스트 + CSV 표 데이터

### 4. RAG 파이프라인
- **LLM**: Upstage Solar-pro2
- **검색 방식**: Top-k=5 유사도 검색
- **프롬프트**: 컨텍스트 기반 질의응답

## 참고사항

- Windows 한글 경로 문제: 벡터 DB는 임시 디렉토리에 저장됩니다
- CSV 파일 생성: `python extract_tables.py` 실행하여 PDF에서 표 추출

## 작업 기여자

- **다현님**: 본문/부칙 분리, 학위 문장 생성, 본문 청킹
- **나현님**: UpstageDocumentParseLoader 활용 (참고)
- **사용자**: 표 데이터 처리 및 벡터화

