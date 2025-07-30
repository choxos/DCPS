from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Case, When, FloatField, F, Max, Min
from django.db import models
from django.views.generic import ListView, DetailView, TemplateView, View
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import DentalCariesStudy, CariesData, ProjectMetadata
import json
from datetime import datetime, timedelta
from django.utils import timezone


class HomeView(TemplateView):
    """Homepage with overview and recent studies"""
    template_name = 'studies/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get summary statistics
        study_stats = DentalCariesStudy.objects.aggregate(
            total_studies=Count('id'),
            total_participants=models.Sum('sample_size'),
            latest_year=Max('publication_year'),
            earliest_year=Min('publication_year'),
        )
        context.update(study_stats)
        
        # Get recent studies
        context['recent_studies'] = DentalCariesStudy.objects.order_by('-publication_year', '-created_at')[:6]
        
        # Get provincial coverage
        context['provincial_coverage'] = DentalCariesStudy.objects.exclude(
            province__isnull=True
        ).values('province').annotate(
            study_count=Count('id'),
            total_participants=models.Sum('sample_size')
        ).order_by('-study_count')[:10]
        
        # Get age group distribution
        context['age_group_stats'] = DentalCariesStudy.objects.values('age_group').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get caries index usage
        context['index_usage'] = DentalCariesStudy.objects.values('caries_index_used').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Quick facts
        context['quick_facts'] = {
            'provinces_covered': DentalCariesStudy.objects.values('province').distinct().count(),
            'years_span': study_stats['latest_year'] - study_stats['earliest_year'] if study_stats['latest_year'] else 0,
            'avg_sample_size': DentalCariesStudy.objects.aggregate(avg=Avg('sample_size'))['avg'] or 0
        }
        
        return context


class StudyListView(ListView):
    """List all studies with filtering and pagination"""
    model = DentalCariesStudy
    template_name = 'studies/study_list.html'
    context_object_name = 'studies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = DentalCariesStudy.objects.all()
        
        # Apply filters from GET parameters
        province = self.request.GET.get('province')
        if province:
            queryset = queryset.filter(province=province)
        
        age_group = self.request.GET.get('age_group')
        if age_group:
            queryset = queryset.filter(age_group=age_group)
        
        caries_index = self.request.GET.get('caries_index')
        if caries_index:
            queryset = queryset.filter(caries_index_used=caries_index)
        
        year_from = self.request.GET.get('year_from')
        if year_from:
            queryset = queryset.filter(publication_year__gte=year_from)
        
        year_to = self.request.GET.get('year_to')
        if year_to:
            queryset = queryset.filter(publication_year__lte=year_to)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-publication_year')
        queryset = queryset.order_by(sort_by)
        
        return queryset.prefetch_related('caries_data')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter options for the sidebar
        context['filter_options'] = {
            'provinces': DentalCariesStudy.objects.values_list('province', flat=True).distinct(),
            'age_groups': DentalCariesStudy.objects.values_list('age_group', flat=True).distinct(),
            'caries_indices': DentalCariesStudy.objects.values_list('caries_index_used', flat=True).distinct(),
            'year_range': DentalCariesStudy.objects.aggregate(
                min_year=Min('publication_year'),
                max_year=Max('publication_year')
            )
        }
        
        # Current filters
        context['current_filters'] = {
            'province': self.request.GET.get('province', ''),
            'age_group': self.request.GET.get('age_group', ''),
            'caries_index': self.request.GET.get('caries_index', ''),
            'year_from': self.request.GET.get('year_from', ''),
            'year_to': self.request.GET.get('year_to', ''),
            'sort': self.request.GET.get('sort', '-publication_year'),
        }
        
        return context


class StudySearchView(ListView):
    """Search studies by keywords"""
    model = DentalCariesStudy
    template_name = 'studies/study_search.html'
    context_object_name = 'studies'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return DentalCariesStudy.objects.filter(
                Q(title__icontains=query) |
                Q(authors__icontains=query) |
                Q(journal__icontains=query) |
                Q(notes__icontains=query)
            ).order_by('-publication_year')
        return DentalCariesStudy.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class StudyDetailView(DetailView):
    """Detailed view of a single study"""
    model = DentalCariesStudy
    template_name = 'studies/study_detail.html'
    context_object_name = 'study'
    slug_field = 'study_id'
    slug_url_kwarg = 'study_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all caries data for this study
        context['caries_data'] = self.object.caries_data.all().order_by('age_category', 'sex')
        
        # Get extraction notes
        context['extraction_notes'] = self.object.extraction_notes.all().order_by('-created_at')
        
        # Related studies (same province and age group)
        context['related_studies'] = DentalCariesStudy.objects.filter(
            province=self.object.province,
            age_group=self.object.age_group
        ).exclude(id=self.object.id)[:5]
        
        return context


