from urllib.parse import quote_plus
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View, ListView
from .models import Post, PostImage, Comment, Subscriber, Image
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm, ContactForm, SearchForm, SubscriberForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Create your views here.
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 20)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag}) 

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 20
    template_name = 'blog/post/list.html'



def post_detail(request, year, month, day, post,):
    template_name: 'post_detail.html'
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    photos = PostImage.objects.filter(post=post)
    share_string = quote_plus(post.body)
    share_string = quote_plus('')
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    if request.method == 'POST':

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj
            # normal comment
            # create comment object but do not save to database
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

        return render(request,
                      'blog/post_detail.html',
                      {'post': post,
                       'photos': photos,
                       'comments': comments,
                       'new_comment': new_comment,
                       'comment_form': comment_form,
                       'similar_posts': similar_posts,
                       'share_string': share_string})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                          search=search_vector,
                          rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-rank')
    return render(request,
                  'blog/post_search.html',
                  {'form': form,
                   'query': query,
                   'results': results})

def home(request, tag_slug=None):
    object_list = Post.published.all( )
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag})

def about(request):
    return render(request, 'blog/About.html')


def contact(request):
    if request.method == 'POST':
        form =  ContactForm(request.POST)

        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']
            message = "{0} has sent you a new message:\n\n{1}".format(sender_name, form.cleaned_data ['message'])
            send_mail('New Enquiry', message, sender_email, ['akinpeluoluwadamilare79@gmail.com'])
            return HTTPResponse('Thanks for contacting us!')
    else:
        form = ContactForm()
    return render(request, 'blog/Contact.html', {'form': form})


def random_digits():
    return "%0.12d" % random.randint(0, 999999999999)

@csrf_exempt
def self(request):
    pics=Image.objects.all()


    if request.method == 'POST':
        sub = Subscriber(email=request.POST['email'], conf_num=random_digits())
        sub.save()
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=sub.email,
            subject='Newsletter Confirmation',
            html_content='Thank you for signing up for my email newsletter! \
                Please complete the process by \
                <a href="{}/confirm/?email={}&conf_num={}"> clicking here to \
                confirm your registration</a>.'.format(request.build_absolute_uri('/confirm/'),
                                                    sub.email,
                                                    sub.conf_num))
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'added', 'form': SubscriberForm()})
    else:
        return render(request, 'blog/self.html', {
                                                  'form': SubscriberForm(),
                                                  'pics':pics })
    
def confirm(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.confirmed = True
        sub.save()
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'confirmed'})
    else:
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'denied'})

def delete(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.delete()
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'unsubscribed'})
    else:
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'denied'})


