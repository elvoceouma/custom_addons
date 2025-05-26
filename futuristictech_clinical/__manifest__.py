# -*- coding: utf-8 -*-
{
    'name': 'Hospital Management',
    'version': '17.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Hospital Management System for Odoo 18',
    'description': """
        This module provides comprehensive hospital management functionality:
        - Campus/Hospital management
        - Patient management
        - Room/Bed allocation
        - Admission and discharge process
        - Medical records
        - Pharmacy integration
        - Billing integration
    """,
    'author': 'Odoo',
    'website': 'https://www.odoo.com',
    'depends': [
        'base',
        'mail',
        'stock',
        'base_accounting_kit',
        'product',
        'uom',
        'hr',
    ],
    'data': 
    [
        'security/hospital_security.xml',
        'security/ir.model.access.csv',
        
        'data/hospital_sequence.xml',
        
        'views/hospital_views.xml',
        'views/admission_views.xml',
        'views/inpatient_admission_views.xml',
        'views/bed_views.xml',
        'views/block_views.xml',
        'views/block_duty_views.xml',
        'views/patient_document_views.xml',
        'views/case_history_views.xml',
        'views/configuration_views.xml',
        'views/discharge_views.xml',
        'views/medication_consent_form_views.xml',
        'views/food_views.xml',
        'views/hospital_evaluation_views.xml',
        'views/hospital_management_admission_views.xml',
        'views/hospital_management_case_history_views.xml',
        'views/hospital_management_medicine_box_views.xml',
        'views/hospital_management_medicine_packing_views.xml',
        'views/hospital_management_outside_consultation_views.xml',
        'views/hospital_management_vaccine_views.xml',
        'views/hospital_management_follow_up_sheet_views.xml',
        'views/hospital_appointment_views.xml',
        'views/hospital_medicine_register_views.xml',
        'views/registration_form_views.xml',
        'views/procedure_forms_views.xml',
        'views/hospital_pysician_views.xml',
        'views/medical_record_views.xml',
        'views/medicine_views.xml',
        'views/patient_views.xml',
        'views/pharmacy_views.xml',
        'views/prescription_views.xml',
        'views/room_views.xml',
        'views/hospital_case_formulation.xml',
        'views/hospital_laboratory_views.xml',
        'views/hospital_independent_examination_views.xml',
        'views/view_hospital_case_formulation_form.xml',
        'views/mental_health_forms_views.xml',
        'views/patient_requisition_views.xml',
        'views/hospital_caretaker_allotment_view.xml',
        'views/investigation_form_views.xml',
        'views/room_inspection_views.xml',
        'views/hospital_doctor_payout_views.xml',
        'views/activity_record_views.xml',
        'views/nurse_assessment_view.xml',
        'views/care_plan_view.xml',
        'views/admission_referral_config_view.xml',
        'views/actions.xml',  
        'views/menu.xml',     
        
        'reports/hospital_reports.xml',
        'reports/inpatient_security_policy_report.xml',
        # 'reports/admission_report.xml',
        # 'reports/discharge_summary.xml',
        # 'reports/prescription_report.xml',
        # 'reports/hospital_reports.xml',
    ],
    'demo': [
        # 'demo/hospital_demo.xml',
    ],
    # 'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        # 'web.assets_backend': [
        #     'hospital_management/static/src/js/**/*',
        #     'hospital_management/static/src/css/**/*',
        # ],
        # 'web.assets_qweb': [
        #     'hospital_management/static/src/xml/**/*',
        # ],
    },
}