from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HospitalCaretakerAllotment(models.Model):
    _name = 'hospital.caretaker.allotment'
    _description = 'Caretaker Allotment Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Status fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # --- Main Information ---
    name = fields.Char(
        string='Requisition Reference',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    caretaker_id = fields.Many2one(
        'hospital.caretaker',
        string='Caretaker',
        tracking=True,
        domain="[('caretaker_type_id', '=', caretaker_type_id)]"
    )
    patient_id = fields.Many2one(
        'hospital.patient',
        string='Patient',
        required=True,
        tracking=True
    )
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Admission',
        domain="[('state','!=','discharge_advised')]",
        tracking=True
    )
    health_center_id = fields.Many2one(
        'hospital.hospital',
        string='Health Center',
        tracking=True
    )
    building_id = fields.Many2one(
        'hospital.building',
        string='Building',
        tracking=True
    )
    purpose = fields.Text(string='Purpose', tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        readonly=True
    )
    caretaker_type_id = fields.Many2one(
        'hospital.caretaker.type',
        string='Caretaker Type',
        tracking=True
    )

    # --- Type of assignment ---
    type = fields.Selection([
        ('finite', 'Finite Period'),
        ('infinite', 'Ongoing Assignment')
    ], string='Assignment Type', default='finite', required=True, tracking=True)

    # --- Date fields based on type ---
    start_date = fields.Date(
        string='Period Start Date',
        tracking=True,
        readonly=False
    )
    end_date = fields.Date(
        string='Period End Date',
        tracking=True,
        readonly=False
    )
    infinite_start_date = fields.Date(
        string='Assignment Start Date',
        tracking=True,
        readonly=False
    )

    @api.depends('state')
    def _compute_readonly_fields(self):
        for record in self:
            is_readonly = record.state == 'approved'
            record.start_date_readonly = is_readonly
            record.end_date_readonly = is_readonly
            record.infinite_start_date_readonly = is_readonly

    # --- Approval and User Information ---
    user_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )
    approved_date = fields.Datetime(
        string='Approved Date',
        readonly=True,
        tracking=True
    )

    # --- Cancellation Information ---
    cancelled_by = fields.Many2one(
        'res.users',
        string='Cancelled By',
        readonly=True,
        tracking=True
    )
    cancelled_date = fields.Datetime(
        string='Cancelled Date',
        readonly=True,
        tracking=True
    )
    cancel_reason = fields.Text(
        string='Cancellation Reason',
        readonly=True,
        tracking=True
    )

    # --- Caretaker Register related fields ---
    caretaker_register_ids = fields.Many2many(
        'hospital.caretaker.register',
        string='Caretaker Registers'
    )
    caretaker_register_count = fields.Integer(
        string='Caretaker Register Count',
        compute='_compute_caretaker_register_count'
    )

    # --- Computed Fields & Constraints ---
    @api.depends('caretaker_register_ids')
    def _compute_caretaker_register_count(self):
        for record in self:
            record.caretaker_register_count = len(record.caretaker_register_ids)

    @api.constrains('start_date', 'end_date', 'type')
    def _check_finite_dates(self):
        for record in self:
            if record.type == 'finite':
                if not record.start_date:
                    raise ValidationError(_("Start Date is required for a finite period assignment."))
                if record.start_date and record.end_date and record.start_date > record.end_date:
                    raise ValidationError(_("Period End Date cannot be earlier than Period Start Date."))

    @api.constrains('infinite_start_date', 'type')
    def _check_infinite_date(self):
        for record in self:
            if record.type == 'infinite' and not record.infinite_start_date:
                raise ValidationError(_("Assignment Start Date is required for an ongoing assignment."))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.caretaker.allotment') or _('New')
        return super().create(vals)

    # --- Actions ---
    def action_approve(self):
        for record in self:
            if record.state != 'draft':
                continue
            
            if record.type == 'finite' and not record.start_date:
                raise ValidationError(_("Start Date is required for a finite period assignment before approval."))
            if record.type == 'infinite' and not record.infinite_start_date:
                raise ValidationError(_("Assignment Start Date is required for an ongoing assignment before approval."))
            if not record.caretaker_id:
                raise ValidationError(_("A Caretaker must be selected before approving the requisition."))

            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            record.message_post(body=_("Caretaker requisition approved."))
        return True

    def action_cancel(self):
        return {
            'name': _('Cancel Requisition'),
            'type': 'ir.actions.act_window',
            'res_model': 'caretaker.requisition.cancel',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_requisition_id': self.id},
        }

    def view_caretaker_register(self):
        self.ensure_one()
        return {
            'name': _('Caretaker Register Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.caretaker.register',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.caretaker_register_ids.ids)],
            'target': 'current',
        }

    def action_do_cancel(self, reason):
        for record in self:
            if record.state != 'approved':
                continue
                
            record.write({
                'state': 'cancelled',
                'cancelled_by': self.env.user.id,
                'cancelled_date': fields.Datetime.now(),
                'cancel_reason': reason,
            })
            record.message_post(body=_("Caretaker requisition cancelled. Reason: %s") % reason)
        return True
    
