from django.shortcuts import render
from django.http import HttpResponse

from easter_egg.models import GameScore
from django.contrib.auth.models import User

import simplejson

def start_game(request):
    return render(request, "easter_egg/game.html", {})

# def fetch_leaderboard(req):
#     scores = GameScore.objects.all()
#     d = {}
#     for s in scores:
#         d['username'] = s.user.username
#         d['score'] = s.score
#     board = simplejson.dumps(d)

#     return HttpResponse(board, content_type='application/json')

def set_score(req):
    b = False
    d = dict(req.GET.lists())
    u = req.user.username
    if type(u)==User:
        best = list(GameScore.objects.order_by('-score')[:5])
        for sc in best:
            if u == sc.username:
                b = True
            else:
                b = False
        if b:
            if d['score']>GameScore.objects.filter(username=u).score:
                GameScore.objects.filter(username=u).delete()
                s = GameScore(score=d['score'], user=u)
                s.save()
        else :
            if d['score']>best[best.length-1]:
                GameScore.objects.filter(username=best[best.length-1].user.username).delete()
                s = GameScore(score=d['score'], user=u)
                s.save()
    return HttpResponse(status=204)


def fetch_leaderboard(req):
    scores = GameScore.objects.order_by('-score')[:5]
    board = {}
    for s in scores:
        board[s.user.username] = s.score

    finalBoard = simplejson.dumps(board)
    return HttpResponse(finalBoard, content_type='application/json')