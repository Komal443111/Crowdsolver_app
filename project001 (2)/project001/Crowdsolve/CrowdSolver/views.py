from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
import random
from .models import Member,Secretary,Categoryname,Issues,Solution,Vote
from django.shortcuts import get_object_or_404



def MemberSignup(request):
    if request.method == 'POST':
        memberName = request.POST.get('membername', '').strip()
        memberContact = request.POST.get('membercontact', '').strip()
        memberEmail = request.POST.get('memberemail', '').strip()
        memberPassword = request.POST.get('memberpass', '')
        memberCpassword = request.POST.get('membercpass', '')
        memberAddress = request.POST.get('memberaddress', '').strip()
        memberFlatnumber = request.POST.get('flatnumber', '').strip()

        if not all([memberName, memberContact, memberEmail, memberPassword, memberCpassword, memberAddress, memberFlatnumber]):
            return render(request, 'membersignup.html', {'err': 'All fields are required'})

        if memberPassword != memberCpassword:
            return render(request, 'membersignup.html', {'err': 'Passwords do not match'})

        if Member.objects.filter(memberMail=memberEmail).exists():
            return render(request, 'membersignup.html', {'err': 'Email already registered'})

        otp = str(random.randint(1000, 9999))

        request.session['signup_data'] = {
            'name': memberName,
            'email': memberEmail,
            'password': make_password(memberPassword),
            'contact': memberContact,
            'address': memberAddress,
            'flatnumber': memberFlatnumber,
        }

        request.session['otp'] = otp
      

        send_mail(
            subject='Your OTP Verification',
            message=f'Your OTP is: {otp}',
            from_email='komalll4416@gmail.com',
            recipient_list=[memberEmail],
            fail_silently=False
        )

        return redirect('verifymember')

    return render(request, 'membersignup.html')




def verifymember(request):
    if request.method == 'POST':
        user_otp = request.POST.get('motp', '').strip()
        actual_otp = request.session.get('otp')
        data = request.session.get('signup_data')

        if not data or not actual_otp:
            return render(request, 'verifymember.html', {'err': 'Session expired. Please sign up again.'})

        if user_otp != actual_otp:
            return render(request, 'verifymember.html', {'err': 'Invalid OTP'})

        new_member = Member.objects.create(
            memberName=data['name'],
            memberMail=data['email'],
            memberPassword=data['password'],
            memberContact=data['contact'],
            memberAddress=data['address'],
            memberFlatnumber=data['flatnumber']
        )

       
        request.session['member_id'] = new_member.id
        request.session['member_name'] = new_member.memberName

        return redirect('admindashboard')

    return render(request, 'verifymember.html')


def memberlogin(request):
    if request.session.get('member_id'):
        return redirect('admindashboard')

    if request.method == 'POST':
        email = request.POST.get('loginmail', '').strip()
        password = request.POST.get('loginpassword', '')

        try:
            member = Member.objects.get(memberMail=email)
        except Member.DoesNotExist:
            return render(request, 'memberlogin.html', {'err': 'Invalid email or password'})

        if not check_password(password, member.memberPassword):
            return render(request, 'memberlogin.html', {'err': 'Invalid email or password'})

        request.session['member_id'] = member.id
        request.session['member_name'] = member.memberName 
        return redirect('admindashboard')

    return render(request, 'memberlogin.html')


def memberlogout(request):
    request.session.flush()
    return redirect('admindashboard')


