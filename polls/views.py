from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone 
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate


from .models import Choice, Question, PollUser

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        latest_question_list = Question.objects.order_by("-pub_date")[:5]
        context = {"latest_question_list": latest_question_list}
        return render(request, "polls/index.html", context)
    else:
        return HttpResponseRedirect("/login")


def detail(request, question_id):
    if request.user:
        q = get_object_or_404(Question, pk=question_id)

        return render(request, "polls/detail.html", {"question": q})
    else:
        return HttpResponseRedirect("/polls/login")

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
    
class DetailView(generic.DetailView):
    ...

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    


def register(request):
    if request.method == "GET":
        return render(request, "polls/register.html", {})

    firstname = request.POST["fname"]
    lastname = request.POST["lname"]
    username = request.POST["username"]
    email = request.POST["email"]
    password = request.POST["password"]
    country = request.POST["country"]

    context = {
        'firstname': firstname,
        'lastname': lastname,
        'username': username,
        'email': email,
        'password': password,
        'country': country,
    }

    if User.objects.filter(username=username).exists():
        context['error'] = 'Օգտանունն արդեն գրանցված է։'
        return render(request, "polls/register.html", context)

    user = User.objects.create_user(
        first_name=firstname,            last_name=lastname,
        username=username,
        password=password,
        email=email
        )
    user.save()
        
        # Ստեղծում ենք PollUser օբյեկտը և կապում ենք այն օգտատիրոջ հետ
    pu = PollUser(user=user, country=country)
    pu.save()

    return HttpResponseRedirect("/polls/login")
    
def _login(request):
    if request.method == "GET":
        return render(request, "polls/login.html", {})
    
    usr = request.POST['username']
    pswd = request.POST['password']
 
    user = authenticate(username=usr, password=pswd)
    if user:
        login(request, user)
        return HttpResponseRedirect("/polls/")
    
    return render(request, "polls/login.html", {"error": "username or password is wrong"})

def log_out(request):
    logout(request)
    return HttpResponseRedirect("/polls/login")

def question(request):
    if request.user.is_authenticated:

        if request.method == "GET":
            return render(request, "polls/question.html", {})
        else:
            qt = request.POST.get("question_text", "")
            user = request.user
            pu = get_object_or_404(PollUser, user=user)
            q = Question(question_text = qt, pub_date = timezone.now(), creator=pu)
            q.save()
            
            choices1 = request.POST.get("choice1", "")
            choices2 = request.POST.get("choice2", "")
            choices3 = request.POST.get("choice3", "")
            choices = [choices1, choices2, choices3]

            for choice in choices:
                if choices:
                    c = Choice(question=q, choice_text=choice)
                    c.save()


            return HttpResponseRedirect("/polls/{}".format(q.id))
    else:
        return HttpResponseRedirect("polls/login")
    
def question_edit(request, question_id):
    q = get_object_or_404(Question, pk=question_id)
    if request.method == 'GET':
        choices = q.choice_set.all()
        if choices.count() < 3:
            for i in range(3 - choices.count()):
                choices.create(choice_text='', question=q)
        
        return render(request, 'polls/question_edit.html', {"question": q, "choices": choices})
    
