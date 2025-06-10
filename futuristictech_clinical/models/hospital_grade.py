# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HospitalGrade(models.Model):
    _name = 'hospital.grade'
    _description = 'Grade/Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'school_id, year, name'
    
    name = fields.Char(string='Name', required=True, tracking=True, help="Grade or Department name (e.g., Grade 10, Computer Science)")
    year = fields.Char(string='Year', tracking=True, help="Academic year or level")
    curriculum = fields.Text(string='Curriculum', help="Optional curriculum description")
    
    # Relationship to school (only child institutions allowed)
    school_id = fields.Many2one(
        'hospital.hospital', 
        string='School/Institution', 
        required=True,
        domain="[('is_parent', '=', False), ('type', 'in', ['school', 'university', 'college'])]",
        ondelete='cascade',
        tracking=True,
        help="The school/institution this grade belongs to"
    )
    
    # Relationships
    classroom_ids = fields.One2many('hospital.classroom', 'grade_id', string='Classrooms/Sections')
    classroom_count = fields.Integer(compute='_compute_classroom_count', string='Classrooms')
    
    # Student and teacher counts (computed from classrooms)
    total_students = fields.Integer(compute='_compute_totals', string='Total Students')
    total_teachers = fields.Integer(compute='_compute_totals', string='Total Teachers')
    total_capacity = fields.Integer(compute='_compute_totals', string='Total Capacity')
    
    # Psychologist assignment
    psychologist_ids = fields.Many2many(
        'res.users',
        'grade_psychologist_rel',
        'grade_id',
        'user_id',
        string='Assigned Psychologists',
        # domain="[('groups_id', 'in', %(base.group_user)d)]",
        help="Psychologists assigned to this grade/department"
    )
    psychologist_count = fields.Integer(compute='_compute_psychologist_count', string='Psychologists')
    
    active = fields.Boolean(default=True)
    
    @api.depends('classroom_ids')
    def _compute_classroom_count(self):
        for record in self:
            record.classroom_count = len(record.classroom_ids)
    
    @api.depends('classroom_ids.student_count', 'classroom_ids.capacity', 'classroom_ids.teacher_id')
    def _compute_totals(self):
        for record in self:
            record.total_students = sum(classroom.student_count for classroom in record.classroom_ids)
            record.total_capacity = sum(classroom.capacity for classroom in record.classroom_ids)
            record.total_teachers = len(record.classroom_ids.filtered('teacher_id'))
    
    @api.depends('psychologist_ids')
    def _compute_psychologist_count(self):
        for record in self:
            record.psychologist_count = len(record.psychologist_ids)
    
    @api.constrains('school_id')
    def _check_school_is_child(self):
        for record in self:
            if record.school_id and record.school_id.is_parent:
                raise ValidationError(_('Grades can only be assigned to child institutions (schools), not parent organizations.'))
    
    def name_get(self):
        result = []
        for record in self:
            if record.year:
                name = f"{record.name} ({record.year})"
            else:
                name = record.name
            result.append((record.id, name))
        return result
    
    def action_view_classrooms(self):
        """Smart button action to view classrooms"""
        self.ensure_one()
        return {
            'name': _('Classrooms'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.classroom',
            'type': 'ir.actions.act_window',
            'domain': [('grade_id', '=', self.id)],
            'context': {
                'default_grade_id': self.id,
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


class HospitalClassroom(models.Model):
    _name = 'hospital.classroom'
    _description = 'Classroom/Section'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'grade_id, name'
    
    name = fields.Char(string='Name', required=True, tracking=True, help="Classroom or section name (e.g., Section A, Room 101)")
    capacity = fields.Integer(string='Capacity', default=30, tracking=True, help="Maximum number of students")
    
    # Relationship to grade
    grade_id = fields.Many2one(
        'hospital.grade', 
        string='Grade/Department', 
        required=True,
        ondelete='cascade',
        tracking=True,
        help="The grade/department this classroom belongs to"
    )
    
    # Related school field for easy access
    school_id = fields.Many2one(
        'hospital.hospital',
        string='School',
        related='grade_id.school_id',
        store=True,
        readonly=True
    )
    
    # Teacher assignment
    teacher_id = fields.Many2one(
        'res.users',
        string='Assigned Teacher',
        # domain="[('groups_id', 'in', %(base.group_user)d)]",
        tracking=True,
        help="Teacher assigned to this classroom"
    )
    
    # Students assignment (Many2many with res.partner or create custom student model)
    student_ids = fields.Many2many(
        'res.partner',
        'classroom_student_rel',
        'classroom_id',
        'student_id',
        string='Assigned Students',
        domain="[('is_company', '=', False)]",
        help="Students assigned to this classroom"
    )
    student_count = fields.Integer(compute='_compute_student_count', string='Students')
    
    # Capacity utilization
    utilization_percentage = fields.Float(compute='_compute_utilization', string='Utilization %')
    is_overcapacity = fields.Boolean(compute='_compute_utilization', string='Over Capacity')
    
    # Psychologist assignment (inherited from grade or specific)
    psychologist_ids = fields.Many2many(
        'res.users',
        'classroom_psychologist_rel',
        'classroom_id',
        'user_id',
        string='Assigned Psychologists',
        # domain="[('groups_id', 'in', %(base.group_user)d)]",
        help="Psychologists assigned specifically to this classroom"
    )
    psychologist_count = fields.Integer(compute='_compute_psychologist_count', string='Psychologists')
    
    # Get all psychologists (from classroom + grade + school)
    all_psychologist_ids = fields.Many2many(
        'res.users',
        compute='_compute_all_psychologists',
        string='All Available Psychologists',
        help="All psychologists available to this classroom (from classroom, grade, and school level)"
    )
    
    active = fields.Boolean(default=True)
    
    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)
    
    @api.depends('student_count', 'capacity')
    def _compute_utilization(self):
        for record in self:
            if record.capacity > 0:
                record.utilization_percentage = (record.student_count / record.capacity) * 100
                record.is_overcapacity = record.student_count > record.capacity
            else:
                record.utilization_percentage = 0
                record.is_overcapacity = False
    
    @api.depends('psychologist_ids')
    def _compute_psychologist_count(self):
        for record in self:
            record.psychologist_count = len(record.psychologist_ids)
    
    @api.depends('psychologist_ids', 'grade_id.psychologist_ids', 'school_id.psychologist_ids')
    def _compute_all_psychologists(self):
        for record in self:
            all_psychologists = record.psychologist_ids
            if record.grade_id:
                all_psychologists |= record.grade_id.psychologist_ids
            if record.school_id:
                all_psychologists |= record.school_id.psychologist_ids
            record.all_psychologist_ids = all_psychologists
    
    @api.constrains('student_count', 'capacity')
    def _check_capacity(self):
        for record in self:
            if record.capacity > 0 and record.student_count > record.capacity:
                # This is just a warning, not a hard constraint
                pass
    
    def name_get(self):
        result = []
        for record in self:
            if record.grade_id:
                name = f"{record.grade_id.name} - {record.name}"
            else:
                name = record.name
            result.append((record.id, name))
        return result
    
    def action_view_students(self):
        """Smart button action to view students"""
        self.ensure_one()
        return {
            'name': _('Students'),
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.student_ids.ids)],
            'context': {
                'default_is_company': False,
            }
        }
    
    def action_view_psychologists(self):
        """Smart button action to view all available psychologists"""
        self.ensure_one()
        return {
            'name': _('Available Psychologists'),
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.all_psychologist_ids.ids)],
        }