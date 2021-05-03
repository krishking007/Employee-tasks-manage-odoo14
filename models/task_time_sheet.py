# -*- coding: utf-8 -*-


from odoo import fields, models

from odoo.exceptions import UserError

class TaskTimeSheet(models.Model):
    _name='task.timesheet'
    _description='Task Time Sheet'
    _inherit = ['mail.thread','mail.activity.mixin']
   
    
    activity_date=fields.Date("Date")
    responsible=fields.Many2one('res.users', 'Responsible')
    description=fields.Char("Description")
    timesheet_id=fields.Many2one('task.schedular', string='timesheets')
    activity_hours=fields.Float("Time")
    
        
