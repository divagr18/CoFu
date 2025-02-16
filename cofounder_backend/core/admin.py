from django.contrib import admin
from .models import Competitor, MarketSignal, ScrapedReview, Startup

admin.site.register(Competitor)
admin.site.register(MarketSignal)
admin.site.register(ScrapedReview)
admin.site.register(Startup)