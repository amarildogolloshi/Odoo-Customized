from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta
import time

class config_appraisal(models.Model):
    _name = 'config.appraisal'
    _description = 'Appraisal Configuration'
    
    job_level_id = fields.Many2one('config.job.level', string="Employee Classification",required=1)
    report_id = fields.Many2one('ir.actions.report.xml', string="Appraisal Type",required=1)

class config_appraisal_rating(models.Model):
    _name = 'config.appraisal.rating'
    
    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    start_rate = fields.Float(string='Start Rate', digits=(16, 2))
    end_rate = fields.Float(string='End Rate', digits=(16, 2))
    description = fields.Char(string="Description")
    
class config_appraisal_evaluation(models.Model):
    _name = 'config.appraisal.evaluation'
    _description = 'Config Appraisal Evaluation'
    _order = 'appraisal_num'
    
    name = fields.Char(string="Name")
    appraisal_num = fields.Selection([(1, '1st'), (2, '2nd'), (3, '3rd'), (4, '4th'), (5, '5th'), (6, '6th'), (7, '7th'), (8, '8th'), (9, '9th'), (10, '10th')], default=1, required=True, string="Appraisal No.")
    due_date = fields.Date(string="Due Date")
    hr_employee_id = fields.Many2one('hr.employee', String="Employee")
        

    
