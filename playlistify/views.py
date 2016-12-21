import spotipy
from django.utils.crypto import get_random_string
from django.template import RequestContext
import pdb
from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy import Spotify

from .models import Playlist, Category, SpotifySession


def start_page(request):
    return render_to_response('playlistify/start.html', {}, context_instance=RequestContext(request))
    
def view_playlist(request, slug):
    playlist = Playlist.objects.get(slug=slug)
    return render_to_response('playlistify/playlist.html', {}, context_instance=RequestContext(request))

def edit_playlist(request, slug=None):
    playlist = None
    if slug and slug != 'add':
        playlist = Playlist.objects.get(slug=slug)
   
    if request.method == 'POST':
        playlist = Playlist(
            name=request.POST.get('name'),
            uri=request.POST.get('uri'),
            description=request.POST.get('description'),
            user=request.user
        )
        playlist.save()
        return HttpResponseRedirect('/dashboard/playlist/' + playlist.slug)
    
    if slug and slug != 'add':
        playlist.name = request.POST.get('name')
        playlist.description = request.POST.get('description')
        playlist.save()
        return HttpResponseRedirect('/dashboard/playlist/' + playlist.slug)
    return render_to_response('playlistify/edit_playlist.html', {'playlist': playlist, 'slug': slug}, context_instance=RequestContext(request)) 

def login_user(request):
    spotify_oauth = SpotifyOAuth(
        settings.SPOTIPY_CLIENT_ID, 
        settings.SPOTIPY_CLIENT_SECRET, 
        settings.SPOTIPY_REDIRECT_URI,
        scope='user-read-email playlist-modify-public user-follow-modify'
    )
    authorize_url = spotify_oauth.get_authorize_url()
    return HttpResponseRedirect(authorize_url)


def dashboard(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render_to_response(
        'playlistify/dashboard.html',
        {'playlists': playlists},
        context_instance=RequestContext(request)
    )


def callback(request):
    spotify_oauth = SpotifyOAuth(
        settings.SPOTIPY_CLIENT_ID, 
        settings.SPOTIPY_CLIENT_SECRET, 
        settings.SPOTIPY_REDIRECT_URI,
        scope='user-read-email playlist-modify-public user-follow-modify'
    )
    oauth_token = request.GET.get('code')
    access_token = spotify_oauth.get_access_token(oauth_token)
    
    spotify = Spotify(auth=access_token.get('access_token'))
    
    me = spotify.me()
    
    # Check spotify session
    current_user = None
    user = None
    try:
        current_user = SpotifySession.objects.get(
            username=me['id']
        )
        user = current_user.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
    except:
        current_user = SpotifySession(username=me.get('id'))
        # Create this
        current_user.access_token = access_token.get('access_token')
        current_user.refresh_token = access_token.get('refresh_token')
        current_user.expires_in = access_token.get('expires_in')
        password = get_random_string(length=32)
        user = User.objects.create_user(me['id'],me['email'], password)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        current_user.user = user
        current_user.save()

    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/dashboard')
    