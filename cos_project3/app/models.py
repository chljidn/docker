from django.db import models
from django.conf import settings
from common.models import User

class ImageUpload(models.Model):
    title = models.CharField(max_length = 100)
    pic = models.ImageField(upload_to='imageupload') #저장 디렉터리 : media/imageupload
    # created_at = models.DateTimeField()
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # image_size = models. ??



class Cos(models.Model):
    id = models.IntegerField(primary_key=True)
    brand = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    ingredient = models.TextField(blank=True, null=True)
    prdname = models.TextField(blank=True, null=True)
    price = models.TextField(blank=True, null=True)
    # 좋아요 기능을 위한 컬럼
    # User 테이블과 N:M 관계를 갖는다.
    category = models.TextField(blank=True, null=True)
    like = models.ManyToManyField(User, related_name='like', blank=True)

    def __str__(self):
        return self.prdname

class CosReviewModel(models.Model):
    reviewName = models.CharField(max_length=500, blank=False)
    reviewImage = models.ImageField(blank=True, upload_to='reviewImages')
    reviewContent = models.TextField(blank=True)
    reviewUser = models.ForeignKey(User, on_delete=models.PROTECT)
    reviewCos = models.ForeignKey(Cos, on_delete=models.CASCADE)
    def __str__(self):
        return self.reviewName