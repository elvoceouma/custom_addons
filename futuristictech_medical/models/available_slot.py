# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class AvailableSlot(models.Model):
    _name = 'available.slot'
    _description = 'Available Time Slots for Appointments'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'from_date desc'
    _rec_name = 'display_name'

    # Basic Information
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    user_id = fields.Many2one('res.users', string='Created By', required=True, 
                              default=lambda self: self.env.user, readonly=True)
    # Fix later if needed
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True, tracking=True,
                                # domain="[('active_doctor', '=', True), ('is_company', '=', False), "
                                #        "('doctor', '=', True), ('book_appointments', '=', True)]"
                                       )
    
    # Campus Information
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    show_sub_campus = fields.Boolean(string='Show Sub Campus', compute='_compute_show_sub_campus')
    sub_campus_id = fields.Many2one('hospital.hospital', string='Sub Campus', tracking=True,
                                    domain="[('parent_id', '=', campus_id)]")
    
    # Time Configuration
    create_type = fields.Selection([
        ('Date', 'Date Range'),
        ('Days', 'Specific Days')
    ], string='Create Type', default='Date', required=True, tracking=True)
    
    from_date = fields.Date(string='From Date', required=True, tracking=True)
    to_date = fields.Date(string='To Date', required=True, tracking=True)
    duration = fields.Integer(string='Duration in Days', default=1)
    
    # Day Selection (for 'Days' type)
    monday = fields.Boolean(string='Monday', default=True)
    tuesday = fields.Boolean(string='Tuesday', default=True)
    wednesday = fields.Boolean(string='Wednesday', default=True)
    thursday = fields.Boolean(string='Thursday', default=True)
    friday = fields.Boolean(string='Friday', default=True)
    saturday = fields.Boolean(string='Saturday', default=False)
    sunday = fields.Boolean(string='Sunday', default=False)
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('booked', 'Booked')
    ], string='State', default='draft', required=True, tracking=True)
    
    # Related Lines
    shift_line = fields.One2many('available.slot.shift', 'slot_id', string='Working Time')
    slot_line = fields.One2many('slot.booking', 'available_slot_id', string='Generated Slots')
    
    # Statistics
    slot_count = fields.Integer(string='Slot Count', compute='_compute_slot_count')
    
    @api.depends('doctor_id', 'from_date', 'to_date')
    def _compute_display_name(self):
        for record in self:
            if record.doctor_id and record.from_date:
                if record.to_date and record.from_date != record.to_date:
                    record.display_name = f"{record.doctor_id.name} ({record.from_date} to {record.to_date})"
                else:
                    record.display_name = f"{record.doctor_id.name} ({record.from_date})"
            else:
                record.display_name = _('New Time Slot')
    
    @api.depends('campus_id')
    def _compute_show_sub_campus(self):
        for record in self:
            # Check if the campus has sub-campuses
            sub_campuses = self.env['hospital.hospital'].search([('parent_id', '=', record.campus_id.id)])
            record.show_sub_campus = bool(sub_campuses)
    
    @api.depends('slot_line')
    def _compute_slot_count(self):
        for record in self:
            record.slot_count = len(record.slot_line)
    
    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        for record in self:
            if record.from_date and record.to_date:
                if record.from_date > record.to_date:
                    raise ValidationError(_("From Date cannot be later than To Date."))
    
    @api.constrains('shift_line')
    def _check_shift_lines(self):
        for record in self:
            if not record.shift_line:
                raise ValidationError(_("Please add at least one working time slot."))
            
            for shift in record.shift_line:
                if shift.from_time >= shift.to_time:
                    raise ValidationError(_("Start time must be before end time in working hours."))
    
    def generate(self):
        """Generate time slots based on configuration"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Can only generate slots from draft state."))
        
        if not self.shift_line:
            raise UserError(_("Please configure working time before generating slots."))
        
        # Clear existing slots
        self.slot_line.unlink()
        
        generated_slots = []
        current_date = self.from_date
        
        while current_date <= self.to_date:
            # Check if we should create slots for this day
            if self._should_create_slots_for_day(current_date):
                for shift in self.shift_line:
                    slots = self._generate_slots_for_shift(current_date, shift)
                    generated_slots.extend(slots)
            
            current_date += timedelta(days=1)
        
        if generated_slots:
            self.env['slot.booking'].create(generated_slots)
            self.state = 'generated'
            self.message_post(
                body=_("Generated %s time slots successfully.") % len(generated_slots),
                subtype_xmlid="mail.mt_note"
            )
        else:
            raise UserError(_("No slots were generated. Please check your configuration."))
        
        return True
    
    def _should_create_slots_for_day(self, date):
        """Check if slots should be created for the given date"""
        if self.create_type == 'Date':
            return True
        
        # For 'Days' type, check the day of week
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        day_mapping = {
            0: self.monday,
            1: self.tuesday,
            2: self.wednesday,
            3: self.thursday,
            4: self.friday,
            5: self.saturday,
            6: self.sunday,
        }
        return day_mapping.get(weekday, False)
    
    def _generate_slots_for_shift(self, date, shift):
        """Generate individual slots for a shift on a specific date"""
        slots = []
        
        # Convert float time to datetime
        start_time = self._float_to_time(shift.from_time)
        end_time = self._float_to_time(shift.to_time)
        
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        # Generate slots with the specified interval
        current_time = start_datetime
        while current_time + timedelta(minutes=shift.interval) <= end_datetime:
            slot_end = current_time + timedelta(minutes=shift.interval)
            
            # Prepare slot values
            slot_vals = {
                'available_slot_id': self.id,
                'name': self.env['ir.sequence'].next_by_code('slot.booking') or _('New'),
                'doctor_id': self.doctor_id.id,
                'campus_id': self.campus_id.id,
                'sub_campus_id': self.sub_campus_id.id if self.sub_campus_id else False,
                'start_datetime': current_time,
                'stop_datetime': slot_end,
                'consultation_type_ids': [(6, 0, shift.consultation_type_ids.ids)],
                'availability': 'open',
                'amount': 0.0,
                'payment_mode': 'cash',
            }
            
            # Set consultation type for backwards compatibility
            if shift.consultation_type_ids:
                consultation_types = shift.consultation_type_ids.mapped('name')
                if 'Virtual Consultation' in consultation_types:
                    slot_vals['consultation_type'] = 'Virtual Consultation'
                elif 'Home-Based Consultation' in consultation_types:
                    slot_vals['consultation_type'] = 'Home-Based Consultation'
                else:
                    slot_vals['consultation_type'] = 'In-person Consultation'
            
            slots.append(slot_vals)
            current_time = slot_end
        
        return slots
    
    def _float_to_time(self, float_time):
        """Convert float time to time object"""
        hours = int(float_time)
        minutes = int((float_time % 1) * 60)
        return datetime.min.time().replace(hour=hours, minute=minutes)
    
    def action_view_slots(self):
        """View generated slots"""
        self.ensure_one()
        return {
            'name': _('Generated Slots'),
            'type': 'ir.actions.act_window',
            'res_model': 'slot.booking',
            'view_mode': 'tree,form',
            'domain': [('available_slot_id', '=', self.id)],
            'context': {
                'default_available_slot_id': self.id,
                'default_doctor_id': self.doctor_id.id,
                'default_campus_id': self.campus_id.id,
            },
            'target': 'current',
        }
    
    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.ensure_one()
        self.slot_line.unlink()
        self.state = 'draft'
        return True


class AvailableSlotShift(models.Model):
    _name = 'available.slot.shift'
    _description = 'Working Time Configuration for Slots'
    _order = 'from_time'

    slot_id = fields.Many2one('available.slot', string='Slot Configuration', required=True, ondelete='cascade')
    from_time = fields.Float(string='Start Time', required=True, help='Start time in 24-hour format')
    to_time = fields.Float(string='End Time', required=True, help='End time in 24-hour format')
    interval = fields.Integer(string='Interval (Minutes)', required=True, default=45,
                              help='Duration of each appointment slot in minutes')
    consultation_type_ids = fields.Many2many(
        'consultation.type',
        'slot_shift_consultation_type_rel',
        'shift_id',
        'consultation_type_id',
        string='Consultation Types',
        required=True
    )
    
    @api.constrains('from_time', 'to_time')
    def _check_times(self):
        for record in self:
            if record.from_time >= record.to_time:
                raise ValidationError(_("Start time must be before end time."))
            
            if record.from_time < 0 or record.from_time >= 24:
                raise ValidationError(_("Start time must be between 0:00 and 23:59."))
            
            if record.to_time < 0 or record.to_time > 24:
                raise ValidationError(_("End time must be between 0:01 and 24:00."))
    
    @api.constrains('interval')
    def _check_interval(self):
        for record in self:
            if record.interval <= 0:
                raise ValidationError(_("Interval must be greater than 0 minutes."))
            
            if record.interval > 480:  # 8 hours
                raise ValidationError(_("Interval cannot be more than 480 minutes (8 hours)."))