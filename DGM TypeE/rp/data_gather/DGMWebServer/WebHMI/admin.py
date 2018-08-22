from django.contrib import admin
from WebHMI.models import Server, InitNetworkInfo, UpdatedNetworkInfo, OtherSettingsInfo


# Register your models here.

admin.site.register(Server)
admin.site.register(InitNetworkInfo)
admin.site.register(UpdatedNetworkInfo)
admin.site.register(OtherSettingsInfo)
