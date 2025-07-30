from django.contrib import admin
from django.utils.html import format_html
from .models import DentalCariesStudy, CariesData, DataExtractionNote, ProjectMetadata


@admin.register(DentalCariesStudy)
class DentalCariesStudyAdmin(admin.ModelAdmin):
    list_display = [
        'study_id', 
        'title_truncated', 
        'publication_year', 
        'province', 
        'age_group', 
        'sample_size',
        'caries_index_used',
        'quality_score'
    ]
    list_filter = [
        'province', 
        'age_group', 
        'study_design', 
        'caries_index_used', 
        'publication_year',
        'risk_of_bias'
    ]
    search_fields = ['title', 'authors', 'study_id', 'journal']
    readonly_fields = ['created_at', 'updated_at', 'extraction_date']
    
    fieldsets = (
        ('Study Identification', {
            'fields': ('study_id', 'title', 'authors')
        }),
        ('Publication Details', {
            'fields': ('journal', 'publication_year', 'doi', 'pubmed_id')
        }),
        ('Study Characteristics', {
            'fields': ('study_design', 'study_setting', 'province', 'city_region')
        }),
        ('Population', {
            'fields': ('sample_size', 'age_group', 'age_min', 'age_max')
        }),
        ('Data Collection', {
            'fields': ('data_collection_start', 'data_collection_end')
        }),
        ('Caries Assessment', {
            'fields': ('caries_index_used', 'examination_criteria')
        }),
        ('Quality Assessment', {
            'fields': ('quality_score', 'risk_of_bias')
        }),
        ('Extraction Metadata', {
            'fields': ('extracted_by', 'extraction_date', 'verified_by', 'verification_date')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def title_truncated(self, obj):
        if len(obj.title) > 60:
            return f"{obj.title[:60]}..."
        return obj.title
    title_truncated.short_description = 'Title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('caries_data')


class CariesDataInline(admin.TabularInline):
    model = CariesData
    extra = 1
    fields = [
        'sex', 
        'age_category', 
        'sample_size_group', 
        'caries_prevalence', 
        'mean_dmft_DMFT',
        'mean_decayed',
        'mean_missing', 
        'mean_filled'
    ]


class DataExtractionNoteInline(admin.TabularInline):
    model = DataExtractionNote
    extra = 0
    fields = ['note_type', 'note_text', 'created_by']
    readonly_fields = ['created_at']


# Add inlines to the study admin
DentalCariesStudyAdmin.inlines = [CariesDataInline, DataExtractionNoteInline]


@admin.register(CariesData)
class CariesDataAdmin(admin.ModelAdmin):
    list_display = [
        'study_title_short',
        'sex',
        'age_category',
        'sample_size_group',
        'caries_prevalence',
        'mean_dmft_DMFT'
    ]
    list_filter = ['sex', 'age_category', 'socioeconomic_status', 'study__province']
    search_fields = ['study__title', 'study__study_id']
    
    def study_title_short(self, obj):
        return f"{obj.study.title[:40]}..." if len(obj.study.title) > 40 else obj.study.title
    study_title_short.short_description = 'Study'


@admin.register(DataExtractionNote)
class DataExtractionNoteAdmin(admin.ModelAdmin):
    list_display = ['study_title_short', 'note_type', 'note_preview', 'created_by', 'created_at']
    list_filter = ['note_type', 'created_by', 'created_at']
    search_fields = ['study__title', 'note_text']
    readonly_fields = ['created_at']
    
    def study_title_short(self, obj):
        return f"{obj.study.title[:30]}..." if len(obj.study.title) > 30 else obj.study.title
    study_title_short.short_description = 'Study'
    
    def note_preview(self, obj):
        return f"{obj.note_text[:50]}..." if len(obj.note_text) > 50 else obj.note_text
    note_preview.short_description = 'Note'


@admin.register(ProjectMetadata)
class ProjectMetadataAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'protocol_version', 'last_updated']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project_name', 'protocol_version', 'last_updated')
        }),
        ('Search Strategy', {
            'fields': ('search_start_date', 'search_end_date', 'databases_searched')
        }),
        ('Inclusion/Exclusion Criteria', {
            'fields': ('inclusion_criteria', 'exclusion_criteria')
        }),
        ('Data Analysis', {
            'fields': ('analysis_software', 'bayesian_model_version')
        })
    ) 