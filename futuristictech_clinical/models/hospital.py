# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Hospital(models.Model):
    _name = 'hospital.hospital'
    _description = 'Hospital/Institution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    complete_name = fields.Char(
        string='Complete Name', compute='_compute_complete_name',
        recursive=True, store=True)
    code = fields.Char(string='Code', tracking=True)
    type = fields.Selection([
        ('organization', 'Organization'),
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('nursing_home', 'Nursing Home'),
        ('community_health_center', 'Community Health Center'),
        ('military_hospital', 'Military Health Center'),
        ('school', 'School'),
        ('university', 'University'),
        ('college', 'College'),
        ('others', 'Others'),
    ], string='Type', required=True, default='organization')
    image = fields.Binary(string='Image')
    
    # Hierarchy fields
    parent_id = fields.Many2one(
        'hospital.hospital', 
        string='Parent Organization', 
        index=True, 
        ondelete='cascade',
        tracking=True,
        help="The parent organization/institution"
    )
    child_ids = fields.One2many(
        'hospital.hospital', 
        'parent_id', 
        string='Child Organizations'
    )
    parent_path = fields.Char(index=True)
    is_parent = fields.Boolean(
        string='Is Parent Organization', 
        compute='_compute_is_parent', 
        store=True,
        help="Automatically computed based on whether this organization has children"
    )
    child_count = fields.Integer(
        string='Child Count', 
        compute='_compute_child_count',
        help="Number of direct child organizations"
    )
    
    # Address fields
    address = fields.Text(string='Address')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip = fields.Char(string='ZIP')
    country = fields.Char(string='Country')
    
    # Contact fields
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    
    active = fields.Boolean(default=True)
    
    # Relationships
    block_ids = fields.One2many('hospital.block', 'hospital_id', string='Blocks')
    pharmacy_ids = fields.One2many('hospital.pharmacy', 'hospital_id', string='Pharmacies')
    grade_ids = fields.One2many('hospital.grade', 'school_id', string='Grades/Departments')
    classroom_ids = fields.One2many('hospital.classroom', 'school_id', string='Classrooms/Sections')
    
    # Counts
    block_count = fields.Integer(compute='_compute_block_count', string='Blocks')
    pharmacy_count = fields.Integer(compute='_compute_pharmacy_count', string='Pharmacies')
    grade_count = fields.Integer(compute='_compute_grade_count', string='Grades')
    classroom_count = fields.Integer(compute='_compute_classroom_count', string='Classrooms')
    total_students = fields.Integer(compute='_compute_student_totals', string='Total Students')
    total_teachers = fields.Integer(compute='_compute_student_totals', string='Total Teachers')
    
    medicine_register_ids = fields.One2many('medicine.register', 'campus_id', string='Medicine Registers')
    
    # Psychologist assignment (for mental health platform)
    psychologist_ids = fields.Many2many(
        'res.users',
        'hospital_psychologist_rel',
        'hospital_id',
        'user_id',
        string='Assigned Psychologists',
        # domain="[('groups_id', 'in', %(base.group_user)d)]",
        help="Psychologists assigned to this organization/institution"
    )
    psychologist_count = fields.Integer(
        compute='_compute_psychologist_count',
        string='Psychologists'
    )
    
    # Inventory-related fields
    patient_requisition_picking_type_id = fields.Many2one('stock.picking.type', string='Patient Requisition Picking Type')
    store_clearance_picking_type_id = fields.Many2one('stock.picking.type', string='Store Clearance Picking Type')
    medicine_packing_picking_type_id = fields.Many2one('stock.picking.type', string='Medicine Packing Picking Type')
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = f"{record.parent_id.complete_name} / {record.name}"
            else:
                record.complete_name = record.name
    
    @api.depends('child_ids')
    def _compute_is_parent(self):
        for record in self:
            record.is_parent = bool(record.child_ids)
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)
    
    @api.depends('grade_ids')
    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)
    
    @api.depends('classroom_ids')
    def _compute_classroom_count(self):
        for record in self:
            record.classroom_count = len(record.classroom_ids)
    
    @api.depends('classroom_ids.student_count', 'classroom_ids.teacher_id')
    def _compute_student_totals(self):
        for record in self:
            record.total_students = sum(classroom.student_count for classroom in record.classroom_ids)
            record.total_teachers = len(record.classroom_ids.filtered('teacher_id'))
    
    @api.depends('block_ids')
    def _compute_block_count(self):
        for record in self:
            record.block_count = len(record.block_ids)
    
    @api.depends('pharmacy_ids')
    def _compute_pharmacy_count(self):
        for record in self:
            record.pharmacy_count = len(record.pharmacy_ids)
    
    @api.depends('psychologist_ids')
    def _compute_psychologist_count(self):
        for record in self:
            record.psychologist_count = len(record.psychologist_ids)
    
    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive organizations.'))
    
    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]
    
    def name_get(self):
        def get_names(cat):
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return " / ".join(reversed(res))
        return [(record.id, get_names(record)) for record in self]

    def action_view_grades(self):
        """Smart button action to view grades"""
        self.ensure_one()
        return {
            'name': _('Grades & Departments'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.grade',
            'type': 'ir.actions.act_window',
            'domain': [('school_id', '=', self.id)],
            'context': {
                'default_school_id': self.id,
            }
        }
    
    def action_view_classrooms(self):
        """Smart button action to view classrooms"""
        self.ensure_one()
        return {
            'name': _('Classrooms & Sections'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.classroom',
            'type': 'ir.actions.act_window',
            'domain': [('school_id', '=', self.id)],
            'context': {
                'default_grade_id': False,  # Will be set when grade is selected
            }
        }

    def action_view_blocks(self):
        """Smart button action to view blocks"""
        self.ensure_one()
        return {
            'name': _('Blocks'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.block',
            'type': 'ir.actions.act_window',
            'domain': [('hospital_id', '=', self.id)],
            'context': {
                'default_hospital_id': self.id,
            }
        }
    
    def action_view_pharmacies(self):
        """Smart button action to view pharmacies"""
        self.ensure_one()
        return {
            'name': _('Pharmacies'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.pharmacy',
            'type': 'ir.actions.act_window',
            'domain': [('hospital_id', '=', self.id)],
            'context': {
                'default_hospital_id': self.id,
            }
        }
    
    def action_view_children(self):
        """Smart button action to view child organizations"""
        self.ensure_one()
        return {
            'name': _('Child Organizations'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.hospital',
            'type': 'ir.actions.act_window',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
            }
        }
    
    def action_view_psychologists(self):
        """Smart button action to view assigned psychologists"""
        self.ensure_one()
        return {
            'name': _('Assigned Psychologists'),
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.psychologist_ids.ids)],
        }
        
    def action_hospital_room(self):
        return {
            'name': _('Rooms'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.room',
            'type': 'ir.actions.act_window',
            'domain': [('hospital_id', '=', self.id)],
        }
    
    def get_all_children(self, include_self=False):
        """Get all children recursively"""
        children = self.env['hospital.hospital']
        if include_self:
            children |= self
        for child in self.child_ids:
            children |= child
            children |= child.get_all_children()
        return children
    
    def get_root_parent(self):
        """Get the root parent organization"""
        if not self.parent_id:
            return self
        return self.parent_id.get_root_parent()