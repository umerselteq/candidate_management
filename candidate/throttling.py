from rest_framework.throttling import UserRateThrottle


class CustomRateThrottle(UserRateThrottle):
    rate = 'custom'
