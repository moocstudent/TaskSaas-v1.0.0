from web.models import UserInfo
from decimal import Decimal

# 给人员增加进取分数，进取分数用来获取一些荣誉及兑换
def compute_forward_score(user_id=None, user=None, forward_score=Decimal('0.00')):
    user = user
    if not user:
        user = UserInfo.objects.filter(id=user_id).first()
    if not user:
        return None
    if type(forward_score) != Decimal():
        forward_score = Decimal(forward_score)
    user.forward_score = user.forward_score + (forward_score)
    user.save()
    return 1

