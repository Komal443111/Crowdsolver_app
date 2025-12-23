from django.db import models
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.
class Member(models.Model):
    memberName = models.CharField((""), max_length=50)
    memberMail = models.EmailField((""), max_length=254)
    memberContact = models.CharField((""), max_length=50)
    memberPassword = models.CharField((""), max_length=50)
    memberAddress = models.CharField((""), max_length=50)
    memberFlatnumber = models.CharField((""), max_length=50)
    

    def __str__(self):
        return self.memberName
    

class Secretary(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
    

class Categoryname(models.Model):
    category_name=models.CharField(max_length=100)   
    def __str__(self):
        return self.category_name 


class Issues(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    category=models.ForeignKey(Categoryname, on_delete=models.CASCADE)
    flat_number=models.CharField(max_length=50)
    image=models.FileField(upload_to='issues/', null=True, blank=True)
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, related_name='issues')
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title
    

class Notification(models.Model):
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='notifications')
    message=models.TextField()


class Solution(models.Model):
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='solutions')
    issue = models.ForeignKey(Issues, on_delete=models.CASCADE, related_name='solutions')
    solution_description=models.TextField()
    is_approved = models.BooleanField(default=False)
    
      
    

    def __str__(self):
        return self.solution_description
    

class Vote(models.Model):
    APPROVE = 'approve'
    REJECT = 'reject'
    VOTE_CHOICES = [
        (APPROVE, 'Approve'),
        (REJECT, 'Reject'),
    ]
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='votes')
    choice = models.CharField(max_length=10, choices=VOTE_CHOICES, default=APPROVE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
   

    class Meta:
        unique_together = ('solution', 'voter')


