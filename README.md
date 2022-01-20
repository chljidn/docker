# RECOS

- recos - 화장품 추천 서비스
- 프론트(Vue) 작성 git URL : https://github.com/chljidn/cos_project_f
## Introduction

- 화장품 성분에 대한 이미지가 업로드되면 이미지에서 성분을 읽어낸 후, 기존 데이터베이스에 존재하는 화장품 목록에서 성분표가 유사한 화장품을 추천하는 서비스 입니다.
- 추천 알고리즘은 코사인 유사도가 사용됩니다.
- 이미지에서 성분을 읽어내는 모듈로 tesseract OCR이 사용됩니다.
- 스크래핑은 현재 서비스 중인 특정 업체의 사이트에서 스크래핑되며, 때문에 스크래핑 코드에서 스크래핑 되는 업체의 url은 원격저장소에 제공되지 않습니다. 또한 스크래핑된 데이터는 상업적인 용도로 사용되지 않습니다.
- cos : 프로젝트 디렉토리(settings.py, celery.py)
- app : 화장품 데이터 스크래핑 및 업로드(scraping.cos_scraping.py), 화장품 성분 이미지업로드(views.image_upload), 화장품 추천(recommend.py)
- common : 인증(회원가입(views.signup_views.py) 및 로그인/로그아웃), Q&A(views.qa_views.py)
- 요구사항은 requirements.txt로 제공됩니다.

## Docker 
* Docker-Compose를 사용하여 컨테이너 어플리케이션을 정의 및 관리한다.
* Docker 내에서 사용가능한 버전의 문제로 djangorestframework-simplejwt==4.4.0, PyJWT==1.7.1 버전을 사용한다. 
* docker-compose를 통해서 각각의 컨테이너를 완성한 후에 Dockerfile를 통해서 생성한 컨테이너들 세팅한다.
* 디렉토리 구조: 
```bash
docker
   ├── nginx
   │     ├── Dockerfile
   │     ├── nginx.conf
   │     └── nginx-g.conf
   ├── cos_pcoject3
   │     ├── Dockerfile
   │     ├── cos
   │     ├── app
   │     ├── common
   │     ├── manage.py
   │     └── ...
   └── docker-compose.yml
``` 

## API - REST API(djangorestframework)

### Rest 
* API 서버로의 요청 및 API 서버의 응답은 HTTP 프로토콜을 따른다. 
* HTTP method는 Get, Post, Put, Delete가 사용된다.
* 각 API를 구분하는 요소로 URI를 사용한다.
* 현재 프로젝트의 프론트 페이지와는 axios를 통해서 데이터를 통신한다.
          
### app directory

#### 스크래핑 - requests_html, celery
   > worker 실행
   
    celery –A cos worker –l INFO –P eventlet     
   
   > beat 실행(스케줄링을 위한 beat)
   
    celery –A cos beat
    
* 스크래핑하는 url은 실제 서비스를 운용하는 법인의 주소이므로 setting 정보와 함께 분리되어 있으며, 원격저장소에는 제공되어 있지 않습니다. 
* cos는 settings.py가 존재하는 cos 디렉토리를 의미한다.
* 현재로는 스크래핑의 스케줄링에 사용하지만, 추후 이미지를 업로드하고 화장품이 추려져 나오는 과정에서 비동기 작업 큐를 사용하여 추천 알고리즘이 진행되는 과정에서도 다른 작업을 할 수 있도록 추가할 예정
    
    
#### 이미지 업로드 및 추천 알고리즘 - pytesseract, cv2, cosine similarity
* 업로드 된 이미지에서 pytesseract(OCR)를 통해서 성분 글자 추출.
* cosine similarity를 통해서 유사도가 제일 높은 10개를 순서대로 추출 후 반환
* 기존에 존재하는 데이터에서 코사인 유사도를 측정하며, 그 중에 가장 유사도가 높은 10개를 반환하므로 반환되는 코사인 유사도가 모두 높음을 보장하지 않음.


### common directory