def admindashboard(request):
    member_id  = request.session.get('member_id')
    resolved_issue = 0
    pending_votes = 0
    if not member_id:
        issue_count = 0
        issue1 = Issues.objects.none()
    else:
        issue_count = Issues.objects.filter(created_by=member_id).count()
        issue1 = Issues.objects.filter(created_by=member_id)

       
        for issue in issue1:
            for solution in issue.solutions.all():
                approve_count = solution.votes.filter(choice=Vote.APPROVE).count()
                reject_count = solution.votes.filter(choice=Vote.REJECT).count()
                if approve_count > reject_count:
                    resolved_issue += 1
                    break  

       
        all_members = Member.objects.exclude(id=member_id)
        for member in all_members:
            has_voted = False
            for issue in issue1:
                for solution in issue.solutions.all():
                    if solution.votes.filter(voter=member).exists():
                        has_voted = True
                        break
                if has_voted:
                    break
            if not has_voted:
                pending_votes += 1

    return render(request, 'admindashboard.html', {'issue_count': issue_count, 'issue1': issue1,'resolved_issue': resolved_issue, 'pending_votes': pending_votes} )



def issuereport(request):
    member_id  = request.session.get('member_id')
    if not member_id:
        return redirect('memberlogin')
    issues = Issues.objects.filter(created_by=member_id)
    return render(request, 'issuereport.html', {'issues': issues} )



def voting(request):
   
    if request.method == 'POST':
        solution_id = request.POST.get('solution_id')
        choice = request.POST.get('choice')
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect('memberlogin') 
        if solution_id and choice in (Vote.APPROVE, Vote.REJECT):
            # only allow voting on approved solutions
            solution = get_object_or_404(Solution, id=solution_id, is_approved=True)
            voter = get_object_or_404(Member, id=member_id)
           
            if not Vote.objects.filter(solution=solution, voter=voter).exists():
                Vote.objects.create(solution=solution, voter=voter, choice=choice)
        return redirect('voting')
     

    member_id = request.session.get('member_id')
    selected_user_id = request.GET.get('user_id')
    suggestions = None
    if selected_user_id:
        suggestions = Solution.objects.filter(created_by=selected_user_id, is_approved=True).select_related('issue', 'created_by')

    all_member = Member.objects.all()

    if not member_id:
        return redirect('memberlogin')
    solutions = Solution.objects.filter(is_approved=True, issue__created_by=member_id).select_related('issue', 'created_by')

    for sol in solutions:
        approve_count = sol.votes.filter(choice=Vote.APPROVE).count()
        reject_count = sol.votes.filter(choice=Vote.REJECT).count()
        total = approve_count + reject_count
        sol.approve_votes = approve_count
        sol.reject_votes = reject_count
        if total > 0:
            sol.approve_percentage = (approve_count / total) * 100
            sol.reject_percentage = (reject_count / total) * 100
        else:
            sol.approve_percentage = 0
            sol.reject_percentage = 0
        sol.user_voted = False
        if member_id:
            sol.user_voted = sol.votes.filter(voter_id=member_id).exists()

      
       
        sol.can_vote = sol.issue.solutions.filter(is_approved=True)
     
    

    return render(request, 'voting.html', {'solutions': solutions, 'member_id': member_id, 'all_member': all_member,'suggestions':suggestions})



def ticketraise(request):
    return render(request, 'ticketraise.html')


def notification(request):
    member_id  = request.session.get('member_id')
    if not member_id:
        return redirect('memberlogin')
    issues = Issues.objects.exclude(created_by_id=member_id)

    notify_issues = Issues.objects.exclude(created_by_id=member_id)
    

    user_issues = Issues.objects.filter(created_by_id=member_id)
    pending_solutions = Solution.objects.filter(issue__in=user_issues, is_approved=False).select_related('issue', 'created_by')

    return render(request, 'notification.html', {
        'notify_issues': notify_issues,
        'pending_solutions': pending_solutions,
        'issues': issues,
    })
    





