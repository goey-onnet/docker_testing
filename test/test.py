# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Course(models.Model):
    _name = 'res.course'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
    trainer_ids = fields.Many2many('res.partner', 'res_partner_res_course_rel1', domain=[('is_trainer', '=', True)], string="Trainer")

class Training(models.Model):
    _name = 'res.training'

    @api.multi
    @api.depends('attendee_ids')
    def _compute_total_attendee(self):
        for training in self:
            if training.attendee_ids:
                training.total_attendees = len(training.attendee_ids)

    name = fields.Char("Name", required=True)
    trainer_id = fields.Many2one('res.partner', domain=[('is_trainer', '=', True)], required=True)
    start_date_time = fields.Datetime('Start Time')
    end_date_time = fields.Datetime('End Time')
    total_hours = fields.Float('Total Hours')
    course_id = fields.Many2one('res.course', required=True, string="Course")
    tag_ids = fields.Many2many('res.partner.category', 'res_training_partner_category_rel', 'training_id', 'category_id', string ="Tags")
    state = fields.Selection([('unconfirmed', 'Unconfirmed'),
                              ('confirmed', 'Confirmed'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], default="unconfirmed", string="Status")
    attendee_ids = fields.Many2many('res.partner', 'res_training_res_partner_rel', 'training_id', 'partner_id', domain=[('is_attendee', '=', True)], string='Attendees')
    total_attendees = fields.Integer("Total Attendees", compute=_compute_total_attendee, store=True)

    @api.multi
    def set_confirm(self):
        self.state = 'confirmed'
        # self.write({'state':'confirmed'}) old api
    @api.multi
    def set_done(self):
        self.state = 'done'

    @api.multi
    def set_cancel(self):
        self.state = 'cancel'

    @api.onchange('start_date_time', 'end_date_time')
    def on_change_start_end_date(self):
        if self.start_date_time and self.end_date_time:
            self.total_hours = (self.end_date_time - self.start_date_time).days

    @api.onchange('course_id')
    def on_change_course_id(self):
         res= {'domain':{}}
         if self.course_id:
             res['domain']['trainer_id'] = [('id', 'in', self.course_id.trainer_ids.ids)]
         else:
             res['domain']['trainer_id'] = [('is_trainer', '=', True)]
         return res

    @api.onchange('trainer_id')
    def on_change_trainer_id(self):
        res = {'domain': {}}
        if self.trainer_id:
            c_ids = self.env['res.course'].search([('trainer_ids', '=', self.trainer_id.id)])
            res['domain']['course_id'] = [('id', 'in', c_ids.ids)]
        else:
            res['domain']['course_id'] = []
        return res

    @api.multi
    def training_test_action(self):
        print ("this is action.........")