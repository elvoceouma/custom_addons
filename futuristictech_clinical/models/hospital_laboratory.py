#  -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LabTestType(models.Model):
    _name = 'hospital.lab.test.type'
    _description = 'Lab Test Type'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    category = fields.Selection([
        ('hematology', 'Hematology'),
        ('biochemistry', 'Biochemistry'),
        ('microbiology', 'Microbiology'),
        ('immunology', 'Immunology'),
        ('urine', 'Urine Analysis'),
        ('molecular', 'Molecular Biology'),
        ('other', 'Other')
    ], string='Category', default='other')



    def save(self):
        # Save the document and return to the list view
        self.ensure_one()
        if not self.file:
            raise ValidationError(_('Please upload a file.'))
        if not self.file_name:
            raise ValidationError(_('Please provide a file name.'))
        self.write({'file_name': self.file_name})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
# Individual Test Type Models
class HematologyTest(models.Model):
    _name = 'hematology.test'
    _description = 'Hematology Test'
    _inherit = 'hospital.lab.test.type'

class BiochemistryTest(models.Model):
    _name = 'biochemistry.test'
    _description = 'Biochemistry Test'
    _inherit = 'hospital.lab.test.type'

class HormonesTest(models.Model):
    _name = 'hormones.test'
    _description = 'Hormones Test'
    _inherit = 'hospital.lab.test.type'

class MicrobiologyTest(models.Model):
    _name = 'microbiology.test'
    _description = 'Microbiology Test'
    _inherit = 'hospital.lab.test.type'

class ImmunologyTest(models.Model):
    _name = 'immunology.test'
    _description = 'Immunology Test'
    _inherit = 'hospital.lab.test.type'

class UrineChemistryTest(models.Model):
    _name = 'urine.chemistry.test'
    _description = 'Urine Chemistry Test'
    _inherit = 'hospital.lab.test.type'

class UrineScreeningTest(models.Model):
    _name = 'urine.screening.test'
    _description = 'Urine Screening Test'
    _inherit = 'hospital.lab.test.type'

class DrugAssaysTest(models.Model):
    _name = 'drug.assays.test'
    _description = 'Drug Assays Test'
    _inherit = 'hospital.lab.test.type'

class MolecularBiologyTest(models.Model):
    _name = 'molecular.biology.test'
    _description = 'Molecular Biology Test'
    _inherit = 'hospital.lab.test.type'

class MiscelleneousTest(models.Model):
    _name = 'miscelleneous.test'
    _description = 'Miscelleneous Test'
    _inherit = 'hospital.lab.test.type'

class ProfileTest(models.Model):
    _name = 'profile.test'
    _description = 'Profile Test'
    _inherit = 'hospital.lab.test.type'