def secretary_login(request):
    if request.session.get('secretary_id'):
        return redirect('secretarydashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            secretary = Secretary.objects.get(email=email, is_active=True)
        except Secretary.DoesNotExist:
            return render(request, 'secretarylogin.html', {'err': 'Invalid credentials'})

        if not secretary.check_password(password):
            return render(request, 'secretarylogin.html', {'err': 'Invalid credentials'})

        # Generate OTP
        otp = str(random.randint(1000, 9999))

        request.session['secretary_otp'] = otp
        request.session['secretary_temp_id'] = secretary.id
       

        send_mail(
            subject='Secretary OTP Verification',
            message=f'Your OTP is: {otp}',
            from_email='komalll4416@gmail.com',
            recipient_list=[secretary.email],
            fail_silently=False
        )

        return redirect('secretaryotp')

    return render(request, 'secretarylogin.html')

def secretary_otp_verify(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp', '').strip()
        actual_otp = request.session.get('secretary_otp')
        secretary_id = request.session.get('secretary_temp_id')

        if not actual_otp or not secretary_id:
            return render(request, 'secretaryotp.html', {
                'err': 'Session expired. Please login again.'
            })

        if user_otp != actual_otp:
            return render(request, 'secretaryotp.html', {
                'err': 'Invalid OTP'
            })

        request.session['secretary_id'] = secretary_id

    

        return redirect('secretarydashboard')

    return render(request, 'secretaryotp.html')

def secretarydashboard(request):
    return render(request, 'secretarydashboard.html')


def raise_issue(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        category = request.POST.get('category', '')
        description = request.POST.get('description', '')
        flat_number = request.POST.get('flat_number', '')
        image = request.FILES.get('image', None)
        member_id = request.session.get('member_id', None)
        if not member_id:
            return redirect('memberlogin')

        # Prevent a member from submitting more than one issue
        if Issues.objects.filter(created_by_id=member_id).exists():
            category_list = Categoryname.objects.all()
            return render(request, 'raise_issue.html', {
                'category': category_list,
                'err': 'You have already submitted an issue. Only one submission is allowed.'
            })

        Issues.objects.create(
            title=title,
            description=description,
            category_id=category,
            flat_number=flat_number,
            image=image,
            created_by_id=member_id
        )
        return redirect('raise_issue')
    category = Categoryname.objects.all()

    return render(request, 'raise_issue.html', {'category': category })





def solution_view(request, issue_id):

    issue = get_object_or_404(Issues, id=issue_id)

    if request.method == 'POST':
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect('memberlogin')
        existing_solution = Solution.objects.filter(issue_id=issue_id, created_by_id=member_id)
        if existing_solution.exists():
            return render(request, 'solution.html', {'issue': issue, 'err': 'You have already submitted a solution for this issue.'})

        solution_description = request.POST.get('solution_description', '').strip()
        if not solution_description:
            return render(request, 'solution.html', {'issue': issue, 'err': 'Solution cannot be empty.'})

    
        Solution.objects.create(
            issue=issue,
            created_by_id=member_id,
            solution_description=solution_description
        )


        return redirect('solution_view', issue_id=issue_id)

    return render(request, 'solution.html', {'issue': issue})


def result_view(request):
    created_by = request.session.get('member_id')
    if not created_by:
        return redirect('memberlogin')
    solution=Solution.objects.filter(created_by=created_by)
    return render(request, 'result_view.html', {'solution': solution})

def user_solutions_view(request):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('memberlogin')

    solutions = Solution.objects.all()

    for sol in solutions:
        approve_count = sol.votes.filter(choice=Vote.APPROVE).count()
        reject_count = sol.votes.filter(choice=Vote.REJECT).count()
        total = approve_count + reject_count
        sol.approve_votes = approve_count
        sol.reject_votes = reject_count
        if total > 0:
            sol.approve_percentage = (approve_count / total) * 100
            sol.reject_percentage = (reject_count / total) * 100
        else:
            sol.approve_percentage = 0
            sol.reject_percentage = 0

    return render(request, 'user_solutions.html', {'solutions': solutions})





def approved_solutions(request, solution_id):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('memberlogin')
    # Only approve if the solution exists, belongs to an issue created by current member and is not already approved
    qs = Solution.objects.filter(id=solution_id, issue__created_by=member_id, is_approved=False)
    if not qs.exists():
        # Nothing to approve (either not found or already approved) — redirect back to notifications
        return redirect('notification')
    qs.update(is_approved=True)
    return redirect('notification')

