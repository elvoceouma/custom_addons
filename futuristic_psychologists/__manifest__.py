{
    'name': 'Clinical Psychology Management',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Clinical Psychology Sessions, Screening, and Assessments Management',
    'description': """
Clinical Psychology Management Module
=====================================
This module provides comprehensive management for:
* Clinical Psychology Screening
* Psychology Sessions
* Psychometric Assessments  
* Advice to Clinical Psychologists
* Discharge Summary
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/clinical_psychologist_screening_views.xml',
        'views/clinical_psychologist_session_views.xml', 
        'views/psychometric_assessment_views.xml',
        'views/advice_clinical_psychologist_views.xml',
        'views/discharge_summary_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}