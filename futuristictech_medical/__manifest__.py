{
    'name': 'FuturisticTech Medical',
    'version': '1.0',
    'summary': 'Comprehensive Medical Management System',
    'description': 'Module for managing hospitals, patients, doctors, and medical cases',
    'author': 'Elvice Ouma',
    'depends': ['base', 'mail', 'stock', 'account', 'hr', 'crm', 'sale_management'],
    'data': [
        # Security
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        
        # Data files
        'data/sequence.xml',
        'data/mail_template_data.xml',
        'data/medical_data.xml',
        
        'views/actions.xml',
        'views/actions_sales.xml',
        # Main views
        'views/hospital_views.xml',
        'views/department_views.xml',
        'views/doctor_views.xml',
        'views/medical_speciality_views.xml',
        'views/patient_views.xml',
        'views/medical_case_views.xml',
        'views/doctor_schedule_views.xml',
        'views/treatment_views.xml',
        'views/pharmacy_views.xml',
        'views/payment_views.xml',
        'views/medical_appointment_views.xml',
        
        # Partner and CRM related views
        'views/res_partners.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'views/medical_case_views.xml',
        'views/medical_prescription_views.xml',
        # 'views/hospital_sales_reporting.xml',
        
        # Additional medical views
        'views/consultation_views.xml',
        'views/medical_labtest_types_views.xml',
        'views/hospital_billing_views.xml',
        'views/evaluation_document_views.xml',
        'views/lab_test_speciality_views.xml',
        'views/oeh_inpatient_views.xml',
        'views/op_visit_views.xml',
        'views/session_assesment_views.xml',
        'views/vitals_specification_views.xml',

        # Wizards
        'wizard/create_hospital_sale_wizard_views.xml',
        
        # Actions and menus
        'views/menu_views.xml',
        'views/sales_menu.xml',
        
        # Reports
        'report/consultation_admission_report.xml',
        'report/report_actions.xml',
        'report/medical_reports.xml',
        'report/report_templates.xml',
    ],
    'demo': [
        'demo/consultation_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'futuristictech_medical/static/src/scss/consultation.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}