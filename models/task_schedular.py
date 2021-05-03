

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz

from odoo import fields, models, api


from odoo.exceptions import UserError

class TaskSchedular(models.Model):
    _name='task.schedular'
    _description='Task Schedular'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'expiry_date ASC'
	
    name=fields.Char('Task name', required=True)
    user_id = fields.Many2one(
        'res.users', string='Responsible', index=True, required=True,
         default=lambda self: self.env.user)
    description=fields.Text('Task description')
    start_date = fields.Date('Start Date', index=True, required=True)
    expiry_date = fields.Date('Expiry Date', index=True, required=True, track_visibility='onchange')
    state=fields.Selection([("new", "New"),
	    ("in_progress", "In Progress"),
	    ("completed", "Completed"),
	    ("expired", "Expired")],
	    default='new', track_visibility='onchange', index=True, group_expand="_expand_states")
    last_modification = fields.Datetime(readonly=True)
    planned_hours = fields.Float("Planned Hours",track_visibility='onchange')
    timesheet_hours = fields.Float("Timesheet", compute='_compute_timesheet_planned_hours', store=True)
    timesheets=fields.One2many('task.timesheet', 'timesheet_id', string='timesheet_id')
    days_to_expiry=fields.Integer('Days to expiry', compute='_days_to_expiry', store=True)
	

    @api.depends('timesheets', 'timesheets.activity_hours')
    def _compute_timesheet_planned_hours(self):
        total_time=0
        for item in self.timesheets:
            total_time = (total_time + item.activity_hours)
        self.timesheet_hours=total_time
    
	

    @api.depends('expiry_date')
    def _days_to_expiry(self):
        date1=datetime.strptime(str(fields.date.today()),'%Y-%m-%d')
        diff_date=0
        for item in self:
            if item.expiry_date:
                diff_date = (datetime.strptime(str(item.expiry_date), '%Y-%m-%d')-(date1)).days
                if diff_date<0 and item.state!='completed':
                    item.state='expired'
		    
        self.days_to_expiry=diff_date
    
	
    _sql_constraints = [('project_date_greater', 'check(expiry_date >= start_date)', 'Error! project start-date must be lower than project expiry_date')]

	
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]


    def write(self, values):
        # help to "YYY-MM-DD"
        values['last_modification']=fields.Datetime.now()
        return super(TaskSchedular, self).write(values)		

    def unlink(self):
	    for task in self:
		    if task.state =='completed':
			    raise UserError("You can not delete completed tasks")
        
