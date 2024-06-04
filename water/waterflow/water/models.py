from django.db import models

class Node(models.Model):
    NODE_TYPE_CHOICES = [
        ('tank', 'Tank'),
        ('valve', 'Valve'),
        ('outlet', 'Outlet'),
        # Add other types as needed
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=NODE_TYPE_CHOICES, default='tap')
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Edge(models.Model):
    source = models.ForeignKey(Node, related_name='source', on_delete=models.CASCADE)
    target = models.ForeignKey(Node, related_name='target', on_delete=models.CASCADE)
    length = models.FloatField()
    flow_rate = models.FloatField()

    def __str__(self):
        return f'{self.source.name} -> {self.target.name}'
    
class NetworkComponent(models.Model):
    name = models.CharField(max_length=100)
    component_type = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name
