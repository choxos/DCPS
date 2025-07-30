from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class DentalCariesStudy(models.Model):
    """Model for dental caries studies included in the systematic review"""
    
    # Study identification
    study_id = models.CharField(max_length=50, unique=True, help_text="Unique study identifier")
    title = models.TextField(help_text="Title of the study")
    authors = models.TextField(help_text="Study authors")
    
    # Publication details
    journal = models.CharField(max_length=500, blank=True, null=True, help_text="Journal name")
    publication_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2050)],
        help_text="Year of publication"
    )
    doi = models.CharField(max_length=255, blank=True, null=True, help_text="DOI of the study")
    pubmed_id = models.CharField(max_length=20, blank=True, null=True, help_text="PubMed ID")
    
    # Study characteristics
    study_design = models.CharField(
        max_length=100,
        choices=[
            ('cross_sectional', 'Cross-sectional'),
            ('longitudinal', 'Longitudinal'),
            ('cohort', 'Cohort'),
            ('case_control', 'Case-control'),
            ('randomized_trial', 'Randomized Controlled Trial'),
            ('other', 'Other'),
        ],
        help_text="Type of study design"
    )
    
    study_setting = models.CharField(
        max_length=100,
        choices=[
            ('population', 'Population-based'),
            ('school', 'School-based'),
            ('clinic', 'Clinic-based'),
            ('community', 'Community-based'),
            ('other', 'Other'),
        ],
        help_text="Study setting"
    )
    
    # Geographic information
    province = models.CharField(
        max_length=100,
        choices=[
            ('AB', 'Alberta'),
            ('BC', 'British Columbia'),
            ('MB', 'Manitoba'),
            ('NB', 'New Brunswick'),
            ('NL', 'Newfoundland and Labrador'),
            ('NS', 'Nova Scotia'),
            ('ON', 'Ontario'),
            ('PE', 'Prince Edward Island'),
            ('QC', 'Quebec'),
            ('SK', 'Saskatchewan'),
            ('NT', 'Northwest Territories'),
            ('NU', 'Nunavut'),
            ('YT', 'Yukon'),
            ('national', 'National/Multi-provincial'),
        ],
        help_text="Canadian province/territory where study was conducted"
    )
    
    city_region = models.CharField(max_length=200, blank=True, null=True, help_text="City or specific region")
    
    # Study population
    sample_size = models.PositiveIntegerField(help_text="Total sample size")
    age_group = models.CharField(
        max_length=50,
        choices=[
            ('preschool', 'Preschool (0-5 years)'),
            ('school_age', 'School age (6-12 years)'),
            ('adolescent', 'Adolescent (13-18 years)'),
            ('adult', 'Adult (19-64 years)'),
            ('elderly', 'Elderly (65+ years)'),
            ('mixed', 'Mixed age groups'),
        ],
        help_text="Primary age group studied"
    )
    
    age_min = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(120)], help_text="Minimum age in years")
    age_max = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(120)], help_text="Maximum age in years")
    
    # Data collection period
    data_collection_start = models.DateField(help_text="Start date of data collection")
    data_collection_end = models.DateField(help_text="End date of data collection")
    
    # Dental caries assessment
    caries_index_used = models.CharField(
        max_length=50,
        choices=[
            ('dmft', 'dmft (deciduous teeth)'),
            ('dmfs', 'dmfs (deciduous teeth surfaces)'),
            ('DMFT', 'DMFT (permanent teeth)'),
            ('DMFS', 'DMFS (permanent teeth surfaces)'),
            ('dmft_DMFT', 'dmft + DMFT (mixed dentition)'),
            ('other', 'Other index'),
        ],
        help_text="Primary dental caries index used"
    )
    
    examination_criteria = models.CharField(
        max_length=100,
        choices=[
            ('who_1997', 'WHO 1997'),
            ('who_2013', 'WHO 2013'),
            ('icdas', 'ICDAS'),
            ('other', 'Other criteria'),
        ],
        help_text="Examination criteria used for caries detection"
    )
    
    # Quality assessment
    quality_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True,
        null=True,
        help_text="Quality assessment score (0-10)"
    )
    
    risk_of_bias = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High'),
            ('unclear', 'Unclear'),
        ],
        blank=True,
        null=True,
        help_text="Overall risk of bias assessment"
    )
    
    # Extraction metadata
    extracted_by = models.CharField(max_length=100, help_text="Name of data extractor")
    extraction_date = models.DateField(auto_now_add=True, help_text="Date of data extraction")
    verified_by = models.CharField(max_length=100, blank=True, null=True, help_text="Name of verifier")
    verification_date = models.DateField(blank=True, null=True, help_text="Date of verification")
    
    # Additional notes
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the study")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dental_caries_studies'
        ordering = ['-publication_year', 'title']
        indexes = [
            models.Index(fields=['study_id']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['province']),
            models.Index(fields=['age_group']),
            models.Index(fields=['caries_index_used']),
        ]
    
    def __str__(self):
        return f"{self.title[:100]}... ({self.publication_year})"
    
    def get_absolute_url(self):
        return reverse('studies:detail', kwargs={'study_id': self.study_id})
    
    @property
    def doi_url(self):
        """Generate URL to DOI"""
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return None
    
    @property
    def pubmed_url(self):
        """Generate URL to PubMed entry"""
        if self.pubmed_id:
            return f"https://pubmed.ncbi.nlm.nih.gov/{self.pubmed_id}/"
        return None


