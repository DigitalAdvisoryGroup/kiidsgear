# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api, _
from odoo.exceptions import Warning,UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gift_voucher = fields.Boolean(string='Gift Voucher')
    child_cate = fields.Boolean(String='Enable Discount For Child Category')
    voucher_show_option = fields.Selection([('slider', 'Slider'), ('notification', 'Notification')], default='slider', string='Voucher show')
    voucher_notification_show = fields.Selection([('pageload', 'Page Load'), ('intervaltime', 'Interval')], default='pageload',string='Voucher show')
    interval_time = fields.Float(string="Enter Minute")
    delay_time = fields.Float(string="Enter Second")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter']
        res.update({
            'gift_voucher': param_obj.sudo().get_param('aspl_website_gift_voucher_ee.gift_voucher'),
            'child_cate': param_obj.sudo().get_param('aspl_website_gift_voucher_ee.child_cate'),
            'voucher_show_option': param_obj.sudo().get_param('aspl_website_gift_voucher_ee.voucher_show_option'),
            'voucher_notification_show': param_obj.sudo().get_param('aspl_website_gift_voucher_ee.voucher_notification_show'),
            'interval_time': float(param_obj.sudo().get_param('aspl_website_gift_voucher_ee.interval_time')),
            'delay_time': float(param_obj.sudo().get_param('aspl_website_gift_voucher_ee.delay_time')),
            })
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter']
        param_obj.sudo().set_param('aspl_website_gift_voucher_ee.gift_voucher',self.gift_voucher)
        param_obj.sudo().set_param('aspl_website_gift_voucher_ee.child_cate',self.child_cate)
        param_obj.sudo().set_param('aspl_website_gift_voucher_ee.voucher_show_option',self.voucher_show_option)
        param_obj.sudo().set_param('aspl_website_gift_voucher_ee.voucher_notification_show',self.voucher_notification_show)
        param_obj.sudo().set_param('aspl_website_gift_voucher_ee.interval_time',self.interval_time)
        param_obj.sudo().set_param('aspl_website_gift_voucher_ee.delay_time',self.delay_time)
        if self.gift_voucher ==  True:
            group_id = self.env.ref('aspl_website_gift_voucher_ee.group_voucher')
            group_id.write({'users': [(4, self.env.user.id)]})
        else:
            group_id = self.env.ref('aspl_website_gift_voucher_ee.group_voucher', False)
            group_id.write({'users': [(3, self.env.user.id)]})

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: