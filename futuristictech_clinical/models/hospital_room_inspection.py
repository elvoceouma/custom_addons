from odoo import models, fields, api
from datetime import datetime


class HospitalRoomInspection(models.Model):
    _name = 'hospital.room.inspection'
    _description = 'Room Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Inspection Reference', required=True, tracking=True)
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    room_id = fields.Many2one('hospital.room', string='Room', required=True, tracking=True)
    block_id = fields.Many2one('hospital.block', string='Block', related='room_id.block_id', store=True, tracking=True)
    remarks = fields.Text(string='Remarks', tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # Fields from the original model
    inspector_id = fields.Many2one('res.users', string='Inspector', tracking=True)
    inspection_date = fields.Datetime(string='Inspection Date', default=fields.Datetime.now, tracking=True)
    cleanliness = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Cleanliness', tracking=True)
    maintenance_required = fields.Boolean(string='Maintenance Required', tracking=True)
    maintenance_notes = fields.Text(string='Maintenance Notes', tracking=True)
    action_taken = fields.Text(string='Action Taken', tracking=True)
    
    def print_inspection_report(self):
        """
        This function prepares data for the inspection report.
        It groups inspections by block and returns structured data.
        """
        result = []
        if self:
            # Group by block
            blocks = {}
            for inspection in self:
                block_name = inspection.block_id.name or 'Unassigned'
                if block_name not in blocks:
                    blocks[block_name] = []
                    
                # Format data for each inspection
                inspection_data = {
                    'room_id': inspection.room_id.name or '',
                    'remarks': inspection.remarks or '',
                    'date': inspection.inspection_date.strftime('%Y-%m-%d %H:%M:%S') if inspection.inspection_date else '',
                    'user': inspection.user_id.name or '',
                }
                blocks[block_name].append(inspection_data)
            
            # Structure data for the report
            for block, inspections in blocks.items():
                result.append({
                    'block': block,
                    'inspection_info': inspections
                })
                
        return result


class HospitalRoomInspectionWizard(models.TransientModel):
    _name = 'hospital.room.inspection.wizard'
    _description = 'Room Inspection Wizard'
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    block_line_id = fields.Many2one('hospital.block', string='Block')
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    
    def inspection_report(self):
        """
        Generate the inspection report based on wizard criteria
        """
        self.ensure_one()
        domain = [
            ('inspection_date', '>=', datetime.combine(self.start_date, datetime.min.time())),
            ('inspection_date', '<=', datetime.combine(self.end_date, datetime.max.time())),
            ('company_id', '=', self.company_id.id)
        ]
        
        if self.block_line_id:
            domain.append(('block_id', '=', self.block_line_id.id))
        
        inspections = self.env['hospital.room.inspection'].search(domain)
        
        if not inspections:
            raise models.UserError("No inspections found for the selected criteria.")
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'futuristictech_clinical.room_inspection_report',
            'report_type': 'qweb-pdf',
            'data': {},
            'context': {'active_ids': inspections.ids},
        }