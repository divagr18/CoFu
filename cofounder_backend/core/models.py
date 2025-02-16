from django.db import models

class Startup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Competitor(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class MarketSignal(models.Model):
    source = models.CharField(max_length=255)  
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  

    def __str__(self):
        return f"{self.source} - {self.query} - {self.timestamp}"


class ScrapedReview(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)  
    review_text = models.TextField()
    rating = models.FloatField(blank=True, null=True)  
    date_published = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Review for {self.competitor.name} from {self.source}"
        
class UserPrompt(models.Model):  
    text = models.TextField()

    def __str__(self):
        return self.text