from django.urls import path
from . import views
app_name = 'candidate'

urlpatterns = [
    path('cache/', views.cache_view, name='cache_view'),
    path('login/', views.login.as_view(), name='login'),
    path('create/', views.CandidateSetByParent.as_view(), name='Candidate-set-by-parent'),
    #path('create/<int:parent_id>', views.CandidateSetByParent.as_view(), name='Candidate-list-by-parent'),
    #path('view', views.CandidateViewSet.as_view(), name='Candidate-list'),
    path('view/', views.CandidateViewSet_By_Id.as_view(), name='Candidate-list-by-id-or-all'),
    path('status/', views.CandidateStatusViewSet.as_view(), name='Candidate-status-view'),
    #path('status/<int:candidate_id>', views.CandidateStatusViewSet.as_view(), name='Candidate-change-status'),
]
