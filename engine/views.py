import uuid
import logging

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from .models import User, Project

from ratelimit.decorators import ratelimit

logger = logging.getLogger('engine')


def index(request):
    return render(request, 'index.html')


def get_uuid(limit=32):
    return str(uuid.uuid4())[:limit]


@ratelimit(key='ip', rate='10/m', block=True, method=ratelimit.UNSAFE)
def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            name = email.split("@")[0]
            
            user = User.objects.create(username=get_uuid(), email=email, 
                                       first_name=name)
            user.set_password(password)
            user.save()

            login(request, user)
            
            return redirect('/login')
    else:
        
        form = SignUpForm()
    return render(request, 'registration/user_signup.html', {'form': form})


def user_logout(request):
    return None


@ratelimit(key='ip', rate='10/m', block=True, method=ratelimit.UNSAFE)
def user_login(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Due to an early bug emails may not be unique. Last subscription wins.
            user = User.objects.filter(email__iexact=email).order_by('-id').first()

            if not user:
                form.add_error(None, "This email does not exist.")
                context = dict(form=form)
                return render(request, "registration/user_login.html", context=context)

            user = authenticate(username=user.username, password=password)

            if not user:
                form.add_error(None, "Invalid password.")
            elif user and not user.is_active:
                form.add_error(None, "This user may not log in.")
            elif user and user.is_active:
                login(request, user)
                logger.info("logged in user.id={}, user.email={}".format(user.id, user.email))
                return redirect("/")
            else:
                # This should not happen normally.
                form.add_error(None, "Invalid form processing.")
        else:
            print(form, form.is_valid())
    else:
        initial = dict(nexturl=request.GET.get('next', '/'))
        form = LoginForm(initial)

    context = dict(form=form)
    return render(request, "registration/user_login.html", context=context)


def list_projects(request):

    projects = Project.objects.all()
    data = dict(object_list=projects)

    print(projects)

    # for proj in projects:
    #     print(proj.title, proj.owner)
    #     print(proj.data_set.all())
    #     print(proj.analysis_set.all())
    #     print(proj.data_set.all()[0].owner)
    #     print('----')
    # print(1/0)

    return render(request, "project.html", data)


def detail_projects(request, project_id):
    return None
