from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Study listing and search
    path('studies/', views.StudyListView.as_view(), name='study_list'),
    path('studies/search/', views.StudySearchView.as_view(), name='study_search'),
    path('studies/<str:study_id>/', views.StudyDetailView.as_view(), name='detail'),
    
    # Data visualization and analytics
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('trends/', views.TrendsView.as_view(), name='trends'),
    
    # API endpoints for charts
    path('api/caries-by-province/', views.CariesByProvinceAPI.as_view(), name='api_caries_province'),
    path('api/caries-by-age/', views.CariesByAgeAPI.as_view(), name='api_caries_age'),
    path('api/temporal-trends/', views.TemporalTrendsAPI.as_view(), name='api_temporal_trends'),
    
    # About and documentation
    path('about/', views.AboutView.as_view(), name='about'),
    path('methodology/', views.MethodologyView.as_view(), name='methodology'),
    path('protocol/', views.ProtocolView.as_view(), name='protocol'),
] 