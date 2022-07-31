# RECOS

- recos - 화장품 추천 서비스
- 프론트(Vue) 작성 git URL : https://github.com/chljidn/cos_project_f
 <br><br>

## Introduction
- 화장품 성분에 대한 이미지가 업로드되면 이미지에서 성분을 읽어낸 후, 기존 데이터베이스에 존재하는 화장품 목록에서 성분표가 유사한 화장품을 추천하는 서비스 입니다.
- 스크래핑은 현재 서비스 중인 특정 업체의 사이트에서 스크래핑되며, 때문에 스크래핑 코드에서 스크래핑 되는 업체의 url은 원격저장소에 제공되지 않습니다. 또한 스크래핑된 데이터는 상업적인 용도로 사용되지 않습니다.
- cos : 프로젝트 디렉토리(settings.py, celery.py)
- app : 화장품 데이터 스크래핑 및 업로드, 화장품 성분 이미지업로드, 화장품 추천, 화장품 리뷰, 좋아요 기능
- common : 로그인/로그아웃, 회원가입/탈퇴, 내 정보 수정, Q&A
 <br><br>
 
## [사용자 기능 및 관련 링크](https://github.com/chljidn/docker/wiki)
- 사용자 기능에 관한 목록은 'wiki'에 작성되어 있습니다.
- 위 링크를 통해서도 확인하실 수 있습니다.
 <br><br>
 
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
 <br><br>
 
## 이슈 및 제작과정에 대한 고민들
- [화장품 추천까지의 시간지연을 celery로 극복할 수 있을까?](https://chljidn-django.tistory.com/7)
- [스크래핑](https://chljidn-django.tistory.com/8)
- [회원 인증(session, jwt)](https://chljidn-django.tistory.com/9)
 <br><br>
 
## 애플리케이션 실행 영상(영상을 클릭하시면 더 크게 보실 수 있습니다.)
### 영상작업은 현재 진행 중입니다. 각 기능에 대한 영상은 추후 차례대로 업로드 될 예정입니다.
- 회원가입 및 로그인
<img src="https://github.com/chljidn/docker/blob/master/signup_login.gif" width="300px" height="200px" >

- 화장품 리스트
<img src="https://github.com/chljidn/docker/blob/master/cosmetic_list_detail.gif" width="300px" height="200px">

- 화장품 추천
<img src="https://github.com/chljidn/docker/blob/master/recommend_app.gif" width="300px" height="200px">

- 좋아요 기능
<img src="https://github.com/chljidn/docker/blob/master/like_app.gif" width="300px" height="200px">

## DB ERD
![](https://github.com/chljidn/docker/blob/master/cos_erd.png)
