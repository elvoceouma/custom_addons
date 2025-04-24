from odoo import models, fields

TEAM_ROLE = [
    ('psychiatrist', 'Psychiatrist'),
    ('senior_registrar', 'Senior Registrar'),
    ('clinical_psychologist', 'Clinical Psychologist'),
    ('counsellor', 'Counsellor'),
    ('caretaker', 'Caretaker'),
    ('physician', 'Physician')
]

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    team_role = fields.Selection(TEAM_ROLE, string='Team Role', tracking=True)
