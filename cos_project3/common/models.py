from django.db import models
from django.apps import apps

# Create your models here.
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone

# -------- User 모델 -----------------------------------------------------------------------------------------
# UserManager의 구성을 cos_project2 보다 좀 더 기존의 UserManager의 값에 가깝게 구성함.
class UserManager(BaseUserManager):
    def _create_user(self, username, email, birth, sex, password, **extra_fields):
        if not email:
            raise ValueError('이메일 주소는 필수로 입력되어야 합니다.')
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        #username = GlobalUserModel.normalize_username(username), # 이거 넣으면 ('cjw',) 이런식으로 저장되는데 이유를 좀 찾아봐야 할듯...
        user = self.model(
            email=self.normalize_email(email), # 이메일의 도메인 부분을 소문자로 처리한다(BaseUserManager에 정의된 함수)
            username = username,
            birth=birth,
            sex=sex,
            **extra_fields
        )
        user.set_password(password) # make_password 한 결과를 뽑아낸다. AbstractBaseUser에 정의된 함수이다
        user.save(using=self.db)

        return user

    def create_user(self, username, email=None, birth=None, sex=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, birth, sex, password, **extra_fields)


    def create_superuser(self, username, email, birth, sex, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(username, email, birth, sex, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Email',
        max_length=100,
        unique=True
    )
    # username 부분은 django의 github에서 abstractuser모델의 username에서 그대로 가져옴
    # 아이디로 입력받은 값이 사용 가능한 값인지 확
    username_validator = UnicodeUsernameValidator()
    username=models.CharField(
        _('username'),
        max_length=100,
        unique=True,
        help_text=_('Required. 100 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("이 아이디는 이미 존재합니다."),
        },
    )

    birth=models.DateField(
        auto_now=False,
        unique=False,
        max_length=50,
    )

    sex = models.CharField(
        max_length=10,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(
        verbose_name=_('Date joined'),
        default=timezone.now
    )

    objects= UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username' # username을 id로 사용한다.
    REQUIRED_FIELDS = ['email','birth', 'sex']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined',)
        #db_table = 'user'

    #def __str__(self):
    #    return self.username

    def get_full_name(self):
        return self.username
    def get_short_name(self):
        return self.username

    #def is_staff(self):
    #    "Is the user a member of staff?"
        # Simplest possible answer: All superusers are staff
    #    return self.is_superuser

    get_full_name.short_description = _('Full name')

# Q&A 게시판 모델
class Qa(models.Model):
    postname = models.CharField(max_length=200)
    content = models.TextField(default='')
    password = models.CharField(max_length=30, null=True)
    # user 테이블의 기본키인 id를 외래키로 사용하게 된다.
    # 한 유저당 여러 개의 Q&A를 작성할 수 있으므로 기본키는 따로 존재하고 외래키는 기본키로 쓰이지 않는다.
    # user(1) --- qa(N)
    qa_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='qa_user', default=None)
    qaDate = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.postname

# 리플 기능
class QaReple(models.Model):
    content = models.TextField()
    # 하나의 qna에 여러 개의 리
    qa = models.ForeignKey(Qa, on_delete=models.CASCADE, db_column='qa')
    # 한 명의 유저가 여러 개의 리플을 남길 수 있음
    # 유저가 탈퇴해도 리플은 삭제되지 않는다.
    repleUser = models.ForeignKey(User, on_delete=models.PROTECT, db_column='user')
    repleDate = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.content