class CariesData(models.Model):
    """Model for specific caries data points from studies"""
    
    study = models.ForeignKey(DentalCariesStudy, on_delete=models.CASCADE, related_name='caries_data')
    
    # Population stratification
    sex = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('mixed', 'Mixed/Combined'),
        ],
        help_text="Sex of the population group"
    )
    
    age_category = models.CharField(max_length=50, help_text="Specific age category (e.g., '6 years', '12 years', '15-17 years')")
    socioeconomic_status = models.CharField(
        max_length=50,
        choices=[
            ('low', 'Low SES'),
            ('middle', 'Middle SES'),
            ('high', 'High SES'),
            ('mixed', 'Mixed SES'),
            ('not_specified', 'Not specified'),
        ],
        blank=True,
        null=True,
        help_text="Socioeconomic status of the group"
    )
    
    # Sample characteristics
    sample_size_group = models.PositiveIntegerField(help_text="Sample size for this specific group")
    
    # Caries prevalence data
    caries_prevalence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Caries prevalence as percentage"
    )
    caries_prevalence_ci_lower = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        help_text="Lower bound of 95% confidence interval"
    )
    caries_prevalence_ci_upper = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        help_text="Upper bound of 95% confidence interval"
    )
    
    # DMFT/dmft data
    mean_dmft_DMFT = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Mean DMFT/dmft score"
    )
    mean_dmft_DMFT_sd = models.FloatField(
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Standard deviation of DMFT/dmft"
    )
    
    # Component breakdown
    mean_decayed = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True, help_text="Mean decayed component")
    mean_missing = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True, help_text="Mean missing component")
    mean_filled = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True, help_text="Mean filled component")
    
    # Additional indices
    care_index = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        help_text="Care index (filled/(decayed+missing+filled) * 100)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'caries_data'
        ordering = ['study', 'age_category', 'sex']
        unique_together = ['study', 'sex', 'age_category', 'socioeconomic_status']
    
    def __str__(self):
        return f"{self.study.title[:50]}... - {self.sex} {self.age_category}"


class DataExtractionNote(models.Model):
    """Model for tracking data extraction notes and decisions"""
    
    study = models.ForeignKey(DentalCariesStudy, on_delete=models.CASCADE, related_name='extraction_notes')
    
    note_type = models.CharField(
        max_length=50,
        choices=[
            ('extraction', 'Data Extraction Note'),
            ('quality', 'Quality Assessment Note'),
            ('clarification', 'Clarification Needed'),
            ('exclusion', 'Exclusion Reason'),
            ('other', 'Other'),
        ],
        help_text="Type of note"
    )
    
    note_text = models.TextField(help_text="Content of the note")
    created_by = models.CharField(max_length=100, help_text="Person who created the note")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'extraction_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.note_type}: {self.note_text[:100]}..."


class ProjectMetadata(models.Model):
    """Model for storing project-level metadata and settings"""
    
    project_name = models.CharField(max_length=200, default="Dental Caries Prevalence in Canada 1990-2025")
    protocol_version = models.CharField(max_length=20, default="1.0")
    last_updated = models.DateTimeField(auto_now=True)
    
    # Search strategy
    search_start_date = models.DateField(help_text="Start date for literature search")
    search_end_date = models.DateField(help_text="End date for literature search")
    databases_searched = models.TextField(help_text="Databases searched (comma-separated)")
    
    # Inclusion/exclusion criteria
    inclusion_criteria = models.TextField(help_text="Study inclusion criteria")
    exclusion_criteria = models.TextField(help_text="Study exclusion criteria")
    
    # Data analysis parameters
    analysis_software = models.CharField(max_length=100, default="R with INLA", help_text="Software used for analysis")
    bayesian_model_version = models.CharField(max_length=50, blank=True, null=True, help_text="Version of Bayesian model")
    
    class Meta:
        db_table = 'project_metadata'
        verbose_name_plural = "Project metadata"
    
    def __str__(self):
        return f"{self.project_name} (v{self.protocol_version})" 