from django.db import models


# Create your models here.
class Server(models.Model):
    type = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=50)
    domain_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    server_name = models.CharField(max_length=50)
    client_name = models.CharField(max_length=50)
    folder_name = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class InitNetworkInfo(models.Model):
    type = models.CharField(max_length=50)
    eth_ip_address = models.CharField(max_length=50)
    eth_mask = models.CharField(max_length=50)
    wlan_ip_address = models.CharField(max_length=50)
    wlan_mask = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class UpdatedNetworkInfo(models.Model):
    type = models.CharField(max_length=50)
    eth_ip_address = models.CharField(max_length=50)
    eth_mask = models.CharField(max_length=50)
    wlan_ip_address = models.CharField(max_length=50)
    wlan_mask = models.CharField(max_length=50)
    wlan_gateway = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class OtherSettingsInfo(models.Model):
    type = models.CharField(max_length=50)
    uprating_rate_min = models.CharField(max_length=50)
    uprating_rate_sec = models.CharField(max_length=50)
    account_id = models.CharField(max_length=50)
    account_pw = models.CharField(max_length=50)
    auth_product = models.CharField(max_length=50)
    auth_serial = models.CharField(max_length=50)
    auth_result = models.BooleanField(default=False)

    def __str__(self):
        return self.type
