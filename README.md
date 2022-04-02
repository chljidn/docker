# RECOS

- recos - 화장품 추천 서비스
- 프론트(Vue) 작성 git URL : https://github.com/chljidn/cos_project_f
## Introduction

- 화장품 성분에 대한 이미지가 업로드되면 이미지에서 성분을 읽어낸 후, 기존 데이터베이스에 존재하는 화장품 목록에서 성분표가 유사한 화장품을 추천하는 서비스 입니다.
- 스크래핑은 현재 서비스 중인 특정 업체의 사이트에서 스크래핑되며, 때문에 스크래핑 코드에서 스크래핑 되는 업체의 url은 원격저장소에 제공되지 않습니다. 또한 스크래핑된 데이터는 상업적인 용도로 사용되지 않습니다.
- cos : 프로젝트 디렉토리(settings.py, celery.py)
- app : 화장품 데이터 스크래핑 및 업로드, 화장품 성분 이미지업로드, 화장품 추천
- common : 로그인/로그아웃, 회원가입/탈퇴, 내 정보 수정, Q&A

## 기술 스택
- python 3.8
- MariaDB
- Docker
- requests_html
- TesseractOCR
- Redis
- Celery
- AWS EC2
- Gunicorn
- Nginx

## 이슈 및 해결과정
- 화장품 추천까지의 시간지연을 celery로 극복할 수 있을까?
- 스크래핑
