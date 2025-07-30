# DCPS - Dental Caries Population Studies

A comprehensive web application for systematic review and analysis of dental caries prevalence in Canada (1990-2025) with projections to 2050.

## 🦷 About

DCPS (Dental Caries Population Studies) is part of the Xera DB research ecosystem, providing a robust platform for dental caries epidemiological research in Canada. The application features:

- **Comprehensive Database**: Systematic collection of DMFT/dmft studies across all Canadian provinces and territories
- **Advanced Analytics**: Bayesian hierarchical modeling for spatial-temporal analysis
- **Interactive Visualizations**: Modern dashboard with charts and trends
- **Research Tools**: Study management, data extraction tracking, and quality assessment

## 🚀 Features

### Core Functionality
- ✅ **Study Management**: Complete CRUD operations for dental caries studies
- ✅ **Data Extraction**: Structured data collection with quality control
- ✅ **Provincial Coverage**: Full Canadian geographic representation
- ✅ **Temporal Analysis**: Trends from 1990-2025 with 2050 projections
- ✅ **Admin Interface**: Comprehensive Django admin for data management

### Analytics (Coming Soon)
- 🔬 **Bayesian Modeling**: Hierarchical spatial-temporal models using R-INLA
- 📊 **Advanced Visualizations**: Interactive maps and trend analysis
- 🎯 **Risk Factor Analysis**: Socioeconomic and geographic determinants
- 📈 **Projections**: Evidence-based forecasting to 2050

### User Interface
- 🎨 **Modern Design**: Clean, professional interface using Xera DB theme
- 📱 **Responsive**: Mobile-friendly Bootstrap 5 design
- ♿ **Accessible**: WCAG compliant with semantic HTML
- 🔍 **Search & Filter**: Advanced study discovery tools

## 🛠 Technical Stack

- **Backend**: Django 4.2 with PostgreSQL
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Styling**: Xera DB unified theme system
- **Analytics**: R + INLA for Bayesian modeling (planned)
- **Deployment**: Gunicorn, Nginx, systemd
- **Security**: SSL, CSRF protection, secure headers

## 📊 Data Structure

### Study Models
- `DentalCariesStudy`: Main study information and metadata
- `CariesData`: Stratified DMFT/dmft data points
- `DataExtractionNote`: Quality assessment and extraction notes
- `ProjectMetadata`: Systematic review protocol information

### Key Fields
- Geographic: Province/territory, city/region
- Demographic: Age groups, sex, socioeconomic status
- Clinical: DMFT/dmft indices, caries prevalence, care index
- Methodological: Study design, examination criteria, quality scores

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/DCPS.git
   cd DCPS
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   # Create PostgreSQL database
   createdb dcps_development
   
   # Or use SQLite for development (default)
   ```

5. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## 🌐 Deployment

For production deployment to your VPS, see the comprehensive deployment guide:

📖 **[DCPS_VPS_DEPLOYMENT_GUIDE.md](DCPS_VPS_DEPLOYMENT_GUIDE.md)**

The guide covers:
- Server setup and dependencies
- Database configuration
- Gunicorn and systemd service
- Nginx configuration with SSL
- Security and monitoring
- Backup procedures

## 📁 Project Structure

```
DCPS/
├── dcps/                  # Django project settings
├── studies/               # Main application
│   ├── models.py         # Data models
│   ├── views.py          # View logic
│   ├── admin.py          # Admin interface
│   └── urls.py           # URL routing
├── templates/            # HTML templates
│   ├── base.html         # Base template with Xera theme
│   └── studies/          # App-specific templates
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── images/           # Images and icons
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## 🎨 Theming

DCPS uses the Xera DB unified theme system with dental health-specific colors:

- **Primary**: Mint green (#059669) representing dental health
- **Secondary**: Teal (#0d9488) for medical context
- **Accent**: Aqua (#06b6d4) for highlights
- **Icons**: Font Awesome with tooth icon (fa-tooth)

## 📈 Data Analysis

The application implements a comprehensive Bayesian hierarchical modeling framework:

```
log(μ_ijkl) = α + X_ijkl'β + S_i + T_j + A_k + G_l + (ST)_ij + (SA)_ik + (TA)_jk + ε_ijkl
```

Where:
- `μ_ijkl`: Expected DMFT/dmft count
- `S_i`: Spatial effects (BYM2 model)
- `T_j`: Temporal effects (RW2 prior)
- `A_k`: Age group effects
- `G_l`: Sex effects
- Interaction terms for complex dependencies

## 🤝 Contributing

We welcome contributions to improve DCPS! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Research Team

- **Ahmad Sofi-Mahmudi** - Principal Investigator
  - Independent researcher, Toronto, ON, Canada
  - Email: a.sofimahmudi@gmail.com

- **Reyhaneh Shoorgashti** - Co-Investigator
  - Islamic Azad University of Medical Sciences, Tehran, Iran

- **Additional Contributors**: Sana Baghizadeh, Zahra Bahmani, Sarvnaz Hosseinipour

## 🔗 Related Projects

DCPS is part of the Xera DB research ecosystem:
- [Open Science Tracker (OST)](https://ost.xeradb.com)
- [Publications Retracted and Citing Tracker (PRCT)](https://prct.xeradb.com)
- [CIHR Project Tracker (CIHRPT)](https://cihrpt.xeradb.com)

## 📞 Contact

For questions, collaboration, or support:

- **Email**: a.sofimahmudi@gmail.com
- **Website**: https://dcps.xeradb.com
- **GitHub**: https://github.com/your-username/DCPS

## 📚 Citation

If you use DCPS in your research, please cite:

```
Sofi-Mahmudi, A., Shoorgashti, R., et al. (2024). Dental Caries Population Studies (DCPS): 
A systematic review and Bayesian analysis of dental caries prevalence in Canada (1990-2025). 
DCPS Database. Available at: https://dcps.xeradb.com
```

---

**Note**: This project is actively under development. Advanced analytics features will be implemented as data extraction progresses. The web application is ready for deployment and data entry.