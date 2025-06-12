from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    speciality_id = fields.Many2one(
        'partner.speciality',
        string='Speciality',
        help='Partner speciality or profession'
    )

    # Role field to define the type of contact
    contact_role = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('psychologist', 'Psychologist'),
        ('other', 'Other'),
    ], string='Role', default='other', tracking=True, 
       help="Define the role of this contact in the institution")
    
    # Student-specific fields
    student_id = fields.Char(string='Student ID', help="Unique student identification number")
    enrollment_date = fields.Date(string='Enrollment Date', help="Date when student was enrolled")
    graduation_date = fields.Date(string='Graduation Date', help="Expected or actual graduation date")
    
    # Parent-Student relationship
    child_ids = fields.Many2many(
        'res.partner',
        'parent_child_rel',
        'parent_id',
        'child_id',
        string='Children',
        domain="[('contact_role', '=', 'student'), ('is_company', '=', False)]",
        help="Students linked to this parent"
    )
    parent_ids = fields.Many2many(
        'res.partner',
        'parent_child_rel',
        'child_id',
        'parent_id',
        string='Parents/Guardians',
        domain="[('contact_role', '=', 'parent'), ('is_company', '=', False)]",
        help="Parents/Guardians linked to this student"
    )
    login = fields.Char(
        string='Login',
        help="Login username for the contact, used for online systems"
    )
    
    # Classroom assignment for students
    classroom_ids = fields.Many2many(
        'hospital.classroom',
        'classroom_student_rel',
        'student_id',
        'classroom_id',
        string='Assigned Classrooms'
    )
    
    # Teacher-specific fields
    teacher_subject = fields.Char(string='Subject Specialization', help="Primary subject taught by teacher")
    teacher_qualification = fields.Text(string='Qualifications', help="Educational qualifications and certifications")
    
    # Employee fields
    employee_id = fields.Char(string='Employee ID', help="Unique employee identification number")
    department = fields.Char(string='Department', help="Department where employee works")
    
    # Psychologist-specific fields
    license_number = fields.Char(string='License Number', help="Professional license number for psychologist")
    specialization = fields.Text(string='Specialization', help="Areas of psychological specialization")
    
    # Computed fields
    child_count = fields.Integer(compute='_compute_child_count', string='Children Count')
    parent_count = fields.Integer(compute='_compute_parent_count', string='Parents Count')
    
    # School/Institution assignment
    institution_ids = fields.Many2many(
        'hospital.hospital',
        'partner_institution_rel',
        'partner_id',
        'institution_id',
        string='Associated Institutions',
        help="Institutions this contact is associated with"
    )
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)
    
    @api.depends('parent_ids')
    def _compute_parent_count(self):
        for record in self:
            record.parent_count = len(record.parent_ids)
    
    @api.constrains('child_ids', 'contact_role')
    def _check_parent_role(self):
        for record in self:
            if record.child_ids and record.contact_role != 'parent':
                raise ValidationError(_('Only contacts with role "Parent" can have children assigned.'))
    
    @api.constrains('parent_ids', 'contact_role')
    def _check_student_role(self):
        for record in self:
            if record.parent_ids and record.contact_role != 'student':
                raise ValidationError(_('Only contacts with role "Student" can have parents assigned.'))
    
    @api.constrains('child_ids', 'parent_ids')
    def _check_circular_relationship(self):
        """Prevent circular parent-child relationships"""
        for record in self:
            if record.id in record.child_ids.ids:
                raise ValidationError(_('A contact cannot be both parent and child of themselves.'))
            if record.id in record.parent_ids.ids:
                raise ValidationError(_('A contact cannot be both parent and child of themselves.'))
    
    @api.onchange('contact_role')
    def _onchange_contact_role(self):
        """Clear inappropriate fields when role changes"""
        if self.contact_role != 'student':
            self.student_id = False
            self.enrollment_date = False
            self.graduation_date = False
            self.parent_ids = [(6, 0, [])]
            self.classroom_ids = [(6, 0, [])]
        elif self.contact_role != 'parent':
            self.child_ids = [(6, 0, [])]
        elif self.contact_role != 'teacher':
            self.teacher_subject = False
            self.teacher_qualification = False
        elif self.contact_role != 'psychologist':
            self.license_number = False
            self.specialization = False
        elif self.contact_role not in ['employee', 'manager']:
            self.employee_id = False
            self.department = False
    
    def name_get(self):
        """Enhanced name display with role"""
        result = []
        for record in self:
            name = record.name or ''
            if record.contact_role and record.contact_role != 'other':
                role_dict = dict(record._fields['contact_role'].selection)
                role_name = role_dict.get(record.contact_role, '')
                if record.student_id and record.contact_role == 'student':
                    name = f"{name} ({role_name} - {record.student_id})"
                elif record.employee_id and record.contact_role in ['employee', 'manager']:
                    name = f"{name} ({role_name} - {record.employee_id})"
                else:
                    name = f"{name} ({role_name})"
            result.append((record.id, name))
        return result
    
    def action_view_children(self):
        """Action to view children of a parent"""
        self.ensure_one()
        return {
            'name': _('Children'),
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.child_ids.ids)],
            'context': {'default_contact_role': 'student'}
        }
    
    def action_view_parents(self):
        """Action to view parents of a student"""
        self.ensure_one()
        return {
            'name': _('Parents/Guardians'),
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.parent_ids.ids)],
            'context': {'default_contact_role': 'parent'}
        }
    
    @api.model
    def create_student_with_parents(self, student_vals, parent_vals_list):
        """Helper method to create a student with associated parents"""
        student = self.create(dict(student_vals, contact_role='student'))
        
        parent_ids = []
        for parent_vals in parent_vals_list:
            parent = self.create(dict(parent_vals, contact_role='parent'))
            parent_ids.append(parent.id)
        
        if parent_ids:
            student.write({'parent_ids': [(6, 0, parent_ids)]})
        
        return student

class PartnerSpeciality(models.Model):
    _name = 'partner.speciality'
    _description = 'Partner Speciality'
    _order = 'name'

    name = fields.Char(
        string='Speciality Name',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Code',
        help='Short code for the speciality'
    )
    description = fields.Text(
        string='Description',
        translate=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Speciality code must be unique!')
    ]