class HospitalCaretakerType(models.Model):
    _name = 'hospital.caretaker.type'
    _description = 'Caretaker Type'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HospitalSpecialPrivileges(models.Model):
    _name = 'hospital.special.privileges'
    _description = 'Special Privileges'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.inpatient.admission', string='Inpatient Admission',
                                            domain="[('state','!=','discharge_advised')]", tracking=True)
    purpose = fields.Text(string='Purpose', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Privilege Type and Time Periods
    privilege_type = fields.Selection([
        ('finite', 'Finite'),
        ('infinite', 'Infinite')
    ], string='Privilege Type', default='finite', tracking=True)
    
    type = fields.Selection([
        ('days', 'Days'),
        ('continuous', 'Continuous')
    ], string='Type', default='continuous', tracking=True)
    
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    
    # Days of week
    sunday = fields.Boolean(string='Sunday')
    monday = fields.Boolean(string='Monday')
    tuesday = fields.Boolean(string='Tuesday')
    wednesday = fields.Boolean(string='Wednesday')
    thursday = fields.Boolean(string='Thursday')
    friday = fields.Boolean(string='Friday')
    saturday = fields.Boolean(string='Saturday')
    
    # Lines
    privilege_line_ids = fields.One2many('hospital.special.privileges.line', 'special_privilege_id', 
                                         string='Privilege Lines')
    
    # Using a shorter relation table name to avoid PostgreSQL identifier length limitation
    special_privilege_register_ids = fields.Many2many(
        'hospital.special.privilege.register', 
        relation='hosp_priv_reg_rel',  # Shortened relation table name
        string='Special Privilege Register'
    )
    special_privilege_register_count = fields.Integer(
        string='Special Privilege Register Count', 
        compute='_compute_special_privilege_register_count'
    )
    
    # Cancellation fields
    cancelled_date = fields.Date(string='Cancelled Date')
    cancelled_by = fields.Many2one('res.users', string='Cancelled By')
    cancel_reason = fields.Text(string='Cancel Reason')
    
    # Other fields
    approved_by = fields.Many2one('res.users', string='Approved By')
    notes = fields.Text(string='Notes')
    
    # Status field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.depends('special_privilege_register_ids')
    def _compute_special_privilege_register_count(self):
        for record in self:
            record.special_privilege_register_count = len(record.special_privilege_register_ids)
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id
        })

    def action_cancel(self):
        self.write({
            'state': 'cancelled',
            'cancelled_by': self.env.user.id,
            'cancelled_date': fields.Date.today()
        })
        return True
    
    def view_special_privilege_register(self):
        return {
            'name': _('Special Privilege Register'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.special.privilege.register',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.special_privilege_register_ids.ids)],
            'context': {'default_special_privilege_id': self.id}
        }


class HospitalSpecialPrivilegesLine(models.Model):
    _name = 'hospital.special.privileges.line'
    _description = 'Special Privileges Line'
    
    special_privilege_id = fields.Many2one('hospital.special.privileges', string='Special Privilege')
    product_id = fields.Many2one('product.product', string='Product', 
                                domain="[('special_privilege','=',True)]", required=True)
    morning = fields.Boolean(string='Morning')
    afternoon = fields.Boolean(string='Afternoon')
    evening = fields.Boolean(string='Evening')
    night = fields.Boolean(string='Night')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    @api.depends('price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.price_unit


class HospitalSpecialPrivilegeRegister(models.Model):
    _name = 'hospital.special.privilege.register'
    _description = 'Hospital Special Privilege Register'
    
    name = fields.Char(string='Name')
    
    # Use the same relation table name as defined in HospitalSpecialPrivileges
    special_privileges_ids = fields.Many2many(
        'hospital.special.privileges',
        relation='hosp_priv_reg_rel',  # Must match the one in HospitalSpecialPrivileges
        string='Special Privileges'
    )