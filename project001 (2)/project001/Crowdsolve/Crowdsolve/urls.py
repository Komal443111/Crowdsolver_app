"""
URL configuration for Crowdsolve project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from CrowdSolver import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.admindashboard, name='admindashboard'),
    path('membersignup/', views.MemberSignup, name='membersignup'),
    path('verifymember/' , views.verifymember  , name='verifymember'),
    path('issuereport/', views.issuereport, name='issuereport'),
    path('notification/', views.notification, name='notification'),
    path('ticketraise/', views.ticketraise , name= 'ticketraise'),
    path('voting/', views.voting, name='voting'),
    path('memberlogin/', views.memberlogin, name='memberlogin'),
    path('memberlogout/', views.memberlogout, name='memberlogout'),
    path('secretarylogin/', views.secretary_login, name='secretarylogin'),
    path('secretaryotp/', views.secretary_otp_verify, name='secretaryotp'),
    path('raise_issue/', views.raise_issue, name='raise_issue'),
    path('logout/', views.memberlogout, name='logout'),
    path('solution_view/<int:issue_id>/', views.solution_view, name='solution_view'),
    path('user_solutions/', views.user_solutions_view, name='user_solutions'),
    path('approveSolution/<int:solution_id>/', views.approved_solutions, name='approveSolution'),



]