#### 인증(회원가입 및 로그인/ 로그아웃) - JsonWebToken
1. 세션 방식(Session Authentication)
2. 쿠키 방식(세션 쿠키, 지속 쿠키)
3. 토큰 방식(Token Authentication, Json Web Token Authentication)
* 토큰 방식 중 JsonWebTokenAuthentication(jwt)를 사용한다. python과 Django에는 jwt에 대해서 python에는 PyJWT모듈이 있으며, Django의 rest_framework에는 simplejwt가 존재한다.
* jwt는 토큰을 저장할 필요가 없으며, access 토큰의 기간이 만료되면 refresh 토큰을 통해서 다시 발급이 가능하므로 access의 토큰 만료기간을 짧게하여 보안에 대한 대비를 할 수 있다.
* rest_framework의 simplejwt를 이용

    > simplejwt 설치 및 settings.py 추가

        pip install djangorestframework-simplejwt

        # settings.py
        INSTALLED_APPS = [
            ...
            'rest_framework_simplejwt',
        ]
        
     > app/serializers.py

        # 기존 serializer 상속 후 수정. username이 response 값에 추가된다.
        class signup_login(TokenObtainPairSerializer):
            def validate(self, attrs):
                data = super().validate(attrs)
                refresh = self.get_token(self.user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)
                data['username'] = self.user.username
                return data
                
    > app/views/auth_views.py

        # 기존의 TokenObtatinPairView의 post를 오버라이딩하여, set_cookie를 통해서 토큰을 set_cookie 헤더에 담아보낸다.
        # 코딩 참고 : https://stackoverflow.com/questions/66197928/django-rest-how-do-i-return-simplejwt-access-and-refresh-tokens-as-httponly-coo
        class MyTokenObtainPairView(TokenObtainPairView):
            ...
            if access is not None:
                      response = Response({}, status=200)
                      response.set_cookie('token', access, httponly=True)
                      response.set_cookie('refresh', refresh, httponly=True)
                      response.set_cookie('email', username, httponly=True)
            ...

## MTV(models, template, views)
- django는 mvc 패턴이 아닌 mtv 패턴이다. mvc 패턴의 view가 template로 대체되고, controller가 view로 대체된다. 
- api 기능은 views.py

### views (views of rest_framework - APIView, Mixins, genericsAPIView, ViewSets)
* view는 rest_framework상의 구현된 view를 사용한다.
* 프로젝트에서는 평균적으로 viewset, APIView로 이루어져 있다.
* viewsets의 router 기능을 사용. 

1) APIView 
    - 가장 기본적인 apiview. CBV에 대응.
2) Mixins   
    - CRUD 기능을 미리 구현해놓은 상태로 제공.
    -  serializer 중복에 대해서 한번만 선언하여 처리할 수 있도록 함.
    -  RetrieveModelMixin(get) ListModelMixin(get), CreateModelMixin(post), UpdateModelMixin(put), DestroyModelMixin(delete)
3) generic views 
    - mixin의 경우, 한 class내에 여러 mixin을 상속받아야하기 때문에 불편할 수 있으므로 이를 각  CRUD에 대한 경우의 수를 모두 만들어 놓고 상속받을 수 있도록 함.
    - ex) generics.RetrieveUpdateAPIView : get/put
    - generics.RetrieveUpdateDestoryAPIView : get / put/ delete
4) ViewSets 
    - 라우팅 기능을 제공한다. 
    - queryset을 한번만 지정하여 사용할 수 있다. 
    - viewset에 존재하는 함수는 mixin의 함수들을 상속받아 구성되어 있다.
    - retrieve(get), create(post), update(put), destroy(delete)

## Database
* 기본적으로 django는 sqlite3를 사용한다.
* 공용 데이터베이스가 따로 마련되어 있지 않으므로 cos_project3/recos_data.csv를 통해서 각각 데이터를 데이터베이스에 구축하여 사용하여야 한다. 
* 현재 프로젝트는 MariaDB를 사용하지만, settings.py에 데이터베이스 환경은 따로 설정되어 있으므로 굳이 MariaDB가 아닌 각각 원하는 DB를 사용할 수 있다.
* 데이터베이스는 docker로 구성하지 않으며 추구 aws상에 구축할 예정이며, 상업적으로는 사용되지 않는다. 