class DashboardView(TemplateView):
    """Main dashboard with key visualizations"""
    template_name = 'studies/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Summary statistics
        context['total_studies'] = DentalCariesStudy.objects.count()
        context['total_participants'] = DentalCariesStudy.objects.aggregate(
            total=models.Sum('sample_size')
        )['total'] or 0
        
        # Provincial distribution
        context['provincial_data'] = list(
            DentalCariesStudy.objects.values('province').annotate(
                count=Count('id'),
                avg_caries=Avg('caries_data__mean_dmft_DMFT')
            ).order_by('-count')
        )
        
        # Age group analysis
        context['age_group_data'] = list(
            CariesData.objects.values('study__age_group').annotate(
                avg_prevalence=Avg('caries_prevalence'),
                avg_dmft=Avg('mean_dmft_DMFT'),
                study_count=Count('study', distinct=True)
            ).order_by('study__age_group')
        )
        
        return context


class AnalyticsView(TemplateView):
    """Advanced analytics and trends"""
    template_name = 'studies/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Placeholder for advanced analytics
        context['analysis_placeholder'] = True
        context['coming_soon_features'] = [
            'Bayesian spatial-temporal modeling',
            'Prevalence trend projections',
            'Risk factor analysis',
            'Geographic hotspot identification',
            'Age-period-cohort effects',
            'Intervention impact assessment'
        ]
        
        return context


class TrendsView(TemplateView):
    """Temporal trends visualization"""
    template_name = 'studies/trends.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Temporal trends data
        context['temporal_data'] = list(
            DentalCariesStudy.objects.values('publication_year').annotate(
                study_count=Count('id'),
                avg_sample_size=Avg('sample_size'),
                avg_caries=Avg('caries_data__mean_dmft_DMFT')
            ).order_by('publication_year')
        )
        
        return context


class AboutView(TemplateView):
    """About page with project information"""
    template_name = 'studies/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get project metadata if available
        try:
            context['project_metadata'] = ProjectMetadata.objects.first()
        except ProjectMetadata.DoesNotExist:
            context['project_metadata'] = None
        
        return context


class MethodologyView(TemplateView):
    """Methodology page"""
    template_name = 'studies/methodology.html'


class ProtocolView(TemplateView):
    """Protocol page"""
    template_name = 'studies/protocol.html'


# API Views for AJAX/Chart data
class CariesByProvinceAPI(View):
    """API endpoint for provincial caries data"""
    
    def get(self, request):
        data = list(
            CariesData.objects.values('study__province').annotate(
                avg_prevalence=Avg('caries_prevalence'),
                avg_dmft=Avg('mean_dmft_DMFT'),
                study_count=Count('study', distinct=True),
                total_participants=models.Sum('sample_size_group')
            ).order_by('-avg_prevalence')
        )
        return JsonResponse({'data': data})


class CariesByAgeAPI(View):
    """API endpoint for age-stratified caries data"""
    
    def get(self, request):
        data = list(
            CariesData.objects.values('age_category').annotate(
                avg_prevalence=Avg('caries_prevalence'),
                avg_dmft=Avg('mean_dmft_DMFT'),
                count=Count('id')
            ).order_by('age_category')
        )
        return JsonResponse({'data': data})


class TemporalTrendsAPI(View):
    """API endpoint for temporal trends"""
    
    def get(self, request):
        # Group by decade for better visualization
        data = list(
            CariesData.objects.extra(
                select={'decade': "FLOOR(EXTRACT(year FROM study__data_collection_start)/10)*10"}
            ).values('decade').annotate(
                avg_prevalence=Avg('caries_prevalence'),
                avg_dmft=Avg('mean_dmft_DMFT'),
                study_count=Count('study', distinct=True)
            ).order_by('decade')
        )
        return JsonResponse({'data': data}) 