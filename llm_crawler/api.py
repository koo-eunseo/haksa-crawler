from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from llm_crawler.crawler import perform_login_and_fetch
from llm_crawler.parser import parse_dl_main
from llm_crawler.enums import CrawlStatus
from llm_crawler.dto import LoginInfo

app = FastAPI(title="LLM Crawler API", version="1.0")

class LoginRequest(BaseModel):
    user_id: str = Field("string", description="학번 또는 사용자 ID")
    password: str = Field("string", description="로그인 비밀번호")

class CourseSummaryResponse(BaseModel):
    cdt: float
    type_name: str
    curi_no: str
    curi_nm: str
    dept_m_alias:str   # 학과
    year:str          # 년도
    smt_cd:str

@app.post(
    "/crawl",
    response_model=list[CourseSummaryResponse],
    summary="학사정보 크롤링 후 요약 반환"
)
def crawl(req: LoginRequest):
    # 1) 크롤링 수행
    login = LoginInfo(
    user_id=req.user_id,
    password=req.password
)
    status, raw_data = perform_login_and_fetch(login)
    if status is not CrawlStatus.SUCCESS or not isinstance(raw_data, dict):
        # 2) 실패 시 500 에러 반환
        raise HTTPException(status_code=400, detail=raw_data)

    # 3) 파싱
    summaries = parse_dl_main(raw_data)
    # 4) Pydantic으로 직렬화
    return [CourseSummaryResponse(
        cdt=s.cdt,
        type_name=s.type_name,
        curi_no=s.curi_no,
        curi_nm=s.curi_nm,
        dept_m_alias=s.dept_m_alias,   # 학과
        year=s.year,           # 년도
        smt_cd=s.smt_cd

    ) for s in summaries]
