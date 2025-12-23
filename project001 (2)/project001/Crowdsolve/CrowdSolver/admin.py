from django.contrib import admin
from .views import Member,Secretary
from .models import Categoryname,Issues,Solution,Vote
class Memberdata(admin.ModelAdmin):
    list_display = ('memberName', 'memberMail', 'memberContact','memberPassword','memberAddress','memberFlatnumber')


admin.site.register(Member, Memberdata)
admin.site.register(Categoryname)
admin.site.register(Issues)
admin.site.register(Secretary)
admin.site.register(Solution)
admin.site.register(Vote)


class SecretaryAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')

  




