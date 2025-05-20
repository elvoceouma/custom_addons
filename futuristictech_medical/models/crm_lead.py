from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging 
_logger = logging.getLogger(__name__)
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Reference and Status
    reference = fields.Char(string='Reference', readonly=True, default='/')
    state = fields.Selection([
        ('lead', 'Lead'),
        ('warm_lead', 'Warm Lead'),
        ('hot_lead', 'Hot Lead'),
        ('opportunity', 'Opportunity'),
        ('customer', 'Customer'),
        ('dead_lead', 'Dead Lead'),
        ('hibernation', 'Hibernation')
    ], string='Status', default='lead', tracking=True)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
    # Statistics
    appointment_count = fields.Integer(compute='_compute_appointment_count', string='Appointment Count')
    visit_count = fields.Integer(compute='_compute_visit_count', string='Visit Count')
    
    
     # Caller Information
    caller_mobile = fields.Char(string='Caller Mobile', required=True)
    caller_name = fields.Char(string='Caller Name', required=True)
    caller_email = fields.Char(string='Caller Email')
    services_looking_for = fields.Many2one('services.master', string='Services Looking For')

    # Address Fields
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    address = fields.Text(string='Full Address', compute='_compute_full_address', store=True)

    @api.depends('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _compute_full_address(self):
        for record in self:
            address_parts = [
                record.street,
                record.street2,
                record.city,
                record.state_id.name if record.state_id else '',
                record.zip,
                record.country_id.name if record.country_id else ''
            ]
            record.address = ', '.join(filter(None, address_parts))

    # Patient Identification Fields
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    is_new_patient = fields.Boolean(string='Is New Patient', default=True)

    # Patient Personal Information
    patient_name = fields.Char(string='Patient Name')
    patient_age = fields.Char(string='Age')
    patient_sex = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Transgender', 'Transgender')
    ], string='Sex')
    date_of_birth = fields.Date(string='Date of Birth')
    patient_mobile = fields.Char(string='Mobile')
    patient_email = fields.Char(string='Email')
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], string='Blood Group')


    # Administrative Fields
    lead_owner = fields.Many2one('res.users', string='Lead Owner')
    assigned_to = fields.Many2one('res.users', string='Assigned to')
    referred_by = fields.Char(string='Referred By')
    customer_category = fields.Selection([
        ('new', 'New'),
        ('returning', 'Returning'),
        ('vip', 'VIP')
    ], string='Customer Category')
    lead_state = fields.Selection([
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('follow_up', 'Follow Up')
    ], string='Lead State')


     # Notification Settings
    marketing_notification = fields.Boolean(string='Marketing Notification', default=True)
    promotional_notification = fields.Boolean(string='Promotional Notification', default=True)
    transactional_notification = fields.Boolean(string='Transactional Notification', default=True)
    whatsapp_updates = fields.Boolean(string='Whatsapp Updates', default=True)
    aadhar_verification = fields.Boolean(string='Aadhar verification')
    
    # Tags
    primary_tag = fields.Many2one('primary.tag', string='Primary Tag')
    secondary_tag = fields.Many2one('secondary.tag', string='Secondary Tag')
    tertiary_tag = fields.Many2one('tertiary.tag', string='Tertiary Tag')
    discard_tag = fields.Many2one('discard.tag', string='Discard Tag')
    source = fields.Many2one('utm.source', string='Source')
    current_source = fields.Many2one('utm.source', string='Current Source')
    do_not_call = fields.Boolean(string='Do Not Call')
    latest_consulting_doctor = fields.Many2one('res.partner', string='Latest Consulting Doctor', domain="[('is_doctor', '=', True)]")

    
    # Previous tr   eatment history fields
    bool_1 = fields.Boolean(string='Consulted Psychiatrist')
    psychiatrist_psychologist = fields.Char(string='Psychiatrist / Psychologist')
    bool_2 = fields.Boolean(string='Consulted Counsellor / Psychologist')
    counseller_psychologist = fields.Many2one('res.partner', string='Counsellor / Psychologist', domain="[('doctor','=',True)]")
    bool_3 = fields.Boolean(string='Treated at Hospitals')
    hospital_1 = fields.Char(string='Hospital 1')
    hospital_2 = fields.Char(string='Hospital 2')
    hospital_3 = fields.Char(string='Hospital 3')
    bool_4 = fields.Boolean(string='Managed at home with proxy consultation and medicines')
    treated_in_rehab = fields.Boolean(string='Treated in a rehab')
    physical_condition = fields.Many2many('physical.condition', 'lead_physical_rel', 'lead_id', 'physic_condition_id', string='Physical Condition')
    referral = fields.Selection([
        ('psychiatrist', 'Psychiatrist'),
        ('counsellor', 'Counsellor or Psychologist'),
        ('none', 'None')
    ], string='Referral')

    # Consultation information
    total_consultations = fields.Integer(string='Total Consultations Availed', default=0)
    in_person_consultations = fields.Integer(string='In-Person Consultations Availed', default=0)
    virtual_consultations = fields.Integer(string='Virtual Consultations Availed', default=0)
    home_consultations = fields.Integer(string='Home-based Consultations Availed', default=0)
    free_screening = fields.Integer(string='Free Screening Availed', default=0)
    consultations_missed = fields.Integer(string='Consultations Missed', default=0)
    consultations_rescheduled = fields.Integer(string='Consultations Rescheduled', default=0)
    consultations_cancelled = fields.Integer(string='Consultations Cancelled', default=0)
    aggregate_feedback = fields.Float(string='Aggregate Feedback Score', default=0.0)

    # Registration form details
    registration_form_id = fields.Many2one('medical.registration.form', string='Registration Form')
    nationality = fields.Many2one('res.country', string='Nationality')
    religion = fields.Selection([
        ('Hindu', 'Hindu'),
        ('Muslim', 'Muslim'),
        ('Christian', 'Christian'),
        ('Sikh', 'Sikh'),
        ('Jain', 'Jain'),
        ('Other', 'Other')
    ], string='Religion')
    languages_known = fields.Many2many('language.master', 'lead_language_rel', 'lead_id', 'language_id', string='Languages Known')
    marital_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
        ('Seperated', 'Seperated'),
        ('Remarried', 'Remarried')
    ], string='Marital Status')
    have_child = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Do you have Children')
    no_child = fields.Integer(string='Number of Children', default=0)
    education_qualification = fields.Selection([
        ('Diploma', 'Diploma'),
        ('Graduate', 'Graduate'),
        ('Post Graduate', 'Post Graduate'),
        ('Others', 'Others')
    ], string='Education Qualification')
    occupation = fields.Selection([
        ('skilled_worker', 'Skilled Worker'),
        ('professional', 'Professional'),
        ('student', 'Student'),
        ('businessman', 'Businessman'),
        ('retired', 'Retired'),
        ('non_professional', 'Non Professional'),
        ('vocation', 'Family Vocation/craft'),
        ('industrilist', 'Industrialist'),
        ('none', 'None'),
        ('specify_any', 'Specify Vocation')
    ], string='Occupation')
    concerns_problems = fields.Text(string='Concerns/Problems')
    service_id = fields.Many2one('services.master', string='Services Looking for')

    # Lead activity data
    first_contacted = fields.Datetime(string='First Contacted')
    last_contacted = fields.Datetime(string='Last Contacted')
    last_heard_from = fields.Datetime(string='Last Heard From')
    last_opened_email = fields.Datetime(string='Last Opened Email')
    last_clicked_link = fields.Datetime(string='Last Clicked on Link in Email')
    emails_opened = fields.Integer(string='Emails Opened', default=0)
    unsubscribed_emails = fields.Boolean(string='Unsubscribed From Emails')
    documents_downloaded = fields.Integer(string='Documents Downloaded', default=0)
    helpline_calls = fields.Integer(string='Helpline calls', default=0)
    events_attended = fields.Integer(string='Events Attended', default=0)
    webinars_attended = fields.Integer(string='Webinars Attended', default=0)
    videos_watched = fields.Integer(string='Videos Watched on website', default=0)
    blogs_read = fields.Integer(string='Blogs Read on website', default=0)
    account_deleted = fields.Boolean(string='Account Deleted')
    subscription_opt_outs = fields.Selection([
        ('none', 'None'),
        ('all', 'All'),
        ('some', 'Some')
    ], string='Subscription Type opt-outs', default='none')
    subscription_opt_ins = fields.Selection([
        ('none', 'None'),
        ('all', 'All'),
        ('some', 'Some')
    ], string='Subscription Type opt-ins', default='none')
    whatsapp_sessions = fields.Integer(string='No. of WhatsApp Sessions', default=0)
    lead_score = fields.Integer(string='Lead Score', default=0)

    # Admission information
    lead_to_rehab = fields.Boolean(string='Lead passed to Rehab / Hospital')
    lead_to_hyderabad = fields.Boolean(string='Lead passed to Hyderabad')
    lead_to_mindtalk = fields.Boolean(string='Lead passed to Mindtalk')
    do_not_call = fields.Boolean(string='Do Not Call')
    latest_consulting_doctor = fields.Many2one('res.partner', string='Latest Consulting Doctor', domain="[('is_doctor', '=', True)]")

    # Relationship fields
    campus_id = fields.Many2one('campus.master', string='Campus')
    clinical_trail_ids = fields.One2many('medical.clinical.trail', 'lead_id', string='Clinical Trails')
    visit_activities_ids = fields.One2many('visits.activities', 'lead_id', string='Activities')
    customer_activity_ids = fields.One2many('customer.activity', 'lead_id', string='Customer Activities')
    slot_link_ids = fields.One2many('appointment.slot.link', 'lead_id', string='Slot Links')
    whatsapp_updates = fields.Boolean(string='Whatsapp Updates', default=True)
    aadhar_verification = fields.Boolean(string='Aadhar verification')
    languages_known = fields.Many2many('language.master', 
                                  'lead_language_rel', 
                                  'lead_id', 
                                  'language_id',
                                  string='Languages Known')


    lead_to_rehab = fields.Boolean(string='Lead passed to Rehab / Hospital')
    lead_to_hyderabad = fields.Boolean(string='Lead passed to Hyderabad')
    lead_to_mindtalk = fields.Boolean(string='Lead passed to Mindtalk')
    @api.model
    def create(self, vals):
        lead = super(CrmLead, self).create(vals)
        # If it's a new patient and patient details are provided, create patient record
        if lead.is_new_patient and lead.patient_name and not lead.patient_id:
            lead.create_patient_from_lead()
        return lead

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        for lead in self:
            # If patient details are updated and it's a new patient, create/update patient record
            if lead.is_new_patient and lead.patient_name and not lead.patient_id:
                lead.create_patient_from_lead()
        return res
    
   


    def create_patient_from_lead(self):
        """Create a new patient record from the lead information"""
        self.ensure_one()
        
        _logger.info("Starting create_patient_from_lead for lead: %s", self.id)
        
        # Skip if no patient name or if already linked to a patient
        if not self.patient_name or self.patient_id:
            _logger.info("Skipping patient creation: patient_name=%s, patient_id=%s", 
                        self.patient_name, self.patient_id)
            return False
        
        # Check if patient already exists with same mobile or email
        domain = []
        
        # Build domain correctly for OR conditions
        if self.patient_mobile and self.patient_email:
            _logger.info("Searching by both mobile and email: %s, %s", 
                        self.patient_mobile, self.patient_email)
            domain = ['|', '|',
                    ('mobile', '=', self.patient_mobile),
                    ('phone', '=', self.patient_mobile),
                    ('email', '=', self.patient_email)]
        elif self.patient_mobile:
            _logger.info("Searching by mobile only: %s", self.patient_mobile)
            domain = ['|',
                    ('mobile', '=', self.patient_mobile),
                    ('phone', '=', self.patient_mobile)]
        elif self.patient_email:
            _logger.info("Searching by email only: %s", self.patient_email)
            domain = [('email', '=', self.patient_email)]
        
        _logger.info("Search domain: %s", domain)
        
        existing_patient = False
        if domain:
            try:
                existing_patient = self.env['hospital.patient'].search(domain, limit=1)
                _logger.info("Existing patient search result: %s", existing_patient)
            except Exception as e:
                _logger.error("Error searching for existing patient: %s", e)
                # Fall back to a simpler search if complex domain fails
                if self.patient_mobile:
                    existing_patient = self.env['hospital.patient'].search([
                        ('mobile', '=', self.patient_mobile)
                    ], limit=1)
                    _logger.info("Fallback mobile search result: %s", existing_patient)
        
        if existing_patient:
            # Link to existing patient
            _logger.info("Linking lead to existing patient: %s", existing_patient.id)
            self.patient_id = existing_patient.id
            return existing_patient
        
        # Create new patient
        _logger.info("Creating new patient record for: %s", self.patient_name)
        patient_vals = {
            'name': self.patient_name,
            'mobile': self.patient_mobile,
            'email': self.patient_email,
            'gender': self.patient_sex.lower() if self.patient_sex else 'other',
            'blood_group': self.blood_group.lower() if self.blood_group else False,
            'dob': self.date_of_birth,
            'date_of_birth': self.date_of_birth,
        }
        
        # Add address fields if they exist
        if hasattr(self, 'street') and self.street:
            patient_vals['street'] = self.street
        
        if hasattr(self, 'city') and self.city:
            patient_vals['city'] = self.city
        
        if hasattr(self, 'state_id') and self.state_id:
            patient_vals['state_id'] = self.state_id.name if hasattr(self.state_id, 'name') else self.state_id
        
        if hasattr(self, 'zip') and self.zip:
            patient_vals['zip'] = self.zip
        
        if hasattr(self, 'country_id') and self.country_id:
            patient_vals['country_id'] = self.country_id.name if hasattr(self.country_id, 'name') else self.country_id
        
        # Add referred by if it exists
        if hasattr(self, 'referred_by') and self.referred_by:
            partner = self.env['res.partner'].search([('name', '=', self.referred_by)], limit=1)
            if partner:
                patient_vals['referred_by'] = partner.id
        
        # Add marital status if it exists
        if hasattr(self, 'marital_status') and self.marital_status:
            patient_vals['marital_status'] = self.marital_status.lower() if self.marital_status else 'single'
        
        _logger.info("Patient values for creation: %s", patient_vals)
        
        try:
            # Create the patient record
            new_patient = self.env['hospital.patient'].create(patient_vals)
            _logger.info("Successfully created patient: %s", new_patient.id)
            
            # Update the sequence for patient_id field if it uses 'New'
            if new_patient.patient_id == 'New':
                new_patient.patient_id = self.env['ir.sequence'].next_by_code('hospital.patient') or 'P-000'
                _logger.info("Updated patient ID to: %s", new_patient.patient_id)
            
            # Link this lead to the created patient
            self.patient_id = new_patient.id
            self.is_new_patient = False
            
            # Log a note in the chatter
            self.message_post(
                body=_("Created new patient record: %s") % new_patient.name,
                subtype_xmlid="mail.mt_note"
            )
            
            return new_patient
        
        except Exception as e:
            _logger.error("Failed to create patient: %s", e)
            raise ValidationError(_("Failed to create patient: %s") % str(e))
    
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.is_new_patient = False
            self.patient_name = self.patient_id.name
            self.patient_mobile = self.patient_id.mobile
            self.patient_email = self.patient_id.email
            self.date_of_birth = self.patient_id.dob or self.patient_id.date_of_birth
            self.patient_sex = self.patient_id.gender
            self.blood_group = self.patient_id.blood_group
            # Copy other relevant fields from patient record
        else:
            self.is_new_patient = True

    @api.onchange('patient_mobile', 'patient_email')
    def _onchange_patient_contact(self):
        """Search for existing patient based on mobile or email"""
        if self.patient_mobile or self.patient_email:
            domain = []
            if self.patient_mobile:
                domain.append('|')
                domain.append(('mobile', '=', self.patient_mobile))
                domain.append(('phone', '=', self.patient_mobile))
            if self.patient_email:
                domain.append(('email', '=', self.patient_email))
            
            if domain:
                existing_patient = self.env['hospital.patient'].search(domain, limit=1)
                if existing_patient and not self.patient_id:
                    self.patient_id = existing_patient.id
                    return {
                        'warning': {
                            'title': _('Existing Patient Found'),
                            'message': _('An existing patient was found and linked to this lead.')
                        }
                    }


    def _prepare_patient_values(self):
        """Prepare values for creating new patient record"""
        # First create or find partner
        partner_vals = {
            'name': self.patient_name,
            'phone': self.patient_mobile,
            'email': self.patient_email,
            'is_patient': True,
        }
            
        if self.patient_mobile or self.patient_email:
            domain = []
            if self.patient_mobile:
                domain.append(('phone', '=', self.patient_mobile))
            if self.patient_email:
                domain.append(('email', '=', self.patient_email))
            partner = self.env['res.partner'].search(domain, limit=1)
            
            if partner:
                partner.write(partner_vals)
            else:
                partner = self.env['res.partner'].create(partner_vals)
        else:
            partner = self.env['res.partner'].create(partner_vals)

        # Prepare patient values
        return {
            'partner_id': partner.id,
            'registration_number': self.env['ir.sequence'].next_by_code('medical.patient'),
            'date_of_birth': self.date_of_birth,
            'gender': self.patient_sex.lower() if self.patient_sex else False,
            'blood_group': self.blood_group,
            'lead_id': self.id,
        }


    # Action methods for buttons
    def action_proceed_to_admission(self):
        self.ensure_one()
        self.state = 'opportunity'
        return True

    def action_book_appointment(self):
        self.ensure_one()
        return {
            'name': _('Book Appointment'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'form',
            'context': {
                'default_patient_id': self.patient_id.id if self.patient_id else False,
                'default_lead_id': self.id
            },
            'target': 'new',
        }

    def action_book_package(self):
        self.ensure_one()
        return {
            'name': _('Book Package'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.package',
            'view_mode': 'form',
            'context': {
                'default_patient_id': self.patient_id.id if self.patient_id else False,
                'default_lead_id': self.id
            },
            'target': 'new',
        }

    # Methods for smart buttons
    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': _('Appointments'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.appointment',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
        }

    def action_view_registration_form(self):
        self.ensure_one()
        if self.registration_form_id:
            return {
                'name': _('Registration Form'),
                'type': 'ir.actions.act_window',
                'res_model': 'medical.registration.form',
                'view_mode': 'form',
                'res_id': self.registration_form_id.id,
            }
        return {
            'name': _('Registration Form'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.registration.form',
            'view_mode': 'form',
            'context': {'default_lead_id': self.id},
            'target': 'current',
        }

    def action_view_visits(self):
        self.ensure_one()
        return {
            'name': _('Visits'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.visits',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
        }

    def action_view_case_history(self):
        self.ensure_one()
        return {
            'name': _('Case History'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.case',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
        }

    def action_view_booked_package(self):
        self.ensure_one()
        return {
            'name': _('Booked Package'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.package',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
        }

    # Compute methods
    def _compute_appointment_count(self):
        for lead in self:
            lead.appointment_count = self.env['medical.appointment'].search_count([
                ('lead_id', '=', lead.id)
            ])

    def _compute_visit_count(self):
        for lead in self:
            lead.visit_count = self.env['crm.visits'].search_count([
                ('lead_id', '=', lead.id)
            ])


                

